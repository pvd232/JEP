"""Run frozen-feature, projection and LoRA baselines as native VIPER stages."""

import math
import shutil
import time
from itertools import count
from pathlib import Path
from typing import Any

import numpy as np
import torch
from torch import nn
from torch.nn import functional as F
from transformers import get_constant_schedule, get_linear_schedule_with_warmup
from viper.randomness import capture_main_process_rng, restore_main_process_rng
from viper.resume import (
    DataLoaderConfiguration,
    DataLoaderResumeState,
    ResumeState,
    load_resume_state,
    save_resume_state,
)
from viper.stages import StageContext, build, eval, train

from csts_pilot.baseline_models import (
    EncoderConfig,
    FitConfig,
    FrozenPairs,
    ScoreConfig,
    TokenPairs,
    encode,
    encoder_settings,
    load_backbone,
    load_tokenizer,
    pad_sequences,
    pair_features,
    passage_keys,
    restore_parameters,
    ridge_candidates,
    ridge_predict,
    state_digest,
    token_sequences,
    trainable_state,
    validate_rows,
)
from csts_pilot.convergence import file_sha256, reset_rng, synchronize, write_json
from csts_pilot.diagnostics import summarize
from csts_pilot.early_stopping import ValidationPatience
from jep_pilot.loaders import load_json, load_model


@build(config=EncoderConfig)
def cache_embeddings(context: StageContext[EncoderConfig]) -> None:
    """Encode each unique passage and condition once within this native cache stage."""
    config = context.config
    rows, identities = [], {}
    for name, path in context.inputs.items():
        selected = load_json(path)
        validate_rows(selected)
        rows.extend(selected)
        identities[name] = file_sha256(path)
    keys = passage_keys(rows)
    tokenizer = load_tokenizer(config)
    sequences = token_sequences(tokenizer, keys, config)
    model = load_backbone(config)
    model.eval()
    vectors, nonpadding_tokens = [], 0
    synchronize(config.device)
    started = time.monotonic()
    if config.device == "cuda":
        torch.cuda.reset_peak_memory_stats()
    with torch.inference_mode():
        for start in range(0, len(keys), config.encode_batch_size):
            batch = pad_sequences(
                tokenizer, sequences[start : start + config.encode_batch_size], config
            )
            nonpadding_tokens += int(batch["attention_mask"].sum())
            vectors.append(encode(model, batch).cpu())
    synchronize(config.device)
    encode_seconds = time.monotonic() - started
    write_started = time.monotonic()
    torch.save(
        {
            "encoder": encoder_settings(config),
            "keys": keys,
            "vectors": torch.cat(vectors),
            "inputs": identities,
        },
        context.outputs["embeddings"],
    )
    write_json(
        context.outputs["timing"],
        {
            "unique_passages": len(keys),
            "nonpadding_input_tokens": nonpadding_tokens,
            "encode_seconds": encode_seconds,
            "cache_write_seconds": time.monotonic() - write_started,
            "peak_cuda_memory_bytes": torch.cuda.max_memory_allocated()
            if config.device == "cuda"
            else 0,
            "encoder": encoder_settings(config),
            "inputs": identities,
        },
    )


def cached_pairs(context: Any, name: str, config: EncoderConfig) -> FrozenPairs:
    """Require the cache to identify the exact raw comparison input."""
    cache = load_model(context.inputs["embeddings"])
    if cache["inputs"].get(name) != file_sha256(context.inputs[name]):
        raise ValueError("The feature cache refers to different comparison bytes.")
    return FrozenPairs(load_json(context.inputs[name]), cache, config)


def scored_rows(rows: list[dict[str, Any]], values: Any) -> list[dict[str, Any]]:
    """Attach finite predictions to their original comparison identities."""
    result = [
        dict(row, prediction=float(value))
        for row, value in zip(rows, values, strict=True)
    ]
    if not all(math.isfinite(row["prediction"]) for row in result):
        raise ValueError("Predictions must be finite.")
    return result


def ranking_value(diagnostics: dict[str, Any]) -> float:
    """Place an undefined validation correlation below every defined correlation."""
    value = diagnostics["spearman"]
    return float(value) if value is not None else -math.inf


def record_validation(context: Any, diagnostics: dict[str, Any], step: int) -> None:
    """Record MSE and each defined validation Spearman through native metrics."""
    context.metrics["validation_mse"].record(diagnostics["mse_0_1"], step=step)
    if diagnostics["spearman"] is not None:
        context.metrics["validation_spearman"].record(
            diagnostics["spearman"], step=step
        )


@train(config=FitConfig)
def fit_static(context: StageContext[FitConfig]) -> None:
    """Fit mean, frozen cosine or ridge while using validation alone for selection."""
    config = context.config
    if config.kind not in {"mean", "cosine", "ridge"}:
        raise ValueError("Static fitting requires mean, cosine or ridge.")
    training = cached_pairs(context, "training", config)
    validation = cached_pairs(context, "validation", config)
    target = np.asarray([row["target"] for row in training.rows], dtype=float)
    started = time.monotonic()
    candidates, trace = [], []
    if config.kind == "ridge":
        candidates = ridge_candidates(
            pair_features(training.left, training.right), target, config.ridge_alphas
        )
    elif config.kind == "mean":
        candidates = [{"mean_prediction": float(target.mean())}]
    else:
        candidates = [{}]
    best, best_rows, best_key = None, None, (-math.inf, -math.inf)
    features = (
        pair_features(validation.left, validation.right)
        if config.kind == "ridge"
        else None
    )
    for fitted in candidates:
        if config.kind == "ridge":
            values = ridge_predict(fitted, features)
        elif config.kind == "mean":
            values = np.full(len(validation.rows), fitted["mean_prediction"])
        else:
            values = (validation.left * validation.right).sum(-1).cpu().tolist()
        rows = scored_rows(validation.rows, values)
        diagnostics = summarize(rows)
        key = (ranking_value(diagnostics), fitted.get("alpha", 0.0))
        trace.append({"alpha": fitted.get("alpha"), "validation": diagnostics})
        if best is None or key > best_key:
            best, best_rows, best_key = fitted, rows, key
    diagnostics = summarize(best_rows)
    model = {
        "kind": config.kind,
        "config": config.model_dump(),
        "fitted": best,
        "validation": diagnostics,
        "epoch": 0,
        "feature_cache_sha256": file_sha256(context.inputs["embeddings"]),
    }
    torch.save(model, context.outputs["model"])
    save_resume_state(
        context.outputs["resume_state"],
        ResumeState(
            optimizer_state={
                "closed_form_solver": {"kind": config.kind, "completed": True}
            },
            main_process_rng=capture_main_process_rng(
                context.numpy_generators, capture_legacy_global=True
            ),
            dataloader=DataLoaderResumeState(
                configuration=DataLoaderConfiguration(workers=0),
                state_dict={
                    "training_sha256": file_sha256(context.inputs["training"]),
                    "validation_sha256": file_sha256(context.inputs["validation"]),
                    "feature_cache_sha256": model["feature_cache_sha256"],
                },
            ),
        ),
    )
    write_json(context.outputs["validation_predictions"], best_rows)
    write_json(
        context.outputs["trace"],
        {
            "status": "complete",
            "config": config.model_dump(),
            "candidates": trace,
            "selected_alpha": best.get("alpha"),
            "selection_split": "validation",
            "elapsed_seconds": time.monotonic() - started,
        },
    )
    record_validation(context, diagnostics, 1)


@torch.no_grad()
def predict_pairs(
    model: nn.Module, pairs: FrozenPairs | TokenPairs, batch_size: int
) -> list[dict[str, Any]]:
    """Run evaluation and preserve the exact row order."""
    model.eval()
    values = []
    for start in range(0, len(pairs.rows), batch_size):
        indices = torch.arange(start, min(start + batch_size, len(pairs.rows)))
        values.extend(pairs.scores(model, indices).float().cpu().tolist())
    return scored_rows(pairs.rows, values)


def save_neural(
    path: Path, model: nn.Module, config: FitConfig, epoch: int, step: int
) -> None:
    """Save projection or adapter weights with the exact completed counters."""
    torch.save(
        {
            "kind": config.kind,
            "config": config.model_dump(),
            "state": trainable_state(model),
            "epoch": epoch,
            "step": step,
        },
        path,
    )


def restore_training(
    context: Any,
    model: nn.Module,
    optimizer: torch.optim.Optimizer,
    generator: torch.Generator,
    updates_per_epoch: int,
) -> dict[str, Any]:
    """Restore matching terminal weights, AdamW moments, RNG and the best incumbent."""
    config = context.config
    saved = load_model(context.inputs["parent_last_model"])
    parent = load_json(context.inputs["parent_trace"])
    resume = load_resume_state(context.inputs["parent_resume"])
    state = resume.dataloader.state_dict
    expected_step = config.start_epoch * updates_per_epoch
    if (
        parent["status"] != "complete"
        or len(parent["epochs"]) != config.start_epoch
        or parent["actual_updates"] != expected_step
        or saved["epoch"] != config.start_epoch
        or saved["step"] != expected_step
        or state["epoch"] != config.start_epoch
        or state["step"] != expected_step
        or state["last_model_sha256"]
        != file_sha256(context.inputs["parent_last_model"])
    ):
        raise ValueError("Parent terminal weights, epoch and resume state disagree.")
    allowed = {
        "train_until_patience",
        "start_epoch",
        "max_epochs",
        "max_seconds",
        "learning_rate",
        "schedule",
        "warmup_fraction",
    }
    current = config.model_dump()
    if any(
        current[key] != value
        for key, value in saved["config"].items()
        if key not in allowed
    ):
        raise ValueError("Continuation changed an undeclared training setting.")
    if parent["selected"]["sha256"] != file_sha256(context.inputs["parent_model"]):
        raise ValueError("The incumbent differs from the parent's selected checkpoint.")
    restore_parameters(model, saved["state"])
    optimizer.load_state_dict(resume.optimizer_state["optimizer"])
    steps = [float(item["step"]) for item in optimizer.state.values() if "step" in item]
    if not steps or any(step != expected_step for step in steps):
        raise ValueError("Restored optimizer steps differ from the terminal epoch.")
    for group in optimizer.param_groups:
        group["lr"] = group["initial_lr"] = config.learning_rate
    generator.set_state(state["generator_state"])
    restore_main_process_rng(resume.main_process_rng, context.numpy_generators)
    if (
        capture_main_process_rng(context.numpy_generators, capture_legacy_global=True)
        != resume.main_process_rng
    ):
        raise ValueError("Restored random state differs from its saved identity.")
    shutil.copyfile(context.inputs["parent_model"], context.outputs["model"])
    shutil.copyfile(
        context.inputs["parent_validation_predictions"],
        context.outputs["validation_predictions"],
    )
    return parent


def fit_neural(
    context: Any,
    model: nn.Module,
    training: FrozenPairs | TokenPairs,
    validation: FrozenPairs | TokenPairs,
) -> None:
    """Train rating MSE with exact microbatch weighting and configured validation patience."""
    config = context.config
    parameters = [p for p in model.parameters() if p.requires_grad]
    optimizer = torch.optim.AdamW(
        parameters, lr=config.learning_rate, weight_decay=config.weight_decay
    )
    updates_per_epoch = math.ceil(len(training.rows) / config.batch_size)
    generator = torch.Generator().manual_seed(config.seed + 100)
    targets = torch.tensor(
        [r["target"] for r in training.rows], dtype=torch.float32, device=config.device
    )
    stopping = ValidationPatience(config.patience, 0.0)
    history, selected, step = [], None, 0
    initial_digest = state_digest(trainable_state(model))
    input_digests = {
        name: file_sha256(path)
        for name, path in context.inputs.items()
        if name in {"training", "validation", "embeddings"}
    }
    if config.start_epoch:
        parent = restore_training(
            context, model, optimizer, generator, updates_per_epoch
        )
        if parent["training_inputs"] != input_digests:
            raise ValueError(
                "Continuation requires the same training, validation and feature bytes."
            )
        history, selected = list(parent["epochs"]), dict(parent["selected"])
        initial_digest = parent["initial_trainable_sha256"]
        stopping.best_score = (
            selected["validation"]["spearman"]
            if selected["validation"]["spearman"] is not None
            else -1.0
        )
        if config.train_until_patience:
            stopping = ValidationPatience(config.patience, 0.0)
            for record in history:
                score = record["validation"]["spearman"]
                stopping.observe(score if score is not None else -1.0)
            if stopping.stale_epochs >= config.patience:
                raise ValueError("The parent already exhausted validation patience.")
        step = config.start_epoch * updates_per_epoch
    total_updates = config.max_epochs * updates_per_epoch
    scheduler = (
        get_constant_schedule(optimizer)
        if config.schedule == "constant"
        else get_linear_schedule_with_warmup(
            optimizer, math.ceil(config.warmup_fraction * total_updates), total_updates
        )
    )
    synchronize(config.device)
    started = time.monotonic()
    if config.device == "cuda":
        torch.cuda.reset_peak_memory_stats()
    reason, epoch = "epoch_budget", config.start_epoch
    epochs_to_run = (
        count(config.start_epoch + 1)
        if config.train_until_patience
        else range(config.start_epoch + 1, config.max_epochs + 1)
    )
    for epoch in epochs_to_run:
        if not config.train_until_patience and len(history) > config.start_epoch:
            expected_epoch_seconds = 1.25 * history[-1]["observed_epoch_seconds"]
            if (
                time.monotonic() - started + expected_epoch_seconds
                >= config.max_seconds
            ):
                reason = "resource_budget"
                break
        model.train()
        order = torch.randperm(len(training.rows), generator=generator)
        order_sha = state_digest({"order": order})
        fit_started, squared_error = time.monotonic(), 0.0
        norms = []
        training_tokens_before, validation_tokens_before = (
            training.nonpadding_tokens,
            validation.nonpadding_tokens,
        )
        for start in range(0, len(order), config.batch_size):
            if (
                not config.train_until_patience
                and time.monotonic() - started >= config.max_seconds
            ):
                raise TimeoutError(
                    "The fitting budget ended inside an epoch; preserve the native attempt for inspection."
                )
            effective = order[start : start + config.batch_size]
            optimizer.zero_grad(set_to_none=True)
            for offset in range(0, len(effective), config.microbatch_size):
                indices = effective[offset : offset + config.microbatch_size]
                scores = training.scores(model, indices)
                with torch.autocast(config.device, enabled=False):
                    loss = F.mse_loss(
                        scores.float(), targets[indices].float(), reduction="sum"
                    ) / len(effective)
                if not torch.isfinite(loss):
                    raise ValueError("Training loss must be finite.")
                loss.backward()
                squared_error += float(loss.detach()) * len(effective)
            norm = torch.nn.utils.clip_grad_norm_(
                parameters, 1.0, error_if_nonfinite=True
            )
            norms.append(float(norm))
            optimizer.step()
            scheduler.step()
            step += 1
            if step % 25 == 0:
                write_json(
                    context.outputs["trace"],
                    {
                        "status": "running",
                        "kind": config.kind,
                        "current_epoch": epoch,
                        "actual_updates": step,
                        "completed_epoch": len(history),
                        "epochs": history,
                        "selected": selected,
                        "epochs_without_improvement": stopping.stale_epochs,
                    },
                )
        synchronize(config.device)
        fit_seconds = time.monotonic() - fit_started
        validation_started = time.monotonic()
        rows = predict_pairs(model, validation, config.microbatch_size)
        diagnostics = summarize(rows)
        synchronize(config.device)
        validation_seconds = time.monotonic() - validation_started
        score = diagnostics["spearman"] if diagnostics["spearman"] is not None else -1.0
        exhausted = stopping.observe(score)
        if selected is None or ranking_value(diagnostics) > ranking_value(
            selected["validation"]
        ):
            save_neural(context.outputs["model"], model, config, epoch, step)
            write_json(context.outputs["validation_predictions"], rows)
            selected = {
                "epoch": epoch,
                "step": step,
                "sha256": file_sha256(context.outputs["model"]),
                "validation": diagnostics,
            }
        record = {
            "epoch": epoch,
            "step": step,
            "training_mse_0_1": squared_error / len(training.rows),
            "validation": diagnostics,
            "fit_seconds": fit_seconds,
            "validation_seconds": validation_seconds,
            "learning_rates": scheduler.get_last_lr(),
            "batch_order_sha256": order_sha,
            "mean_preclip_gradient_norm": float(np.mean(norms)),
            "training_nonpadding_input_tokens": training.nonpadding_tokens
            - training_tokens_before,
            "validation_nonpadding_input_tokens": validation.nonpadding_tokens
            - validation_tokens_before,
            "epochs_without_improvement": stopping.stale_epochs,
        }
        history.append(record)
        context.metrics["training_objective"].record(
            record["training_mse_0_1"], step=epoch
        )
        record_validation(context, diagnostics, epoch)
        record["observed_epoch_seconds"] = time.monotonic() - fit_started
        write_json(
            context.outputs["trace"],
            {
                "status": "running",
                "kind": config.kind,
                "current_epoch": epoch,
                "actual_updates": step,
                "completed_epoch": len(history),
                "epochs": history,
                "selected": selected,
                "epochs_without_improvement": stopping.stale_epochs,
            },
        )
        print({"kind": config.kind, **record}, flush=True)
        if exhausted:
            reason = "validation_patience"
            break
    completed_epoch = len(history)
    save_neural(context.outputs["last_model"], model, config, completed_epoch, step)
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
                    "epoch": completed_epoch,
                    "step": step,
                    "generator_state": generator.get_state(),
                    "last_model_sha256": file_sha256(context.outputs["last_model"]),
                },
            ),
        ),
    )
    write_json(
        context.outputs["trace"],
        {
            "status": "complete",
            "config": config.model_dump(),
            "selected": selected,
            "epochs": history,
            "actual_updates": step,
            "stop_reason": reason,
            "initial_trainable_sha256": initial_digest,
            "training_inputs": input_digests,
            "updates_per_epoch": updates_per_epoch,
            "phase_elapsed_seconds": time.monotonic() - started,
            "trainable_parameter_count": sum(p.numel() for p in parameters),
            "peak_cuda_memory_bytes": torch.cuda.max_memory_allocated()
            if config.device == "cuda"
            else 0,
            "continuation_parent_last_sha256": file_sha256(
                context.inputs["parent_last_model"]
            )
            if config.start_epoch
            else None,
        },
    )


@train(config=FitConfig)
def fit_projection(context: StageContext[FitConfig]) -> None:
    """Fit a bias-free projection over the shared frozen conditioned embeddings."""
    if context.config.kind != "projection":
        raise ValueError("Projection fitting requires the projection scorer.")
    reset_rng(context.config.seed)
    config = context.config
    training, validation = (
        cached_pairs(context, "training", config),
        cached_pairs(context, "validation", config),
    )
    model = nn.Linear(
        config.embedding_dimension, config.projection_dimension, bias=False
    ).to(config.device)
    fit_neural(context, model, training, validation)


@train(config=FitConfig)
def fit_lora(context: StageContext[FitConfig]) -> None:
    """Train attention adapters against rating MSE while freezing the Qwen base."""
    if context.config.kind != "lora":
        raise ValueError("Adapter fitting requires the LoRA scorer.")
    reset_rng(context.config.seed)
    config = context.config
    tokenizer, model = load_tokenizer(config), load_backbone(config, adapters=config)
    training = TokenPairs(load_json(context.inputs["training"]), config, tokenizer)
    validation = TokenPairs(load_json(context.inputs["validation"]), config, tokenizer)
    fit_neural(context, model, training, validation)


def verify_test_inputs(context: Any) -> dict[str, Any]:
    """Reject changed model, selection or test bytes before loading a backbone."""
    config = context.config
    if file_sha256(context.inputs["selection"]) != config.selection_sha256:
        raise ValueError("The selection document differs from its frozen identity.")
    selection = load_json(context.inputs["selection"])
    if (
        selection["status"] != "checkpoints_frozen"
        or selection["candidates"][config.kind]["sha256"] != config.model_sha256
    ):
        raise ValueError("The scorer is absent from the frozen selection.")
    if (
        file_sha256(context.inputs["model"]) != config.model_sha256
        or file_sha256(context.inputs["test"]) != config.test_sha256
    ):
        raise ValueError("The frozen model or test cohort bytes differ.")
    saved = load_model(context.inputs["model"])
    if saved["kind"] != config.kind or encoder_settings(
        FitConfig.model_validate(saved["config"])
    ) != encoder_settings(config):
        raise ValueError(
            "The selected model representation differs from the test configuration."
        )
    return saved


@build(config=ScoreConfig)
def capture_predictions(context: StageContext[ScoreConfig]) -> None:
    """Seal one frozen candidate's predictions before independent metric execution."""
    started = time.monotonic()
    saved = verify_test_inputs(context)
    config = context.config
    rows = load_json(context.inputs["test"])
    validate_rows(rows)
    if load_json(context.inputs["holdout"]) != list(range(len(rows))):
        raise ValueError("Test indices differ from the frozen cohort.")
    synchronize(config.device)
    if config.kind == "lora":
        fit_config = FitConfig.model_validate(
            {**saved["config"], "device": config.device}
        )
        model = load_backbone(fit_config, adapters=fit_config)
        restore_parameters(model, saved["state"])
        pairs = TokenPairs(rows, config, load_tokenizer(config))
        predictions = predict_pairs(model, pairs, fit_config.microbatch_size)
    else:
        pairs = cached_pairs(context, "test", config)
        if config.kind == "projection":
            model = nn.Linear(
                config.embedding_dimension,
                saved["config"]["projection_dimension"],
                bias=False,
            ).to(config.device)
            restore_parameters(model, saved["state"])
            predictions = predict_pairs(model, pairs, 128)
        elif config.kind == "ridge":
            predictions = scored_rows(
                rows,
                ridge_predict(saved["fitted"], pair_features(pairs.left, pairs.right)),
            )
        elif config.kind == "mean":
            predictions = scored_rows(
                rows, [saved["fitted"]["mean_prediction"]] * len(rows)
            )
        else:
            predictions = scored_rows(
                rows, (pairs.left * pairs.right).sum(-1).cpu().tolist()
            )
    synchronize(config.device)
    write_json(context.outputs["predictions"], predictions)
    write_json(
        context.outputs["timing"],
        {
            "scoring_including_model_load_seconds": time.monotonic() - started,
            "rows": len(rows),
            "model_sha256": config.model_sha256,
            "test_sha256": config.test_sha256,
            "original_selection_sha256": config.selection_sha256,
            "predictions_sha256": file_sha256(context.outputs["predictions"]),
        },
    )


@eval(config=ScoreConfig)
def evaluate_baseline(context: StageContext[ScoreConfig]) -> None:
    """Verify saved prediction bytes and expose them to native CPU metric workers."""
    verify_test_inputs(context)
    binding = load_json(context.inputs["snapshot_timing"])
    if (
        binding["model_sha256"] != context.config.model_sha256
        or binding["test_sha256"] != context.config.test_sha256
        or binding["predictions_sha256"]
        != file_sha256(context.inputs["snapshot_predictions"])
    ):
        raise ValueError(
            "The saved predictions refer to different model, test or artifact bytes."
        )
    rows = load_json(context.inputs["test"])
    predictions = load_json(context.inputs["snapshot_predictions"])
    if len(rows) != len(predictions) or any(
        {key: value for key, value in scored.items() if key != "prediction"} != row
        for row, scored in zip(rows, predictions, strict=True)
    ):
        raise ValueError(
            "Prediction identities or labels differ from the frozen test cohort."
        )
    scored_rows(rows, [row["prediction"] for row in predictions])
    if load_json(context.inputs["holdout"]) != list(range(len(rows))):
        raise ValueError("Test indices differ from the frozen cohort.")
    shutil.copyfile(
        context.inputs["snapshot_predictions"], context.outputs["predictions"]
    )
    shutil.copyfile(context.inputs["snapshot_timing"], context.outputs["timing"])
