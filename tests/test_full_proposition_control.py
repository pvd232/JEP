"""Check concurrent control selection and writing progress without model forwards."""

import json
from pathlib import Path

import pytest

from csts_pilot import convergence_run
from csts_pilot import full_proposition_control as worker
from csts_pilot.convergence_run import artifact_source
from csts_pilot.proposition_evidence_run import validate_settings


def test_control_selects_matching_epoch_even_after_an_extra_completed_epoch(
    tmp_path, monkeypatch
):
    """A rejected writing epoch must also be excluded from the control's parent."""
    trace = tmp_path / "trace.json"
    trace.write_text(json.dumps({"completed_epoch": 5, "actual_updates": 950}))
    monkeypatch.setattr(worker, "artifact_path", lambda *args: trace)
    records = [{"epoch": i} for i in range(1, 7)]
    assert (
        worker.matched_control_record(records, {"epoch": 5, "step": 950}) == records[4]
    )
    with pytest.raises(ValueError, match="updates"):
        worker.matched_control_record(records, {"epoch": 5, "step": 949})
    with pytest.raises(ValueError, match="not completed"):
        worker.matched_control_record(records[:4], {"epoch": 5, "step": 950})


def test_concurrent_control_waits_for_observed_writing_progress(tmp_path):
    """Waiting for writing progress limits speculative control training to one extra epoch."""
    directory = tmp_path / "results"
    directory.mkdir()
    summary = {
        "runs": [],
        "in_flight": {"name": "evidence_pretrain", "experiment_id": "writing"},
    }
    (directory / "summary.json").write_text(json.dumps(summary))
    assert worker.writing_frontier(tmp_path, directory) == 1
    trace = (
        tmp_path
        / "experiments/writing/runs/evidence_pretrain/run/artifacts/train/trace/trace.json"
    )
    trace.parent.mkdir(parents=True)
    trace.write_text(json.dumps({"completed_epoch": 4}))
    assert worker.writing_frontier(tmp_path, directory) == 5


def test_full_comparison_requires_writing_references_and_patience_one():
    """The uncapped protocol accepts the writing criterion and rejects missing references."""
    settings = json.loads(
        (
            Path(__file__).resolve().parents[1]
            / "configs/csts-qwen-jep-v1-four-epoch.json"
        ).read_text()
    )
    settings.update(
        proposition_until_patience=True, proposition_validation={"sha256": "a" * 64}
    )
    settings["phases"]["pretrain"]["max_epochs"] = 1
    validate_settings(settings)
    settings["proposition_validation"] = {}
    with pytest.raises(ValueError, match="held-out"):
        validate_settings(settings)


def test_validation_selected_parent_preserves_its_data_role(monkeypatch):
    """A writing checkpoint selected with held-out references keeps validation restriction downstream."""
    reference = {
        "sha256": "a" * 64,
        "bytes": 1,
        "kind": "resolved_run",
        "stored_at": {
            "kind": "local",
            "workspace": "/tmp/work",
            "store": ".viper/store",
            "store_id": "c" * 32,
            "commit": "b" * 64,
            "path": "run/resolved.yaml",
        },
    }
    monkeypatch.setattr(
        convergence_run, "run_artifact", lambda *args, **kwargs: kwargs["data_role"]
    )
    assert (
        artifact_source(
            {"reference": reference, "data_role": "validation"}, "train", "model"
        )
        == "validation"
    )
    assert artifact_source({"reference": reference}, "train", "model") == "training"
