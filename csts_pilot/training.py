"""Fit a T5 bi-encoder with development selection through native VIPER stages."""

import json
import math
import random
import time
from pathlib import Path
from typing import Any

import torch
from pydantic import Field
from torch import nn
from torch.nn import functional as F
from transformers import AutoTokenizer, T5EncoderModel, get_linear_schedule_with_warmup
from viper.config import EvalConfig, TrainConfig
from viper.randomness import capture_main_process_rng
from viper.resume import (
    DataLoaderConfiguration,
    DataLoaderResumeState,
    ResumeState,
    save_resume_state,
)
from viper.stages import StageContext, eval, train

from csts_pilot.diagnostics import summarize
from jep_pilot.loaders import load_json, load_model


class CstsConfig(TrainConfig):
    """Declare the backbone, optimizer, sampling and stopping rules."""

    model_id: str = "google/flan-t5-small"
    revision: str = "0fc9ddf78a1e988dac52e2dac162b0ede4fd74ab"
    condition: bool = True
    projection_dimension: int = Field(default=128, ge=1)
    encoder_learning_rate: float = Field(default=3e-5, gt=0)
    projection_learning_rate: float = Field(default=1e-3, gt=0)
    batch_size: int = Field(default=32, ge=1)
    max_epochs: int = Field(default=8, ge=1)
    patience: int = Field(default=3, ge=1)
    warmup_fraction: float = Field(default=0.1, ge=0, lt=1)
    weight_decay: float = Field(default=0.01, ge=0)
    max_length: int = Field(default=160, ge=8)
    seed: int = 7
    device: str = "cuda"
    fit_check: bool = False


class RatingEncoder(nn.Module):
    """Condition token states on a question and pool passage token states."""

    def __init__(self, config: CstsConfig) -> None:
        super().__init__()
        self.encoder = T5EncoderModel.from_pretrained(
            config.model_id, revision=config.revision
        )
        self.projection = nn.Linear(
            self.encoder.config.d_model, config.projection_dimension, bias=False
        )

    def forward(self, batch: dict[str, torch.Tensor]) -> torch.Tensor:
        """Return unit embeddings with condition tokens excluded from the mean."""
        hidden = self.encoder(
            input_ids=batch["input_ids"], attention_mask=batch["attention_mask"]
        ).last_hidden_state.float()
        mask = batch["pool_mask"].unsqueeze(-1)
        pooled = (hidden * mask).sum(1) / mask.sum(1).clamp_min(1)
        return F.normalize(self.projection(pooled).float(), dim=-1)


def mixed_precision(config: CstsConfig) -> Any:
    """Refresh cast weights inside VIPER's enclosing autocast context."""
    return torch.autocast(
        "cuda",
        dtype=torch.bfloat16,
        enabled=config.device == "cuda",
        cache_enabled=False,
    )


def prepare_tokens(
    rows: list[dict[str, Any]], config: CstsConfig, tokenizer: Any
) -> dict[str, torch.Tensor]:
    """Tokenize once and retain the exact passage span for masked mean pooling."""
    texts, starts = [], []
    for side in ("sentence1", "sentence2"):
        for row in rows:
            prefix = (
                f"Condition: {row['condition']}\nPassage: "
                if config.condition
                else "Passage: "
            )
            texts.append(prefix + row[side])
            starts.append(len(prefix))
    encoded = tokenizer(
        texts,
        padding=True,
        truncation=True,
        max_length=config.max_length,
        return_offsets_mapping=True,
        return_tensors="pt",
    )
    offsets = encoded.pop("offset_mapping")
    passage_start = torch.tensor(starts).unsqueeze(-1)
    pool_mask = (offsets[:, :, 1] > passage_start) & (
        offsets[:, :, 1] > offsets[:, :, 0]
    )
    if not pool_mask.any(dim=1).all():
        raise ValueError("A passage was fully truncated or its pooling mask is empty.")
    return {
        "input_ids": encoded["input_ids"].to(config.device),
        "attention_mask": encoded["attention_mask"].to(config.device),
        "pool_mask": pool_mask.to(config.device),
    }


def score_batch(
    model: RatingEncoder, tokens: dict[str, torch.Tensor], indices: torch.Tensor, n: int
) -> torch.Tensor:
    """Encode both passages in one call and return their cosine similarity."""
    sides = torch.cat((indices, indices + n))
    selected = {key: value[sides] for key, value in tokens.items()}
    width = int(selected["attention_mask"].sum(1).max().item())
    selected = {key: value[:, :width] for key, value in selected.items()}
    left, right = model(selected).chunk(2)
    return (left * right).sum(-1)


@torch.no_grad()
def predict(
    model: RatingEncoder,
    rows: list[dict[str, Any]],
    tokens: dict[str, torch.Tensor],
    config: CstsConfig,
) -> list[dict[str, Any]]:
    """Save individual predictions with identities for independent diagnostics."""
    model.eval()
    values: list[float] = []
    for start in range(0, len(rows), 128):
        index = torch.arange(start, min(start + 128, len(rows)), device=config.device)
        with mixed_precision(config):
            values.extend(
                score_batch(model, tokens, index, len(rows)).float().cpu().tolist()
            )
    return [
        dict(row, prediction=value) for row, value in zip(rows, values, strict=True)
    ]


def write_json(path: Path, value: Any) -> None:
    """Write strict JSON so nonfinite measurements fail immediately."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, allow_nan=False) + "\n")


@train(config=CstsConfig)
def fit(context: StageContext[CstsConfig]) -> None:
    """Train full epochs and save the checkpoint with minimum development MSE."""
    config = context.config
    random.seed(config.seed)
    torch.manual_seed(config.seed)
    torch.set_num_threads(4)
    torch.set_float32_matmul_precision("high")
    if config.device == "cuda":
        torch.cuda.reset_peak_memory_stats()
    training = load_json(context.inputs["training"])
    development = load_json(context.inputs["development"])
    if config.fit_check:
        training = random.Random(7).sample(training, 64)
        development = training
    tokenizer = AutoTokenizer.from_pretrained(
        config.model_id, revision=config.revision, use_fast=True
    )
    model = RatingEncoder(config).to(config.device)
    training_tokens = prepare_tokens(training, config, tokenizer)
    development_tokens = prepare_tokens(development, config, tokenizer)
    target = torch.tensor([row["target"] for row in training], device=config.device)
    optimizer = torch.optim.AdamW(
        [
            {"params": model.encoder.parameters(), "lr": config.encoder_learning_rate},
            {
                "params": model.projection.parameters(),
                "lr": config.projection_learning_rate,
            },
        ],
        weight_decay=config.weight_decay,
    )
    steps_per_epoch = math.ceil(len(training) / config.batch_size)
    total_steps = config.max_epochs * steps_per_epoch
    scheduler = get_linear_schedule_with_warmup(
        optimizer, math.ceil(config.warmup_fraction * total_steps), total_steps
    )
    baseline = float(torch.mean((target - target.mean()) ** 2))
    initial_rows = predict(model, development, development_tokens, config)
    initial = summarize(initial_rows)
    generator = torch.Generator().manual_seed(config.seed + 100)
    best_mse, best_epoch, stale, step = float("inf"), 0, 0, 0
    history: list[dict[str, Any]] = []
    batch_trace: list[dict[str, Any]] = []
    start_time = time.monotonic()
    for epoch in range(1, config.max_epochs + 1):
        model.train()
        order = torch.randperm(len(training), generator=generator)
        epoch_error = torch.zeros((), device=config.device)
        for start in range(0, len(order), config.batch_size):
            index = order[start : start + config.batch_size].to(config.device)
            optimizer.zero_grad(set_to_none=True)
            with mixed_precision(config):
                scores = score_batch(model, training_tokens, index, len(training))
                loss = F.mse_loss(scores, target[index])
            loss.backward()
            gradient_norm = torch.nn.utils.clip_grad_norm_(
                model.parameters(), 1.0, error_if_nonfinite=True
            )
            optimizer.step()
            scheduler.step()
            step += 1
            epoch_error += loss.detach() * len(index)
            if step % 25 == 0:
                batch_trace.append(
                    {
                        "step": step,
                        "mse": float(loss.detach()),
                        "gradient_norm": float(gradient_norm),
                        "encoder_lr": scheduler.get_last_lr()[0],
                        "projection_lr": scheduler.get_last_lr()[1],
                    }
                )
        dev_rows = predict(model, development, development_tokens, config)
        diagnostics = summarize(dev_rows)
        train_mse = float(epoch_error / len(training))
        context.metrics["training_mse"].record(train_mse, step=epoch)
        context.metrics["development_mse"].record(diagnostics["mse_0_1"], step=epoch)
        history.append(
            {
                "epoch": epoch,
                "step": step,
                "training_mse": train_mse,
                "development": diagnostics,
                "elapsed_seconds": time.monotonic() - start_time,
            }
        )
        print(
            json.dumps(
                {
                    "epoch": epoch,
                    "train_mse": train_mse,
                    "dev_mse": diagnostics["mse_0_1"],
                    "dev_spearman": diagnostics["spearman"],
                }
            ),
            flush=True,
        )
        if diagnostics["mse_0_1"] < best_mse:
            best_mse, best_epoch, stale = diagnostics["mse_0_1"], epoch, 0
            context.outputs["model"].parent.mkdir(parents=True, exist_ok=True)
            torch.save(
                {
                    "config": config.model_dump(),
                    "state": {
                        key: value.detach().cpu()
                        for key, value in model.state_dict().items()
                    },
                    "best_epoch": epoch,
                    "development_mse": best_mse,
                },
                context.outputs["model"],
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
            write_json(context.outputs["development_predictions"], dev_rows)
        else:
            stale += 1
        if config.fit_check and best_mse < min(
            baseline * 0.7, initial["mse_0_1"] * 0.5
        ):
            break
        if stale >= config.patience:
            break
    saved = load_model(context.outputs["model"])
    model.load_state_dict(saved["state"])
    train_rows = predict(model, training, training_tokens, config)
    write_json(
        context.outputs["trace"],
        {
            "config": config.model_dump(),
            "initial_development": initial,
            "train_mean_baseline_mse": baseline,
            "best_epoch": best_epoch,
            "best_development_mse": best_mse,
            "epochs": history,
            "batches": batch_trace,
            "selected_training": summarize(train_rows),
            "fit_check_passed": (
                best_mse < min(baseline * 0.7, initial["mse_0_1"] * 0.5)
            )
            if config.fit_check
            else None,
            "elapsed_seconds": time.monotonic() - start_time,
            "peak_cuda_memory_bytes": torch.cuda.max_memory_allocated()
            if config.device == "cuda"
            else 0,
            "parameter_count": sum(
                parameter.numel() for parameter in model.parameters()
            ),
        },
    )


@eval(config=EvalConfig)
def evaluate(context: StageContext[EvalConfig]) -> None:
    """Evaluate a selected checkpoint using original and omitted conditions."""
    saved = load_model(context.inputs["model"])
    config = CstsConfig.model_validate(saved["config"])
    model = RatingEncoder(config).to(config.device)
    model.load_state_dict(saved["state"])
    tokenizer = AutoTokenizer.from_pretrained(
        config.model_id, revision=config.revision, use_fast=True
    )
    rows = load_json(context.inputs["test"])
    if load_json(context.inputs["holdout"]) != list(range(len(rows))):
        raise ValueError("Evaluation indices differ from the reserved evaluation set.")
    tokens = prepare_tokens(rows, config, tokenizer)
    predictions = predict(model, rows, tokens, config)
    write_json(context.outputs["predictions"], predictions)
