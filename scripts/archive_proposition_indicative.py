"""Publish completed indicative artifacts through VIPER's standalone-file API."""

import argparse
import hashlib
import json
from pathlib import Path

from viper.storage import ViperCloudDestination, publish_resolved_files

from csts_pilot.background_storage import _save

PREFIX = "csts_proposition_indicative_20261026"


def checked_payload(root, directory, settings_path, source_commit, settings_sha256):
    """Bind completed outputs and frozen small inputs without rereading checkpoints."""
    if directory.is_symlink() or settings_path.is_symlink():
        raise ValueError("Archive source paths must be physical task paths.")
    root, directory = root.resolve(strict=True), directory.resolve(strict=True)
    settings_path = settings_path.resolve(strict=True)
    if not directory.is_relative_to(
        root / "indicative_results"
    ) or not settings_path.is_relative_to(root):
        raise ValueError("Archive one completed indicative result directory.")
    required = {
        "summary.json",
        "results.json",
        "indicative_report.json",
        "indicative_report.md",
    }
    required |= {
        f"{arm}/{phase}_{kind}"
        for arm in ("ratings", "evidence")
        for phase in ("pretrain", "ratings")
        for kind in ("model.pt", "optimizer.pt", "trace.json")
    }
    required |= {
        f"{arm}/validation_predictions.json" for arm in ("ratings", "evidence")
    }
    if any(not (directory / name).is_file() for name in required):
        raise ValueError(
            "Completed checkpoints, traces, predictions and reports are required."
        )
    summary, results = [
        json.loads((directory / name).read_text())
        for name in ("summary.json", "results.json")
    ]
    if (
        summary.get("status") != "complete"
        or results["protocol"]["source_commit"] != source_commit
        or summary["provenance"]["source_commit"] != source_commit
    ):
        raise ValueError(
            "Results must be complete and bound to the exact execution source."
        )
    with settings_path.open("rb") as stream:
        if hashlib.file_digest(stream, "sha256").hexdigest() != settings_sha256:
            raise ValueError("The frozen execution settings changed.")
    settings = json.loads(settings_path.read_text())
    if results["protocol"]["settings_sha256"] != settings_sha256:
        raise ValueError("Results identify different execution settings.")
    paths = list(directory.rglob("*"))
    if any(path.is_symlink() for path in paths):
        raise ValueError("Archive sources must contain regular files and directories.")
    files = {
        f"{PREFIX}/{path.relative_to(root).as_posix()}": path
        for path in paths
        if path.is_file()
    }
    bindings = {
        **settings["splits"],
        **{
            name: settings[name]
            for name in (
                "answers",
                "provenance",
                "audit_gate",
                "report_cohorts",
                "baseline_predictions",
            )
        },
    }
    for spec in bindings.values():
        path = root / spec["path"]
        with path.open("rb") as stream:
            if hashlib.file_digest(stream, "sha256").hexdigest() != spec["sha256"]:
                raise ValueError("A frozen source input changed before publication.")
        files[f"{PREFIX}/{spec['path']}"] = path
    files[f"{PREFIX}/{settings_path.relative_to(root).as_posix()}"] = settings_path
    destination = ViperCloudDestination.model_validate(
        settings["publication_destination"]
    )
    if (destination.owner, destination.workspace) != (
        "pvd232",
        "jep_csts_joint_20261021",
    ):
        raise ValueError("Use the existing JEP publication destination.")
    return root, files, destination


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for flag in ("root", "directory", "settings", "source-commit", "settings-sha256"):
        parser.add_argument(f"--{flag}", required=True)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    root = Path(args.root)
    directory, settings_path = root / args.directory, root / args.settings
    root, files, destination = checked_payload(
        root, directory, settings_path, args.source_commit, args.settings_sha256
    )
    receipt = directory.with_name(directory.name + ".viper.json")
    record = {
        "status": "pending",
        "source_commit": args.source_commit,
        "settings_sha256": args.settings_sha256,
        "files": len(files),
        "bytes": sum(path.stat().st_size for path in files.values()),
        "local_files_preserved": True,
    }
    if args.dry_run:
        print(json.dumps(record))
        return
    _save(receipt, record)
    references = publish_resolved_files(root, destination, files)
    record.update(
        status="published",
        references={
            name: value.model_dump(mode="json") for name, value in references.items()
        },
    )
    _save(receipt, record)
    receipt_references = publish_resolved_files(
        root, destination, {f"{PREFIX}/publication_receipt.json": receipt}
    )
    record["receipt_reference"] = receipt_references[
        f"{PREFIX}/publication_receipt.json"
    ].model_dump(mode="json")
    _save(receipt, record)
    print(
        json.dumps(
            {"status": "published", "receipt": str(receipt), "files": len(references)}
        )
    )


if __name__ == "__main__":
    main()
