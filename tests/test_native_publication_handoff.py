"""Keep the next computation independent of outstanding Cloud publication."""

import importlib.util
import json
import sys
import threading
from pathlib import Path
from types import SimpleNamespace

import pytest

spec = importlib.util.spec_from_file_location(
    "reviewed_native_run",
    Path(__file__).parents[1] / "csts_pilot/native_comparison_run.py",
)
native_run = importlib.util.module_from_spec(spec)
spec.loader.exec_module(native_run)


def test_completed_handoff_returns_while_publication_is_outstanding(
    tmp_path, monkeypatch
):
    started, release = threading.Event(), threading.Event()
    workers = []

    def publisher(args, **kwargs):
        assert args[:3] == [sys.executable, "-m", "csts_pilot.native_comparison_run"]
        assert "--publish-completed" in args
        worker = threading.Thread(target=lambda: (started.set(), release.wait(3)))
        worker.start()
        workers.append(worker)
        return SimpleNamespace(pid=1234)

    monkeypatch.setattr(native_run.subprocess, "Popen", publisher)
    try:
        native_run.queue_completed_publication(
            tmp_path, tmp_path, {"status": "succeeded"}
        )
        assert started.wait(1)
        assert workers[0].is_alive()
        assert (
            json.loads((tmp_path / "summary.json").read_text())["cloud_status"]
            == "pending"
        )
    finally:
        release.set()
        for worker in workers:
            worker.join(2)


def test_completion_receipt_waits_for_successful_publication(tmp_path, monkeypatch):
    (tmp_path / "configs").mkdir()
    destination = {
        "kind": "viper_cloud",
        "owner": "pvd232",
        "workspace": "jep_csts_joint_20261021",
    }
    (tmp_path / "configs/csts-native-comparison.json").write_text(
        json.dumps({"publication_destination": destination})
    )
    queue = tmp_path / "queue.json"
    queue.write_text(json.dumps({"status": "pending"}))
    summary = {
        "status": "succeeded",
        "seed": 8,
        "selected": {},
        "runs": [{"name": "fit", "publication_queue": str(queue)}],
        "terminal": {"name": "fit"},
    }
    (tmp_path / "summary.json").write_text(json.dumps(summary))
    monkeypatch.setattr(native_run, "drain_publications", lambda *a, **k: None)
    with pytest.raises(RuntimeError):
        native_run.publish_completed(tmp_path, tmp_path)
    assert not (tmp_path / "final-publication.json").exists()
    queue.write_text(
        json.dumps({"status": "published", "reference": {"sha256": "a" * 64}})
    )
    monkeypatch.setattr(
        native_run,
        "publish_resolved_files",
        lambda *a: {
            "receipt": SimpleNamespace(model_dump=lambda **k: {"sha256": "b" * 64})
        },
    )
    native_run.publish_completed(tmp_path, tmp_path)
    completed = json.loads((tmp_path / "summary.json").read_text())
    assert completed["cloud_status"] == "published"
    assert completed["terminal"]["cloud_reference"] == {"sha256": "a" * 64}
    assert (
        json.loads((tmp_path / "final-publication.json").read_text())["status"]
        == "published"
    )
