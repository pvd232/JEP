"""Verify actual staged data and native artifacts, not declarative trial labels."""
from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any
from csts_pilot.full_data_prompt_protocol import PROMPTS, digest_file, digest_object


def verify_staged_fit_inputs(inputs: Any, contract: dict[str, Any]) -> None:
    """Reject changed bytes, counts, labels or overlapping groups before loading Qwen."""
    if set(contract) != {"training", "validation"}:
        raise ValueError("Fit contract must bind exactly training and validation, never test.")
    loaded = {}
    for split in ("training", "validation"):
        spec = contract[split]
        path = Path(inputs[split])
        if digest_file(path) != spec["sha256"]:
            raise ValueError(f"Actual staged {split} bytes differ from the protocol.")
        rows = json.loads(path.read_text())
        if len(rows) != spec["rows"] or len({r["group_id"] for r in rows}) != spec["groups"]:
            raise ValueError(f"Actual staged {split} count/groups differ.")
        if len({r["row_id"] for r in rows}) != len(rows):
            raise ValueError(f"Actual staged {split} contains duplicate row identities.")
        for row in rows:
            rating, target = float(row["rating"]), float(row["target"])
            if (not math.isfinite(rating) or not math.isfinite(target)
                    or not 1 <= rating <= 5 or not 0 <= target <= 1
                    or abs(target - (rating - 1) / 4) > 1e-12):
                raise ValueError(f"Actual staged {split} contains invalid rating/target labels.")
        loaded[split] = rows
    for field in ("row_id", "group_id"):
        if {r[field] for r in loaded["training"]} & {r[field] for r in loaded["validation"]}:
            raise ValueError(f"Staged training and validation overlap by {field}.")


def verify_fit_configuration(actual: dict[str, Any], expected: dict[str, Any],
                             arm: str, seed: int) -> None:
    """Compare persisted JSON values while preserving every scientific parameter."""
    actual_json = json.loads(json.dumps(actual, allow_nan=False))
    expected_json = json.loads(json.dumps(expected, allow_nan=False))
    for key, value in expected_json.items():
        if key in {"max_epochs", "start_epoch"}:
            continue
        if key not in actual_json or actual_json[key] != value:
            raise ValueError(f"Checkpoint/trace differs in {key} for requested {arm}/seed{seed}.")


def seal_native_selection(root: Path, protocol: dict[str, Any], source_commit: str,
                          arm: str, seed: int, record: dict[str, Any],
                          training_source_commit: str | None = None) -> dict[str, Any]:
    """Derive a final selection only from verified native trace, model and predictions.

    This reads training/validation artifacts only. It never reads test examples.
    The caller retains the authentic execution result/reference, not just a name.
    """
    from csts_pilot.convergence_run import artifact_path
    from csts_pilot.diagnostics import summarize
    from csts_pilot.full_data_prompt_native import fit_arguments
    from csts_pilot.baseline_models import FitConfig
    from jep_pilot.loaders import load_model

    if record.get("status") != "succeeded" or record.get("source_commit") != source_commit:
        raise ValueError("Native execution/source has not succeeded for this candidate.")
    if not isinstance(record.get("reference"), dict) or not record["reference"]:
        raise ValueError("Actual native execution reference missing.")
    trace_path = artifact_path(record, "train", "trace", "trace.json")
    model_path = artifact_path(record, "train", "model", "model.pt")
    predictions_path = artifact_path(record, "train", "validation_predictions", "predictions.json")
    trace = json.loads(trace_path.read_text())
    saved = load_model(model_path)
    predictions = json.loads(predictions_path.read_text())
    if trace.get("status") != "complete" or trace.get("stop_reason") != "validation_patience":
        raise ValueError("Trial is incomplete, budget-censored, or not patience-stopped.")
    history = trace.get("epochs", [])
    if not history or [r["epoch"] for r in history] != list(range(1, len(history) + 1)):
        raise ValueError("Invalid native epoch sequence.")
    if trace["actual_updates"] != 190 * len(history):
        raise ValueError("Native trace did not use the full training cohort each epoch.")
    expected_inputs = {k: protocol["splits"][k]["sha256"] for k in ("training", "validation")}
    if trace.get("training_inputs") != expected_inputs:
        raise ValueError("Native training input hashes do not match the protocol.")
    expected = FitConfig.model_validate(fit_arguments(protocol, arm, seed, len(history)-1)).model_dump()
    for actual in (trace["config"], saved["config"]):
        verify_fit_configuration(actual, expected, arm, seed)
    best = trace["selected"]
    rank = lambda r: r["validation"]["spearman"] if r["validation"]["spearman"] is not None else -math.inf
    first_best = max(history, key=rank)
    if best["epoch"] != first_best["epoch"] or saved["epoch"] != best["epoch"]:
        raise ValueError("Checkpoint is not the first strictly best validation epoch.")
    model_sha, pred_sha = digest_file(model_path), digest_file(predictions_path)
    if best["sha256"] != model_sha or best.get("validation_predictions_sha256") != pred_sha:
        raise ValueError("Selected native checkpoint/prediction generation mismatch.")
    validation_path = root / protocol["splits"]["validation"]["path"]
    if digest_file(validation_path) != expected_inputs["validation"]:
        raise ValueError("Validation input changed during selection sealing.")
    validation = json.loads(validation_path.read_text())
    identity = ("row_id", "pair_id", "group_id", "sentence1", "sentence2", "condition", "target", "rating")
    if len(predictions) != len(validation):
        raise ValueError("Selected validation prediction coverage is incomplete.")
    for original, prediction in zip(validation, predictions, strict=True):
        if any(original[k] != prediction[k] for k in identity):
            raise ValueError("Selected validation predictions refer to different examples.")
    recomputed = summarize(predictions)
    for key in ("spearman", "mse_0_1"):
        if recomputed[key] is None or abs(recomputed[key] - best["validation"][key]) > 1e-11:
            raise ValueError("Validation-selected metrics failed independent recomputation.")
    return {
        "trial_id": f"{arm}_seed{seed}", "arm": arm, "seed": seed,
        "training_source_commit": training_source_commit or source_commit,
        "execution_source_commit": source_commit, "protocol_sha256": digest_object(protocol),
        "prompt_sha256": digest_object(PROMPTS[arm]),
        "native_run_id": digest_object(record["reference"]), "native_run_reference": record["reference"],
        "trace_sha256": digest_file(trace_path), "model_sha256": model_sha,
        "validation_predictions_sha256": pred_sha,
        "training_sha256": expected_inputs["training"], "validation_sha256": expected_inputs["validation"],
        "selected_epoch": best["epoch"], "completed_epochs": len(history),
        "actual_updates": trace["actual_updates"], "stop_reason": trace["stop_reason"],
        "selection_metric": "validation_spearman", "test_used": False,
        "validation_metrics": recomputed,
        "initial_trainable_sha256": trace["initial_trainable_sha256"],
        "batch_order_sha256": [r["batch_order_sha256"] for r in history],
    }
