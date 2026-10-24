"""Reject altered report exports and preserve the completed benchmark references."""

import copy
import hashlib
import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from csts_pilot import baseline_collect as collector
from csts_pilot import baseline_report as report


def digest(path):
    """Identify one fixture file by exact bytes."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path, value):
    """Serialize fixture records with ordinary JSON types."""
    path.write_text(json.dumps(value))


def seal(directory):
    """Build a transfer manifest after the synthetic native receipt is written."""
    write(
        directory / "files.json",
        {
            path.name: {"sha256": digest(path), "bytes": path.stat().st_size}
            for path in directory.glob("*.json")
            if path.name != "files.json"
        },
    )


@pytest.fixture
def collected(tmp_path):
    """Use existing prediction bytes as report fixtures, with zero model inference."""
    root = Path(__file__).parents[1]
    settings = report.read_json(root / "configs/csts-tranche-2.json")
    rows = report.read_json(root / settings["references"]["flan"]["path"])
    phase = tmp_path / "phase"
    phase.mkdir()
    kinds = ("mean", "cosine", "ridge", "projection")
    for kind in kinds:
        predictions = copy.deepcopy(rows)
        for row in predictions:
            row["prediction"] = 0.5 if kind == "mean" else row["prediction"]
        write(phase / f"{kind}_predictions.json", predictions)
    write(
        phase / "projection_trace.json",
        {
            "config": {"start_epoch": 0},
            "epochs": [{"fit_seconds": 1.0, "validation_seconds": 0.2}],
            "selected": {"epoch": 1},
            "stop_reason": "validation_patience",
            "actual_updates": 3,
        },
    )
    write(
        phase / "selection.json",
        {
            "status": "checkpoints_frozen",
            "provisional_winner": "cosine",
            "candidates": {
                kind: {"run": {"reference": {"sha256": "a" * 64}}} for kind in kinds
            },
        },
    )
    summary = {
        "status": "complete",
        "phase": "frozen",
        "source_commit": "a" * 40,
        "settings": settings,
        "gpu_stage_seconds": 1.0,
        "runs": [],
        "test": [{"candidate": kind} for kind in kinds],
        "selection_sha256": digest(phase / "selection.json"),
        "in_flight": None,
    }
    write(phase / "summary.json", summary)
    receipt = {
        "status": "verified",
        "summary_sha256": digest(phase / "summary.json"),
        "exports": {
            f"{kind}_predictions.json": {
                "sha256": digest(phase / f"{kind}_predictions.json")
            }
            for kind in kinds
        },
    }
    write(phase / "native_verification.json", receipt)
    seal(phase)
    return root, phase, tmp_path / "output"


def test_report_reuses_reference_predictions_and_keeps_mean_rank_undefined(collected):
    """Independent analysis preserves references and returns zero identical-score contrasts."""
    root, phase, output = collected
    result = report.build_report(root, [phase], output, draws=8)
    assert result["scores"]["mean"]["spearman"] is None
    assert result["scores"]["projection"]["n"] == 2620
    assert result["paired_intervals"]["groups"] == 1241
    for contrast in result["paired_intervals"]["contrasts"].values():
        assert contrast["spearman"]["difference"] == 0
        assert contrast["spearman"]["ci95"] == [0.0, 0.0]
    assert (output / "csts_tranche2_report.md").is_file()


def test_report_rejects_changed_prediction_bytes(collected):
    """A transferred prediction file must still match its recorded native export."""
    _, phase, _ = collected
    path = phase / "projection_predictions.json"
    path.write_text(path.read_text() + " ")
    with pytest.raises(ValueError, match="file bytes differ"):
        report.verify_files(phase)


def test_report_rejects_manifest_omission_of_prediction_file(collected):
    """Require each prediction's native export check after a manifest omission."""
    _, phase, _ = collected
    manifest = report.read_json(phase / "files.json")
    del manifest["projection_predictions.json"]
    write(phase / "files.json", manifest)
    with pytest.raises(ValueError, match="producer identity|omits"):
        report.verify_files(phase)


def test_report_rejects_changed_pair_or_condition_identity():
    """Reject changed passage comparisons despite equal numeric labels."""
    root = Path(__file__).parents[1]
    rows = report.read_json(
        root / "training_outputs/csts_continuation_mse_predictions.json"
    )
    changed = copy.deepcopy(rows)
    changed[0]["condition"] = "different condition"
    with pytest.raises(ValueError, match="comparisons differ"):
        report.same_comparisons({"a": rows, "b": changed})


def test_collection_blocks_pending_cloud_receipts(tmp_path, monkeypatch):
    """Final collection waits for publication while leaving model execution untouched."""
    write(tmp_path / "selection.json", {})
    write(tmp_path / "job.json", {"status": "pending", "request": {"source": {}}})
    write(
        tmp_path / "summary.json",
        {
            "status": "complete",
            "in_flight": None,
            "selection_sha256": digest(tmp_path / "selection.json"),
            "runs": [
                {
                    "name": "train_projection",
                    "status": "succeeded",
                    "reference": {},
                    "publication_queue": str(tmp_path / "job.json"),
                }
            ],
        },
    )
    monkeypatch.setattr(
        collector, "read_source", lambda _root: SimpleNamespace(repository="fixture")
    )
    monkeypatch.setattr(
        collector.api,
        "verify_run",
        lambda *_args: pytest.fail("Verification preceded publication readiness."),
    )
    with pytest.raises(ValueError, match="publication remains pending"):
        collector.collect_phase(tmp_path, tmp_path)


def test_collection_exports_the_verified_native_prediction_bytes(tmp_path, monkeypatch):
    """Collection replaces a stale export with bytes from its verified native producer."""
    path = tmp_path / "native" / "resolved.yaml"
    path.parent.mkdir()
    path.write_text("fixture")
    for name in ("predictions", "timing"):
        artifact = path.parent / "artifacts" / "test" / name / f"{name}.json"
        artifact.parent.mkdir(parents=True)
        write(artifact, {"native": name})
    directory = tmp_path / "collected"
    directory.mkdir()
    write(directory / "projection_predictions.json", {"stale": True})
    write(directory / "selection.json", {})
    reference = {"sha256": "a" * 64}
    write(
        directory / "job.json",
        {
            "status": "published",
            "request": {"source": reference},
            "reference": {"sha256": "b" * 64},
        },
    )
    write(
        directory / "summary.json",
        {
            "status": "complete",
            "source_commit": "c" * 40,
            "in_flight": None,
            "selection_sha256": digest(directory / "selection.json"),
            "runs": [
                {
                    "name": "test_projection",
                    "status": "succeeded",
                    "reference": reference,
                    "path": str(path),
                    "publication_queue": str(directory / "job.json"),
                }
            ],
        },
    )
    monkeypatch.setattr(
        collector, "read_source", lambda _root: SimpleNamespace(repository="fixture")
    )
    monkeypatch.setattr(
        collector.api, "verify_run", lambda *_args: SimpleNamespace(measurement_count=2)
    )
    receipt = collector.collect_phase(tmp_path, directory)
    assert receipt["measurements_verified"] == 2
    assert report.read_json(directory / "projection_predictions.json") == {
        "native": "predictions"
    }
    assert receipt["exports"]["projection_predictions.json"]["sha256"] == digest(
        directory / "projection_predictions.json"
    )
