"""Release old research payloads after a verified VIPER cloud round trip."""

import argparse
import hashlib
import json
import os
import shutil
from pathlib import Path
from typing import Any

from viper.cloud import GcsRepository, ViperCloud, ViperCloudDestination


def fingerprint(path: Path) -> tuple[int, int, int, int]:
    """Detect replacement or modification while a source is being archived."""
    stat = path.stat()
    return stat.st_dev, stat.st_ino, stat.st_size, stat.st_mtime_ns


def archive_file(
    path: Path, root: Path, scratch: Path, cloud: Any, destination: Any
) -> dict:
    """Publish, restore, record the durable reference, then remove one source."""
    before = fingerprint(path)
    relative = path.relative_to(root).as_posix()
    reference = cloud.resolved_files(destination, {f"legacy/{relative}": path})[
        f"legacy/{relative}"
    ]
    restored = scratch / f"{reference.sha256}.verify"
    cloud.fetch_to_path(reference, restored)
    try:
        with path.open("rb") as stream:
            digest = hashlib.file_digest(stream, "sha256").hexdigest()
        if fingerprint(path) != before or digest != reference.sha256:
            raise RuntimeError(f"Source changed during archival: {path}")
        receipt = {
            "original_path": str(path),
            "bytes": reference.bytes,
            "reference": reference.model_dump(mode="json"),
            "verification": "VIPER restore verified the complete payload before deletion.",
        }
        raw = (json.dumps(receipt, indent=2) + "\n").encode()
        # Keep a durable retrieval receipt as well as the payload itself.
        cloud.resolved_files(destination, {f"receipts/{reference.sha256}.json": raw})
        pointer = path.with_name(path.name + ".viper.json")
        temporary = pointer.with_suffix(pointer.suffix + ".tmp")
        with temporary.open("wb") as stream:
            stream.write(raw)
            stream.flush()
            os.fsync(stream.fileno())
        temporary.replace(pointer)
        if fingerprint(path) != before:
            raise RuntimeError(f"Source changed before deletion: {path}")
        path.unlink()
        return receipt
    finally:
        restored.unlink(missing_ok=True)


def main() -> None:
    """Archive large inactive research files while retaining code and environments."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, action="append", required=True)
    parser.add_argument("--minimum-mib", type=int, default=128)
    args = parser.parse_args()
    root = Path("/home/machina")
    scratch = Path("/mnt/rico-source-data/jep-storage-verification-20261021")
    scratch.mkdir(exist_ok=True)
    excluded = {
        ".git",
        ".venv",
        "__pycache__",
        ".cache",
        "site-packages",
        "dist-packages",
        "node_modules",
    }
    files = []
    for directory in args.root:
        if not directory.is_relative_to(root) or directory == root:
            raise ValueError(
                "Select explicit research directories beneath /home/machina."
            )
        for base, dirs, names in os.walk(directory, followlinks=False):
            dirs[:] = [
                name
                for name in dirs
                if name not in excluded and not Path(base, name).is_symlink()
            ]
            for name in names:
                path = Path(base, name)
                if (
                    not path.is_symlink()
                    and path.is_file()
                    and path.stat().st_size >= args.minimum_mib * 2**20
                ):
                    files.append(path)
    files.sort(key=lambda path: (-path.stat().st_size, str(path)))
    cloud = ViperCloud(
        Path("/"),
        GcsRepository(bucket="mantra-mlfg-prod-uscentral1-8e7a", prefix="viper"),
    )
    destination = ViperCloudDestination(
        owner="pvd232", workspace="legacy_disk_archive_20261021"
    )
    log = Path("/mnt/rico-source-data/jep-storage-cleanup-20261021.jsonl")
    print(
        json.dumps(
            {
                "candidates": len(files),
                "logical_bytes": sum(path.stat().st_size for path in files),
            }
        ),
        flush=True,
    )
    with log.open("a") as stream:
        for path in files:
            try:
                receipt = archive_file(path, root, scratch, cloud, destination)
                record = dict(
                    receipt,
                    status="archived_and_removed",
                    root_free_bytes=shutil.disk_usage(root).free,
                )
            except (OSError, RuntimeError, ValueError) as error:
                record = {
                    "original_path": str(path),
                    "status": "retained_after_error",
                    "error": str(error),
                }
            stream.write(json.dumps(record) + "\n")
            stream.flush()
            os.fsync(stream.fileno())
            print(json.dumps(record), flush=True)


if __name__ == "__main__":
    main()
