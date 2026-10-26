"""Seal captured proposition requests on CPU and queue native cloud promotion."""

import argparse
import fcntl
import json
import os
import re
import shutil
import tempfile
import time
import uuid
from pathlib import Path
from typing import Any

from pydantic import Field
from viper import execution
from viper.authoring import experiment, input, plan, replicate, stage, variant
from viper.config import BuildConfig
from viper.outputs import StageOutputs, output
from viper.references import GitFileRef
from viper.repository import read_source
from viper.runtime import CPUComputeSpec, LocalEnvSpec, observe_python_env
from viper.stages import StageContext, build
from viper.storage import LocalStorageDestination, ViperCloudDestination, load_storage_settings

from csts_pilot.background_storage import queue_publication
from csts_pilot.convergence import file_sha256, write_json
from csts_pilot.convergence_run import artifact_path
from jep_pilot.loaders import load_bytes, load_json

NATIVE_ROOT = Path("/home/machina/jep-csts-proposition-lora-20261026")
SOURCE_ROOT = Path(
    "/home/machina/jep-csts-answer-input-20261026/answer_input_results/"
    "proposition_capture_full/full_v2_6895d17242704944"
)
ARCHIVE_NAME = re.compile(r"capture-checkpoint-[0-9]{4,}-([0-9a-f]{16})\.tar\.gz")


class ArchiveConfig(BuildConfig):
    """Bind a closed byte archive to its exact installed identity and origin."""

    archive_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    archive_bytes: int = Field(ge=1)
    original_source_path: str


def save_receipt(path: Path, value: dict[str, Any]) -> None:
    """Commit the controller receipt atomically before advancing to a new archive."""
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", dir=path.parent, suffix=".tmp", delete=False) as stream:
            temporary = Path(stream.name)
            json.dump(value, stream, indent=2, allow_nan=False)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        temporary.replace(path)
        descriptor = os.open(path.parent, os.O_RDONLY)
        try:
            os.fsync(descriptor)
        finally:
            os.close(descriptor)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def checked_archive(path: Path, source_directory: Path, expected_sha256: str | None = None) -> tuple[str, int]:
    """Check a regular closed archive and its content-addressed name in bounded memory."""
    source_directory = source_directory.resolve(strict=True)
    resolved = path.resolve(strict=True)
    match = ARCHIVE_NAME.fullmatch(path.name)
    if path.is_symlink() or not resolved.is_relative_to(source_directory) or not resolved.is_file() or match is None:
        raise ValueError("Only installed content-addressed task archives may be sealed.")
    identity = file_sha256(resolved)
    if not identity.startswith(match.group(1)) or (expected_sha256 is not None and identity != expected_sha256):
        raise ValueError("The installed source archive hash differs from its declared identity.")
    size = resolved.stat().st_size
    if size < 1:
        raise ValueError("The installed source archive is empty.")
    return identity, size


def stage_archive(root: Path, source: Path, identity: str, size: int) -> Path:
    """Copy verified bytes into the native workspace without opening the archive."""
    directory = root / "csts_data/proposition_capture_archives"
    directory.mkdir(parents=True, exist_ok=True)
    if directory.resolve(strict=True) != directory or not directory.is_relative_to(root):
        raise ValueError("Native archive staging must remain inside the physical task workspace.")
    destination = directory / f"{identity}.tar.gz"
    if destination.exists():
        if destination.is_symlink() or destination.stat().st_size != size or file_sha256(destination) != identity:
            raise ValueError("Preserve the existing staged archive; its bytes differ.")
    else:
        descriptor, name = tempfile.mkstemp(prefix=f"{identity}.", suffix=".tmp", dir=directory)
        os.close(descriptor)
        temporary = Path(name)
        try:
            shutil.copyfile(source, temporary)
            if temporary.stat().st_size != size or file_sha256(temporary) != identity:
                raise ValueError("The closed source archive changed during the native staging copy.")
            with temporary.open("rb") as stream:
                os.fsync(stream.fileno())
            temporary.replace(destination)
        finally:
            temporary.unlink(missing_ok=True)
    if source.stat().st_size != size or file_sha256(source) != identity:
        raise ValueError("The original closed source archive changed during staging.")
    return destination


@build(config=ArchiveConfig)
def seal_archive(context: StageContext[ArchiveConfig]) -> None:
    """Publish opaque capture bytes and their receipt as sealed native artifacts."""
    config = context.config
    source = context.inputs["archive"]
    if source.stat().st_size != config.archive_bytes or file_sha256(source) != config.archive_sha256:
        raise ValueError("The native archive input bytes changed before sealing.")
    target = context.outputs["archive"]
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, target)
    if target.stat().st_size != config.archive_bytes or file_sha256(target) != config.archive_sha256:
        raise ValueError("The sealed archive output differs from its checked input bytes.")
    write_json(context.outputs["receipt"], {
        "archive_sha256": config.archive_sha256,
        "archive_bytes": config.archive_bytes,
        "original_source_path": config.original_source_path,
        "archive_extracted": False,
        "optimizer_updates": 0,
        "compute": "cpu",
    })


def verify_native_archive(record: dict[str, Any], identity: str, size: int, origin: str) -> None:
    """Check both native artifacts before first publication or later requeueing."""
    if record.get("status") != "succeeded":
        raise ValueError("Archive publication requires a successfully sealed native run.")
    archive = artifact_path(record, "archive", "archive", "archive.gz")
    receipt_path = artifact_path(record, "archive", "receipt", "receipt.json")
    if (
        not archive.is_file() or archive.stat().st_size != size
        or file_sha256(archive) != identity or not receipt_path.is_file()
    ):
        raise ValueError("The completed native archive artifacts differ from the capture identity.")
    expected = {
        "archive_sha256": identity, "archive_bytes": size,
        "original_source_path": origin, "archive_extracted": False,
        "optimizer_updates": 0, "compute": "cpu",
    }
    if load_json(receipt_path) != expected:
        raise ValueError("The completed native archive receipt differs from the capture identity.")


def seal_one(
    root: Path, source_path: Path, identity: str, size: int,
    source: Any, environment: Any, destination: Any, retry_failed: bool = False,
) -> dict[str, Any]:
    """Seal a new content identity once; otherwise verify and requeue its native run."""
    directory = root / "answer_input_results/proposition_capture_archive"
    directory.mkdir(parents=True, exist_ok=True)
    receipt_path = directory / f"{identity}.json"
    record = load_json(receipt_path) if receipt_path.exists() else None
    if record is not None:
        if record.get("archive_sha256") != identity or record.get("archive_bytes") != size:
            raise ValueError("The archive controller receipt changed content identity.")
        if record.get("status") == "sealed":
            verify_native_archive(record["run"], identity, size, record["original_source_path"])
            from viper.references import ResolvedRunRef

            reference = ResolvedRunRef.model_validate(record["run"]["reference"])
            record["publication_queue"] = str(queue_publication(root, reference, destination))
            save_receipt(receipt_path, record)
            return record
        if not retry_failed:
            raise ValueError("Preserve the interrupted archive receipt; --retry-failed is required for a new CPU sealing attempt.")
        previous_attempts = record.get("attempts", [])
        if not previous_attempts:
            raise ValueError("The interrupted archive receipt has no recoverable attempt identity.")
        previous_path = directory / f"{identity}-attempt-{previous_attempts[-1]['attempt']}.json"
        if previous_path.exists() and load_json(previous_path) != record:
            raise ValueError("Preserve the previous failed archive attempt receipt; its contents differ.")
        if not previous_path.exists():
            save_receipt(previous_path, record)
    staged = stage_archive(root, source_path, identity, size)
    attempts = [*record.get("attempts", [])] if record is not None else []
    attempt = uuid.uuid4().hex[:8]
    record = {
        "status": "running", "archive_sha256": identity, "archive_bytes": size,
        "original_source_path": str(source_path), "source_commit": source.commit,
        "attempts": [*attempts, {"attempt": attempt, "started_unix": time.time()}],
    }
    save_receipt(receipt_path, record)
    configured = stage(
        seal_archive, stage_id="archive", config=ArchiveConfig(
            archive_sha256=identity, archive_bytes=size, original_source_path=str(source_path),
        ),
        inputs=(input("archive", path=staged.relative_to(root).as_posix(), data_role="training"),),
        outputs=StageOutputs(
            archive=output(path="archive.gz", loader=load_bytes, data_role="training"),
            receipt=output(path="receipt.json", loader=load_json, data_role="training"),
        ), reuse="never",
    )
    trial = experiment(
        experiment_id=f"csts_proposition_archive_{identity[:16]}_{attempt}",
        variants=(variant("capture_archive", stages=(configured,), estimator=configured.outputs["receipt"]),),
        replicates=(replicate(seed=7),),
    )
    record["experiment_id"] = trial.experiment_id
    save_receipt(receipt_path, record)
    env = LocalEnvSpec(
        compute=CPUComputeSpec(),
        lockfile=GitFileRef(repository=source.repository, commit=source.commit, path="tranche2_requirements.txt"),
        python_env=environment,
    )
    try:
        result = execution.run(
            plan(experiment=trial, source=source, env=env), timeout_seconds=900,
            trusted_source_repositories=frozenset({str(source.repository)}),
        )
        native = {
            "name": "capture_archive", "status": result.status, "path": str(result.path),
            "reference": result.reference.model_dump(mode="json"),
        }
        record["run"] = native
        if result.status != "succeeded":
            raise RuntimeError(f"Native CPU archive sealing failed: {result.path}")
        verify_native_archive(native, identity, size, str(source_path))
        record.update(status="sealed", sealed_unix=time.time())
        # Persist the native reference before spawning the independent uploader.
        save_receipt(receipt_path, record)
        record["publication_queue"] = str(queue_publication(root, result.reference, destination))
        save_receipt(receipt_path, record)
        return record
    except Exception as exc:
        if record.get("status") != "sealed":
            record.update(status="failed", error_type=type(exc).__name__)
            save_receipt(receipt_path, record)
        raise


def run(
    root: Path, archive_directory: Path, archive: Path | None = None,
    expected_sha256: str | None = None, retry_failed: bool = False,
) -> dict[str, Any]:
    """Seal all installed task archives and enqueue promotion without a GPU lock."""
    root = root.resolve(strict=True)
    allowed_root = NATIVE_ROOT.resolve(strict=True)
    source_root = SOURCE_ROOT.resolve(strict=True)
    archive_directory = archive_directory.resolve(strict=True)
    if root != allowed_root or not archive_directory.is_relative_to(source_root):
        raise ValueError("Archive sealing is restricted to the explicit tranche-8 task workspaces.")
    if not isinstance(load_storage_settings(root).destination, LocalStorageDestination):
        raise TypeError("Native capture archives must seal locally before asynchronous promotion.")
    settings = load_json(root / "configs/csts-qwen-evidence.json")
    destination = ViperCloudDestination.model_validate(settings["publication_destination"])
    source, environment = read_source(root), observe_python_env()
    if archive is None:
        if expected_sha256 is not None:
            raise ValueError("An explicit full hash requires a single --archive.")
        paths = sorted(archive_directory.glob("capture-checkpoint-*.tar.gz"))
    else:
        path = archive if archive.is_absolute() else archive_directory / archive
        paths = [path]
    directory = root / "answer_input_results/proposition_capture_archive"
    directory.mkdir(parents=True, exist_ok=True)
    records = []
    with (directory / "seal.lock").open("a+") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        for path in paths:
            identity, size = checked_archive(path, archive_directory, expected_sha256)
            record = seal_one(root, path, identity, size, source, environment, destination, retry_failed)
            records.append(record)
            print(json.dumps({
                "event": "capture_archive_sealed", "archive_sha256": identity,
                "archive_bytes": size, "publication_queue": record["publication_queue"],
            }, allow_nan=False), flush=True)
    result = {"status": "complete", "archives": len(records), "sealed_bytes": sum(r["archive_bytes"] for r in records), "records": records}
    save_receipt(directory / "latest.json", result)
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=NATIVE_ROOT)
    parser.add_argument("--archive-directory", type=Path, default=SOURCE_ROOT)
    parser.add_argument("--archive", type=Path)
    parser.add_argument("--sha256")
    parser.add_argument("--retry-failed", action="store_true")
    args = parser.parse_args()
    result = run(args.root, args.archive_directory, args.archive, args.sha256, args.retry_failed)
    print(json.dumps({
        "event": "capture_archive_batch_complete", "status": result["status"],
        "archives": result["archives"], "sealed_bytes": result["sealed_bytes"],
        "receipt": str(args.root / "answer_input_results/proposition_capture_archive/latest.json"),
        "promotion_waited": False,
    }, allow_nan=False), flush=True)
