"""Native VIPER stages for matched rating-loss and convergence comparisons."""

import hashlib
import json
import math
import os
import random
import shutil
import time
from pathlib import Path
from typing import Any, Literal

import numpy as np
import torch
from pydantic import Field, model_validator
from transformers import AutoTokenizer, get_linear_schedule_with_warmup
from viper.config import BuildConfig, EvalConfig, MetricConfig
from viper.metrics import MetricContext, metric
from viper.randomness import capture_main_process_rng
from viper.resume import (
    DataLoaderConfiguration,
    DataLoaderResumeState,
    ResumeState,
    save_resume_state,
)
from viper.stages import StageContext, build, eval, train

from csts_pilot.diagnostics import summarize
from csts_pilot.early_stopping import ValidationPatience
from csts_pilot.joint import AnswerEncoder, predictions, rating_loss, select
from csts_pilot.training import CstsConfig, mixed_precision, prepare_tokens
from jep_pilot.loaders import load_json, load_model


class ConvergenceConfig(CstsConfig):
    """Declare the objective and both validation-selected checkpoint windows."""

    rating_objective: Literal["mse", "pearson"] = "mse"
    max_epochs: int = Field(default=24, ge=1)
    prefix_epochs: int = Field(default=8, ge=1)
    patience: int | None = Field(default=5, ge=1)
    min_delta: float = Field(default=0.0, ge=0, allow_inf_nan=False)
    max_seconds: float = Field(default=1800, gt=0)

    @model_validator(mode="after")
    def validate_windows(self) -> "ConvergenceConfig":
        if self.prefix_epochs > self.max_epochs:
            raise ValueError("The prefix window must fit within the full epoch budget.")
        return self


class InitializationConfig(BuildConfig):
    """Identify the single saved initialization shared by both training arms."""

    model_id: str = "google/flan-t5-small"
    revision: str = "0fc9ddf78a1e988dac52e2dac162b0ede4fd74ab"
    projection_dimension: int = 128
    seed: int = 7


class TestConfig(EvalConfig):
    """Bind test scoring to one checkpoint and the frozen selection document."""

    model_sha256: str
    selection_sha256: str
    test_sha256: str


class CheckpointConfig(BuildConfig):
    """Identify frozen bytes republished under VIPER's canonical model name."""

    model_sha256: str


def file_sha256(path: Path) -> str:
    """Hash checkpoint bytes without holding another model copy in memory."""
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def write_json(path: Path, value: Any) -> None:
    """Replace one progress record atomically while the runner holds its lock."""
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    with temporary.open("w") as stream:
        stream.write(json.dumps(value, indent=2, allow_nan=False) + "\n")
        stream.flush()
        os.fsync(stream.fileno())
    temporary.replace(path)


def reset_rng(seed: int) -> None:
    """Reset Python, NumPy and Torch before each matched arm."""
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)


def rng_digests(device: str) -> dict[str, str]:
    """Record the RNG identities immediately before the first update."""
    states = {
        "python": repr(random.getstate()).encode(),
        "numpy": np.random.get_state()[1].tobytes()
        + repr(np.random.get_state()[2:]).encode(),
        "torch_cpu": torch.get_rng_state().numpy().tobytes(),
    }
    if device == "cuda":
        states["torch_cuda"] = torch.cuda.get_rng_state().cpu().numpy().tobytes()
    return {name: hashlib.sha256(value).hexdigest() for name, value in states.items()}


def synchronize(device: str) -> None:
    """Include completed CUDA work in elapsed-time measurements."""
    if device == "cuda":
        torch.cuda.synchronize()


def save_checkpoint(
    path: Path, model: AnswerEncoder, config: ConvergenceConfig, epoch: int
) -> None:
    """Save detached weights with the exact configuration and completed epoch."""
    torch.save(
        {
            "config": config.model_dump(),
            "state": {
                key: value.detach().cpu() for key, value in model.state_dict().items()
            },
            "epoch": epoch,
        },
        path,
    )


@build(config=InitializationConfig)
def initialize(context: StageContext[InitializationConfig]) -> None:
    """Publish one CPU initialization artifact; both arms restore these bytes."""
    reset_rng(context.config.seed)
    config = CstsConfig(**context.config.model_dump(), device="cpu")
    model = AnswerEncoder(config)
    torch.save(
        {"state": model.state_dict(), "seed": config.seed}, context.outputs["model"]
    )


@build(config=CheckpointConfig)
def promote_checkpoint(context: StageContext[CheckpointConfig]) -> None:
    """Copy a selected checkpoint without loading or changing its weights."""
    if file_sha256(context.inputs["checkpoint"]) != context.config.model_sha256:
        raise ValueError("The checkpoint differs from its frozen identity.")
    shutil.copyfile(context.inputs["checkpoint"], context.outputs["model"])
    if file_sha256(context.outputs["model"]) != context.config.model_sha256:
        raise ValueError("Checkpoint publication changed the frozen bytes.")


@metric(metric_id="validation_spearman", mode="stateless")
def validation_spearman(_context: MetricContext[MetricConfig], value: float) -> float:
    """Record the common checkpoint-selection criterion."""
    return value


@metric(metric_id="validation_mse", mode="stateless")
def validation_mse(_context: MetricContext[MetricConfig], value: float) -> float:
    """Record MSE on ratings rescaled to the 0–1 target scale."""
    return value


@metric(metric_id="training_objective", mode="stateless")
def training_objective(_context: MetricContext[MetricConfig], value: float) -> float:
    """Record each arm's actual optimization objective."""
    return value


@train(config=ConvergenceConfig)
def fit(context: StageContext[ConvergenceConfig]) -> None:
    """Train one rating arm and retain the best prefix and full checkpoints."""
    config = context.config
    reset_rng(config.seed)
    torch.set_num_threads(4)
    torch.set_float32_matmul_precision("high")
    if config.device == "cuda":
        torch.cuda.reset_peak_memory_stats()
    training = load_json(context.inputs["training"])
    validation = load_json(context.inputs["validation"])
    tokenizer = AutoTokenizer.from_pretrained(
        config.model_id, revision=config.revision, use_fast=True
    )
    model = AnswerEncoder(config).to(config.device)
    model.load_state_dict(load_model(context.inputs["initial_model"])["state"])
    tokens = prepare_tokens(training, config, tokenizer)
    validation_tokens = prepare_tokens(validation, config, tokenizer)
    targets = torch.tensor(
        [row["target"] for row in training], device=config.device, dtype=torch.float32
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
    updates_per_epoch = math.ceil(len(training) / config.batch_size)
    total_updates = config.max_epochs * updates_per_epoch
    warmup_updates = math.ceil(config.warmup_fraction * total_updates)
    scheduler = get_linear_schedule_with_warmup(
        optimizer, warmup_updates, total_updates
    )
    permutation_rng = torch.Generator().manual_seed(config.seed + 100)
    initial_predictions, _ = predictions(model, validation, validation_tokens, config)
    trace: dict[str, Any] = {
        "config": config.model_dump(),
        "status": "training",
        "epochs": [],
        "selected": {},
        "initial_model_sha256": file_sha256(context.inputs["initial_model"]),
        "initial_validation": summarize(initial_predictions),
        "initial_rng": rng_digests(config.device),
        "updates_per_epoch": updates_per_epoch,
        "total_updates": total_updates,
        "warmup_updates": warmup_updates,
        "nonpadding_input_tokens_per_epoch": int(tokens["attention_mask"].sum()),
    }
    synchronize(config.device)
    started = time.monotonic()
    step, epoch, batch_start = 0, 0, 0
    order = torch.empty(0, dtype=torch.long)
    best_full = best_prefix = -math.inf
    stopping = ValidationPatience(config.patience, config.min_delta)
    trace["stop_reason"] = "epoch_budget"
    try:
        for epoch in range(1, config.max_epochs + 1):
            model.train()
            order = torch.randperm(len(training), generator=permutation_rng)
            order_digest = hashlib.sha256(order.numpy().tobytes()).hexdigest()
            device_order = order.to(config.device)
            totals = torch.zeros(2, device=config.device)
            constant_target_batches = torch.zeros(
                (), device=config.device, dtype=torch.int64
            )
            synchronize(config.device)
            epoch_started = time.monotonic()
            for batch_start in range(0, len(training), config.batch_size):
                if time.monotonic() - started >= config.max_seconds:
                    raise TimeoutError(
                        "The common experiment resource ceiling was reached."
                    )
                indices = device_order[batch_start : batch_start + config.batch_size]
                batch, _ = select(tokens, indices, len(training))
                optimizer.zero_grad(set_to_none=True)
                with mixed_precision(config):
                    vectors, _ = model.encode(batch)
                left, right = vectors.chunk(2)
                scores = (left * right).sum(-1)
                loss = rating_loss(scores, targets[indices], config.rating_objective)
                mse = rating_loss(scores, targets[indices], "mse")
                if not torch.isfinite(loss):
                    raise FloatingPointError("The rating objective became nonfinite.")
                loss.backward()
                torch.nn.utils.clip_grad_norm_(
                    model.parameters(), 1.0, error_if_nonfinite=True
                )
                optimizer.step()
                scheduler.step()
                totals += torch.stack((loss.detach(), mse.detach())) * len(indices)
                constant_target_batches += (
                    targets[indices].max().eq(targets[indices].min())
                )
                step += 1
            synchronize(config.device)
            fit_seconds = time.monotonic() - epoch_started
            validation_started = time.monotonic()
            validation_predictions, _ = predictions(
                model, validation, validation_tokens, config
            )
            diagnostic = summarize(validation_predictions)
            synchronize(config.device)
            validation_seconds = time.monotonic() - validation_started
            rho = diagnostic["spearman"]
            if rho is None or not math.isfinite(rho):
                raise FloatingPointError("Validation Spearman became undefined.")
            patience_exhausted = stopping.observe(rho)
            objective_value, mse_value = (totals / len(training)).cpu().tolist()
            record = {
                "epoch": epoch,
                "step": step,
                "batch_order_sha256": order_digest,
                "training_objective": objective_value,
                "training_mse_0_1": mse_value,
                "constant_target_batches": int(constant_target_batches),
                "validation": diagnostic,
                "fit_seconds": fit_seconds,
                "validation_seconds": validation_seconds,
                "elapsed_seconds": time.monotonic() - started,
                "epochs_without_improvement": stopping.stale_epochs,
                "learning_rates": scheduler.get_last_lr(),
            }
            # Strict improvement keeps the earlier epoch when validation ranks tie.
            if rho > best_full:
                best_full = rho
                save_checkpoint(context.outputs["model"], model, config, epoch)
                write_json(
                    context.outputs["validation_predictions"], validation_predictions
                )
                trace["selected"]["full"] = {
                    "epoch": epoch,
                    "validation": diagnostic,
                    "sha256": file_sha256(context.outputs["model"]),
                }
            if epoch <= config.prefix_epochs and rho > best_prefix:
                best_prefix = rho
                # Copy exact bytes so identical prefix/full checkpoints share an identity.
                shutil.copyfile(
                    context.outputs["model"], context.outputs["prefix_model"]
                )
                shutil.copyfile(
                    context.outputs["validation_predictions"],
                    context.outputs["prefix_validation_predictions"],
                )
                trace["selected"]["prefix"] = dict(trace["selected"]["full"])
            trace["epochs"].append(record)
            for name, value in (
                ("training_objective", objective_value),
                ("validation_mse", diagnostic["mse_0_1"]),
                ("validation_spearman", rho),
            ):
                context.metrics[name].record(value, step=epoch)
            write_json(context.outputs["trace"], trace)
            print(json.dumps(record), flush=True)
            if epoch >= config.prefix_epochs and patience_exhausted:
                trace["stop_reason"] = "validation_patience"
                break
        trace["status"] = "complete"
    except BaseException as error:
        trace["status"] = "failed"
        trace["failure"] = {
            "type": type(error).__name__,
            "message": str(error),
            "epoch": epoch,
            "step": step,
        }
        write_json(context.outputs["trace"], trace)
        raise
    finally:
        # The resume state belongs to these final weights, independently of selection.
        save_checkpoint(
            context.outputs["last_model"], model, config, len(trace["epochs"])
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
                        "completed_epochs": len(trace["epochs"]),
                        "epoch": epoch,
                        "step": step,
                        "batch_start": batch_start,
                        "epoch_order": order,
                        "generator_state": permutation_rng.get_state(),
                        "early_stopping": {
                            "best_score": stopping.best_score,
                            "stale_epochs": stopping.stale_epochs,
                        },
                    },
                ),
            ),
        )
        synchronize(config.device)
        trace["elapsed_seconds"] = time.monotonic() - started
        trace["actual_updates"] = step
        trace["peak_cuda_memory_bytes"] = (
            torch.cuda.max_memory_allocated() if config.device == "cuda" else 0
        )
        write_json(context.outputs["trace"], trace)


@eval(config=TestConfig)
def test_checkpoint(context: StageContext[TestConfig]) -> None:
    """Score one frozen checkpoint and apply its frozen validation calibration."""
    if file_sha256(context.inputs["selection"]) != context.config.selection_sha256:
        raise ValueError("The selection document differs from the frozen identity.")
    selection = load_json(context.inputs["selection"])
    identity = file_sha256(context.inputs["model"])
    if (
        identity != context.config.model_sha256
        or selection["status"] != "checkpoints_frozen"
    ):
        raise ValueError("Test scoring requires a checkpoint frozen before testing.")
    candidates = [
        row for row in selection["candidates"].values() if row["sha256"] == identity
    ]
    if not candidates:
        raise ValueError("The checkpoint is absent from the frozen comparison.")
    if file_sha256(context.inputs["test"]) != context.config.test_sha256:
        raise ValueError("Test bytes differ from the approved cohort.")
    saved = load_model(context.inputs["model"])
    config = ConvergenceConfig.model_validate(saved["config"])
    model = AnswerEncoder(config).to(config.device)
    model.load_state_dict(saved["state"])
    rows = load_json(context.inputs["test"])
    if load_json(context.inputs["holdout"]) != list(range(len(rows))):
        raise ValueError("Test indices differ from the frozen test cohort.")
    tokenizer = AutoTokenizer.from_pretrained(
        config.model_id, revision=config.revision, use_fast=True
    )
    tokens = prepare_tokens(rows, config, tokenizer)
    started = time.monotonic()
    scored, _ = predictions(model, rows, tokens, config)
    fitted = candidates[0]["calibration"]
    for row in scored:
        row["calibrated_prediction"] = fitted["a"] * row["prediction"] + fitted["c"]
    synchronize(config.device)
    write_json(context.outputs["predictions"], scored)
    write_json(
        context.outputs["timing"],
        {"prediction_seconds": time.monotonic() - started, "rows": len(rows)},
    )


@metric(metric_id="test_mse", mode="stateless")
def test_mse(context: MetricContext[MetricConfig]) -> float:
    """Independently measure test MSE from the immutable predictions."""
    rows = load_json(context.artifacts["predictions"])
    return float(np.mean([(row["prediction"] - row["target"]) ** 2 for row in rows]))


@metric(metric_id="test_spearman", mode="stateless")
def test_spearman(context: MetricContext[MetricConfig]) -> float:
    """Independently measure test ranking from the immutable predictions."""
    from scipy.stats import spearmanr

    rows = load_json(context.artifacts["predictions"])
    value = float(
        spearmanr(
            [r["prediction"] for r in rows], [r["target"] for r in rows]
        ).statistic
    )
    if not math.isfinite(value):
        raise ValueError("Test Spearman is undefined.")
    return value
