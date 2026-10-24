"""Matched evidence-pretraining controls with passage-only similarity inference."""

import json
import math
import random
import shutil
import time
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Literal

import torch
from pydantic import ConfigDict, Field
from transformers import AutoTokenizer
from viper.config import BuildConfig
from viper.randomness import capture_main_process_rng
from viper.resume import (
    DataLoaderConfiguration,
    DataLoaderResumeState,
    ResumeState,
    save_resume_state,
)
from viper.stages import StageContext, build, eval, train

from csts_pilot.answers import answer_id, parse_response, review_accepts
from csts_pilot.convergence import (
    TestConfig,
    file_sha256,
    reset_rng,
    rng_digests,
    synchronize,
    write_json,
)
from csts_pilot.data import canonical
from csts_pilot.diagnostics import summarize
from csts_pilot.early_stopping import ValidationPatience
from csts_pilot.joint import AnswerEncoder, predictions, rating_loss, select
from csts_pilot.training import CstsConfig, mixed_precision, prepare_tokens
from jep_pilot.loaders import load_json, load_model

Arm = Literal["ratings", "evidence", "shuffled"]


class PreparationConfig(BuildConfig):
    """Bind the previously generated teacher cache and source partitions."""

    model_config = ConfigDict(extra="forbid", frozen=True)
    answers_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    training_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    validation_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    shuffle_seed: int = 61024


class EvidenceConfig(CstsConfig):
    """One phase of a prospectively specified, matched three-arm screen."""

    model_config = ConfigDict(extra="forbid", frozen=True)
    arm: Arm
    phase: Literal["pretrain", "ratings"]
    training_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    validation_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    prepared_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    initial_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    linear_epochs: int = Field(default=24, ge=1)
    continuation_encoder_rate: float = Field(default=3e-6, gt=0)
    continuation_projection_rate: float = Field(default=1e-4, gt=0)
    max_seconds: float = Field(default=2400, gt=0)


class EvidenceTestConfig(TestConfig):
    """Name the frozen arm as well as the checkpoint and cohort identities."""

    arm: Arm


class EvidencePredictionConfig(BuildConfig):
    """Bind GPU prediction capture to the same frozen test identities."""

    arm: Arm
    model_sha256: str
    selection_sha256: str
    test_sha256: str


def checked_cache(path: Path) -> dict[str, dict[str, Any]]:
    """Reject duplicates, altered identities and unverified accepted evidence."""
    records = {}
    for line in path.read_text().splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        key = answer_id(row["passage"], row["condition"])
        if key != row["id"] or key in records or type(row.get("valid")) is not bool:
            raise ValueError(
                "Teacher cache identity, uniqueness or acceptance changed."
            )
        if row["valid"]:
            parsed = parse_response(row["passage"], row.get("response", ""))
            if (
                not parsed["valid"]
                or parsed["answer"] != row.get("answer")
                or not review_accepts(row.get("review_response", ""))
            ):
                raise ValueError("An accepted teacher answer fails its source checks.")
        records[key] = row
    return records


def passage_keys(rows: list[dict[str, Any]]) -> set[str]:
    """Identify single-passage inputs independently of similarity labels."""
    return {
        answer_id(row[side], row["condition"])
        for row in rows
        for side in ("sentence1", "sentence2")
    }


def aligned_and_shuffled(
    keys: set[str], records: dict[str, dict[str, Any]], seed: int
) -> tuple[dict[str, str], dict[str, str], dict[str, str]]:
    """Shuffle within training conditions and share only effectively changed keys."""
    groups: dict[str, list[str]] = defaultdict(list)
    for key in sorted(keys):
        if records[key]["valid"]:
            groups[canonical(records[key]["condition"])].append(key)
    aligned, shuffled, donors = {}, {}, {}
    rng = random.Random(seed)
    for members in groups.values():
        rng.shuffle(members)
        members.sort(key=lambda key: canonical(records[key]["answer"]))
        counts = Counter(canonical(records[key]["answer"]) for key in members)
        offset = max(counts.values())
        if len(counts) < 2:
            continue
        rotated = members[offset:] + members[:offset]
        for key, donor in zip(members, rotated, strict=True):
            if canonical(records[key]["answer"]) == canonical(records[donor]["answer"]):
                continue
            aligned[key], shuffled[key] = (
                records[key]["answer"],
                records[donor]["answer"],
            )
            donors[key] = donor
        kept = [key for key in members if key in aligned]
        if Counter(canonical(aligned[key]) for key in kept) != Counter(
            canonical(shuffled[key]) for key in kept
        ):
            raise ValueError("Shuffling changed the answer distribution.")
    if not aligned or set(aligned) != set(shuffled):
        raise ValueError("No effective, matched within-condition shuffle is available.")
    return aligned, shuffled, donors


@build(config=PreparationConfig)
def prepare_evidence(context: StageContext[PreparationConfig]) -> None:
    """Freeze training-only shuffles, common coverage and the cached source audit."""
    config = context.config
    for name, digest in (
        ("answers", config.answers_sha256),
        ("training", config.training_sha256),
        ("validation", config.validation_sha256),
    ):
        if file_sha256(context.inputs[name]) != digest:
            raise ValueError(f"Changed preparation input: {name}.")
    training, validation = (
        load_json(context.inputs["training"]),
        load_json(context.inputs["validation"]),
    )
    train_keys, dev_keys = passage_keys(training), passage_keys(validation)
    if train_keys & dev_keys:
        raise ValueError("Training and validation share passage-condition inputs.")
    records = checked_cache(context.inputs["answers"])
    if set(records) != train_keys | dev_keys:
        raise ValueError(
            "The teacher cache differs from the declared training/validation inputs."
        )
    aligned, shuffled, donors = aligned_and_shuffled(
        train_keys, records, config.shuffle_seed
    )
    common_rows = [
        row
        for row in training
        if any(
            answer_id(row[side], row["condition"]) in aligned
            for side in ("sentence1", "sentence2")
        )
    ]
    audit = {
        "cache_records": len(records),
        "accepted_records": sum(r["valid"] for r in records.values()),
        "training_keys": len(train_keys),
        "validation_keys": len(dev_keys),
        "supervised_training_keys": len(aligned),
        "stage_a_comparisons": len(common_rows),
        "unchanged_supervised_answers": 0,
        "shuffle_scope": "training only, within condition",
        "stage_a_coverage": "identical comparison subset and answer mask in all arms",
        "stage_a_transition": "terminal weights after six fixed epochs",
        "expert_verified": False,
    }
    write_json(
        context.outputs["prepared"],
        {
            "training": common_rows,
            "aligned": aligned,
            "shuffled": shuffled,
            "donors": donors,
            "audit": audit,
        },
    )


def targets_for_rows(
    rows: list[dict[str, Any]], mapping: dict[str, str], tokenizer: Any, device: str
) -> torch.Tensor:
    """Mask unsupported answers while preserving the same passage order as pooling."""
    keys = [
        answer_id(row[side], row["condition"])
        for side in ("sentence1", "sentence2")
        for row in rows
    ]
    encoded = tokenizer(
        [mapping.get(key, "") for key in keys], padding=True, return_tensors="pt"
    )
    labels = encoded["input_ids"].masked_fill(encoded["attention_mask"].eq(0), -100)
    for index, key in enumerate(keys):
        if key not in mapping:
            labels[index] = -100
    return labels.to(device)


def phase_rates(
    config: EvidenceConfig, epoch: int, update: int, updates_per_epoch: int
) -> tuple[float, float]:
    """Preserve the 24-epoch rating schedule, then the recorded constant-rate phase."""
    if config.phase == "ratings" and epoch > config.linear_epochs:
        return config.continuation_encoder_rate, config.continuation_projection_rate
    epochs = config.max_epochs if config.phase == "pretrain" else config.linear_epochs
    total = epochs * updates_per_epoch
    warmup = math.ceil(config.warmup_fraction * total)
    factor = (
        update / warmup
        if update < warmup
        else max(0, (total - update) / max(1, total - warmup))
    )
    return (
        config.encoder_learning_rate * factor,
        config.projection_learning_rate * factor,
    )


def save_evidence_checkpoint(
    path: Path, model: AnswerEncoder, config: EvidenceConfig, epoch: int, step: int
) -> None:
    """Store detached weights with their actual epoch and optimizer-update identity."""
    torch.save(
        {
            "config": config.model_dump(),
            "epoch": epoch,
            "step": step,
            "state": {k: v.detach().cpu() for k, v in model.state_dict().items()},
        },
        path,
    )


@train(config=EvidenceConfig)
def fit_evidence(context: StageContext[EvidenceConfig]) -> None:
    """Fit one controlled phase; choose rating checkpoints only with validation."""
    config = context.config
    for name, digest in (
        ("training", config.training_sha256),
        ("validation", config.validation_sha256),
        ("prepared", config.prepared_sha256),
        ("initial_model", config.initial_sha256),
    ):
        if file_sha256(context.inputs[name]) != digest:
            raise ValueError(f"Changed training input: {name}.")
    reset_rng(config.seed)
    torch.set_num_threads(2)
    torch.set_float32_matmul_precision("high")
    if config.device == "cuda":
        torch.cuda.reset_peak_memory_stats()
    prepared = load_json(context.inputs["prepared"])
    training = (
        prepared["training"]
        if config.phase == "pretrain"
        else load_json(context.inputs["training"])
    )
    validation = load_json(context.inputs["validation"])
    tokenizer = AutoTokenizer.from_pretrained(
        config.model_id, revision=config.revision, use_fast=True
    )
    model = AnswerEncoder(config).to(config.device)
    model.load_state_dict(load_model(context.inputs["initial_model"])["state"])
    tokens, dev_tokens = (
        prepare_tokens(training, config, tokenizer),
        prepare_tokens(validation, config, tokenizer),
    )
    mapping = prepared["shuffled" if config.arm == "shuffled" else "aligned"]
    labels = (
        targets_for_rows(training, mapping, tokenizer, config.device)
        if config.phase == "pretrain"
        else None
    )
    targets = torch.tensor(
        [r["target"] for r in training], dtype=torch.float32, device=config.device
    )
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
    generator = torch.Generator().manual_seed(config.seed + 100)
    updates_per_epoch = math.ceil(len(training) / config.batch_size)
    stopping = ValidationPatience(config.patience, 0.0)
    initial_rng = rng_digests(config.device)
    history, selected, step = [], None, 0
    started = time.monotonic()
    for epoch in range(1, config.max_epochs + 1):
        model.train()
        order = torch.randperm(len(training), generator=generator)
        order_sha = __import__("hashlib").sha256(order.numpy().tobytes()).hexdigest()
        total_loss, total_mse, total_ce, norms = 0.0, 0.0, 0.0, []
        for start in range(0, len(order), config.batch_size):
            if time.monotonic() - started > config.max_seconds:
                raise TimeoutError(
                    "A controlled phase exceeded its declared fit allowance."
                )
            indices = order[start : start + config.batch_size].to(config.device)
            batch, sides = select(tokens, indices, len(training))
            rates = phase_rates(config, epoch, step, updates_per_epoch)
            for group, rate in zip(optimizer.param_groups, rates, strict=True):
                group["lr"] = rate
            optimizer.zero_grad(set_to_none=True)
            with mixed_precision(config):
                z, hidden = model.encode(batch)
                left, right = z.chunk(2)
                mse = rating_loss((left * right).sum(-1), targets[indices], "mse")
                use_evidence = config.phase == "pretrain" and config.arm != "ratings"
                if use_evidence:
                    assert labels is not None
                    selected_labels = labels[sides]
                    if not selected_labels.ne(-100).any():
                        raise ValueError(
                            "A supposedly covered batch has no supervised evidence."
                        )
                    loss = model.answer_loss(
                        hidden, batch["attention_mask"], selected_labels
                    )
                else:
                    loss = mse
            if not torch.isfinite(loss):
                raise ValueError("A training loss is nonfinite.")
            loss.backward()
            norm = torch.nn.utils.clip_grad_norm_(
                model.parameters(), 1.0, error_if_nonfinite=True
            )
            optimizer.step()
            norms.append(float(norm))
            total_loss += float(loss.detach()) * len(indices)
            total_mse += float(mse.detach()) * len(indices)
            total_ce += float(loss.detach()) * len(indices) if use_evidence else 0.0
            step += 1
        scored, _ = predictions(model, validation, dev_tokens, config)
        diagnostic = summarize(scored)
        value = diagnostic["spearman"]
        if value is None or not math.isfinite(value):
            raise ValueError("Validation Spearman is undefined.")
        stale = stopping.observe(value)
        if selected is None or value > selected["validation"]["spearman"]:
            save_evidence_checkpoint(
                context.outputs["model"], model, config, epoch, step
            )
            write_json(context.outputs["validation_predictions"], scored)
            selected = {
                "epoch": epoch,
                "step": step,
                "validation": diagnostic,
                "sha256": file_sha256(context.outputs["model"]),
            }
        record = {
            "epoch": epoch,
            "step": step,
            "training_objective": total_loss / len(training),
            "training_mse": total_mse / len(training),
            "training_answer_ce": total_ce / len(training),
            "validation": diagnostic,
            "learning_rates": list(rates),
            "batch_order_sha256": order_sha,
            "mean_preclip_gradient_norm": sum(norms) / len(norms),
            "epochs_without_improvement": stopping.stale_epochs,
            "elapsed_seconds": time.monotonic() - started,
        }
        history.append(record)
        for name, value in (
            ("training_objective", record["training_objective"]),
            ("validation_mse", diagnostic["mse_0_1"]),
            ("validation_spearman", diagnostic["spearman"]),
        ):
            context.metrics[name].record(value, step=epoch)
        print(
            json.dumps(dict(arm=config.arm, phase=config.phase, **record)), flush=True
        )
        if config.phase == "ratings" and epoch == config.linear_epochs:
            stopping.stale_epochs = 0
        if config.phase == "ratings" and epoch > config.linear_epochs and stale:
            break
    synchronize(config.device)
    save_evidence_checkpoint(context.outputs["last_model"], model, config, epoch, step)
    save_resume_state(
        context.outputs["resume_state"],
        ResumeState(
            optimizer_state={
                "optimizer": optimizer.state_dict(),
                "config": config.model_dump(),
                "torch_rng": torch.get_rng_state(),
                "cuda_rng": torch.cuda.get_rng_state_all()
                if config.device == "cuda"
                else [],
            },
            main_process_rng=capture_main_process_rng(
                context.numpy_generators, capture_legacy_global=True
            ),
            dataloader=DataLoaderResumeState(
                configuration=DataLoaderConfiguration(workers=0),
                state_dict={
                    "completed_epochs": epoch,
                    "step": step,
                    "generator_state": generator.get_state(),
                    "terminal_model_sha256": file_sha256(context.outputs["last_model"]),
                    "early_stopping": {
                        "best_score": stopping.best_score,
                        "stale_epochs": stopping.stale_epochs,
                    },
                },
            ),
        ),
    )
    write_json(
        context.outputs["trace"],
        {
            "config": config.model_dump(),
            "epochs": history,
            "selected": selected,
            "completed_epoch": epoch,
            "updates": step,
            "training_rows": len(training),
            "initial_rng": initial_rng,
            "initial_sha256": config.initial_sha256,
            "preparation": prepared["audit"],
            "transition_artifact": "last_model"
            if config.phase == "pretrain"
            else "model",
            "stop_reason": "fixed_pretraining_budget"
            if config.phase == "pretrain"
            else "validation_patience"
            if epoch < config.max_epochs
            else "epoch_ceiling",
            "terminal_sha256": file_sha256(context.outputs["last_model"]),
            "elapsed_seconds": time.monotonic() - started,
            "peak_cuda_memory_bytes": torch.cuda.max_memory_allocated()
            if config.device == "cuda"
            else 0,
        },
    )


def verify_evidence_test(context: Any) -> dict[str, Any]:
    """Require one of the prospectively frozen rating-stage candidates."""
    config = context.config
    if file_sha256(context.inputs["selection"]) != config.selection_sha256:
        raise ValueError("Changed frozen selection.")
    selection = load_json(context.inputs["selection"])
    if (
        selection["status"] != "checkpoints_frozen"
        or selection["candidates"][config.arm]["sha256"] != config.model_sha256
    ):
        raise ValueError("Model is absent from the frozen arm selection.")
    if (
        file_sha256(context.inputs["model"]) != config.model_sha256
        or file_sha256(context.inputs["test"]) != config.test_sha256
    ):
        raise ValueError("Changed checkpoint or test cohort.")
    saved = load_model(context.inputs["model"])
    if saved["config"]["arm"] != config.arm or saved["config"]["phase"] != "ratings":
        raise ValueError("Wrong training phase or arm for test scoring.")
    return saved


@build(config=EvidencePredictionConfig)
def capture_evidence_predictions(
    context: StageContext[EvidencePredictionConfig],
) -> None:
    """Capture source-passage similarities without teacher evidence or generation."""
    saved = verify_evidence_test(context)
    config = EvidenceConfig.model_validate(saved["config"])
    model = AnswerEncoder(config).to(config.device)
    model.load_state_dict(saved["state"])
    tokenizer = AutoTokenizer.from_pretrained(
        config.model_id, revision=config.revision, use_fast=True
    )
    rows = load_json(context.inputs["test"])
    if load_json(context.inputs["holdout"]) != list(range(len(rows))):
        raise ValueError("Changed holdout indices.")
    scored, _ = predictions(
        model, rows, prepare_tokens(rows, config, tokenizer), config
    )
    write_json(context.outputs["predictions"], scored)
    write_json(
        context.outputs["binding"],
        {
            "model_sha256": context.config.model_sha256,
            "test_sha256": context.config.test_sha256,
            "selection_sha256": context.config.selection_sha256,
            "predictions_sha256": file_sha256(context.outputs["predictions"]),
        },
    )


@eval(config=EvidenceTestConfig)
def evaluate_evidence(context: StageContext[EvidenceTestConfig]) -> None:
    """Verify the sealed prediction/cohort binding before independent CPU metrics."""
    verify_evidence_test(context)
    binding = load_json(context.inputs["binding"])
    expected = {
        "model_sha256": context.config.model_sha256,
        "test_sha256": context.config.test_sha256,
        "selection_sha256": context.config.selection_sha256,
        "predictions_sha256": file_sha256(context.inputs["snapshot_predictions"]),
    }
    if binding != expected:
        raise ValueError("Changed prediction binding.")
    rows, scored = (
        load_json(context.inputs["test"]),
        load_json(context.inputs["snapshot_predictions"]),
    )
    if len(rows) != len(scored) or any(
        {k: v for k, v in b.items() if k != "prediction"} != a
        for a, b in zip(rows, scored, strict=True)
    ):
        raise ValueError("Predictions differ from the frozen cohort.")
    if load_json(context.inputs["holdout"]) != list(range(len(rows))):
        raise ValueError("Changed holdout indices.")
    summarize(scored)
    shutil.copyfile(
        context.inputs["snapshot_predictions"], context.outputs["predictions"]
    )
