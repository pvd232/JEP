"""Native stages for the frozen-backbone evidence-readout mechanism screen."""

import itertools
import json
import math
import re
import time
from pathlib import Path
from typing import Any, Literal

import numpy as np
import torch
from pydantic import Field
from torch.nn import functional as F
from viper.config import EvalConfig, MetricConfig, TrainConfig
from viper.metrics import FloatComparator, MetricContext, MetricDependency, measure
from viper.metrics import metric as declare_metric
from viper.randomness import capture_main_process_rng
from viper.resume import (
    DataLoaderConfiguration,
    DataLoaderResumeState,
    ResumeState,
    save_resume_state,
)
from viper.stages import StageContext, build, eval, train

from csts_pilot.baseline_models import (
    PROMPT,
    EncoderConfig,
    FitConfig,
    last_token_pool,
    load_backbone,
    load_tokenizer,
    pad_sequences,
    restore_parameters,
    state_digest,
    trainable_state,
    validate_rows,
)
from csts_pilot.condition_reference import native_layout
from csts_pilot.convergence import file_sha256, write_json
from csts_pilot.evidence_attention import token_metadata
from csts_pilot.evidence_readout import (
    ARMS,
    COMPARATOR_ARMS,
    CONTRASTS,
    SCHEMA_VERSION,
    EvidenceReadout,
    SymmetricComparison,
    clone_state,
    gradient_diagnostic,
    matched_initial_heads,
    metric_values,
    object_sha256,
    pack_batch,
    paired_intervals,
    predict,
    readout_vectors,
    selection_loss,
    training_targets,
    validate_cache,
    validate_capture,
)
from jep_pilot.loaders import load_json, load_model


def emit(event: str, **values: Any) -> None:
    """Stream finite, caption-free progress to the native worker log."""
    print(json.dumps({"event": event, **values}, allow_nan=False), flush=True)


@declare_metric(metric_id="readout_test_evidence_advantage", mode="stateless")
def evidence_advantage(context: MetricContext[MetricConfig]) -> float:
    """Expose the fixed test contrast as a native metric, without selecting on it."""
    value = float(load_json(context.artifacts["report"])["primary_C_minus_B"]["mean"])
    if not math.isfinite(value):
        raise ValueError("The held-out evidence advantage must be finite.")
    return value


def readout_evaluation_metric() -> Any:
    """Bind the final report explicitly for VIPER's separate metric worker."""
    return measure(
        evidence_advantage,
        dependencies=(
            MetricDependency(source="artifact", name="report", data_role="eval"),
        ),
        comparator=FloatComparator(mode="absolute", tolerance=1e-12),
    )


class ReadoutExtractionConfig(EncoderConfig):
    """Bind the frozen adapter, original rows, and optional training teacher."""

    model_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    rows_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    split: Literal["training", "validation", "test", "interventions"]
    records_sha256: str | None = Field(default=None, pattern=r"^[0-9a-f]{64}$")
    provenance_sha256: str | None = Field(default=None, pattern=r"^[0-9a-f]{64}$")
    audit_gate_sha256: str | None = Field(default=None, pattern=r"^[0-9a-f]{64}$")
    selection_sha256: str | None = Field(default=None, pattern=r"^[0-9a-f]{64}$")


class ReadoutFitConfig(TrainConfig):
    """Fit both heads in lockstep; neither head chooses the other's checkpoint."""

    seed: int = Field(default=7, ge=0)
    device: Literal["cpu", "cuda"] = "cuda"
    query_dim: int = Field(default=128, ge=1)
    evidence_weight: float = Field(default=0.1, gt=0, allow_inf_nan=False)
    learning_rate: float = Field(default=0.001, gt=0, allow_inf_nan=False)
    weight_decay: float = Field(default=0.01, ge=0, allow_inf_nan=False)
    batch_size: int = Field(default=32, ge=1)
    max_epochs: int = Field(default=48, ge=1)
    patience: int = Field(default=5, ge=1)
    comparison_max_epochs: int = Field(default=48, ge=1)
    comparison_patience: int = Field(default=5, ge=1)
    training_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    validation_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    training_cache_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    validation_cache_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")


class ReadoutEvaluationConfig(EvalConfig):
    """Evaluate frozen seed pairs on one complete held-out cohort."""

    device: Literal["cpu", "cuda"] = "cuda"
    rows_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    cache_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    intervention_rows_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    intervention_cache_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    model_sha256: dict[str, str]
    selection_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    bootstrap_draws: int = Field(default=2000, ge=1)
    bootstrap_seed: int = 61027
    ratings_cache_sha256: str | None = Field(default=None, pattern=r"^[0-9a-f]{64}$")
    cohorts_sha256: str | None = Field(default=None, pattern=r"^[0-9a-f]{64}$")


def checked(path: Path, expected: str) -> None:
    """Fail closed on changed input bytes, before deserialization."""
    if file_sha256(path) != expected:
        raise ValueError(f"Changed readout input: {path.name}.")


def checked_selection(path: Path, expected: str) -> dict[str, str]:
    """Require a frozen selection record before any held-out extraction."""
    checked(path, expected)
    frozen = load_json(path)
    if (
        frozen.get("status") != "checkpoints_frozen"
        or frozen.get("test_scores_used_for_selection") is not False
        or not frozen.get("models")
    ):
        raise ValueError(
            "Test access requires frozen models selected without test scores."
        )
    return {seed: item["sha256"] for seed, item in frozen["models"].items()}


@build(config=ReadoutExtractionConfig)
def extract_readout(context: StageContext[ReadoutExtractionConfig]) -> None:
    """Cache source states, causal condition means, and the exact parent EOD readout."""
    config, started = context.config, time.monotonic()
    if config.split in {"test", "interventions"}:
        if config.selection_sha256 is None:
            raise ValueError("Held-out extraction requires a frozen selection hash.")
        checked_selection(context.inputs["selection"], config.selection_sha256)
    elif config.selection_sha256 is not None or "selection" in context.inputs:
        raise ValueError("Fitting-cohort extraction must precede selection.")
    checked(context.inputs["model"], config.model_sha256)
    checked(context.inputs["rows"], config.rows_sha256)
    rows = load_json(context.inputs["rows"])
    validate_rows(rows)
    if config.split == "training":
        if config.records_sha256 is None:
            raise ValueError(
                "Training extraction requires the pinned evidence capture."
            )
        checked(context.inputs["records"], config.records_sha256)
        records = load_json(context.inputs["records"])
        if not isinstance(records, list):
            raise ValueError("Teacher capture must be a list of records.")
        if config.provenance_sha256 is None or config.audit_gate_sha256 is None:
            raise ValueError(
                "Seal the teacher provenance and gate in the extraction stage."
            )
        checked(context.inputs["provenance"], config.provenance_sha256)
        checked(context.inputs["audit_gate"], config.audit_gate_sha256)
        validate_capture(
            load_json(context.inputs["provenance"]),
            load_json(context.inputs["audit_gate"]),
            config.records_sha256,
            config.rows_sha256,
            config.audit_gate_sha256,
            len(records),
        )
    else:
        if any(
            v is not None
            for v in (
                config.records_sha256,
                config.provenance_sha256,
                config.audit_gate_sha256,
            )
        ) or any(k in context.inputs for k in ("records", "provenance", "audit_gate")):
            raise ValueError("Held-out extraction cannot bind teacher records.")
        records = []
    keys, left, right = native_layout(rows)
    saved = load_model(context.inputs["model"])
    fit = FitConfig.model_validate(
        {k: saved["config"][k] for k in FitConfig.model_fields if k in saved["config"]}
    )
    fit = fit.model_copy(update={"device": config.device})
    if fit.kind != "lora":
        raise ValueError("The parent must be the trained attention-only LoRA model.")
    for name in ("model_id", "revision", "max_length", "embedding_dimension"):
        if getattr(config, name) != getattr(fit, name):
            raise ValueError(f"Changed parent encoder setting: {name}.")
    if config.encode_batch_size != 4:
        raise ValueError("Preserve the parent's two-comparison extraction layout.")
    tokenizer = load_tokenizer(config)
    metadata = token_metadata(tokenizer, keys, config)
    targets, coverage = training_targets(keys, metadata, records)
    if config.split == "training" and not any(t.sum() > 0 for t in targets):
        raise ValueError("No supervised evidence survived literal alignment.")
    model = load_backbone(fit, adapters=fit)
    restore_parameters(model, saved["state"])
    before = state_digest(trainable_state(model))
    model.eval().requires_grad_(False)
    del saved
    values, queries, eod, pointers = [], [], [], [0]
    if config.device == "cuda":
        torch.cuda.reset_peak_memory_stats()
    with torch.inference_mode():
        for start in range(0, len(keys), config.encode_batch_size):
            selected = metadata[start : start + config.encode_batch_size]
            batch = pad_sequences(tokenizer, [m["input_ids"] for m in selected], config)
            with torch.autocast(
                config.device,
                enabled=config.device == "cuda",
                dtype=torch.bfloat16,
                cache_enabled=False,
            ):
                hidden = model(**batch).last_hidden_state
            eod.append(last_token_pool(hidden, batch["attention_mask"]).cpu())
            for local, meta in enumerate(selected):
                shift = (
                    hidden.shape[1] - len(meta["input_ids"])
                    if tokenizer.padding_side == "left"
                    else 0
                )
                p = torch.tensor(meta["passage_indices"], device=config.device) + shift
                c = (
                    torch.tensor(meta["condition_indices"], device=config.device)
                    + shift
                )
                values.append(hidden[local, p].cpu().to(torch.bfloat16))
                queries.append(hidden[local, c].float().mean(0).cpu())
                pointers.append(pointers[-1] + len(p))
            if start % 200 == 0 or start + len(selected) == len(keys):
                emit(
                    "readout_extraction",
                    split=config.split,
                    done=start + len(selected),
                    total=len(keys),
                    seconds=time.monotonic() - started,
                )
    after = state_digest({n: p for n, p in model.named_parameters() if "lora_" in n})
    if before != after:
        raise ValueError("Frozen adapter bytes changed during extraction.")
    cache = {
        "schema_version": SCHEMA_VERSION,
        "keys": keys,
        "left": left,
        "right": right,
        "pointers": pointers,
        "token_values": torch.cat(values),
        "condition_states": torch.stack(queries),
        "eod_vectors": torch.cat(eod),
        "span_targets": torch.cat([t[1:] for t in targets]),
        "null_targets": torch.stack([t[0] for t in targets]),
        "metadata": metadata,
        "embedding_dimension": config.embedding_dimension,
        "split": config.split,
        "rows_sha256": config.rows_sha256,
        "records_sha256": config.records_sha256,
        "model_sha256": config.model_sha256,
        "revision": config.revision,
        "prompt": PROMPT,
        "adapter_before_sha256": before,
        "adapter_after_sha256": after,
        "coverage": coverage,
        "selection_sha256": config.selection_sha256,
    }
    validate_cache(cache, rows)
    torch.save(cache, context.outputs["cache"])
    write_json(
        context.outputs["diagnostics"],
        {
            "split": config.split,
            "rows": len(rows),
            "occurrences": len(keys),
            "source_tokens": pointers[-1],
            "coverage": coverage,
            "frozen_adapter_sha256": before,
            "seconds": time.monotonic() - started,
            "cache_sha256": file_sha256(context.outputs["cache"]),
            "peak_cuda_bytes": torch.cuda.max_memory_allocated()
            if config.device == "cuda"
            else 0,
        },
    )


def train_pair(
    training: dict[str, Any],
    validation: dict[str, Any],
    training_rows: list[dict[str, Any]],
    validation_rows: list[dict[str, Any]],
    config: ReadoutFitConfig,
    on_epoch: Any = None,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]]:
    """Pure paired fitting engine, also exercised by the CPU integration fixture."""
    validate_cache(training, training_rows)
    validate_cache(validation, validation_rows)
    if training["split"] != "training" or validation["split"] != "validation":
        raise ValueError("Paired fitting binds training and validation only.")
    if {r["group_id"] for r in training_rows} & {
        r["group_id"] for r in validation_rows
    }:
        raise ValueError("Training and validation source groups overlap.")
    for name in (
        "model_sha256",
        "revision",
        "prompt",
        "embedding_dimension",
        "adapter_before_sha256",
    ):
        if training[name] != validation[name]:
            raise ValueError(f"The paired caches use different encoders: {name}.")
    heads = matched_initial_heads(
        training["embedding_dimension"], config.query_dim, config.seed
    )
    initial_hash = state_digest(clone_state(heads["ratings"]))
    heads = {a: h.to(config.device) for a, h in heads.items()}
    optimizers = {
        a: torch.optim.AdamW(
            h.parameters(), lr=config.learning_rate, weight_decay=config.weight_decay
        )
        for a, h in heads.items()
    }
    generator = torch.Generator().manual_seed(config.seed)
    best: dict[str, dict[str, Any]] = {
        a: {"spearman": -float("inf"), "epoch": 0, "state": None} for a in ARMS
    }
    history, predictions, gradients = [], {}, {}
    target = torch.tensor([r["target"] for r in training_rows], device=config.device)
    stale, updates = 0, 0
    for epoch in range(1, config.max_epochs + 1):
        order = torch.randperm(len(training_rows), generator=generator).tolist()
        totals = {a: 0.0 for a in ARMS}
        rating_totals = {a: 0.0 for a in ARMS}
        evidence_totals = {a: 0.0 for a in ARMS}
        teacher_hits = {a: 0 for a in ARMS}
        supervised_units = 0
        for start in range(0, len(order), config.batch_size):
            ix = order[start : start + config.batch_size]
            positions = [training["left"][i] for i in ix] + [
                training["right"][i] for i in ix
            ]
            tokens, condition, mask, gold = pack_batch(
                training, positions, config.device
            )
            for arm, head in heads.items():
                head.train()
                vectors, logits, _ = head(tokens, condition, mask)
                predicted = (vectors[: len(ix)] * vectors[len(ix) :]).sum(1)
                rating_loss = F.mse_loss(predicted, target[ix])
                evidence_loss, units = selection_loss(logits, mask, gold)
                rating_totals[arm] += float(rating_loss.detach()) * len(ix)
                evidence_totals[arm] += float(evidence_loss.detach()) * units
                teacher_hits[arm] += int(
                    (gold.gather(1, logits.detach().argmax(1)[:, None]) > 0).sum()
                )
                if arm == "evidence":
                    supervised_units += units
                    if start == 0:
                        gradients[str(epoch)] = gradient_diagnostic(
                            head, rating_loss, evidence_loss, config.evidence_weight
                        )
                loss = rating_loss + (
                    config.evidence_weight * evidence_loss if arm == "evidence" else 0
                )
                if not torch.isfinite(loss):
                    raise ValueError("Nonfinite paired objective.")
                optimizers[arm].zero_grad(set_to_none=True)
                loss.backward()
                norm = torch.nn.utils.clip_grad_norm_(
                    head.parameters(), 1.0, error_if_nonfinite=True
                )
                if not torch.isfinite(norm):
                    raise ValueError("Nonfinite readout gradient.")
                optimizers[arm].step()
                totals[arm] += float(loss.detach()) * len(ix)
            updates += 1
        metrics, improved = {}, False
        for arm, head in heads.items():
            values, _, _ = predict(head, validation, config.device)
            metrics[arm] = metric_values(validation_rows, values)
            rho = metrics[arm]["spearman"]
            if rho is None:
                raise ValueError(
                    "Validation Spearman is undefined; no checkpoint can be selected."
                )
            if rho > best[arm]["spearman"]:
                best[arm] = {
                    "spearman": rho,
                    "epoch": epoch,
                    "state": clone_state(head),
                }
                predictions[arm] = values.tolist()
                improved = True
        stale = 0 if improved else stale + 1
        record = {
            "epoch": epoch,
            "updates_per_arm": updates,
            "order_sha256": object_sha256(order),
            "validation": metrics,
            "training_objective": {a: totals[a] / len(order) for a in ARMS},
            "training_rating_mse": {a: rating_totals[a] / len(order) for a in ARMS},
            "training_teacher_ce": {
                a: evidence_totals[a] / supervised_units if supervised_units else None
                for a in ARMS
            },
            "training_teacher_top1_agreement": {
                a: teacher_hits[a] / supervised_units if supervised_units else None
                for a in ARMS
            },
            "evidence_supervised_occurrences": supervised_units,
            "joint_stale_epochs": stale,
        }
        history.append(record)
        emit("readout_epoch", seed=config.seed, **record)
        if on_epoch is not None:
            on_epoch(record)
        if stale >= config.patience:
            break
    model = {
        "schema_version": SCHEMA_VERSION,
        "config": config.model_dump(),
        "embedding_dimension": training["embedding_dimension"],
        "parent_model_sha256": training["model_sha256"],
        "frozen_adapter_sha256": training["adapter_before_sha256"],
        "training_groups": sorted({r["group_id"] for r in training_rows}),
        "validation_groups": sorted({r["group_id"] for r in validation_rows}),
        "selected": best,
        "last_state": {a: clone_state(h) for a, h in heads.items()},
    }
    trace = {
        "status": "complete",
        "seed": config.seed,
        "initial_state_sha256": initial_hash,
        "epochs": history,
        "updates_per_arm": updates,
        "gradient_diagnostics": gradients,
        "stop_reason": "joint_validation_patience"
        if stale >= config.patience
        else "epoch_ceiling",
        "budget_censored": stale < config.patience,
        "selected_epoch": {a: best[a]["epoch"] for a in ARMS},
        "selected_state_sha256": {a: state_digest(best[a]["state"]) for a in ARMS},
        "training_evidence_coverage": training["coverage"],
    }
    terminal = {
        "optimizer": {a: o.state_dict() for a, o in optimizers.items()},
        "epoch": epoch,
        "updates": updates,
        "generator_state": generator.get_state(),
        "joint_stale_epochs": stale,
    }
    comparison, comparison_trace, comparison_predictions, comparison_terminal = (
        fit_comparisons(
            heads,
            best,
            training,
            validation,
            training_rows,
            validation_rows,
            config,
            on_epoch,
            len(history),
        )
    )
    model["comparisons"] = comparison
    trace["comparison"] = comparison_trace
    predictions.update(comparison_predictions)
    terminal["comparison"] = comparison_terminal
    return model, trace, predictions, terminal


def fit_comparisons(
    heads: dict[str, EvidenceReadout],
    selected: dict[str, Any],
    training: dict[str, Any],
    validation: dict[str, Any],
    training_rows: list[dict[str, Any]],
    validation_rows: list[dict[str, Any]],
    config: ReadoutFitConfig,
    on_epoch: Any = None,
    step_offset: int = 0,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]]:
    """Fit D/E only after freezing B/C, so the comparison intervention is identifiable."""
    vectors: dict[str, dict[str, torch.Tensor]] = {}
    before = {}
    for arm, head in heads.items():
        head.load_state_dict(selected[arm]["state"], strict=True)
        head.zero_grad(set_to_none=True)
        head.eval().requires_grad_(False)
        before[arm] = state_digest(clone_state(head))
        vectors[arm] = {
            name: readout_vectors(head, cache, config.device)[0]
            .detach()
            .to(config.device)
            for name, cache in (("training", training), ("validation", validation))
        }
    comparators = {
        arm: SymmetricComparison(training["embedding_dimension"]).to(config.device)
        for arm in ARMS
    }
    optimizers = {
        arm: torch.optim.AdamW(
            c.parameters(), lr=config.learning_rate, weight_decay=config.weight_decay
        )
        for arm, c in comparators.items()
    }
    target = torch.tensor([r["target"] for r in training_rows], device=config.device)
    generator = torch.Generator().manual_seed(config.seed + 10000)

    def scores(arm: str, split: str) -> torch.Tensor:
        z = vectors[arm][split]
        cache = training if split == "training" else validation
        return comparators[arm](z[cache["left"]], z[cache["right"]])

    best, predictions = {}, {}
    for arm, comparator in comparators.items():
        with torch.no_grad():
            values = scores(arm, "validation").cpu().numpy()
        rho = metric_values(validation_rows, values)["spearman"]
        if rho is None:
            raise ValueError("Comparison epoch-zero Spearman is undefined.")
        best[arm] = {"epoch": 0, "spearman": rho, "state": clone_state(comparator)}
        predictions[arm + "_comparison"] = values.tolist()
    initial = state_digest(clone_state(comparators["ratings"]))
    history, stale, updates = [], 0, 0
    for epoch in range(1, config.comparison_max_epochs + 1):
        order = torch.randperm(len(training_rows), generator=generator).tolist()
        totals = {a: 0.0 for a in ARMS}
        for start in range(0, len(order), config.batch_size):
            ix = order[start : start + config.batch_size]
            for arm, comparator in comparators.items():
                z = vectors[arm]["training"]
                left = [training["left"][i] for i in ix]
                right = [training["right"][i] for i in ix]
                loss = F.mse_loss(comparator(z[left], z[right]), target[ix])
                if not torch.isfinite(loss):
                    raise ValueError("Nonfinite comparison objective.")
                optimizers[arm].zero_grad(set_to_none=True)
                loss.backward()
                torch.nn.utils.clip_grad_norm_(
                    comparator.parameters(), 1.0, error_if_nonfinite=True
                )
                optimizers[arm].step()
                totals[arm] += float(loss.detach()) * len(ix)
            updates += 1
        metrics, improved = {}, False
        for arm, comparator in comparators.items():
            with torch.no_grad():
                values = scores(arm, "validation").cpu().numpy()
            metrics[arm] = metric_values(validation_rows, values)
            rho = metrics[arm]["spearman"]
            if rho is None:
                raise ValueError("Comparison validation Spearman is undefined.")
            if rho > best[arm]["spearman"]:
                best[arm] = {
                    "epoch": epoch,
                    "spearman": rho,
                    "state": clone_state(comparator),
                }
                predictions[arm + "_comparison"] = values.tolist()
                improved = True
        stale = 0 if improved else stale + 1
        record = {
            "phase": "comparison",
            "epoch": epoch,
            "native_step": step_offset + epoch,
            "updates_per_arm": updates,
            "order_sha256": object_sha256(order),
            "validation": metrics,
            "training_objective": {a: totals[a] / len(order) for a in ARMS},
            "joint_stale_epochs": stale,
        }
        history.append(record)
        emit("comparison_epoch", seed=config.seed, **record)
        if on_epoch is not None:
            on_epoch(record)
        if stale >= config.comparison_patience:
            break
    after = {a: state_digest(clone_state(h)) for a, h in heads.items()}
    if before != after or any(
        p.grad is not None for h in heads.values() for p in h.parameters()
    ):
        raise ValueError("A frozen readout changed or received comparison gradients.")
    trace = {
        "epochs": history,
        "initial_state_sha256": initial,
        "readout_before_sha256": before,
        "readout_after_sha256": after,
        "selected_epoch": {a: b["epoch"] for a, b in best.items()},
        "selected_state_sha256": {a: state_digest(b["state"]) for a, b in best.items()},
        "updates_per_arm": updates,
        "budget_censored": stale < config.comparison_patience,
        "stop_reason": "joint_validation_patience"
        if stale >= config.comparison_patience
        else "epoch_ceiling",
    }
    return (
        {
            "selected": best,
            "last_state": {a: clone_state(c) for a, c in comparators.items()},
        },
        trace,
        predictions,
        {
            "optimizer": {a: o.state_dict() for a, o in optimizers.items()},
            "generator_state": generator.get_state(),
            "epoch": epoch,
            "updates": updates,
            "joint_stale_epochs": stale,
        },
    )


@train(config=ReadoutFitConfig)
def fit_readout(context: StageContext[ReadoutFitConfig]) -> None:
    """Select heads by validation Spearman and seal selected and terminal states separately."""
    config = context.config
    for name, expected in (
        ("training", config.training_sha256),
        ("validation", config.validation_sha256),
        ("training_cache", config.training_cache_sha256),
        ("validation_cache", config.validation_cache_sha256),
    ):
        checked(context.inputs[name], expected)

    def report(record: dict[str, Any]) -> None:
        epoch = record.get("native_step", record["epoch"])
        context.metrics["training_objective"].record(
            float(np.mean(list(record["training_objective"].values()))), step=epoch
        )
        for name in ("mse_0_1", "spearman"):
            context.metrics[
                "validation_mse" if name == "mse_0_1" else "validation_spearman"
            ].record(
                float(np.mean([record["validation"][a][name] for a in ARMS])),
                step=epoch,
            )
        write_json(
            context.outputs["trace"],
            {"status": "running", "seed": config.seed, "latest": record},
        )

    model, trace, predictions, terminal = train_pair(
        load_model(context.inputs["training_cache"]),
        load_model(context.inputs["validation_cache"]),
        load_json(context.inputs["training"]),
        load_json(context.inputs["validation"]),
        config,
        report,
    )
    torch.save(model, context.outputs["model"])
    selected_step = len(trace["epochs"]) + len(trace["comparison"]["epochs"]) + 1
    trace["native_selected_metric_step"] = selected_step
    selected_metrics = {
        a: metric_values(
            load_json(context.inputs["validation"]), np.asarray(predictions[a])
        )
        for a in predictions
    }
    context.metrics["validation_spearman"].record(
        float(np.mean([m["spearman"] for m in selected_metrics.values()])),
        step=selected_step,
    )
    context.metrics["validation_mse"].record(
        float(np.mean([m["mse_0_1"] for m in selected_metrics.values()])),
        step=selected_step,
    )
    write_json(context.outputs["trace"], trace)
    write_json(context.outputs["validation_predictions"], predictions)
    save_resume_state(
        context.outputs["resume_state"],
        ResumeState(
            optimizer_state=terminal["optimizer"],
            main_process_rng=capture_main_process_rng(
                context.numpy_generators, capture_legacy_global=True
            ),
            dataloader=DataLoaderResumeState(
                configuration=DataLoaderConfiguration(workers=0),
                state_dict={k: v for k, v in terminal.items() if k != "optimizer"},
            ),
        ),
    )


def selection_diagnostics(
    weights: list[torch.Tensor], null: np.ndarray
) -> dict[str, Any]:
    """Describe concentration and answerability without inventing held-out evidence labels."""
    entropy = [float(-(w * w.clamp_min(1e-30).log()).sum()) for w in weights]
    return {
        "mean_conditional_source_entropy": float(np.mean(entropy)),
        "mean_null_probability": float(np.mean(null)),
        "null_probability_quantiles": np.quantile(null, [0.1, 0.5, 0.9]).tolist(),
        "rows_abstained_or_dropped": 0,
    }


def condition_diagnostics(
    rows: list[dict[str, Any]], predictions: np.ndarray
) -> dict[str, Any]:
    """Retain condition-level ordering without exporting caption or condition text."""
    groups: dict[str, list[int]] = {}
    for i, row in enumerate(rows):
        groups.setdefault(object_sha256(row["condition"]), []).append(i)
    return {
        key: metric_values([rows[i] for i in ix], predictions[ix])
        for key, ix in groups.items()
    }


def paired_condition_diagnostics(
    rows: list[dict[str, Any]], predictions: np.ndarray
) -> dict[str, Any]:
    """Compare condition changes on the identical unordered sentence pair only."""
    groups: dict[tuple[str, str], list[int]] = {}
    for i, row in enumerate(rows):
        groups.setdefault(
            tuple(sorted((row["sentence1"], row["sentence2"]))), []
        ).append(i)
    margins, hits, ties = [], 0, 0
    for ix in groups.values():
        for i, j in itertools.combinations(ix, 2):
            truth = rows[i]["target"] - rows[j]["target"]
            if truth == 0 or rows[i]["condition"] == rows[j]["condition"]:
                continue
            delta = float(predictions[i] - predictions[j])
            hits += int(delta * truth > 0)
            ties += int(delta == 0)
            margins.append((delta - truth) ** 2)
    return {
        "comparisons": len(margins),
        "strict_correct": hits,
        "ties": ties,
        "accuracy_half_ties": (hits + 0.5 * ties) / len(margins) if margins else None,
        "difference_mse_0_1": float(np.mean(margins)) if margins else None,
    }


def family_diagnostics(
    rows: list[dict[str, Any]], predictions: np.ndarray, cohorts: dict[str, Any] | None
) -> dict[str, Any]:
    """Report overlapping descriptive families with explicit membership counts."""
    if cohorts is None:
        return {}
    mapping = cohorts["splits"]["test"]["condition_families"]
    colour = re.compile(cohorts["colour_regex"], re.IGNORECASE)
    members: dict[str, list[int]] = {}
    for i, row in enumerate(rows):
        members.setdefault(mapping.get(row["condition"], "unmapped"), []).append(i)
        if colour.search(row["condition"]):
            members.setdefault("colour", []).append(i)
    return {
        name: {
            **metric_values([rows[i] for i in ix], predictions[ix]),
            "row_ids": [rows[i]["row_id"] for i in ix],
        }
        for name, ix in members.items()
    }


def intervention_diagnostics(
    rows: list[dict[str, Any]],
    cache: dict[str, Any],
    predictions: np.ndarray,
    weights: list[torch.Tensor],
    null: np.ndarray,
) -> list[dict[str, Any]]:
    """Use independently re-encoded text edits, with labels specified before execution."""
    by_case: dict[str, dict[str, int]] = {}
    for i, row in enumerate(rows):
        by_case.setdefault(row["case"], {})[row["edit"]] = i
    result = []
    for case, ix in by_case.items():
        if set(ix) != {"base", "irrelevant", "relevant", "missing"}:
            raise ValueError(
                "An intervention case needs all four predeclared text variants."
            )
        base = float(predictions[ix["base"]])
        record = {
            "case": case,
            "source_tokens": {
                edit: cache["pointers"][cache["left"][i] + 1]
                - cache["pointers"][cache["left"][i]]
                for edit, i in ix.items()
            },
            "scores": {e: float(predictions[i]) for e, i in ix.items()},
            "irrelevant_absolute_change": abs(
                float(predictions[ix["irrelevant"]]) - base
            ),
            "relevant_score_decrease": base - float(predictions[ix["relevant"]]),
        }
        if weights:
            mass, nulls = {}, {}
            for edit, i in ix.items():
                position = cache["left"][i]
                quote = rows[i]["evidence_quote"]
                passage = rows[i]["sentence1"]
                start = passage.find(quote) if quote else -1
                offsets = cache["metadata"][position]["passage_offsets"]
                selected = [
                    j
                    for j, (a, b) in enumerate(offsets)
                    if start >= 0 and max(a, start) < min(b, start + len(quote))
                ]
                mass[edit] = (
                    float(weights[position][selected].sum()) if selected else None
                )
                nulls[edit] = float(null[position])
            record.update(
                conditional_quoted_evidence_mass=mass,
                null_probability=nulls,
                missing_minus_answered_null=nulls["missing"] - nulls["base"],
            )
        result.append(record)
    return result


@eval(config=ReadoutEvaluationConfig)
def evaluate_readout(context: StageContext[ReadoutEvaluationConfig]) -> None:
    """Score all frozen heads, the parent, and prospective synthetic interventions."""
    config = context.config
    if (
        checked_selection(context.inputs["selection"], config.selection_sha256)
        != config.model_sha256
    ):
        raise ValueError("Evaluation models differ from the frozen selection.")
    for name, expected in (
        ("test", config.rows_sha256),
        ("cache", config.cache_sha256),
        ("intervention_rows", config.intervention_rows_sha256),
        ("intervention_cache", config.intervention_cache_sha256),
    ):
        checked(context.inputs[name], expected)
    rows, cases = (
        load_json(context.inputs["test"]),
        load_json(context.inputs["intervention_rows"]),
    )
    if load_json(context.inputs["holdout"]) != list(range(len(rows))):
        raise ValueError(
            "The held-out indices must cover the complete original cohort."
        )
    cache, edited = (
        load_model(context.inputs["cache"]),
        load_model(context.inputs["intervention_cache"]),
    )
    validate_cache(cache, rows)
    validate_cache(edited, cases)
    if any(c["selection_sha256"] != config.selection_sha256 for c in (cache, edited)):
        raise ValueError("Held-out caches refer to another checkpoint selection.")
    if cache["split"] != "test" or edited["split"] != "interventions":
        raise ValueError(
            "Final evaluation requires held-out test and intervention caches."
        )
    predictions, results = {}, {}
    baseline, _, _ = predict(None, cache)
    results["A_parent"] = metric_values(rows, baseline)
    cohorts = None
    if config.cohorts_sha256 is not None:
        checked(context.inputs["cohorts"], config.cohorts_sha256)
        cohorts = load_json(context.inputs["cohorts"])
    pair_diagnostics = {"A_parent": paired_condition_diagnostics(rows, baseline)}
    families = {"A_parent": family_diagnostics(rows, baseline, cohorts)}
    references = {"A_parent": baseline.tolist()}
    if config.ratings_cache_sha256 is not None:
        checked(context.inputs["ratings_cache"], config.ratings_cache_sha256)
        ratings_cache = load_model(context.inputs["ratings_cache"])
        validate_cache(ratings_cache, rows)
        if (
            ratings_cache["split"] != "test"
            or ratings_cache["selection_sha256"] != config.selection_sha256
        ):
            raise ValueError(
                "The ratings reference must use the frozen test selection."
            )
        reference, _, _ = predict(None, ratings_cache)
        references["R_ratings_parent"] = reference.tolist()
        results["R_ratings_parent"] = metric_values(rows, reference)
        pair_diagnostics["R_ratings_parent"] = paired_condition_diagnostics(
            rows, reference
        )
        families["R_ratings_parent"] = family_diagnostics(rows, reference, cohorts)
    per_condition: dict[str, Any] = {"A_parent": condition_diagnostics(rows, baseline)}
    if "R_ratings_parent" in references:
        per_condition["R_ratings_parent"] = condition_diagnostics(
            rows, np.asarray(references["R_ratings_parent"])
        )
    base_edits, _, _ = predict(None, edited)
    interventions: dict[str, Any] = {
        "A_parent": intervention_diagnostics(
            cases, edited, base_edits, [], np.array([])
        )
    }
    for seed, digest in config.model_sha256.items():
        binding = (
            "model" if seed == next(iter(config.model_sha256)) else f"model_{seed}"
        )
        checked(context.inputs[binding], digest)
        saved = load_model(context.inputs[binding])
        if (
            saved["config"]["seed"] != int(seed)
            or saved["parent_model_sha256"] != cache["model_sha256"]
            or edited["model_sha256"] != cache["model_sha256"]
        ):
            raise ValueError("Frozen seed or parent identity changed.")
        if {r["group_id"] for r in rows} & set(
            saved["training_groups"] + saved["validation_groups"]
        ):
            raise ValueError("Test source groups overlap fitting cohorts.")
        predictions[seed], results[seed], interventions[seed] = {}, {}, {}
        per_condition[seed] = {}
        pair_diagnostics[seed], families[seed] = {}, {}
        for arm in (*ARMS, *COMPARATOR_ARMS):
            readout_arm = arm.removesuffix("_comparison")
            head = EvidenceReadout(
                saved["embedding_dimension"], saved["config"]["query_dim"]
            ).to(config.device)
            head.load_state_dict(saved["selected"][readout_arm]["state"], strict=True)
            comparator = None
            if arm in COMPARATOR_ARMS:
                comparator = SymmetricComparison(saved["embedding_dimension"]).to(
                    config.device
                )
                comparator.load_state_dict(
                    saved["comparisons"]["selected"][readout_arm]["state"], strict=True
                )
            values, weights, null = predict(head, cache, config.device, comparator)
            predictions[seed][arm] = values.tolist()
            per_condition[seed][arm] = condition_diagnostics(rows, values)
            pair_diagnostics[seed][arm] = paired_condition_diagnostics(rows, values)
            families[seed][arm] = family_diagnostics(rows, values, cohorts)
            results[seed][arm] = {
                **metric_values(rows, values),
                **selection_diagnostics(weights, null),
                "readout_selected_epoch": saved["selected"][readout_arm]["epoch"],
                "comparison_selected_epoch": saved["comparisons"]["selected"][
                    readout_arm
                ]["epoch"]
                if comparator is not None
                else None,
                "prediction_range": [float(values.min()), float(values.max())],
                "fraction_outside_0_1": float(np.mean((values < 0) | (values > 1))),
            }
            values, weights, null = predict(head, edited, config.device, comparator)
            interventions[seed][arm] = intervention_diagnostics(
                cases, edited, values, weights, null
            )
    contrasts = {}
    for name, coefficients in CONTRASTS.items():
        deltas = [
            sum(
                weight * results[s][a]["spearman"] for a, weight in coefficients.items()
            )
            for s in predictions
        ]
        mse = [
            sum(weight * results[s][a]["mse_0_1"] for a, weight in coefficients.items())
            for s in predictions
        ]
        contrasts[name] = {
            "per_seed": deltas,
            "mean": float(np.mean(deltas)),
            "sample_std": float(np.std(deltas, ddof=1)) if len(deltas) > 1 else None,
            "mse_delta_per_seed": mse,
            "mse_delta_mean": float(np.mean(mse)),
            "group_bootstrap_95": paired_intervals(
                rows,
                predictions,
                config.bootstrap_draws,
                config.bootstrap_seed,
                coefficients,
            ),
        }
    report = {
        "results": results,
        "primary_C_minus_B": contrasts["C_minus_B"],
        "contrasts": contrasts,
        "interventions": interventions,
        "per_condition": per_condition,
        "paired_condition": pair_diagnostics,
        "families": families,
        "interpretation": "C-B and E-D test evidence objectives under fixed comparison policies. D-B and E-C test comparison fitting on identical frozen readout vectors. E-D still includes the downstream refit. Synthetic edits do not prove rationale faithfulness.",
    }
    write_json(context.outputs["report"], report)
    write_json(
        context.outputs["predictions"],
        {
            "row_ids": [r["row_id"] for r in rows],
            **references,
            "seeds": predictions,
        },
    )
    emit(
        "readout_final_scores",
        results=results,
        primary_C_minus_B=report["primary_C_minus_B"],
    )
