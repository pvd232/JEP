"""Check immutable snapshots, background progress, and failed first publication."""

import hashlib
import importlib.util
import sys
import threading
from pathlib import Path
from types import ModuleType, SimpleNamespace

import pytest


@pytest.fixture
def module(monkeypatch):
    native = ModuleType("viper.storage")
    native.ViperCloud = SimpleNamespace()
    native.ViperCloudDestination = SimpleNamespace(model_validate=lambda value: value)
    native.publish_resolved_files = lambda *args: None
    monkeypatch.setitem(sys.modules, "viper.storage", native)
    spec = importlib.util.spec_from_file_location(
        "checkpoint_fixture",
        Path(__file__).parents[1] / "csts_pilot/checkpoint_cloud.py",
    )
    loaded = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(loaded)
    return loaded


def fake_cloud(module, monkeypatch, gate=None, entered=None, block_first=False):
    objects = {}

    def publish(root, destination, files):
        if (
            gate is not None
            and (block_first or len(objects) >= 3)
            and any(k.endswith("resume.pt") for k in files)
        ):
            entered.set()
            assert gate.wait(3)
        refs = {}
        for name, path in files.items():
            data = Path(path).read_bytes()
            digest = hashlib.sha256(data).hexdigest()
            objects[digest] = data
            refs[name] = SimpleNamespace(
                sha256=digest,
                stored_at=name,
                model_dump=lambda mode, digest=digest: {"sha256": digest},
            )
        return refs

    def fetch(ref, destination):
        Path(destination).write_bytes(objects[ref.sha256])

    monkeypatch.setattr(module, "publish_resolved_files", publish)
    monkeypatch.setattr(
        module,
        "ViperCloud",
        SimpleNamespace(for_reference=lambda *a: SimpleNamespace(fetch_to_path=fetch)),
    )
    return objects


def test_subsequent_upload_allows_progress_and_uses_immutable_bytes(
    module, monkeypatch, tmp_path
):
    gate, entered = threading.Event(), threading.Event()
    objects = fake_cloud(module, monkeypatch, gate, entered)
    source = tmp_path / "active.pt"
    source.write_bytes(b"first weights")
    publisher = module.CheckpointCloud(tmp_path, {}, {})
    publisher.submit({"resume.pt": source}, {"epoch": 1})
    source.write_bytes(b"second weights")
    future = publisher.submit({"resume.pt": source}, {"epoch": 2})
    assert entered.wait(3)
    assert not future.done()
    source.write_bytes(b"third weights")
    gate.set()
    publisher.finish()
    assert b"second weights" in objects.values()
    assert b"third weights" not in objects.values()
    assert publisher.previous is not None


def test_first_failed_publication_stops_before_continuation(
    module, monkeypatch, tmp_path
):
    attempts = []

    def fail(*args):
        attempts.append(1)
        raise OSError("Cloud unavailable")

    monkeypatch.setattr(module, "publish_resolved_files", fail)
    monkeypatch.setattr(module.time, "sleep", lambda _: None)
    source = tmp_path / "active.pt"
    source.write_bytes(b"weights")
    publisher = module.CheckpointCloud(tmp_path, {}, {})
    with pytest.raises(OSError):
        publisher.submit({"resume.pt": source}, {"epoch": 1})
    with pytest.raises(OSError):
        publisher.finish()
    assert len(attempts) == 3
    assert publisher.previous is None


def test_first_upload_can_run_without_blocking_and_finish_waits(
    module, monkeypatch, tmp_path
):
    gate, entered = threading.Event(), threading.Event()
    objects = fake_cloud(module, monkeypatch, gate, entered, block_first=True)
    source = tmp_path / "active.pt"
    source.write_bytes(b"sealed initial state")
    publisher = module.CheckpointCloud(
        tmp_path, {}, {}, wait_for_first=False, prefix="native/checkpoints"
    )
    try:
        pending = publisher.submit({"resume.pt": source}, {"epoch": 0})
        assert entered.wait(3)
        assert not pending.done()
        source.write_bytes(b"later state")
    finally:
        gate.set()
        publisher.finish()
    assert b"sealed initial state" in objects.values()
    assert b"later state" not in objects.values()
    assert publisher.previous is not None
