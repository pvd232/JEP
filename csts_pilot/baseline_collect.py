"""Verify completed native baselines and gather their small reporting artifacts."""

import argparse
import shutil
from pathlib import Path
from typing import Any

from viper import api
from viper.repository import read_source, resolve_root

from csts_pilot.convergence import file_sha256, write_json
from csts_pilot.convergence_run import artifact_path
from jep_pilot.loaders import load_json


def collect_phase(root: Path, directory: Path) -> dict[str, Any]:
    """Require completed cloud receipts and verify every local native graph."""
    summary = load_json(directory / "summary.json")
    if summary["status"] != "complete" or summary["in_flight"] is not None:
        raise ValueError(
            "Collect only a completed computation with zero active invocations."
        )
    trusted = frozenset({str(read_source(root).repository)})
    records, measurements, exports = [], 0, {}
    if file_sha256(directory / "selection.json") != summary["selection_sha256"]:
        raise ValueError("The collected selection differs from its frozen summary.")
    for record in summary["runs"]:
        if record["status"] != "succeeded":
            raise ValueError("Every retained native stage must have succeeded.")
        job = load_json(Path(record["publication_queue"]))
        if (
            job["status"] != "published"
            or job["request"]["source"] != record["reference"]
        ):
            raise ValueError(
                "Cloud publication remains pending or refers to another run."
            )
        result = api.verify_run(
            api.VerifyRunRequest(
                root=root,
                path=Path(record["path"]),
                trusted_source_repositories=trusted,
            )
        )
        files = []
        if (
            record["name"].startswith("train_")
            and record["name"] != "train_validation_embeddings"
        ):
            kind = record["name"][len("train_") :]
            files = [
                ("train", "trace", "trace.json", f"{kind}_trace.json"),
                (
                    "train",
                    "validation_predictions",
                    "predictions.json",
                    f"{kind}_validation_predictions.json",
                ),
            ]
        elif record["name"].startswith("test_") and record["name"] != "test_embeddings":
            kind = record["name"][len("test_") :]
            files = [
                ("test", "predictions", "predictions.json", f"{kind}_predictions.json"),
                ("test", "timing", "timing.json", f"{kind}_evaluation_timing.json"),
            ]
        for stage_id, artifact, filename, exported in files:
            original = artifact_path(record, stage_id, artifact, filename)
            shutil.copyfile(original, directory / exported)
            exports[exported] = {
                "sha256": file_sha256(original),
                "producer": record["reference"],
                "stage": stage_id,
                "artifact": artifact,
            }
        measurements += result.measurement_count
        records.append(
            {
                "name": record["name"],
                "local_reference": record["reference"],
                "cloud_reference": job["reference"],
                "measurements_verified": result.measurement_count,
                "promotion_seconds": job.get("promotion_seconds"),
            }
        )
    receipt = {
        "status": "verified",
        "source_commit": summary["source_commit"],
        "runs": records,
        "measurements_verified": measurements,
        "summary_sha256": file_sha256(directory / "summary.json"),
        "exports": exports,
    }
    write_json(directory / "native_verification.json", receipt)
    manifest = {}
    for path in sorted(directory.glob("*.json")):
        if path.name != "files.json":
            manifest[path.name] = {
                "sha256": file_sha256(path),
                "bytes": path.stat().st_size,
            }
    write_json(directory / "files.json", manifest)
    return receipt


def main() -> None:
    """Verify and collect a chosen completed phase."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path)
    args = parser.parse_args()
    receipt = collect_phase(resolve_root(), args.directory.resolve())
    print(
        {
            "status": receipt["status"],
            "measurements_verified": receipt["measurements_verified"],
        }
    )


if __name__ == "__main__":
    main()
