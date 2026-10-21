"""Train the shared T5 encoder with rating and answer-generation losses."""

import json
import math
import random
import time
from typing import Any, Literal

import torch
from pydantic import Field
from torch import nn
from torch.nn import functional as F
from transformers import (
    AutoTokenizer,
    T5ForConditionalGeneration,
    get_linear_schedule_with_warmup,
)
from transformers.modeling_outputs import BaseModelOutput
from viper.config import EvalConfig
from viper.randomness import capture_main_process_rng
from viper.resume import (
    DataLoaderConfiguration,
    DataLoaderResumeState,
    ResumeState,
    save_resume_state,
)
from viper.stages import StageContext, eval, train

from csts_pilot.answers import answer_id
from csts_pilot.diagnostics import summarize
from csts_pilot.training import CstsConfig, mixed_precision, prepare_tokens, write_json
from jep_pilot.loaders import load_answers, load_json, load_model


class JointConfig(CstsConfig):
    """Choose one objective while preserving inputs and student initialization."""

    objective: Literal["ratings", "answers", "joint"] = "joint"
    annotation_weight: float = Field(default=0.2, ge=0)
    shuffle_answers: bool = False
    checkpoint_metric: Literal["mse", "spearman"] = "mse"
    fixed_epoch_budget: bool = False


def selection_score(
    config: JointConfig, diagnostic: dict[str, Any], answer_ce: float | None
) -> float:
    """Use a minimization score while preserving the historical default."""
    value = (
        answer_ce
        if config.objective == "answers"
        else diagnostic[config.checkpoint_metric]
        if config.checkpoint_metric == "spearman"
        else diagnostic["mse_0_1"]
    )
    if value is None or not math.isfinite(value):
        raise ValueError("The checkpoint selection metric must be finite.")
    return (
        -value
        if config.objective != "answers" and config.checkpoint_metric == "spearman"
        else value
    )


class AnswerEncoder(nn.Module):
    """Give rating prediction and answer generation the same contextual states."""

    def __init__(self, config: JointConfig) -> None:
        super().__init__()
        self.t5 = T5ForConditionalGeneration.from_pretrained(
            config.model_id, revision=config.revision
        )
        self.projection = nn.Linear(
            self.t5.config.d_model, config.projection_dimension, bias=False
        )

    def encode(
        self, batch: dict[str, torch.Tensor]
    ) -> tuple[torch.Tensor, torch.Tensor]:
        """Pool passage states and preserve all states for the decoder."""
        hidden = self.t5.encoder(
            input_ids=batch["input_ids"], attention_mask=batch["attention_mask"]
        ).last_hidden_state
        mask = batch["pool_mask"].unsqueeze(-1)
        pooled = (hidden.float() * mask).sum(1) / mask.sum(1).clamp_min(1)
        return F.normalize(self.projection(pooled).float(), dim=-1), hidden

    def forward(self, batch: dict[str, torch.Tensor]) -> torch.Tensor:
        """Expose the same cosine representation as the rating-only encoder."""
        return self.encode(batch)[0]

    def answer_loss(
        self, hidden: torch.Tensor, attention: torch.Tensor, labels: torch.Tensor
    ) -> torch.Tensor:
        """Average cross-entropy within each accepted answer, then across answers."""
        decoded = self.t5(
            encoder_outputs=BaseModelOutput(last_hidden_state=hidden),
            attention_mask=attention,
            decoder_input_ids=self.t5.prepare_decoder_input_ids_from_labels(labels),
            use_cache=False,
        )
        token_loss = F.cross_entropy(
            decoded.logits.float().transpose(1, 2),
            labels,
            ignore_index=-100,
            reduction="none",
        )
        valid = labels.ne(-100)
        lengths = valid.sum(1)
        per_answer = (token_loss * valid).sum(1) / lengths.clamp_min(1)
        return (per_answer * lengths.gt(0)).sum() / lengths.gt(0).sum().clamp_min(1)


def answer_labels(
    rows: list[dict[str, Any]],
    answers: dict[str, dict[str, Any]],
    tokenizer: Any,
    config: JointConfig,
    *,
    shuffle: bool = False,
) -> torch.Tensor:
    """Cache all answer tokens and shuffle only among training caption conditions."""
    keys = [
        answer_id(row[side], row["condition"])
        for side in ("sentence1", "sentence2")
        for row in rows
    ]
    mapping = {
        key: answers[key]["answer"] for key in set(keys) if answers[key]["valid"]
    }
    if shuffle:
        groups: dict[str, list[str]] = {}
        for key in sorted(mapping):
            groups.setdefault(answers[key]["condition"], []).append(key)
        rng = random.Random(999)
        for members in groups.values():
            values = [mapping[key] for key in members]
            rng.shuffle(values)
            mapping.update(zip(members, values, strict=True))
    strings = [mapping.get(key, "") for key in keys]
    batch = tokenizer(strings, padding=True, return_tensors="pt")
    labels = batch["input_ids"].masked_fill(batch["attention_mask"].eq(0), -100)
    for index, key in enumerate(keys):
        if key not in mapping:
            labels[index] = -100
    return labels.to(config.device)


def select(
    tokens: dict[str, torch.Tensor], indices: torch.Tensor, n: int
) -> tuple[dict[str, torch.Tensor], torch.Tensor]:
    """Select both sides entirely on the device without a host synchronization."""
    sides = torch.cat((indices, indices + n))
    return {key: value[sides] for key, value in tokens.items()}, sides


@torch.no_grad()
def predictions(
    model: AnswerEncoder,
    rows: list[dict[str, Any]],
    tokens: dict[str, torch.Tensor],
    config: JointConfig,
    labels: torch.Tensor | None = None,
) -> tuple[list[dict[str, Any]], float | None]:
    """Evaluate the same source comparisons and optionally teacher-forced answers."""
    model.eval()
    scores = []
    total_ce = torch.zeros((), device=config.device)
    count = torch.zeros((), device=config.device)
    for start in range(0, len(rows), 128):
        indices = torch.arange(start, min(start + 128, len(rows)), device=config.device)
        batch, sides = select(tokens, indices, len(rows))
        with mixed_precision(config):
            z, hidden = model.encode(batch)
            left, right = z.chunk(2)
            scores.append((left * right).sum(-1).float())
            if labels is not None:
                selected_labels = labels[sides]
                valid_count = selected_labels.ne(-100).any(1).sum()
                ce = model.answer_loss(hidden, batch["attention_mask"], selected_labels)
                total_ce += ce * valid_count
                count += valid_count
    values = torch.cat(scores).cpu().tolist()
    ce_value = float(total_ce / count.clamp_min(1)) if labels is not None else None
    return [
        dict(row, prediction=value) for row, value in zip(rows, values, strict=True)
    ], ce_value


@train(config=JointConfig)
def fit(context: StageContext[JointConfig]) -> None:
    """Select annotations by CE and ratings by the configured development metric."""
    config = context.config
    torch.manual_seed(config.seed)
    random.seed(config.seed)
    torch.set_num_threads(4)
    torch.set_float32_matmul_precision("high")
    torch.cuda.reset_peak_memory_stats()
    training = load_json(context.inputs["training"])
    development = load_json(context.inputs["development"])
    tokenizer = AutoTokenizer.from_pretrained(
        config.model_id, revision=config.revision, use_fast=True
    )
    model = AnswerEncoder(config).to(config.device)
    if "initial_model" in context.inputs:
        model.load_state_dict(load_model(context.inputs["initial_model"])["state"])
    tokens = prepare_tokens(training, config, tokenizer)
    dev_tokens = prepare_tokens(development, config, tokenizer)
    answers = load_answers(context.inputs["answers"])
    labels = answer_labels(
        training, answers, tokenizer, config, shuffle=config.shuffle_answers
    )
    dev_labels = answer_labels(development, answers, tokenizer, config)
    answer_coverage = {
        "training": float(labels.ne(-100).any(1).float().mean()),
        "development": float(dev_labels.ne(-100).any(1).float().mean()),
    }
    answer_token_counts = {
        "training_nonpadding_per_epoch": int(labels.ne(-100).sum()),
        "development_nonpadding_per_pass": int(dev_labels.ne(-100).sum()),
        "training_padded_width": labels.shape[1],
        "development_padded_width": dev_labels.shape[1],
    }
    target = torch.tensor([row["target"] for row in training], device=config.device)
    optimizer = torch.optim.AdamW(
        [
            {"params": model.t5.parameters(), "lr": config.encoder_learning_rate},
            {
                "params": model.projection.parameters(),
                "lr": config.projection_learning_rate,
            },
        ],
        weight_decay=config.weight_decay,
    )
    steps_per_epoch = math.ceil(len(training) / config.batch_size)
    total_steps = steps_per_epoch * config.max_epochs
    scheduler = get_linear_schedule_with_warmup(
        optimizer, math.ceil(config.warmup_fraction * total_steps), total_steps
    )
    generator = torch.Generator().manual_seed(config.seed + 100)
    best, best_epoch, stale, step = float("inf"), 0, 0, 0
    history = []
    initial_rows, initial_ce = predictions(
        model, development, dev_tokens, config, dev_labels
    )
    initial_development = dict(summarize(initial_rows), answer_ce=initial_ce)
    gradient_check = None
    started = time.monotonic()
    for epoch in range(1, config.max_epochs + 1):
        model.train()
        # Copy the shuffled order once per epoch. Tokens and labels stay in VRAM.
        order = torch.randperm(len(training), generator=generator).to(config.device)
        totals = torch.zeros(2, device=config.device)
        for start in range(0, len(training), config.batch_size):
            indices = order[start : start + config.batch_size]
            batch, sides = select(tokens, indices, len(training))
            optimizer.zero_grad(set_to_none=True)
            with mixed_precision(config):
                z, hidden = model.encode(batch)
                left, right = z.chunk(2)
                mse = F.mse_loss((left * right).sum(-1), target[indices])
                ce = (
                    model.answer_loss(hidden, batch["attention_mask"], labels[sides])
                    if config.objective != "ratings"
                    else torch.zeros((), device=config.device)
                )
                loss = (
                    ce
                    if config.objective == "answers"
                    else mse + config.annotation_weight * ce
                )
            if step == 0 and config.objective == "joint":
                shared = model.t5.encoder.block[0].layer[0].SelfAttention.q.weight
                rating_gradient = torch.autograd.grad(mse, shared, retain_graph=True)[
                    0
                ].float()
                answer_gradient = torch.autograd.grad(ce, shared, retain_graph=True)[
                    0
                ].float()
                gradient_check = {
                    "rating_norm": float(rating_gradient.norm()),
                    "answer_norm": float(answer_gradient.norm()),
                    "weighted_answer_to_rating_ratio": float(
                        config.annotation_weight
                        * answer_gradient.norm()
                        / rating_gradient.norm().clamp_min(1e-12)
                    ),
                    "cosine": float(
                        F.cosine_similarity(
                            rating_gradient.flatten(), answer_gradient.flatten(), dim=0
                        )
                    ),
                }
            loss.backward()
            torch.nn.utils.clip_grad_norm_(
                model.parameters(), 1.0, error_if_nonfinite=True
            )
            optimizer.step()
            scheduler.step()
            totals += torch.stack((mse.detach(), ce.detach())) * len(indices)
            step += 1
        dev_rows, dev_ce = predictions(
            model, development, dev_tokens, config, dev_labels
        )
        diagnostic = summarize(dev_rows)
        train_mse, train_ce = (totals / len(training)).cpu().tolist()
        for name, value in (
            ("training_mse", train_mse),
            ("development_mse", diagnostic["mse_0_1"]),
            ("training_answer_ce", train_ce),
            ("development_answer_ce", dev_ce),
        ):
            context.metrics[name].record(value, step=epoch)
        if config.checkpoint_metric == "spearman":
            context.metrics["development_spearman"].record(
                diagnostic["spearman"], step=epoch
            )
        history.append(
            {
                "epoch": epoch,
                "step": step,
                "training_mse": train_mse,
                "training_answer_ce": train_ce,
                "development_answer_ce": dev_ce,
                "development": diagnostic,
                "elapsed_seconds": time.monotonic() - started,
            }
        )
        selected = selection_score(config, diagnostic, dev_ce)
        if selected < best:
            best, best_epoch, stale = selected, epoch, 0
            torch.save(
                {
                    "config": config.model_dump(),
                    "state": {
                        key: value.detach().cpu()
                        for key, value in model.state_dict().items()
                    },
                    "best_epoch": epoch,
                },
                context.outputs["model"],
            )
            write_json(context.outputs["development_predictions"], dev_rows)
        else:
            stale += 1
        print(json.dumps(history[-1]), flush=True)
        if stale >= config.patience and not config.fixed_epoch_budget:
            break
    selected_epoch = next(row for row in history if row["epoch"] == best_epoch)
    write_json(
        context.outputs["trace"],
        {
            "config": config.model_dump(),
            "initial_development": initial_development,
            "answer_coverage": answer_coverage,
            "answer_token_counts": answer_token_counts,
            "training_nonpadding_answer_tokens": answer_token_counts[
                "training_nonpadding_per_epoch"
            ]
            * len(history)
            if config.objective != "ratings"
            else 0,
            "initial_shared_gradients": gradient_check,
            "epochs": history,
            "best_epoch": best_epoch,
            "best_development_mse": selected_epoch["development"]["mse_0_1"],
            "selection_metric": "answer_ce"
            if config.objective == "answers"
            else config.checkpoint_metric,
            "best_selection_value": -best
            if config.objective != "answers" and config.checkpoint_metric == "spearman"
            else best,
            "elapsed_seconds": time.monotonic() - started,
            "peak_cuda_memory_bytes": torch.cuda.max_memory_allocated(),
        },
    )
    save_resume_state(
        context.outputs["resume_state"],
        ResumeState(
            optimizer_state={
                "optimizer": optimizer.state_dict(),
                "scheduler": scheduler.state_dict(),
            },
            main_process_rng=capture_main_process_rng(
                context.numpy_generators, capture_legacy_global=True
            ),
            dataloader=DataLoaderResumeState(
                configuration=DataLoaderConfiguration(workers=0),
                state_dict={
                    "completed_epoch": epoch,
                    "step": step,
                    "generator_state": generator.get_state(),
                },
            ),
        ),
    )


@eval(config=EvalConfig)
def evaluate(context: StageContext[EvalConfig]) -> None:
    """Score reserved comparisons using source passages and their conditions."""
    saved = load_model(context.inputs["model"])
    config = JointConfig.model_validate(saved["config"])
    model = AnswerEncoder(config).to(config.device)
    model.load_state_dict(saved["state"])
    tokenizer = AutoTokenizer.from_pretrained(
        config.model_id, revision=config.revision, use_fast=True
    )
    rows = load_json(context.inputs["test"])
    if load_json(context.inputs["holdout"]) != list(range(len(rows))):
        raise ValueError("Evaluation indices differ from the reserved evaluation set.")
    tokens = prepare_tokens(rows, config, tokenizer)
    scored, _ = predictions(model, rows, tokens, config)
    write_json(context.outputs["predictions"], scored)
