"""Check report arithmetic and failure guards with small synthetic predictions."""

import hashlib
import json

import pytest

from csts_pilot import convergence_report


def report_fixture(tmp_path):
    """Write an explicitly synthetic completed result for CPU report checks."""
    inputs = tmp_path / "synthetic-results"
    inputs.mkdir()
    rows = [
        {
            "row_id": f"r{i}",
            "group_id": f"g{i // 2}",
            "pair_id": f"p{i // 2}",
            "condition": f"q{i % 2}",
            "rating": 1 + 4 * (i % 2),
            "target": float(i % 2),
            "prediction": 0.25 + 0.5 * (i % 2),
            "calibrated_prediction": float(i % 2),
        }
        for i in range(12)
    ]
    candidates = {}
    for arm in ("mse", "pearson"):
        for window in ("prefix", "full"):
            name = f"{arm}_{window}"
            candidates[name] = {
                "epoch": 1,
                "sha256": arm,
                "calibration": {"a": 2.0, "c": -0.5},
            }
            (inputs / f"{name}_predictions.json").write_text(json.dumps(rows))
        trace = {
            "actual_updates": 9,
            "elapsed_seconds": 6,
            "nonpadding_input_tokens_per_epoch": 72,
            "peak_cuda_memory_bytes": 0,
            "config": {"seed": 7, "max_epochs": 3, "prefix_epochs": 1},
            "selected": {"full": {"epoch": 1}},
            "epochs": [
                {
                    "epoch": epoch,
                    "step": 3 * epoch,
                    "fit_seconds": 1.0,
                    "validation_seconds": 0.5,
                    "training_objective": 0.2,
                    "training_mse_0_1": 0.2,
                    "validation": {"mse_0_1": 0.2, "spearman": 0.5},
                }
                for epoch in (1, 2, 3)
            ],
        }
        (inputs / f"{arm}_trace.json").write_text(json.dumps(trace))
    selection = {"candidates": candidates, "provisional_loss": "mse"}
    raw = json.dumps(selection).encode()
    (inputs / "selection.json").write_bytes(raw)
    summary = {
        "status": "complete",
        "source_commit": "synthetic-test-fixture",
        "evaluation_source_commit": "synthetic-evaluation-repair",
        "selection_sha256": hashlib.sha256(raw).hexdigest(),
        "gpu_stage_seconds": 0,
        "runs": [],
        "settings": {
            "gpu_budget_seconds": 1800,
            "splits": {"test": {"rows": 12, "groups": 6}},
            "training": {"seed": 7, "max_epochs": 3},
            "bootstrap_draws": 12,
            "bootstrap_seed": 61021,
        },
    }
    (inputs / "summary.json").write_text(json.dumps(summary))
    return inputs


def test_cpu_report_recomputes_scale_intervals_and_compute(tmp_path, monkeypatch):
    inputs = report_fixture(tmp_path)
    output = tmp_path / "report"
    monkeypatch.setattr(
        convergence_report,
        "render_curves",
        lambda _traces, path: path.write_bytes(b"plot-fixture"),
    )
    report = convergence_report.build_report(inputs, output)
    raw = report["candidates"]["mse_full"]["raw"]
    assert raw["mse_0_1"] == 0.0625
    assert raw["mse_1_5"] == 1
    assert report["paired_intervals"]["draws"] == 12
    assert report["compute"]["mse"]["nonpadding_input_tokens"] == 216
    assert report["source_commit"] == "synthetic-test-fixture"
    assert report["evaluation_source_commit"] == "synthetic-evaluation-repair"
    markdown = (output / "csts_tranche1_report.md").read_text()
    assert "12 shared bootstrap samples" in markdown
    assert "MSE: 3 epochs, PEARSON: 3 epochs" in markdown
    assert len((output / "csts_tranche1_epochs.csv").read_text().splitlines()) == 7


def test_report_rejects_a_changed_frozen_selection(tmp_path):
    inputs = report_fixture(tmp_path)
    (inputs / "selection.json").write_text("{}")
    with pytest.raises(ValueError, match="pre-test identity"):
        convergence_report.build_report(inputs, tmp_path / "report")


def test_report_rejects_calibration_fitted_after_test_scores(tmp_path):
    inputs = report_fixture(tmp_path)
    path = inputs / "mse_full_predictions.json"
    rows = json.loads(path.read_text())
    rows[0]["calibrated_prediction"] = 0.1
    path.write_text(json.dumps(rows))
    with pytest.raises(ValueError, match="frozen validation fit"):
        convergence_report.build_report(inputs, tmp_path / "report")


def test_report_describes_patience_as_validation_stopping(tmp_path, monkeypatch):
    """Keep an early-stopped report distinct from a stationarity claim."""
    inputs = report_fixture(tmp_path)
    path = inputs / "mse_trace.json"
    trace = json.loads(path.read_text())
    trace["stop_reason"] = "validation_patience"
    trace["config"]["patience"] = 5
    path.write_text(json.dumps(trace))
    monkeypatch.setattr(
        convergence_report,
        "render_curves",
        lambda _traces, path: path.write_bytes(b"plot-fixture"),
    )
    output = tmp_path / "report"
    convergence_report.build_report(inputs, output)
    markdown = (output / "csts_tranche1_report.md").read_text()
    assert "training-loss stationarity remains unresolved" in markdown
