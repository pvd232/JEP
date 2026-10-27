"""Verify the sealed Colab run and continue the original comparison without retraining."""

import argparse
import fcntl
import json
import os
import shutil
import subprocess
import time
from pathlib import Path

from viper import api
from viper.repository import read_source

from csts_pilot.convergence import file_sha256, write_json
from csts_pilot.convergence_run import artifact_path
from csts_pilot.proposition_evidence_run import phase_config
from csts_pilot.qwen_evidence import validate_matched_phases


def finish(root: Path, mirror: Path, name: str, operator: Path) -> None:
    """Require native verification and matched inputs before resuming test selection."""
    receipt = operator / "resumed.json"
    if receipt.exists():
        return
    handoff = json.loads((operator / "handoff.json").read_text())
    if handoff["status"] != "ratings_control_completed_proposition_delegated_to_colab":
        raise ValueError("The original control must finish before ownership changes.")
    record = json.loads((mirror / "migration_result.json").read_text())
    if record["status"] != "succeeded" or record["name"] != "evidence_ratings":
        raise ValueError("The Colab training run has not succeeded.")
    if not Path(record["path"]).resolve().is_relative_to(mirror.resolve()):
        raise ValueError("The imported native run is outside its recovered workspace.")
    subprocess.run(
        ["git", "fetch", "--no-tags", "--update-shallow", str(mirror), "HEAD"],
        cwd=root,
        check=True,
        capture_output=True,
    )
    trusted = frozenset(
        {str(read_source(root).repository), str(read_source(mirror).repository)}
    )
    api.verify_run(
        api.VerifyRunRequest(
            root=root, path=Path(record["path"]), trusted_source_repositories=trusted
        )
    )
    directory = root / "qwen_evidence_results" / name
    summary_path = directory / "summary.json"
    summary = json.loads(summary_path.read_text())
    runs = {run["name"]: run for run in summary["runs"]}
    if "evidence_ratings" in runs:
        raise ValueError("A proposition ratings run is already registered.")
    if runs["ratings_ratings"]["status"] != "succeeded":
        raise ValueError("Preserve the unfinished ratings control.")
    flight = summary.get("in_flight")
    if flight and flight["name"] != "evidence_ratings":
        raise ValueError("An unrelated stage is still in flight.")
    prepared = artifact_path(runs["prepare"], "prepare", "prepared", "prepared.json")
    parent = artifact_path(runs["evidence_pretrain"], "train", "last_model", "model.pt")
    expected = phase_config(
        summary["settings"], "evidence", "ratings", prepared, parent
    )
    actual = json.loads(
        artifact_path(record, "train", "trace", "trace.json").read_text()
    )
    if actual["protocol_config"] != {
        **expected.model_dump(mode="json"),
        "microbatch_size": 32,
    }:
        raise ValueError(
            "Colab changed a training setting beyond the declared microbatch."
        )
    traces = {
        arm: {
            phase: json.loads(
                artifact_path(
                    runs[f"{arm}_{phase}"], "train", "trace", "trace.json"
                ).read_text()
            )
            for phase in ("pretrain", "ratings")
            if f"{arm}_{phase}" in runs
        }
        for arm in ("ratings", "evidence")
    }
    traces["evidence"]["ratings"] = actual
    validate_matched_phases(traces, 4)
    write_json(operator / "summary.before_registration.json", summary)
    summary["runs"].append(record)
    summary["in_flight"] = None
    summary["status"] = "running"
    summary["colab_migration"] = {
        "source_commit": json.loads((mirror / "migration_status.json").read_text())[
            "source_commit"
        ],
        "hardware": record["hardware"],
        "microbatch_size": 32,
        "overall_batch_size": expected.batch_size,
        "parent_sha256": file_sha256(parent),
        "native_run_verified": True,
        "completed_measurements_reused": True,
    }
    shutil.copyfile(
        artifact_path(record, "train", "trace", "trace.json"),
        directory / "evidence_ratings_trace.json",
    )
    write_json(summary_path, summary)
    command = json.loads((operator / "supervisor_args.json").read_text())
    with (operator / "resumed-supervisor.log").open("ab") as log:
        worker = subprocess.Popen(
            command,
            cwd=root,
            env=os.environ.copy(),
            stdin=subprocess.DEVNULL,
            stdout=log,
            stderr=subprocess.STDOUT,
            start_new_session=True,
        )
    write_json(
        receipt,
        {
            "pid": worker.pid,
            "started_unix": time.time(),
            "colab_run": record,
            "test_used_for_selection": False,
        },
    )


def main() -> None:
    """Accept one recovered workspace and preserve a single finalization owner."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--mirror", type=Path, required=True)
    parser.add_argument("--name", required=True)
    parser.add_argument("--operator", type=Path, required=True)
    args = parser.parse_args()
    args.operator.mkdir(parents=True, exist_ok=True)
    with (args.operator / "finalize.lock").open("a+") as owner:
        fcntl.flock(owner, fcntl.LOCK_EX | fcntl.LOCK_NB)
        finish(args.root, args.mirror, args.name, args.operator)


if __name__ == "__main__":
    main()
