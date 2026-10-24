"""Queue native VIPER cloud promotion independently of model computation."""

from __future__ import annotations

import argparse
import fcntl
import hashlib
import json
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from viper.references import ResolvedRunRef
    from viper.storage import ViperCloudDestination


def _save(path: Path, record: dict[str, Any]) -> None:
    """Commit one queue record atomically, including file and directory sync."""
    temporary: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", dir=path.parent, suffix=".tmp", delete=False
        ) as stream:
            temporary = Path(stream.name)
            json.dump(record, stream, indent=2, allow_nan=False)
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


def queue_publication(
    root: Path, reference: ResolvedRunRef, destination: ViperCloudDestination
) -> Path:
    """Persist an immutable run reference, then start an independent CPU worker."""
    root = root.resolve(strict=True)
    if reference.stored_at.kind != "local":
        raise ValueError("Background promotion requires a sealed local VIPER run.")
    directory = root / ".viper" / "publication_queue"
    directory.mkdir(parents=True, exist_ok=True)
    request = {
        "root": str(root),
        "source": reference.model_dump(mode="json"),
        "destination": destination.model_dump(mode="json"),
    }
    identity = hashlib.sha256(json.dumps(request, sort_keys=True).encode()).hexdigest()
    path = directory / f"{identity}.json"
    with (directory / "enqueue.lock").open("a+") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        if path.exists():
            record = json.loads(path.read_text())
            if record["request"] != request:
                raise ValueError("Publication queue identity collision.")
            if record["status"] == "published":
                return path
        else:
            _save(path, {"request": request, "status": "pending", "attempts": 0})
    # The request survives a failed spawn or a parent process exit. A later
    # `python -m csts_pilot.background_storage --root ...` drains it again.
    try:
        with (directory / "worker.log").open("ab") as log:
            subprocess.Popen(
                [sys.executable, "-m", __name__, "--root", str(root)],
                cwd=root,
                stdin=subprocess.DEVNULL,
                stdout=log,
                stderr=subprocess.STDOUT,
                start_new_session=True,
            )
    except OSError as error:
        print(
            json.dumps(
                {"publication_pending": str(path), "error_type": type(error).__name__}
            ),
            file=sys.stderr,
            flush=True,
        )
    return path


def _promote(root: Path, source: dict, destination: dict) -> ResolvedRunRef:
    """Load VIPER only after owning the worker lock and finding pending work."""
    from viper import execution
    from viper.references import ResolvedRunRef
    from viper.storage import ViperCloudDestination

    return execution.promote_run_to_cloud(
        root,
        ResolvedRunRef.model_validate(source),
        ViperCloudDestination.model_validate(destination),
    )


def drain_publications(root: Path, retry_failed: bool = False) -> None:
    """Serialize publishers; retry interrupted uploads without invoking training."""
    root = root.resolve(strict=True)
    directory = root / ".viper" / "publication_queue"
    directory.mkdir(parents=True, exist_ok=True)
    # Every enqueue starts a worker. Waiting for this lock closes the race
    # between the current worker's final scan and a newly committed request.
    with (directory / "worker.lock").open("a+") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        for path in sorted(directory.glob("*.json")):
            record = json.loads(path.read_text())
            if record["status"] == "published":
                continue
            if record["status"] == "uploading":
                record.update(status="failed", error_type="InterruptedPublication")
                _save(path, record)
            if record["request"]["root"] != str(root):
                raise ValueError("Publication request belongs to another workspace.")
            limit = record["attempts"] + 3 if retry_failed else 3
            while record["attempts"] < limit and record["status"] != "published":
                record.update(status="uploading", attempts=record["attempts"] + 1)
                _save(path, record)
                started = time.monotonic()
                try:
                    published = _promote(
                        root,
                        record["request"]["source"],
                        record["request"]["destination"],
                    )
                except Exception as error:
                    record.update(status="failed", error_type=type(error).__name__)
                else:
                    record.update(
                        status="published", reference=published.model_dump(mode="json")
                    )
                    record.pop("error_type", None)
                record["last_promotion_seconds"] = time.monotonic() - started
                record["promotion_seconds"] = (
                    record.get("promotion_seconds", 0.0)
                    + (record["last_promotion_seconds"])
                )
                _save(path, record)
                if record["status"] == "failed" and record["attempts"] < limit:
                    time.sleep(min(2 ** (record["attempts"] - 1), 4))


def main() -> None:
    """Resume publication only; this command has no model execution path."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", required=True, type=Path)
    parser.add_argument("--retry-failed", action="store_true")
    args = parser.parse_args()
    drain_publications(args.root, retry_failed=args.retry_failed)


if __name__ == "__main__":
    main()
