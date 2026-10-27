"""Start the approved four-epoch follow-up after the preceding comparison is published."""

import argparse
import fcntl
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

from scripts.supervise_proposition_pilot import read, save


def parent_completed(report: dict[str, Any], name: str) -> bool:
    """Require both exhausted patience checks and successful final publication."""
    if not report:
        return False
    if report.get("identity", {}).get("run_name") != name:
        raise ValueError("The published parent report belongs to another comparison.")
    result = report.get("pilot_decision", {})
    return report.get("run_status") == "complete" and result.get(
        "stopping_reasons"
    ) == {
        "ratings": "validation_patience",
        "evidence": "validation_patience",
    }


def main() -> None:
    """Persist one waiting process, then hand the follow-up to its native supervisor."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--operator", type=Path, required=True)
    parser.add_argument("--parent-operator", type=Path, required=True)
    parser.add_argument("--parent-name", required=True)
    parser.add_argument("--name", required=True)
    parser.add_argument("--settings", required=True)
    parser.add_argument("--git-environment", type=Path, required=True)
    args = parser.parse_args()
    args.operator.mkdir(parents=True, exist_ok=True)
    environment = {**os.environ, **read(args.git_environment)}
    with (args.operator / "queue.lock").open("a+") as owner:
        fcntl.flock(owner, fcntl.LOCK_EX | fcntl.LOCK_NB)
        while True:
            parent_report = args.parent_operator / "published_report.json"
            if parent_report.exists() and parent_completed(
                read(parent_report), args.parent_name
            ):
                break
            if (args.parent_operator / "failure.json").exists():
                save(
                    args.operator / "queue.json",
                    {"status": "parent_failed", "preserve_completed_outputs": True},
                )
                raise RuntimeError(
                    "Inspect the parent failure before starting the follow-up."
                )
            save(
                args.operator / "queue.json",
                {
                    "status": "waiting_for_parent_publication",
                    "queue_pid": os.getpid(),
                    "parent_name": args.parent_name,
                    "name": args.name,
                    "checked_unix": time.time(),
                },
            )
            time.sleep(30)
        save(
            args.operator / "queue.json",
            {"status": "starting", "name": args.name, "checked_unix": time.time()},
        )
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "scripts.supervise_proposition_pilot",
                "--root",
                str(args.root),
                "--operator",
                str(args.operator),
                "--name",
                args.name,
                "--settings",
                args.settings,
                "--git-environment",
                str(args.git_environment),
                "--deadline",
                "0",
            ],
            cwd=args.root,
            env=environment,
            check=False,
        )
        save(
            args.operator / "queue.json",
            {
                "status": "complete" if result.returncode == 0 else "failed",
                "returncode": result.returncode,
                "name": args.name,
                "checked_unix": time.time(),
            },
        )
        if result.returncode:
            raise RuntimeError(
                "Follow-up supervisor failed; preserve its completed measurements."
            )


if __name__ == "__main__":
    main()
