"""Compare cached single-passage answers using the frozen selected Qwen encoder."""

import json
import math
import os
import time
from pathlib import Path
from typing import Any, Literal

import numpy as np
import torch
from pydantic import Field
from viper.stages import StageContext, build

from csts_pilot.answers import answer_id
from csts_pilot.baseline_models import (
    EncoderConfig,
    FitConfig,
    encode,
    load_backbone,
    load_tokenizer,
    pad_sequences,
    restore_parameters,
    state_digest,
    token_sequences,
    trainable_state,
    validate_rows,
)
from csts_pilot.condition_reference import arm_metrics, native_layout, recall_cutoff
from csts_pilot.convergence import file_sha256, synchronize, write_json
from csts_pilot.diagnostics import summarize
from csts_pilot.evidence_controls import checked_cache
from jep_pilot.loaders import load_json, load_model

ARMS = ("cached_span_conditioned", "cached_span_generic")
GENERIC_CONDITION = "overall meaning"


class AnswerInputConfig(EncoderConfig):
    """Pin the checkpoint, comparisons, teacher cache and saved comparator."""

    model_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    rows_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    answers_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    baseline_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    split: Literal["validation"] = "validation"
    encode_batch_size: Literal[4] = 4
    max_seconds: float = Field(default=1200, gt=0, allow_inf_nan=False)


def emit(event: str, **values: Any) -> None:
    """Stream progress to the native log and optional independent sidecar."""
    message = json.dumps({"event": event, **values}, allow_nan=False)
    print(message, flush=True)
    if destination := os.environ.get("CSTS_ANSWER_INPUT_EVENTS"):
        with Path(destination).open("a") as stream:
            stream.write(message + "\n")
            stream.flush()


def baseline_scores(
    rows: list[dict[str, Any]], saved: list[dict[str, Any]]
) -> np.ndarray:
    """Align sealed scores by exact row contents without rerunning the model."""
    lookup = {row["row_id"]: row for row in saved}
    if len(lookup) != len(saved) or set(lookup) != {r["row_id"] for r in rows}:
        raise ValueError("Saved comparator comparison identities differ.")
    result = []
    for row in rows:
        old = lookup[row["row_id"]]
        if {key: value for key, value in old.items() if key != "prediction"} != row:
            raise ValueError("Saved comparator row contents differ.")
        prediction = float(old["prediction"])
        if not math.isfinite(prediction):
            raise ValueError("Saved comparator prediction must be finite.")
        result.append(prediction)
    return np.asarray(result, dtype=np.float64)


def replaced_rows(
    rows: list[dict[str, Any]], records: dict[str, dict[str, Any]], arm: str
) -> tuple[list[dict[str, Any]], list[int], list[int]]:
    """Replace accepted sides; fallback retains the original condition and passage."""
    if arm not in ARMS:
        raise ValueError("Unknown answer-input arm.")
    active, indices, counts = [], [], []
    for index, row in enumerate(rows):
        chosen = []
        for side in ("sentence1", "sentence2"):
            record = records.get(answer_id(row[side], row["condition"]))
            chosen.append(record if record is not None and record["valid"] else None)
        count = sum(record is not None for record in chosen)
        counts.append(count)
        if not count:
            continue
        changed = dict(row)
        # Conditions may differ by side when the generic arm needs one fallback.
        changed["side_conditions"] = []
        for side, record in zip(("sentence1", "sentence2"), chosen, strict=True):
            changed[side] = record["answer"] if record is not None else row[side]
            changed["side_conditions"].append(
                GENERIC_CONDITION
                if record is not None and arm == "cached_span_generic"
                else row["condition"]
            )
        active.append(changed)
        indices.append(index)
    return active, indices, counts


def answer_layout(
    rows: list[dict[str, Any]],
) -> tuple[list[tuple[str, str]], list[int], list[int]]:
    """Keep the native two-comparison, left-then-right inference layout."""
    keys, left, right = native_layout(rows)
    for index, row in enumerate(rows):
        keys[left[index]] = (row["side_conditions"][0], row["sentence1"])
        keys[right[index]] = (row["side_conditions"][1], row["sentence2"])
    return keys, left, right


def decide(metrics: dict[str, Any]) -> dict[str, Any]:
    """Apply the prespecified validation gate to both complete hybrid systems."""
    native = metrics["saved_qwen"]
    eligibility = {}
    for arm in ARMS:
        result = metrics[arm]
        rank = result["spearman"]
        order = result["condition_changes"]["accuracy_ties_half"]
        native_order = native["condition_changes"]["accuracy_ties_half"]
        gain = None if rank is None else rank - native["spearman"]
        fpr_change = (
            result["operating_point"]["false_positive_rate"]
            - native["operating_point"]["false_positive_rate"]
        )
        order_change = (
            None if order is None or native_order is None else order - native_order
        )
        eligibility[arm] = {
            "spearman_change": gain,
            "false_positive_rate_change": fpr_change,
            "condition_ordering_change": order_change,
            "eligible": bool(
                gain is not None
                and gain >= 0.005 - 1e-12
                and fpr_change <= 0.01 + 1e-12
                and order_change is not None
                and order_change >= -0.01 - 1e-12
            ),
        }
    eligible = [arm for arm in ARMS if eligibility[arm]["eligible"]]
    selected = (
        max(eligible, key=lambda arm: metrics[arm]["spearman"]) if eligible else None
    )
    return {
        "selected_arm": selected,
        "eligibility": eligibility,
        "test_scores_used_for_selection": False,
        "thresholds": {
            arm: result["operating_point"]["cutoff"] for arm, result in metrics.items()
        },
    }


@build(config=AnswerInputConfig)
def infer(context: StageContext[AnswerInputConfig]) -> None:
    """Evaluate two frozen answer-as-input arms with zero optimizer updates."""
    config = context.config
    started = time.monotonic()
    for name, digest in (
        ("rows", config.rows_sha256),
        ("answers", config.answers_sha256),
        ("model", config.model_sha256),
        ("baseline_predictions", config.baseline_sha256),
    ):
        if file_sha256(context.inputs[name]) != digest:
            raise ValueError(f"Changed answer-input stage input: {name}.")
    rows = load_json(context.inputs["rows"])
    validate_rows(rows)
    baseline = baseline_scores(rows, load_json(context.inputs["baseline_predictions"]))
    records = checked_cache(context.inputs["answers"])
    saved = load_model(context.inputs["model"])
    fit = FitConfig.model_validate(saved["config"])
    if fit.kind != "lora":
        raise ValueError(
            "The answer-input diagnostic requires the selected LoRA model."
        )
    for name in ("model_id", "revision", "embedding_dimension", "max_length"):
        if getattr(fit, name) != getattr(config, name):
            raise ValueError(f"Checkpoint encoder setting differs: {name}.")
    fit = fit.model_copy(update={"device": config.device})
    tokenizer = load_tokenizer(config)
    emit("loading_model", split=config.split, rows=len(rows))
    model = load_backbone(fit, adapters=fit)
    restore_parameters(model, saved["state"])
    before = state_digest(trainable_state(model))
    del saved
    model.eval()
    model.requires_grad_(False)
    adapters = {name: p for name, p in model.named_parameters() if "lora_" in name}
    if config.device == "cuda":
        torch.cuda.reset_peak_memory_stats()
    baseline_cutoff = recall_cutoff(rows, baseline)
    recall = arm_metrics(rows, baseline, baseline_cutoff)["operating_point"]["recall"]
    metrics = {"saved_qwen": arm_metrics(rows, baseline, baseline_cutoff)}
    predictions, cache, coverage = {}, {}, {}
    last_emit = time.monotonic()
    tokens = 0
    with torch.inference_mode():
        for arm in ARMS:
            active, indices, counts = replaced_rows(rows, records, arm)
            keys, left, right = answer_layout(active)
            sequences = token_sequences(tokenizer, keys, config) if keys else []
            chunks = []
            for start in range(0, len(sequences), 4):
                if time.monotonic() - started > config.max_seconds:
                    raise TimeoutError("Answer-input extraction allowance exhausted.")
                batch = pad_sequences(tokenizer, sequences[start : start + 4], config)
                chunks.append(encode(model, batch).cpu())
                tokens += int(batch["attention_mask"].sum())
                now = time.monotonic()
                if now - last_emit >= 15 or start + 4 >= len(sequences):
                    emit(
                        "extraction_progress",
                        arm=arm,
                        done=min(start + 4, len(sequences)),
                        total=len(sequences),
                        elapsed_seconds=round(now - started, 2),
                    )
                    last_emit = now
            vectors = (
                torch.cat(chunks)
                if chunks
                else torch.empty((0, config.embedding_dimension))
            )
            scores = baseline.copy()
            if indices:
                scores[indices] = (vectors[left] * vectors[right]).sum(1).numpy()
            if not np.isfinite(scores).all():
                raise ValueError("Answer-input predictions must be finite.")
            # The achieved baseline recall is an integer ratio. A tiny downward
            # offset avoids rounding its product up to one extra positive.
            cutoff = recall_cutoff(rows, scores, recall=max(1e-12, recall - 1e-12))
            metrics[arm] = arm_metrics(rows, scores, cutoff)
            predictions[arm] = [
                dict(row, prediction=float(score))
                for row, score in zip(rows, scores, strict=True)
            ]
            coverage[arm] = {}
            for count, name in ((2, "both"), (1, "one"), (0, "neither")):
                subset = [i for i, value in enumerate(counts) if value == count]
                coverage[arm][name] = {
                    "rows": len(subset),
                    "candidate": summarize([predictions[arm][i] for i in subset])
                    if subset
                    else None,
                    "baseline": summarize(
                        [dict(rows[i], prediction=float(baseline[i])) for i in subset]
                    )
                    if subset
                    else None,
                }
            cache[arm] = {
                "vectors": vectors,
                "keys": keys,
                "active_row_indices": indices,
                "left": left,
                "right": right,
            }
            emit("arm_result", arm=arm, split=config.split, **metrics[arm])
    synchronize(config.device)
    after = state_digest(adapters)
    if before != after:
        raise ValueError("Adapter state changed during frozen answer inference.")
    result = {
        "metrics": metrics,
        "coverage": coverage,
        "selection": decide(metrics),
        "optimizer_updates": 0,
        "baseline_rerun": False,
        "representation": "Accepted cached extractive answers; original-passage fallback per unavailable side.",
        "expert_verified": False,
        "config": config.model_dump(),
    }
    for name in ("predictions", "result", "vectors", "timing"):
        context.outputs[name].parent.mkdir(parents=True, exist_ok=True)
    write_json(context.outputs["predictions"], predictions)
    write_json(context.outputs["result"], result)
    torch.save(cache, context.outputs["vectors"])
    write_json(
        context.outputs["timing"],
        {
            "total_seconds": time.monotonic() - started,
            "nonpadding_tokens": tokens,
            "optimizer_updates": 0,
            "adapter_state_before_sha256": before,
            "adapter_state_after_sha256": after,
            "peak_cuda_memory_bytes": torch.cuda.max_memory_allocated()
            if config.device == "cuda"
            else 0,
        },
    )
    emit("validation_selection", **result["selection"])
