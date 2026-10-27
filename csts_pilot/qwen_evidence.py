"""Teach the existing Qwen encoder evidence tokens before rating regression."""

import time
from pathlib import Path
from types import SimpleNamespace
from typing import Any, Literal

import torch
from pydantic import Field
from safetensors.torch import load_file
from torch import nn
from torch.nn import functional as F
from viper.randomness import capture_main_process_rng
from viper.resume import (
    DataLoaderConfiguration,
    DataLoaderResumeState,
    ResumeState,
    save_resume_state,
)
from viper.stages import StageContext, build, train

from csts_pilot.answers import answer_id
from csts_pilot.baseline_models import (
    EOD,
    FitConfig,
    TokenPairs,
    load_backbone,
    load_tokenizer,
    pad_sequences,
    restore_parameters,
    state_digest,
    token_sequences,
    trainable_state,
    validate_rows,
)
from csts_pilot.baseline_stages import (
    fit_neural,
    predict_pairs,
    record_validation,
    save_neural,
)
from csts_pilot.convergence import (
    file_sha256,
    reset_rng,
    rng_digests,
    synchronize,
    write_json,
)
from csts_pilot.diagnostics import summarize
from csts_pilot.evidence_controls import PreparationConfig, checked_cache, passage_keys
from jep_pilot.loaders import load_json, load_model


class QwenEvidenceConfig(FitConfig):
    """Freeze one arm, one phase and all auxiliary-training input identities."""

    arm: Literal["ratings", "evidence"]
    phase: Literal["pretrain", "ratings"]
    training_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    validation_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    prepared_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    parent_sha256: str | None = Field(default=None, pattern=r"^[0-9a-f]{64}$")
    head_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    max_answer_tokens: int = Field(default=64, ge=2)

    def fit_config(self) -> FitConfig:
        """Keep inference checkpoints compatible with the reviewed rating scorer."""
        return FitConfig.model_validate(
            {key: getattr(self, key) for key in FitConfig.model_fields}
        )


@build(config=PreparationConfig)
def prepare_qwen_evidence(context: StageContext[PreparationConfig]) -> None:
    """Use accepted training evidence only, with the same row subset in both arms."""
    config = context.config
    for name, digest in (
        ("answers", config.answers_sha256),
        ("training", config.training_sha256),
        ("validation", config.validation_sha256),
    ):
        if file_sha256(context.inputs[name]) != digest:
            raise ValueError(f"Changed preparation input: {name}.")
    training = load_json(context.inputs["training"])
    validation = load_json(context.inputs["validation"])
    validate_rows(training)
    validate_rows(validation)
    train_keys, dev_keys = passage_keys(training), passage_keys(validation)
    records = checked_cache(context.inputs["answers"])
    if train_keys & dev_keys or set(records) != train_keys | dev_keys:
        raise ValueError(
            "Teacher-cache coverage or train/validation separation changed."
        )
    aligned = {
        key: records[key]["answer"]
        for key in sorted(train_keys)
        if records[key]["valid"]
    }
    common = [
        row
        for row in training
        if any(
            answer_id(row[side], row["condition"]) in aligned
            for side in ("sentence1", "sentence2")
        )
    ]
    if not common or not aligned:
        raise ValueError("No accepted training evidence.")
    write_json(
        context.outputs["prepared"],
        {
            "training": common,
            "aligned": aligned,
            "audit": {
                "training_rows": len(training),
                "stage_a_comparisons": len(common),
                "supervised_training_keys": len(aligned),
                "validation_evidence_used_for_training": False,
                "expert_verified": False,
                "transition": "terminal weights after the common fixed update budget",
            },
        },
    )


def evidence_tokens(
    rows: list[dict[str, Any]],
    mapping: dict[str, str],
    tokenizer: Any,
    config: FitConfig,
    max_answer_tokens: int,
) -> dict[str, tuple[list[int], list[int]]]:
    """Append evidence after the exact embedding prefix; label answer tokens only."""
    entries = {}
    for row in rows:
        for side in ("sentence1", "sentence2"):
            key = answer_id(row[side], row["condition"])
            if key in mapping and key not in entries:
                entries[key] = (row["condition"], row[side])
    if not entries:
        raise ValueError("No accepted evidence tokens to prepare.")
    # Batch both calls. The shared prefix tokenizer checks the full vocabulary;
    # repeating that operation per answer is expensive for Qwen's 151k tokens.
    prefixes = token_sequences(tokenizer, list(entries.values()), config)
    answers = tokenizer(
        [mapping[key] for key in entries],
        add_special_tokens=False,
        padding=False,
        truncation=False,
    )["input_ids"]
    eod = tokenizer.get_vocab()[EOD]
    result = {}
    for key, prefix, answer in zip(entries, prefixes, answers, strict=True):
        if not answer or len(answer) + 1 > max_answer_tokens:
            raise ValueError(
                "An evidence answer is empty or exceeds its declared token ceiling."
            )
        # The prefix includes EOD, as at embedding inference. Under causal
        # attention, evidence tokens cannot change any prefix hidden state.
        result[key] = (prefix + answer + [eod], [-100] * len(prefix) + answer + [eod])
    return result


def evidence_batch(
    selected: list[dict[str, Any]],
    sequences: dict[str, tuple[list[int], list[int]]],
    tokenizer: Any,
    config: FitConfig,
) -> tuple[dict[str, torch.Tensor], torch.Tensor]:
    """Retain only supported answers, including duplicate exposure from pair sampling."""
    keys = [
        answer_id(row[side], row["condition"])
        for side in ("sentence1", "sentence2")
        for row in selected
    ]
    values = [sequences[key] for key in keys if key in sequences]
    if not values:
        raise ValueError("An evidence microbatch has no accepted targets.")
    batch = pad_sequences(tokenizer, [ids for ids, _ in values], config)
    width = batch["input_ids"].shape[1]
    labels = []
    for ids, target in values:
        padding = [-100] * (width - len(ids))
        labels.append(
            padding + target if tokenizer.padding_side == "left" else target + padding
        )
    return batch, torch.tensor(labels, device=config.device)


def answer_loss_sum(
    hidden: torch.Tensor, labels: torch.Tensor, head: nn.Module
) -> torch.Tensor:
    """Sum per-answer mean causal CE, projecting only supervised positions."""
    mask = labels[:, 1:].ne(-100)
    lengths = mask.sum(1)
    if (lengths == 0).any():
        raise ValueError("Every evidence sequence needs supervised answer tokens.")
    logits = head(hidden[:, :-1][mask])
    losses = F.cross_entropy(logits.float(), labels[:, 1:][mask], reduction="none")
    answer_indices = torch.arange(len(labels), device=labels.device)[:, None].expand_as(
        mask
    )[mask]
    totals = losses.new_zeros(len(labels)).scatter_add(0, answer_indices, losses)
    return (totals / lengths).sum()


def load_head(path: Path, config: QwenEvidenceConfig) -> nn.Module:
    """Use a verified pretrained vocabulary projection, frozen during auxiliary training."""
    if file_sha256(path) != config.head_sha256:
        raise ValueError("The pretrained output-head bytes changed.")
    tensors = load_file(str(path), device="cpu")
    if set(tensors) != {"weight"}:
        raise ValueError("Unexpected vocabulary-head tensors.")
    weight = tensors["weight"]
    if (
        weight.ndim != 2
        or weight.shape[1] != config.embedding_dimension
        or not torch.isfinite(weight).all()
    ):
        raise ValueError("Invalid pretrained vocabulary projection.")
    head = nn.Linear(config.embedding_dimension, len(weight), bias=False, device="meta")
    head.weight = nn.Parameter(
        weight.to(
            config.device,
            dtype=torch.bfloat16 if config.device == "cuda" else torch.float32,
        ),
        requires_grad=False,
    )
    return head


def save_first_phase(
    context: Any,
    model: nn.Module,
    optimizer: Any,
    generator: Any,
    config: FitConfig,
    epoch: int,
    step: int,
) -> None:
    """Persist terminal adapters and optimizer/RNG state before rating training."""
    save_neural(context.outputs["last_model"], model, config, epoch, step)
    save_neural(context.outputs["model"], model, config, epoch, step)
    save_resume_state(
        context.outputs["resume_state"],
        ResumeState(
            optimizer_state={"optimizer": optimizer.state_dict()},
            main_process_rng=capture_main_process_rng(
                context.numpy_generators, capture_legacy_global=True
            ),
            dataloader=DataLoaderResumeState(
                configuration=DataLoaderConfiguration(workers=0),
                state_dict={
                    "epoch": epoch,
                    "step": step,
                    "generator_state": generator.get_state(),
                    "last_model_sha256": file_sha256(context.outputs["last_model"]),
                },
            ),
        ),
    )


@train(config=QwenEvidenceConfig)
def fit_qwen_evidence(context: StageContext[QwenEvidenceConfig]) -> None:
    """Run fixed phase A or the existing patience-selected rating phase B."""
    config = context.config
    for name in ("training", "validation", "prepared"):
        if file_sha256(context.inputs[name]) != getattr(config, name + "_sha256"):
            raise ValueError(f"Changed {name} input.")
    if (
        config.kind != "lora"
        or config.start_epoch
        or config.schedule != "constant"
        or config.warmup_fraction
    ):
        raise ValueError(
            "This comparison requires fresh phase optimizers and constant-rate LoRA."
        )
    if (config.phase == "ratings") != (config.parent_sha256 is not None):
        raise ValueError("Only phase B restores a terminal phase-A checkpoint.")
    prepared = load_json(context.inputs["prepared"])
    fit = config.fit_config()
    reset_rng(config.seed)
    tokenizer = load_tokenizer(fit)
    model = load_backbone(fit, adapters=fit)
    if config.parent_sha256 is not None:
        if file_sha256(context.inputs["parent_model"]) != config.parent_sha256:
            raise ValueError("Terminal phase-A checkpoint identity changed.")
        saved = load_model(context.inputs["parent_model"])
        restore_parameters(model, saved["state"])
    training_rows = (
        prepared["training"]
        if config.phase == "pretrain"
        else load_json(context.inputs["training"])
    )
    training = TokenPairs(training_rows, fit, tokenizer)
    validation = TokenPairs(load_json(context.inputs["validation"]), fit, tokenizer)
    # A repeatable phase boundary also removes model-loading/head-loading RNG effects.
    reset_rng(config.seed + (1000 if config.phase == "pretrain" else 2000))
    initial_rng = rng_digests(config.device)
    if config.phase == "ratings":
        inner = SimpleNamespace(
            config=fit,
            inputs=context.inputs,
            outputs=context.outputs,
            metrics=context.metrics,
            numpy_generators=context.numpy_generators,
        )
        fit_neural(inner, model, training, validation)
        trace = load_json(context.outputs["trace"])
        trace.update(
            arm=config.arm,
            phase=config.phase,
            parent_sha256=config.parent_sha256,
            initial_rng=initial_rng,
            protocol_config=config.model_dump(),
        )
        write_json(context.outputs["trace"], trace)
        return

    sequences = evidence_tokens(
        training_rows, prepared["aligned"], tokenizer, fit, config.max_answer_tokens
    )
    head = (
        load_head(context.inputs["head"], config) if config.arm == "evidence" else None
    )
    reset_rng(config.seed + 1000)
    params = [p for p in model.parameters() if p.requires_grad]
    optimizer = torch.optim.AdamW(
        params, lr=fit.learning_rate, weight_decay=fit.weight_decay
    )
    generator = torch.Generator().manual_seed(config.seed + 100)
    targets = torch.tensor(
        [row["target"] for row in training_rows], device=config.device
    )
    initial = state_digest(trainable_state(model))
    epochs: list[dict[str, Any]] = []
    step = 0
    started = time.monotonic()
    first_gradient = None
    for epoch in range(1, config.max_epochs + 1):
        model.train()
        order = torch.randperm(len(training_rows), generator=generator)
        total_loss, total_units, input_tokens = 0.0, 0, 0
        for start in range(0, len(order), config.batch_size):
            if time.monotonic() - started >= config.max_seconds:
                raise TimeoutError(
                    "The fixed first-phase budget was not completed; preserve the attempt."
                )
            indices = order[start : start + config.batch_size]
            selected = [training_rows[i] for i in indices.tolist()]
            units = (
                sum(
                    answer_id(r[s], r["condition"]) in sequences
                    for r in selected
                    for s in ("sentence1", "sentence2")
                )
                if head is not None
                else len(indices)
            )
            optimizer.zero_grad(set_to_none=True)
            for offset in range(0, len(indices), config.microbatch_size):
                micro = indices[offset : offset + config.microbatch_size]
                if head is None:
                    loss = (
                        F.mse_loss(
                            training.scores(model, micro).float(),
                            targets[micro].float(),
                            reduction="sum",
                        )
                        / units
                    )
                else:
                    chosen = [training_rows[i] for i in micro.tolist()]
                    batch, labels = evidence_batch(chosen, sequences, tokenizer, fit)
                    input_tokens += int(batch["attention_mask"].sum())
                    with torch.autocast(
                        config.device,
                        enabled=config.device == "cuda",
                        dtype=torch.bfloat16,
                        cache_enabled=False,
                    ):
                        hidden = model(**batch).last_hidden_state
                        loss = answer_loss_sum(hidden, labels, head) / units
                if not torch.isfinite(loss):
                    raise ValueError("Nonfinite auxiliary-training loss.")
                loss.backward()
                total_loss += float(loss.detach()) * units
            gradient = float(
                torch.nn.utils.clip_grad_norm_(params, 1.0, error_if_nonfinite=True)
            )
            if first_gradient is None:
                first_gradient = gradient
                if gradient <= 0:
                    raise ValueError(
                        "The first-phase objective does not reach the shared adapters."
                    )
            optimizer.step()
            step += 1
            total_units += units
            if step % 25 == 0:
                write_json(
                    context.outputs["trace"],
                    {
                        "status": "running",
                        "arm": config.arm,
                        "phase": "pretrain",
                        "current_epoch": epoch,
                        "updates": step,
                        "epochs": epochs,
                        "completed_epoch": epoch - 1,
                        "elapsed_seconds": time.monotonic() - started,
                    },
                )
        predictions = predict_pairs(model, validation, fit.microbatch_size)
        diagnostics = summarize(predictions)
        record_validation(context, diagnostics, epoch)
        context.metrics["training_objective"].record(
            total_loss / total_units, step=epoch
        )
        record = {
            "epoch": epoch,
            "step": step,
            "training_objective": total_loss / total_units,
            "validation": diagnostics,
            "batch_order_sha256": state_digest({"order": order}),
            "supervised_units": total_units,
            "answer_input_tokens": input_tokens,
            "rating_input_tokens": training.nonpadding_tokens,
            "elapsed_seconds": time.monotonic() - started,
        }
        epochs.append(record)
        save_first_phase(context, model, optimizer, generator, fit, epoch, step)
        write_json(context.outputs["validation_predictions"], predictions)
        write_json(
            context.outputs["trace"],
            {
                "status": "complete" if epoch == config.max_epochs else "running",
                "arm": config.arm,
                "phase": "pretrain",
                "config": config.model_dump(),
                "initial_trainable_sha256": initial,
                "terminal_trainable_sha256": state_digest(trainable_state(model)),
                "initial_rng": initial_rng,
                "epochs": epochs,
                "completed_epoch": epoch,
                "actual_updates": step,
                "training_rows": len(training_rows),
                "first_shared_adapter_gradient_norm": first_gradient,
                "terminal_model_sha256": file_sha256(context.outputs["last_model"]),
                "elapsed_seconds": time.monotonic() - started,
                "stop_reason": "fixed_update_budget"
                if epoch == config.max_epochs
                else None,
            },
        )
        print({"arm": config.arm, "phase": "pretrain", **record}, flush=True)
    synchronize(config.device)


def validate_matched_phases(
    traces: dict[str, dict[str, Any]],
    phase_a_epochs: int,
    *,
    allow_budget_censoring: bool = False,
) -> None:
    """Check exposure and restored weights; permit declared pilot time limits explicitly."""
    first = traces["ratings"]["pretrain"]
    accepted_stops = {"validation_patience", "epoch_budget"}
    if allow_budget_censoring:
        accepted_stops.add("resource_budget")
    for arm in ("ratings", "evidence"):
        a, b = traces[arm]["pretrain"], traces[arm]["ratings"]
        if b["stop_reason"] not in accepted_stops:
            raise ValueError(
                "Rating training was budget-censored; preserve its checkpoint before testing."
            )
        for key in (
            "initial_trainable_sha256",
            "actual_updates",
            "training_rows",
            "initial_rng",
        ):
            if a[key] != first[key]:
                raise ValueError(f"Unmatched first-phase {key}.")
        if (
            a["completed_epoch"] != phase_a_epochs
            or a["stop_reason"] != "fixed_update_budget"
        ):
            raise ValueError("Incomplete fixed first phase.")
        if [e["batch_order_sha256"] for e in a["epochs"]] != [
            e["batch_order_sha256"] for e in first["epochs"]
        ]:
            raise ValueError("Different first-phase comparison orders.")
        if (
            b["initial_trainable_sha256"] != a["terminal_trainable_sha256"]
            or b["parent_sha256"] != a["terminal_model_sha256"]
        ):
            raise ValueError("Phase B did not restore terminal phase-A adapters.")
        reference = traces["ratings"]["ratings"]
        count = min(len(b["epochs"]), len(reference["epochs"]))
        if b["initial_rng"] != reference["initial_rng"] or [
            e["batch_order_sha256"] for e in b["epochs"][:count]
        ] != [e["batch_order_sha256"] for e in reference["epochs"][:count]]:
            raise ValueError("Different second-phase RNG or comparison orders.")
