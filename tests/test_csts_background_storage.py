"""Observe durable queue recovery and model progress during delayed cloud writes."""

import json
import threading
from types import SimpleNamespace

import pytest
from viper import execution
from viper.references import LocalFileRef, ResolvedRunRef
from viper.storage import ViperCloudDestination

from csts_pilot import background_storage as storage


def local_reference(root, digest="a"):
    """Create a schema-valid local identity without running a model."""
    return ResolvedRunRef(
        sha256=digest * 64,
        bytes=10,
        stored_at=LocalFileRef(
            workspace=root,
            store_id="1" * 32,
            commit="b" * 64,
            path="experiments/fixture/resolved.yaml",
        ),
    )


@pytest.fixture
def queue(monkeypatch, tmp_path):
    """Keep every test offline and reject any model-execution attempt."""
    monkeypatch.setattr(storage.subprocess, "Popen", lambda *args, **kwargs: None)
    monkeypatch.setattr(storage.time, "sleep", lambda _seconds: None)
    monkeypatch.setattr(
        execution,
        "run",
        lambda *args, **kwargs: pytest.fail("Publication invoked model execution."),
    )
    return tmp_path, ViperCloudDestination(owner="owner", workspace="study")


def test_enqueue_returns_with_pending_work_and_reuses_the_same_identity(queue):
    """Queue creation has no synchronous cloud-publication call."""
    root, destination = queue
    reference = local_reference(root)
    path = storage.queue_publication(root, reference, destination)
    assert json.loads(path.read_text())["status"] == "pending"
    assert storage.queue_publication(root, reference, destination) == path
    assert len(list(path.parent.glob("*.json"))) == 1


def test_worker_reconstructs_native_references_before_promotion(queue, monkeypatch):
    """Exercise the actual lazy native adapter with schema-valid queue bytes."""
    root, destination = queue
    reference = local_reference(root)
    calls = []

    def promote(workspace, source, target):
        calls.append((workspace, source, target))
        return source

    monkeypatch.setattr(execution, "promote_run_to_cloud", promote)
    result = storage._promote(
        root, reference.model_dump(mode="json"), destination.model_dump(mode="json")
    )
    assert result == reference
    assert calls == [(root, reference, destination)]


def test_spawn_failure_preserves_pending_work_for_a_later_worker(queue, monkeypatch):
    """A launcher error leaves computation free to proceed."""

    def fail(*_args, **_kwargs):
        raise OSError("fixture launcher failure")

    monkeypatch.setattr(storage.subprocess, "Popen", fail)
    root, destination = queue
    path = storage.queue_publication(root, local_reference(root), destination)
    assert json.loads(path.read_text())["status"] == "pending"


def test_cloud_failure_retries_and_only_success_sets_published(queue, monkeypatch):
    """Persist failures separately from the already verified local run."""
    root, destination = queue
    path = storage.queue_publication(root, local_reference(root), destination)
    calls = []

    def promote(*args):
        calls.append(args)
        if len(calls) < 3:
            raise TimeoutError("fixture transient cloud failure")
        return SimpleNamespace(model_dump=lambda **_kwargs: {"fixture": "published"})

    monkeypatch.setattr(storage, "_promote", promote)
    storage.drain_publications(root)
    record = json.loads(path.read_text())
    assert record["status"] == "published"
    assert record["attempts"] == 3
    assert "error_type" not in record
    assert record["promotion_seconds"] >= 0
    storage.drain_publications(root)
    assert len(calls) == 3


def test_interrupted_worker_resumes_from_durable_request(queue, monkeypatch):
    """A process exit after the attempt record leaves a reusable immutable source."""
    root, destination = queue
    path = storage.queue_publication(root, local_reference(root), destination)

    def crash(*_args):
        raise SystemExit("fixture process exit")

    monkeypatch.setattr(storage, "_promote", crash)
    with pytest.raises(SystemExit):
        storage.drain_publications(root)
    assert json.loads(path.read_text())["status"] == "uploading"
    monkeypatch.setattr(
        storage,
        "_promote",
        lambda *_args: SimpleNamespace(model_dump=lambda **_kwargs: {}),
    )
    storage.drain_publications(root)
    assert json.loads(path.read_text())["status"] == "published"


def test_exhausted_uploads_remain_visible_until_explicit_retry(queue, monkeypatch):
    """Keep a failed publication from masquerading as a cloud success."""
    root, destination = queue
    path = storage.queue_publication(root, local_reference(root), destination)

    def fail(*_args):
        raise TimeoutError("fixture permanent cloud failure")

    monkeypatch.setattr(storage, "_promote", fail)
    storage.drain_publications(root)
    record = json.loads(path.read_text())
    assert record["status"] == "failed"
    assert record["attempts"] == 3
    storage.drain_publications(root)
    assert json.loads(path.read_text())["attempts"] == 3
    monkeypatch.setattr(
        storage,
        "_promote",
        lambda *_args: SimpleNamespace(model_dump=lambda **_kwargs: {}),
    )
    storage.drain_publications(root, retry_failed=True)
    assert json.loads(path.read_text())["status"] == "published"


def test_final_report_refuses_an_unpublished_study(queue, monkeypatch):
    """A report receipt cannot bypass a failed study publication."""
    from csts_pilot import convergence_publication

    root, destination = queue
    reference = local_reference(root)
    storage.queue_publication(root, reference, destination)
    monkeypatch.setattr(
        convergence_publication, "drain_publications", lambda _root: None
    )
    with pytest.raises(RuntimeError, match="still pending"):
        convergence_publication.cloud_report_reference(root, reference)


def test_enqueue_progresses_while_a_cloud_write_is_blocked(queue, monkeypatch):
    """Use events to prove independence without assuming a fast network or clock."""
    root, destination = queue
    storage.queue_publication(root, local_reference(root), destination)
    entered, release = threading.Event(), threading.Event()

    def promote(*_args):
        entered.set()
        assert release.wait(timeout=5)
        return SimpleNamespace(model_dump=lambda **_kwargs: {})

    monkeypatch.setattr(storage, "_promote", promote)
    worker = threading.Thread(target=storage.drain_publications, args=(root,))
    worker.start()
    try:
        assert entered.wait(timeout=5)
        second = storage.queue_publication(
            root, local_reference(root, "c"), destination
        )
        assert json.loads(second.read_text())["status"] == "pending"
        assert worker.is_alive()
    finally:
        release.set()
        worker.join(timeout=5)
    assert worker.is_alive() is False
