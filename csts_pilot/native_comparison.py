"""Train fresh Qwen adapters and a symmetric comparison through rating error."""

import gc
import math
import shutil
import time
from typing import Literal

import numpy as np
import torch
from pydantic import Field
from torch import nn
from torch.nn import functional as F
from viper.randomness import capture_main_process_rng, restore_main_process_rng
from viper.resume import (
    DataLoaderConfiguration,
    DataLoaderResumeState,
    ResumeState,
    load_resume_state,
    save_resume_state,
)
from viper.stages import StageContext, build, train

from csts_pilot import evidence_readout_progress as progress
from csts_pilot.baseline_models import (
    EncoderConfig,
    FitConfig,
    TokenPairs,
    encode,
    encoder_settings,
    load_backbone,
    load_tokenizer,
    pad_sequences,
    restore_parameters,
    state_digest,
    trainable_state,
)
from csts_pilot.baseline_stages import record_validation, scored_rows
from csts_pilot.checkpoint_cloud import CheckpointCloud
from csts_pilot.convergence import file_sha256, reset_rng, synchronize, write_json
from csts_pilot.diagnostics import summarize
from csts_pilot.early_stopping import ValidationPatience
from csts_pilot.evidence_readout import SymmetricComparison
from jep_pilot.loaders import load_json, load_model

SCORER = "native_symmetric_comparison"


class NativeComparisonConfig(FitConfig):
    """Pin one joint fit and its epoch checkpoint publication destination."""

    kind: Literal["lora"] = "lora"
    learning_rate: float = 0.00002
    comparison_learning_rate: float = Field(default=0.001, gt=0)
    comparison_weight_decay: float = Field(default=0.01, ge=0)
    patience: int = 10
    microbatch_size: int = 2
    autotune_microbatch: bool = True
    max_seconds: float = 86400
    training_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    validation_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    checkpoint_root: str | None = None
    checkpoint_destination: dict[str, str] | None = None
    progress_path: str | None = None


class NativeScoreConfig(EncoderConfig):
    """Require a frozen selected model and declared prediction input bytes."""

    model_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    rows_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    selection_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")


class JointEncoder(nn.Module):
    """Keep the backbone and comparison together for state and gradient routing."""

    def __init__(self, backbone: nn.Module, dimension: int):
        super().__init__()
        self.backbone = backbone
        self.comparison = SymmetricComparison(dimension)


class JointPairs(TokenPairs):
    """Use the existing prompt and tokenization with the learned scorer."""

    def vectors(self, model: JointEncoder, indices: torch.Tensor):
        selected = [self.rows[i] for i in indices.cpu().tolist()]
        keys = [
            (row["condition"], row[side])
            for side in ("sentence1", "sentence2")
            for row in selected
        ]
        batch = pad_sequences(
            self.tokenizer, [self.sequences[key] for key in keys], self.config
        )
        self.nonpadding_tokens += int(batch["attention_mask"].sum())
        return encode(model.backbone, batch).chunk(2)

    def scores(self, model: JointEncoder, indices: torch.Tensor):
        left, right = self.vectors(model, indices)
        with torch.autocast(left.device.type, enabled=False):
            return model.comparison(left.float(), right.float())


def optimizer_for(model: JointEncoder, config: NativeComparisonConfig):
    """Give the LoRA factors and comparison their declared AdamW groups."""
    adapter = [p for p in model.backbone.parameters() if p.requires_grad]
    comparison = list(model.comparison.parameters())
    if (
        not adapter
        or not comparison
        or set(map(id, adapter)) & set(map(id, comparison))
    ):
        raise ValueError("Require distinct nonempty adapter and comparison groups.")
    return torch.optim.AdamW(
        [
            {
                "params": adapter,
                "lr": config.learning_rate,
                "weight_decay": config.weight_decay,
            },
            {
                "params": comparison,
                "lr": config.comparison_learning_rate,
                "weight_decay": config.comparison_weight_decay,
            },
        ],
        betas=(0.9, 0.999),
        eps=1e-8,
        fused=config.device == "cuda",
    )


def logical_batch_backward(model, pairs, indices, targets, microbatch):
    """Weight every pair equally, including the final partial logical batch."""
    total = torch.zeros((), device=targets.device)
    for offset in range(0, len(indices), microbatch):
        chosen = indices[offset : offset + microbatch]
        scores = pairs.scores(model, chosen)
        error = F.mse_loss(scores.float(), targets[chosen].float(), reduction="sum")
        (error / len(indices)).backward()
        total += error.detach()
    if not torch.isfinite(total):
        raise ValueError("The logical rating batch produced a nonfinite error.")
    return total


def gradient_norm(parameters):
    values = [p.grad.detach().float().norm() for p in parameters if p.grad is not None]
    return float(torch.stack(values).norm()) if values else 0.0


def parameter_norm(parameters):
    return float(torch.stack([p.detach().float().norm() for p in parameters]).norm())


def tune_microbatch(model, pairs, targets, config):
    """Benchmark a single unchanged logical batch without optimizer updates."""
    if config.device != "cuda" or not config.autotune_microbatch:
        return config.microbatch_size, []

    # Longest rows exercise the largest padding requirement before scientific fitting.
    def length(i):
        row = pairs.rows[i]
        return max(
            len(pairs.sequences[(row["condition"], row[s])])
            for s in ("sentence1", "sentence2")
        )

    indices = torch.tensor(
        sorted(range(len(pairs.rows)), key=length, reverse=True)[: config.batch_size]
    )
    candidates = (
        (8, 16, 32)
        if torch.cuda.get_device_properties(0).total_memory >= 38 * 1024**3
        else (2, 4, 8)
    )
    records = []
    model.train()
    for size in candidates:
        if size > config.batch_size:
            continue
        model.zero_grad(set_to_none=True)
        reset_rng(config.seed + 2000)
        torch.cuda.reset_peak_memory_stats()
        started = time.monotonic()
        try:
            logical_batch_backward(model, pairs, indices, targets, size)
            torch.cuda.synchronize()
            records.append(
                {
                    "microbatch": size,
                    "seconds": time.monotonic() - started,
                    "peak_bytes": torch.cuda.max_memory_allocated(),
                    "status": "passed",
                }
            )
        except torch.cuda.OutOfMemoryError:
            records.append({"microbatch": size, "status": "out_of_memory"})
            model.zero_grad(set_to_none=True)
            gc.collect()
            torch.cuda.empty_cache()
            break
    model.zero_grad(set_to_none=True)
    reset_rng(config.seed + 2000)
    valid = [r for r in records if r["status"] == "passed"]
    if not valid:
        raise RuntimeError("Microbatch profiling found no fitting configuration.")
    return min(valid, key=lambda r: r["seconds"])["microbatch"], records


@torch.inference_mode()
def validation_predictions(model, pairs, batch_size, initial=None):
    """Capture predictions and reuse the same vectors to measure embedding changes."""
    model.eval()
    lefts, rights, values, cosines = [], [], [], []
    for start in range(0, len(pairs.rows), batch_size):
        ids = torch.arange(start, min(start + batch_size, len(pairs.rows)))
        left, right = pairs.vectors(model, ids)
        values.extend(model.comparison(left.float(), right.float()).cpu().tolist())
        cosines.extend((left.float() * right.float()).sum(-1).cpu().tolist())
        lefts.append(left.float().cpu())
        rights.append(right.float().cpu())
    vectors = {"left": torch.cat(lefts), "right": torch.cat(rights)}
    rows = scored_rows(pairs.rows, values)
    correction = np.asarray(values) - np.asarray(cosines)
    diagnostics = {
        "score_min": min(values),
        "score_max": max(values),
        "correction_min": float(correction.min()),
        "correction_max": float(correction.max()),
        "correction_mean": float(correction.mean()),
    }
    if initial is not None:
        diagnostics["mean_initial_embedding_cosine"] = float(
            torch.cat([(vectors[k] * initial[k]).sum(-1) for k in vectors]).mean()
        )
    return rows, vectors, diagnostics


def save_joint(path, model, config, epoch, step):
    torch.save(
        {
            "kind": SCORER,
            "config": config.model_dump(),
            "state": trainable_state(model),
            "epoch": epoch,
            "step": step,
        },
        path,
    )


def fit_joint(context, model, training, validation):
    """Fit the declared objective and preserve complete epoch boundary resume state."""
    config = context.config
    progress.configure(config.progress_path)
    optimizer = optimizer_for(model, config)
    parameters = [p for p in model.parameters() if p.requires_grad]
    generator = torch.Generator().manual_seed(config.seed + 10000)
    targets = torch.tensor(
        [r["target"] for r in training.rows], dtype=torch.float32, device=config.device
    )
    identities = {
        name: file_sha256(context.inputs[name]) for name in ("training", "validation")
    }
    for name, digest in identities.items():
        if digest != getattr(config, name + "_sha256"):
            raise ValueError(f"Changed {name} input bytes.")
    stopping = ValidationPatience(config.patience)
    history, selected, step, epoch = [], None, 0, 0
    initial_digest = state_digest(trainable_state(model))
    initial_vectors = None
    microbatch, profile = config.microbatch_size, []
    if config.start_epoch:
        parent = load_resume_state(context.inputs["parent_resume"])
        state = parent.dataloader.state_dict
        saved = load_model(context.inputs["parent_last_model"])
        current = config.model_dump()
        runtime = {
            "start_epoch",
            "max_epochs",
            "max_seconds",
            "device",
            "microbatch_size",
            "autotune_microbatch",
            "checkpoint_root",
            "progress_path",
        }
        if any(current[k] != v for k, v in saved["config"].items() if k not in runtime):
            raise ValueError("Resume changed a scientific training setting.")
        if (
            state["inputs"] != identities
            or saved["kind"] != SCORER
            or state["epoch"] != config.start_epoch
            or saved["epoch"] != state["epoch"]
            or saved["step"] != state["step"]
            or file_sha256(context.inputs["parent_last_model"])
            != state["last_model_sha256"]
        ):
            raise ValueError("Resume model, counters and input identities disagree.")
        restore_parameters(model, saved["state"])
        optimizer.load_state_dict(parent.optimizer_state["optimizer"])
        expected_steps = config.start_epoch * math.ceil(
            len(training.rows) / config.batch_size
        )
        if state["step"] != expected_steps or any(
            int(item["step"]) != expected_steps
            for item in optimizer.state.values()
            if "step" in item
        ):
            raise ValueError("Resume optimizer moments and epoch counters disagree.")
        generator.set_state(state["generator_state"])
        restore_main_process_rng(parent.main_process_rng, context.numpy_generators)
        epoch, step = state["epoch"], state["step"]
        history, selected = state["history"], state["selected"]
        stopping.best_score, stopping.stale_epochs = (
            state["best_score"],
            state["stale_epochs"],
        )
        initial_digest = state["initial_digest"]
        initial_vectors = load_model(context.inputs["parent_initial_vectors"])
        for name in ("model", "validation_predictions", "initial_vectors"):
            shutil.copyfile(context.inputs["parent_" + name], context.outputs[name])
        if file_sha256(context.outputs["model"]) != selected["sha256"]:
            raise ValueError("Restored selected checkpoint hash differs.")
        if config.autotune_microbatch:
            microbatch, profile = tune_microbatch(model, training, targets, config)
            restore_main_process_rng(parent.main_process_rng, context.numpy_generators)
    else:
        microbatch, profile = tune_microbatch(model, training, targets, config)
        if initial_digest != state_digest(trainable_state(model)):
            raise ValueError("Profiling changed an initial parameter.")
        reset_rng(config.seed + 2000)
        rows, initial_vectors, diagnostics = validation_predictions(
            model, validation, max(microbatch, config.encode_batch_size)
        )
        torch.save(initial_vectors, context.outputs["initial_vectors"])
        metrics = summarize(rows)
        if metrics["spearman"] is None:
            raise ValueError("Initialization requires defined validation Spearman.")
        stopping.observe(metrics["spearman"])
        save_joint(context.outputs["model"], model, config, 0, 0)
        write_json(context.outputs["validation_predictions"], rows)
        selected = {
            "epoch": 0,
            "step": 0,
            "sha256": file_sha256(context.outputs["model"]),
            "validation": metrics,
        }
        progress.append(
            "native_initial_validation",
            seed=config.seed,
            epoch=0,
            validation={"Joint": metrics},
        )
    cloud = (
        CheckpointCloud(
            config.checkpoint_root,
            config.checkpoint_destination,
            config.model_dump(),
            wait_for_first=False,
            prefix="csts_native_comparison_20261028/checkpoints",
        )
        if config.checkpoint_root
        else None
    )
    started = time.monotonic()
    reason = "epoch_ceiling"

    def checkpoint():
        save_joint(context.outputs["last_model"], model, config, epoch, step)
        trace = {
            "status": "running",
            "kind": SCORER,
            "config": config.model_dump(),
            "seed": config.seed,
            "epochs": history,
            "selected": selected,
            "completed_epoch": epoch,
            "actual_updates": step,
            "epochs_without_improvement": stopping.stale_epochs,
            "initial_trainable_sha256": initial_digest,
            "training_inputs": identities,
            "effective_microbatch_size": microbatch,
            "microbatch_profile": profile,
            "phase_elapsed_seconds": time.monotonic() - started,
        }
        write_json(context.outputs["trace"], trace)
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
                        "inputs": identities,
                        "last_model_sha256": file_sha256(context.outputs["last_model"]),
                        "history": history,
                        "selected": selected,
                        "initial_digest": initial_digest,
                        "best_score": stopping.best_score,
                        "stale_epochs": stopping.stale_epochs,
                        "microbatch": microbatch,
                    },
                ),
            ),
        )
        if cloud is not None:
            files = {
                "resume.pt": context.outputs["resume_state"],
                "last_model.pt": context.outputs["last_model"],
                "model.pt": context.outputs["model"],
                "trace.json": context.outputs["trace"],
                "predictions.json": context.outputs["validation_predictions"],
            }
            if epoch == config.start_epoch:
                files["initial_vectors.pt"] = context.outputs["initial_vectors"]
            cloud.submit(files, {"seed": config.seed, "epoch": epoch, "step": step})
        return trace

    try:
        checkpoint()
        for epoch in range(config.start_epoch + 1, config.max_epochs + 1):
            if time.monotonic() - started > config.max_seconds:
                raise TimeoutError(
                    "Resume the last completed epoch from its Cloud checkpoint."
                )
            model.train()
            order = torch.randperm(len(training.rows), generator=generator)
            order_digest = state_digest({"order": order})
            squared = torch.zeros((), device=config.device)
            norms, adapter_norms, comparison_norms = [], [], []
            begin = time.monotonic()
            for start in range(0, len(order), config.batch_size):
                chosen = order[start : start + config.batch_size]
                optimizer.zero_grad(set_to_none=True)
                squared += logical_batch_backward(
                    model, training, chosen, targets, microbatch
                )
                if start == 0 or step % 25 == 0:
                    adapter_norms.append(
                        gradient_norm(optimizer.param_groups[0]["params"])
                    )
                    comparison_norms.append(
                        gradient_norm(optimizer.param_groups[1]["params"])
                    )
                norm = torch.nn.utils.clip_grad_norm_(
                    parameters, 1.0, error_if_nonfinite=True
                )
                norms.append(float(norm))
                optimizer.step()
                step += 1
                if step % 25 == 0:
                    progress.append(
                        "native_rating_updates",
                        seed=config.seed,
                        epoch=epoch,
                        completed=start + len(chosen),
                        total=len(order),
                        name=f"optimizer updates {step}",
                    )
            synchronize(config.device)
            fit_seconds = time.monotonic() - begin
            begin = time.monotonic()
            rows, _, diagnostics = validation_predictions(
                model,
                validation,
                max(microbatch, config.encode_batch_size),
                initial_vectors,
            )
            metrics = summarize(rows)
            if metrics["spearman"] is None:
                raise ValueError("Validation Spearman became undefined.")
            exhausted = stopping.observe(metrics["spearman"])
            if metrics["spearman"] > selected["validation"]["spearman"]:
                save_joint(context.outputs["model"], model, config, epoch, step)
                write_json(context.outputs["validation_predictions"], rows)
                selected = {
                    "epoch": epoch,
                    "step": step,
                    "sha256": file_sha256(context.outputs["model"]),
                    "validation": metrics,
                }
            record = {
                "epoch": epoch,
                "step": step,
                "training_mse_0_1": float(squared) / len(training.rows),
                "validation": metrics,
                "fit_seconds": fit_seconds,
                "validation_seconds": time.monotonic() - begin,
                "batch_order_sha256": order_digest,
                "mean_preclip_gradient_norm": float(np.mean(norms)),
                "sampled_adapter_gradient_norm": float(np.mean(adapter_norms)),
                "sampled_comparison_gradient_norm": float(np.mean(comparison_norms)),
                "adapter_factor_norm": parameter_norm(
                    optimizer.param_groups[0]["params"]
                ),
                "comparison_norm": parameter_norm(optimizer.param_groups[1]["params"]),
                "comparison_bias": float(model.comparison.residual.bias.detach()),
                "epochs_without_improvement": stopping.stale_epochs,
                "diagnostics": diagnostics,
            }
            history.append(record)
            context.metrics["training_objective"].record(
                record["training_mse_0_1"], step=epoch
            )
            record_validation(context, metrics, epoch)
            progress.append(
                "native_rating_epoch",
                seed=config.seed,
                epoch=epoch,
                validation={"Joint": metrics},
                name=f"selected epoch {selected['epoch']}; fit seconds {fit_seconds:.1f}",
            )
            checkpoint()
            print({"seed": config.seed, **record}, flush=True)
            if exhausted:
                reason = "validation_patience"
                break
        trace = load_json(context.outputs["trace"])
        trace.update(
            status="complete" if reason == "validation_patience" else "incomplete",
            stop_reason=reason,
            budget_censored=reason != "validation_patience",
        )
        write_json(context.outputs["trace"], trace)
        if cloud is not None:
            cloud.submit(
                {
                    "resume.pt": context.outputs["resume_state"],
                    "last_model.pt": context.outputs["last_model"],
                    "model.pt": context.outputs["model"],
                    "trace.json": context.outputs["trace"],
                    "predictions.json": context.outputs["validation_predictions"],
                },
                {
                    "seed": config.seed,
                    "epoch": epoch,
                    "step": step,
                    "status": trace["status"],
                },
            )
    finally:
        if cloud is not None:
            cloud.finish()
            write_json(
                context.outputs["checkpoint_receipts"],
                {
                    "status": "published",
                    "publications": [f.result() for f in cloud.futures],
                },
            )


@train(config=NativeComparisonConfig)
def fit_native_comparison(context: StageContext[NativeComparisonConfig]) -> None:
    reset_rng(context.config.seed)
    tokenizer = load_tokenizer(context.config)
    model = JointEncoder(
        load_backbone(context.config, adapters=context.config),
        context.config.embedding_dimension,
    ).to(context.config.device)
    training = JointPairs(
        load_json(context.inputs["training"]), context.config, tokenizer
    )
    validation = JointPairs(
        load_json(context.inputs["validation"]), context.config, tokenizer
    )
    fit_joint(context, model, training, validation)


@build(config=NativeScoreConfig)
def capture_native_comparison(context: StageContext[NativeScoreConfig]) -> None:
    config = context.config
    for name, expected in (
        ("model", config.model_sha256),
        ("rows", config.rows_sha256),
        ("selection", config.selection_sha256),
    ):
        if file_sha256(context.inputs[name]) != expected:
            raise ValueError(f"Changed frozen {name} bytes.")
    selection = load_json(context.inputs["selection"])
    if config.model_sha256 not in selection["selected_model_sha256"].values():
        raise ValueError(
            "Prediction model is absent from the frozen executed seed list."
        )
    saved = load_model(context.inputs["model"])
    if saved["kind"] != SCORER:
        raise ValueError("Native scoring requires the stored learned comparison.")
    fitted = NativeComparisonConfig.model_validate(
        {**saved["config"], "device": config.device}
    )
    if encoder_settings(fitted) != encoder_settings(config):
        raise ValueError("Prediction representation differs from the saved encoder.")
    reset_rng(fitted.seed)
    model = JointEncoder(
        load_backbone(fitted, adapters=fitted), fitted.embedding_dimension
    ).to(config.device)
    restore_parameters(model, saved["state"])
    pairs = JointPairs(
        load_json(context.inputs["rows"]), fitted, load_tokenizer(fitted)
    )
    rows, _, diagnostics = validation_predictions(
        model, pairs, config.encode_batch_size
    )
    write_json(context.outputs["predictions"], rows)
    write_json(
        context.outputs["diagnostics"],
        {
            "model_sha256": config.model_sha256,
            "rows_sha256": config.rows_sha256,
            "selection_sha256": config.selection_sha256,
            "rows": len(rows),
            **diagnostics,
        },
    )
