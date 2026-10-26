"""Preserve exact raw capture bytes and avoid duplicate native sealing."""

import hashlib
import json
from pathlib import Path
from types import SimpleNamespace

import pytest
from viper.references import LocalFileRef, ResolvedRunRef

from csts_pilot import proposition_archive as module
from csts_pilot.convergence import file_sha256
from jep_pilot.loaders import load_json


def capture(tmp_path, data=b"opaque closed capture archive"):
    identity = hashlib.sha256(data).hexdigest()
    source = tmp_path / f"capture-checkpoint-0001-{identity[:16]}.tar.gz"
    source.write_bytes(data)
    return source, identity, len(data)


def test_source_archive_rejects_changed_content_before_staging(tmp_path):
    source, identity, _ = capture(tmp_path)
    source.write_bytes(b"changed capture")
    with pytest.raises(ValueError, match="source archive hash differs"):
        module.checked_archive(source, tmp_path, identity)


def test_source_archive_rejects_symlink_to_an_outside_file(tmp_path):
    outside = tmp_path / "outside"
    outside.mkdir()
    source, identity, _ = capture(outside)
    allowed = tmp_path / "allowed"
    allowed.mkdir()
    link = allowed / source.name
    link.symlink_to(source)
    with pytest.raises(ValueError, match="installed content-addressed task archives"):
        module.checked_archive(link, allowed, identity)


def test_native_archive_stage_rejects_changed_input_and_emits_nothing(tmp_path):
    source, identity, size = capture(tmp_path)
    source.write_bytes(b"tampered")
    context = SimpleNamespace(
        config=module.ArchiveConfig(archive_sha256=identity, archive_bytes=size, original_source_path=str(source)),
        inputs={"archive": source},
        outputs={"archive": tmp_path / "out/archive.gz", "receipt": tmp_path / "receipt.json"},
    )
    with pytest.raises(ValueError, match="input bytes changed"):
        module.seal_archive(context)
    assert not context.outputs["archive"].exists()
    assert not context.outputs["receipt"].exists()


def test_native_archive_stage_preserves_opaque_bytes_without_extraction(tmp_path):
    source, identity, size = capture(tmp_path)
    context = SimpleNamespace(
        config=module.ArchiveConfig(archive_sha256=identity, archive_bytes=size, original_source_path=str(source)),
        inputs={"archive": source},
        outputs={"archive": tmp_path / "out/archive.gz", "receipt": tmp_path / "receipt.json"},
    )
    module.seal_archive(context)
    assert context.outputs["archive"].read_bytes() == source.read_bytes()
    assert file_sha256(context.outputs["archive"]) == identity
    receipt = load_json(context.outputs["receipt"])
    assert receipt["archive_sha256"] == identity
    assert receipt["archive_bytes"] == size
    assert receipt["archive_extracted"] is False
    assert receipt["optimizer_updates"] == 0


def test_staging_preserves_original_and_rejects_an_existing_conflicting_copy(tmp_path):
    root = tmp_path / "native"
    root.mkdir()
    source_dir = tmp_path / "source"
    source_dir.mkdir()
    source, identity, size = capture(source_dir)
    staged = module.stage_archive(root, source, identity, size)
    assert source.read_bytes() == staged.read_bytes()
    staged.write_bytes(b"conflicting staged bytes")
    with pytest.raises(ValueError, match="Preserve the existing staged archive"):
        module.stage_archive(root, source, identity, size)
    assert source.read_bytes() == b"opaque closed capture archive"


def test_verified_sealed_archive_requeues_without_invoking_execution(tmp_path, monkeypatch):
    source, identity, size = capture(tmp_path)
    native = tmp_path / "native"
    native.mkdir()
    local = ResolvedRunRef(
        sha256="a" * 64, bytes=10,
        stored_at=LocalFileRef(workspace=native, store_id="1" * 32, commit="b" * 64, path="experiments/fixture/resolved.yaml"),
    )
    record = {"path": str(native / "experiment/resolved.yaml"), "reference": local.model_dump(mode="json")}
    sealed = native / "sealed/archive.gz"
    sealed.parent.mkdir()
    sealed.write_bytes(source.read_bytes())
    directory = native / "answer_input_results/proposition_capture_archive"
    directory.mkdir(parents=True)
    index_path = directory / f"{identity}.json"
    index_path.write_text(json.dumps({
        "status": "sealed", "archive_sha256": identity, "archive_bytes": size,
        "run": record, "attempts": [],
    }))
    calls = []
    monkeypatch.setattr(module, "artifact_path", lambda *_args: sealed)
    monkeypatch.setattr(module, "queue_publication", lambda root, reference, destination: calls.append((root, reference, destination)) or native / "queue.json")
    monkeypatch.setattr(module.execution, "run", lambda *_args, **_kwargs: pytest.fail("A sealed archive was executed twice."))
    result = module.seal_one(native, source, identity, size, None, None, "destination")
    assert calls == [(native, local, "destination")]
    assert result["status"] == "sealed"
    assert Path(result["publication_queue"]) == native / "queue.json"
    assert load_json(index_path)["publication_queue"] == str(native / "queue.json")
