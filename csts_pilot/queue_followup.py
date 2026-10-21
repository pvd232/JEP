"""Run the annotation pilot and joint study after the baseline evaluation."""

import fcntl
import hashlib
import json
import os
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path("/mnt/rico-source-data/jep-joint-csts-20261021")
BASELINE = Path("/home/machina/jep-csts-20261021")


def write_state(phase: str, **details: object) -> None:
    """Keep the controller's dependency and review status visible."""
    value = {"phase": phase, "pid": os.getpid(), **details}
    path = ROOT / "csts_results/queue_state.json"
    temporary = path.with_suffix(".tmp")
    temporary.write_text(json.dumps(value, indent=2) + "\n")
    temporary.replace(path)
    print(json.dumps(value), flush=True)


def main() -> None:
    """Keep one controller and require an annotation audit before joint training."""
    results = ROOT / "csts_results"
    results.mkdir(exist_ok=True)
    with (results / "queue.lock").open("w") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        source = subprocess.check_output(
            ["git", "-C", str(ROOT), "rev-parse", "HEAD"], text=True
        ).strip()
        launcher = {"pid": os.getpid(), "source_commit": source}
        (results / "launcher.json").write_text(json.dumps(launcher, indent=2) + "\n")
        write_state("waiting_for_baseline_evaluation")
        while True:
            baseline = json.loads((BASELINE / "csts_results/summary.json").read_text())
            if (
                baseline.get("status") == "complete"
                and len(baseline.get("evaluation", [])) == 6
            ):
                break
            time.sleep(20)
        next_source = os.environ.get("JEP_FOLLOWUP_SOURCE")
        if next_source:
            subprocess.run(
                [
                    "git",
                    "-C",
                    str(ROOT),
                    "fetch",
                    "origin",
                    "experiment/csts-joint-20261021",
                ],
                check=True,
            )
            subprocess.run(
                ["git", "-C", str(ROOT), "switch", "--detach", next_source], check=True
            )
            launcher["source_commit"] = next_source
            (results / "launcher.json").write_text(
                json.dumps(launcher, indent=2) + "\n"
            )
        write_state("annotation_pilot_running")
        subprocess.run(
            [
                sys.executable,
                "-m",
                "csts_pilot.joint_run",
                "--annotation-limit",
                "128",
                "--annotation-offset",
                "128",
            ],
            cwd=ROOT,
            check=True,
        )
        summary = json.loads((results / "summary.json").read_text())
        trial = next(
            row for row in summary["runs"] if row["name"] == "annotation_pilot"
        )
        answers = (
            Path(trial["path"]).parent / "artifacts/annotate/answers/answers.jsonl"
        )
        digest = hashlib.file_digest(answers.open("rb"), "sha256").hexdigest()
        write_state(
            "awaiting_annotation_review", answer_file=str(answers), sha256=digest
        )
        review_path = results / "annotation_review.json"
        while not review_path.exists():
            time.sleep(20)
        review = json.loads(review_path.read_text())
        if review.get("answer_sha256") != digest or review.get("approved") is not True:
            raise RuntimeError(
                "The annotation audit did not approve this pilot artifact."
            )
        write_state("joint_study_running", annotation_review=str(review_path))
        subprocess.run(
            [sys.executable, "-m", "csts_pilot.joint_run"], cwd=ROOT, check=True
        )
        write_state("complete")


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        write_state("stopped_after_error", error=str(error))
        raise
