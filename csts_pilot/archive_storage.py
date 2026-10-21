"""Release old research payloads after a verified VIPER cloud round trip."""

import argparse
import hashlib
import json
import os
import shutil
import time
from pathlib import Path
from typing import Any

from viper.cloud import GcsRepository, ViperCloud, ViperCloudDestination


def fingerprint(path: Path) -> tuple[int, int, int, int]:
    """Detect replacement or modification while a source is being archived."""
    stat = path.stat()
    return stat.st_dev, stat.st_ino, stat.st_size, stat.st_mtime_ns


def archive_file(
    path: Path,
    root: Path,
    scratch: Path,
    cloud: Any,
    destination: Any,
    *,
    remove_original: bool = True,
) -> dict:
    """Publish, restore, record the durable reference, then remove one source."""
    before = fingerprint(path)
    relative = path.relative_to(root).as_posix()
    reference = cloud.resolved_files(destination, {f"legacy/{relative}": path})[
        f"legacy/{relative}"
    ]
    restored = scratch / f"{reference.sha256}.verify"
    try:
        cloud.fetch_to_path(reference, restored)
        with restored.open("rb") as stream:
            restored_digest = hashlib.file_digest(stream, "sha256").hexdigest()
        if (
            restored_digest != reference.sha256
            or restored.stat().st_size != reference.bytes
        ):
            raise RuntimeError(f"Restored payload differs from its reference: {path}")
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
        if remove_original:
            path.unlink()
        return receipt
    finally:
        restored.unlink(missing_ok=True)


def main() -> None:
    """Archive large inactive research files while retaining code and environments."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, action="append", required=True)
    parser.add_argument("--minimum-mib", type=int, default=128)
    parser.add_argument("--inventory", type=Path, required=True)
    parser.add_argument("--prepare-only", action="store_true")
    args = parser.parse_args()
    root = Path("/home/machina")
    allowed = {
        root / "MANTRA/experiments",
        root / "rico-treated-qc-20261006",
        root / "rico-controlstate-stopping-experiment",
    }
    if set(args.root) != allowed or args.minimum_mib != 128:
        raise ValueError(
            "Cleanup requires the exact approved roots and size threshold."
        )
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
    if args.inventory.exists():
        inventory = json.loads(args.inventory.read_text())
    else:
        if (
            len(files) != 362
            or sum(path.stat().st_size for path in files) != 177547327016
        ):
            raise ValueError("Candidates differ from the approved 362-file inventory.")
        # Preserve files referenced by shared MANTRA runtime code and contracts.
        references = {str(path): [] for path in files}
        live_roots = [
            root / "MANTRA" / name
            for name in (
                "src",
                "data/contracts",
                "data/processed/benchmarks",
                "sota2",
                "final_paper3",
                "scripts",
            )
        ]
        needles = {
            str(path): (
                str(path),
                str(path.relative_to(root / "MANTRA")),
                path.parts[5],
            )
            for path in files
            if path.is_relative_to(root / "MANTRA/experiments")
        }
        for live_root in live_roots:
            for base, dirs, names in os.walk(live_root, followlinks=False):
                dirs[:] = [
                    name
                    for name in dirs
                    if name not in excluded and not Path(base, name).is_symlink()
                ]
                for name in names:
                    source = Path(base, name)
                    if (
                        source.suffix
                        not in {".py", ".json", ".yaml", ".yml", ".toml", ".sh"}
                        or source.is_symlink()
                    ):
                        continue
                    if source.stat().st_size > 16 * 2**20:
                        continue
                    text = source.read_text(errors="replace")
                    for target, patterns in needles.items():
                        if any(pattern in text for pattern in patterns):
                            references[target].append(str(source))
        inventory = {
            "approval": "Explicit user approval, 2026-10-21: upload, restore-verify, then delete these 362 files.",
            "files": [
                {
                    "path": str(path),
                    "fingerprint": list(fingerprint(path)),
                    "runtime_references": references[str(path)],
                }
                for path in files
            ],
            "logical_bytes": sum(path.stat().st_size for path in files),
        }
        args.inventory.parent.mkdir(parents=True, exist_ok=True)
        args.inventory.write_text(json.dumps(inventory, indent=2) + "\n")
    entries = inventory["files"]
    if len(entries) != 362 or inventory["logical_bytes"] != 177547327016:
        raise ValueError("The saved inventory differs from the approved scope.")
    if len({entry["path"] for entry in entries}) != len(entries):
        raise ValueError("The inventory repeats a path.")
    for entry in entries:
        path = Path(entry["path"])
        if (
            not any(path.is_relative_to(directory) for directory in allowed)
            or path.is_symlink()
        ):
            raise ValueError(f"Invalid inventory path: {path}")
    if args.prepare_only:
        print(
            json.dumps(
                {
                    "inventory": str(args.inventory),
                    "candidates": len(entries),
                    "logical_bytes": inventory["logical_bytes"],
                    "referenced_files_retained": sum(
                        bool(entry["runtime_references"]) for entry in entries
                    ),
                }
            ),
            flush=True,
        )
        return
    cloud = ViperCloud(
        Path("/"),
        GcsRepository(bucket="mantra-mlfg-prod-uscentral1-8e7a", prefix="viper"),
    )
    destination = ViperCloudDestination(
        owner="pvd232", workspace="legacy_disk_archive_20261021"
    )
    cloud.resolved_files(destination, {"archive_inventory.json": args.inventory})
    log = Path("/mnt/rico-source-data/jep-storage-cleanup-20261021.jsonl")
    print(
        json.dumps(
            {
                "candidates": len(entries),
                "logical_bytes": inventory["logical_bytes"],
            }
        ),
        flush=True,
    )
    with log.open("a") as stream:
        for entry in entries:
            path = Path(entry["path"])
            try:
                if not path.exists():
                    pointer = path.with_name(path.name + ".viper.json")
                    receipt = json.loads(pointer.read_text())
                    if (
                        receipt["original_path"] != str(path)
                        or receipt["bytes"] != entry["fingerprint"][2]
                    ):
                        raise ValueError(
                            "The retrieval receipt differs from the inventory."
                        )
                    print(
                        json.dumps(
                            {"original_path": str(path), "status": "already_archived"}
                        ),
                        flush=True,
                    )
                    continue
                if list(fingerprint(path)) != entry["fingerprint"]:
                    raise ValueError(
                        "Source differs from its approved inventory fingerprint."
                    )
                keep = bool(entry["runtime_references"])
                receipt = archive_file(
                    path, root, scratch, cloud, destination, remove_original=not keep
                )
                record = dict(
                    receipt,
                    status="archived_and_retained" if keep else "archived_and_removed",
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
    cloud.resolved_files(destination, {"archive_receipts.jsonl": log})
    latest = {
        json.loads(line)["original_path"]: json.loads(line)
        for line in log.read_text().splitlines()
        if line.strip()
    }
    records = [latest[entry["path"]] for entry in entries]
    complete = all(
        record["status"] in {"archived_and_removed", "archived_and_retained"}
        for record in records
    )
    state = {
        "status": "complete" if complete else "retained_after_error",
        "completed_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "pid": os.getpid(),
        "inventory": str(args.inventory),
        "files": len(records),
        "removed": sum(
            record["status"] == "archived_and_removed" for record in records
        ),
        "retained": sum(
            record["status"] == "archived_and_retained" for record in records
        ),
        "removed_bytes": sum(
            record.get("bytes", 0)
            for record in records
            if record["status"] == "archived_and_removed"
        ),
        "root_free_bytes": shutil.disk_usage(root).free,
    }
    state_path = log.with_suffix(".state.json")
    completion = cloud.resolved_files(
        destination,
        {"archive_completion.json": (json.dumps(state, indent=2) + "\n").encode()},
    )["archive_completion.json"]
    state["cloud_completion"] = completion.model_dump(mode="json")
    state_path.write_text(json.dumps(state, indent=2) + "\n")
    print(json.dumps(state), flush=True)
    if not complete:
        raise RuntimeError("Some sources were retained after archival errors.")


if __name__ == "__main__":
    main()
