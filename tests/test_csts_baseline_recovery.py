"""Observe prediction reuse across CPU verification and source-code recovery."""

import json
from pathlib import Path
from types import SimpleNamespace

import pytest
import torch

from csts_pilot import baseline_run as runner
from csts_pilot import baseline_stages as stages
from csts_pilot.baseline_models import EncoderConfig, FitConfig, ScoreConfig
from csts_pilot.convergence import file_sha256
from jep_pilot.loaders import load_json


def test_cpu_evaluation_preserves_snapshot_bytes_and_rejects_tampering(
    tmp_path, monkeypatch
):
    """CPU metric recovery consumes saved predictions and performs zero backbone loads."""
    fit = FitConfig(
        kind="mean",
        device="cpu",
        model_id="fixture",
        revision="a" * 40,
        embedding_dimension=2,
    )
    model, test, selection, predictions, timing, holdout = [
        tmp_path / name
        for name in (
            "model.pt",
            "test.json",
            "selection.json",
            "predictions.json",
            "timing.json",
            "holdout.json",
        )
    ]
    rows = [
        {
            "row_id": f"r{i}",
            "group_id": f"g{i}",
            "pair_id": f"p{i}",
            "condition": "animal",
            "sentence1": "a cat",
            "sentence2": "a dog",
            "rating": 1 + 4 * i,
            "target": float(i),
        }
        for i in range(2)
    ]
    test.write_text(json.dumps(rows))
    predictions.write_text(json.dumps([dict(row, prediction=0.5) for row in rows]))
    torch.save({"kind": "mean", "config": fit.model_dump()}, model)
    selection.write_text(
        json.dumps(
            {
                "status": "checkpoints_frozen",
                "candidates": {"mean": {"sha256": file_sha256(model)}},
            }
        )
    )
    timing.write_text(
        json.dumps(
            {
                "model_sha256": file_sha256(model),
                "test_sha256": file_sha256(test),
                "predictions_sha256": file_sha256(predictions),
            }
        )
    )
    holdout.write_text(json.dumps([0, 1]))
    config = ScoreConfig(
        **{key: getattr(fit, key) for key in EncoderConfig.model_fields},
        kind="mean",
        model_sha256=file_sha256(model),
        selection_sha256=file_sha256(selection),
        test_sha256=file_sha256(test),
    )
    context = SimpleNamespace(
        config=config,
        inputs={
            "model": model,
            "selection": selection,
            "test": test,
            "holdout": holdout,
            "snapshot_predictions": predictions,
            "snapshot_timing": timing,
        },
        outputs={
            "predictions": tmp_path / "verified.json",
            "timing": tmp_path / "verified-timing.json",
        },
    )
    monkeypatch.setattr(
        stages,
        "load_backbone",
        lambda *_args, **_kwargs: pytest.fail("CPU verification loaded a backbone."),
    )
    stages.evaluate_baseline(context)
    assert context.outputs["predictions"].read_bytes() == predictions.read_bytes()
    predictions.write_text(predictions.read_text() + " ")
    with pytest.raises(ValueError, match="saved predictions refer"):
        stages.evaluate_baseline(context)


def test_source_recovery_reuses_prediction_producer_and_retries_cpu_metrics():
    """A failed CPU EVAL retries while its successful model measurement is reused."""
    settings = load_json(Path(__file__).parents[1] / "configs/csts-tranche-2.json")
    predicted = {
        "name": "predict_lora",
        "status": "succeeded",
        "reference": {"sha256": "a" * 64},
    }
    parent = {
        "status": "failed",
        "in_flight": None,
        "phase": "lora",
        "settings": settings,
        "runs": [predicted, {"name": "test_lora", "status": "failed"}],
    }
    runner.validate_recovery_parent(parent, settings, "lora")
    assert runner.reusable_parent_stage(parent, "predict_lora", True) is predicted
    assert runner.reusable_parent_stage(parent, "test_lora", True) is None


def test_recovery_blocks_uncertain_invocations_and_failed_model_measurements():
    """Preserve uncertain or failed model work for explicit native-artifact inspection."""
    settings = load_json(Path(__file__).parents[1] / "configs/csts-tranche-2.json")
    parent = {
        "status": "failed",
        "in_flight": {"stage": "predict_lora"},
        "phase": "lora",
        "settings": settings,
        "runs": [{"name": "predict_lora", "status": "failed"}],
    }
    with pytest.raises(ValueError, match="Reconcile"):
        runner.validate_recovery_parent(parent, settings, "lora")
    parent["in_flight"] = None
    with pytest.raises(ValueError, match="failed measurement artifact"):
        runner.reusable_parent_stage(parent, "predict_lora", True)


def test_prediction_capture_and_cpu_evaluation_use_distinct_native_stages():
    """GPU prediction capture feeds immutable artifacts into a CPU EVAL declaration."""
    settings = load_json(Path(__file__).parents[1] / "configs/csts-tranche-2.json")
    ref = {
        "sha256": "a" * 64,
        "bytes": 1,
        "stored_at": {
            "kind": "gcs",
            "bucket": "fixture",
            "owner": "owner",
            "workspace": "study",
            "revision": "b" * 64,
            "path": "experiments/fixture/resolved.yaml",
        },
    }
    record = {"reference": ref}
    candidate = {"sha256": "c" * 64, "run": record}
    captured = runner.prediction_stage(
        "lora", candidate, record, None, settings, "selection.json", "d" * 64
    )
    evaluated = runner.evaluation_stage(
        "lora", candidate, record, record, settings, "selection.json", "d" * 64
    )
    assert captured.spec.kind == "build"
    assert captured.spec.config.device == "cuda"
    assert evaluated.spec.kind == "eval"
    assert evaluated.spec.config.device == "cpu"
    assert evaluated.spec.inputs["snapshot_predictions"].artifact.stage_id == "predict"
