"""Run the bounded overnight pilot and publish its results from the GPU host."""

import argparse
import json
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Any

from scripts.export_proposition_epoch_scores import collect, markdown

BRANCH = "experiment/csts-proposition-evidence-20261026"
REPORT = "training_outputs/proposition_full_20261026"


def save(path: Path, value: Any) -> None:
    """Replace controller state while retaining native measurement artifacts."""
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, indent=2, allow_nan=False) + "\n")
    temporary.replace(path)


def read(path: Path) -> Any:
    """Read a saved controller or native-stage record."""
    return json.loads(path.read_text())


def decision(summary: dict[str, Any], selection: dict[str, Any]) -> dict[str, Any]:
    """Apply the declared validation-only trigger after both checkpoints are frozen."""
    if (
        summary["status"] != "complete"
        or selection.get("status") != "checkpoints_frozen"
        or selection["test_scores_used_for_selection"] is not False
    ):
        raise ValueError(
            "A decision requires both frozen checkpoints and completed scoring."
        )
    scores = {
        arm: selection["candidates"][arm]["validation"]["spearman"]
        for arm in ("ratings", "evidence")
    }
    delta = scores["evidence"] - scores["ratings"]
    return {
        "criterion": "Selected proposition-model validation Spearman exceeds the selected ratings-control validation Spearman.",
        "positive": delta > 0,
        "validation_spearman": scores,
        "validation_difference": delta,
        "test_spearman": {
            arm: summary["live_scores"][arm]["spearman"] for arm in scores
        },
        "test_used_for_generation_decision": False,
        "selected_epochs": {
            arm: selection["candidates"][arm]["epoch"] for arm in scores
        },
        "training_seed": summary["settings"]["training"]["seed"],
        "source_commit": summary["source_commit"],
        "dataset_revision": summary["settings"]["dataset_revision"],
        "scope": "One-seed pilot with existing proposition coverage and a bounded training budget.",
    }


def publish(
    root: Path, operator: Path, files: dict[str, str], environment: dict[str, str]
) -> str:
    """Publish a normal commit over the latest score-table branch."""

    def git(
        args: list[str], content: str | None = None, extra: dict[str, str] | None = None
    ) -> str:
        result = subprocess.run(
            ["git", *args],
            cwd=root,
            env={**environment, **(extra or {})},
            input=content,
            text=True,
            capture_output=True,
            check=True,
            timeout=60,
        )
        return result.stdout.strip()

    for attempt in range(3):
        git(["fetch", "origin", BRANCH])
        parent = git(["rev-parse", "FETCH_HEAD"])
        with tempfile.TemporaryDirectory(
            prefix="publication-", dir=operator
        ) as directory:
            extra = {"GIT_INDEX_FILE": str(Path(directory) / "index")}
            git(["read-tree", parent], extra=extra)
            for filename, content in files.items():
                blob = git(["hash-object", "-w", "--stdin"], content)
                git(
                    [
                        "update-index",
                        "--add",
                        "--cacheinfo",
                        f"100644,{blob},{filename}",
                    ],
                    extra=extra,
                )
            tree = git(["write-tree"], extra=extra)
            commit = git(
                ["commit-tree", tree, "-p", parent],
                "Update overnight jep-csts-v1 pilot\n",
            )
        try:
            git(["push", "origin", f"{commit}:refs/heads/{BRANCH}"])
            return commit
        except subprocess.CalledProcessError:
            if attempt == 2:
                raise
    raise RuntimeError("Publication did not finish.")


def render(
    report: dict[str, Any], result: dict[str, Any] | None, operator: Path
) -> str:
    """Place the current result, generation decision and epoch curves on one page."""
    prefix = [
        "# Overnight pilot: jep-csts-v1",
        "",
        "Training: **6,051** comparisons. Validation: **1,576**. Test: **2,430**.",
        "",
        "Both models use validation patience **2**, with an equal **8,100-second** ratings-training budget per model. The morning report deadline is **8:00 a.m. ET, October 27**.",
        "",
        "[Earlier V4.1 comparison](v41_final_epoch_scores.md)",
        "",
    ]
    if result is not None:
        prefix += [
            "## Pilot result",
            "",
            "| Model | Selected validation Spearman | Test Spearman | Selected ratings epoch |",
            "|---|---:|---:|---:|",
        ]
        for arm, label in (
            ("ratings", "Ratings control"),
            ("evidence", "Proposition model"),
        ):
            prefix.append(
                f"| {label} | {result['validation_spearman'][arm]:.6f} | {result['test_spearman'][arm]:.6f} | {result['selected_epochs'][arm]} |"
            )
        prefix += [
            "",
            f"Proposition-model validation difference: **{result['validation_difference']:+.6f}**.",
            f"Ratings training stopped because: {result.get('stopping_reasons', {})}. A resource-budget stop means the overnight time limit ended training before patience 2 was reached.",
            "",
            "Missing proposition generation: **queued**."
            if result["positive"]
            else "Missing proposition generation: **not queued; the pilot's validation difference was zero or negative**.",
            "",
            "This is a one-seed screening result. Selected checkpoints were frozen before test scoring. [Detailed comparison and source-group intervals](comparison_report.md).",
            "",
        ]
    if (operator / "deadline_notice.json").exists():
        prefix += [
            "## Morning status",
            "",
            read(operator / "deadline_notice.json")["message"],
            "",
        ]
    return "\n".join(prefix) + markdown(report)


def snapshot(
    root: Path,
    name: str,
    operator: Path,
    environment: dict[str, str],
    result: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Publish a current trace snapshot while keeping the last valid snapshot available."""
    previous_path = operator / "last_report.json"
    previous = read(previous_path) if previous_path.exists() else None
    report = collect(root, name, previous=previous)
    report["dataset_revision"] = "jep-csts-v1"
    if result is not None:
        report["pilot_decision"] = result
    save(previous_path, report)
    normalized = {
        key: value for key, value in report.items() if key != "updated_at_utc"
    }
    signature_path = operator / "published_report.json"
    if not signature_path.exists() or read(signature_path) != normalized:
        body = render(report, result, operator)
        files = {
            REPORT + "/epoch_scores.json": json.dumps(report, indent=2) + "\n",
            REPORT + "/epoch_scores.md": body,
        }
        if result is not None:
            files[REPORT + "/morning_report.md"] = body
            files[REPORT + "/pilot_decision.json"] = json.dumps(result, indent=2) + "\n"
            for filename in (
                "csts_proposition_evidence_report.md",
                "csts_proposition_evidence_results.json",
            ):
                source = root / "training_outputs" / filename
                target = (
                    "comparison_report.md"
                    if filename.endswith(".md")
                    else "comparison_results.json"
                )
                files[REPORT + "/" + target] = (
                    source.read_text()
                    if source.exists()
                    else "Detailed CPU analysis is pending; completed native predictions are retained.\n"
                    if filename.endswith(".md")
                    else json.dumps(
                        {"status": "pending", "native_predictions_retained": True}
                    )
                    + "\n"
                )
        publish(root, operator, files, environment)
        save(signature_path, normalized)
    return report


def watchdog(
    root: Path, name: str, operator: Path, environment: dict[str, str], deadline: float
) -> None:
    """Publish retained results when the deadline arrives during training."""
    while time.time() < deadline:
        published = operator / "published_report.json"
        if published.exists() and read(published).get("pilot_decision") is not None:
            return
        time.sleep(min(30, max(0, deadline - time.time())))
    decision_path = operator / "pilot_decision.json"
    if decision_path.exists():
        snapshot(root, name, operator, environment, read(decision_path))
        return
    notice = {
        "message": "The morning deadline arrived before the full pilot completed. The epoch tables below show the retained results. No positive-result claim has been made.",
        "checked_unix": time.time(),
    }
    save(operator / "deadline_notice.json", notice)
    report = snapshot(root, name, operator, environment)
    body = render(report, None, operator)
    publish(
        root,
        operator,
        {REPORT + "/epoch_scores.md": body, REPORT + "/morning_report.md": body},
        environment,
    )


def main() -> None:
    """Keep training, publication and the morning deadline independent of this chat."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--operator", type=Path, required=True)
    parser.add_argument("--name", required=True)
    parser.add_argument("--settings", required=True)
    parser.add_argument("--git-environment", type=Path, required=True)
    parser.add_argument("--deadline", type=float, required=True)
    parser.add_argument("--watchdog", action="store_true")
    args = parser.parse_args()
    args.operator.mkdir(parents=True, exist_ok=True)
    environment = {**os.environ, **read(args.git_environment)}
    if args.watchdog:
        watchdog(args.root, args.name, args.operator, environment, args.deadline)
        return
    with (args.operator / "watchdog.log").open("ab", buffering=0) as log:
        guard = subprocess.Popen(
            [sys.executable, __file__, *sys.argv[1:], "--watchdog"],
            cwd=args.root,
            env=environment,
            stdin=subprocess.DEVNULL,
            stdout=log,
            stderr=subprocess.STDOUT,
            start_new_session=True,
        )
    with (args.operator / "training.log").open("ab", buffering=0) as log:
        child = subprocess.Popen(
            [
                "flock",
                "-n",
                "/home/machina/jep-csts-qwen-evidence-20261024/.viper/overnight_gpu.lock",
                sys.executable,
                "-m",
                "csts_pilot.proposition_evidence_run",
                "--settings",
                args.settings,
                "--name",
                args.name,
                "--execute",
            ],
            cwd=args.root,
            env=environment,
            stdin=subprocess.DEVNULL,
            stdout=log,
            stderr=subprocess.STDOUT,
            start_new_session=True,
        )
        save(
            args.operator / "launch.json",
            {
                "supervisor_pid": os.getpid(),
                "training_pid": child.pid,
                "watchdog_pid": guard.pid,
                "deadline": args.deadline,
                "source_revision": subprocess.check_output(
                    ["git", "rev-parse", "HEAD"], cwd=args.root, text=True
                ).strip(),
            },
        )
        summary_path = args.root / "qwen_evidence_results" / args.name / "summary.json"
        while child.poll() is None:
            try:
                if summary_path.exists():
                    snapshot(args.root, args.name, args.operator, environment)
                save(
                    args.operator / "heartbeat.json",
                    {
                        "status": "training",
                        "checked_unix": time.time(),
                        "training_pid": child.pid,
                    },
                )
            except (OSError, ValueError, subprocess.SubprocessError) as error:
                save(
                    args.operator / "publication_error.json",
                    {"error": str(error), "checked_unix": time.time()},
                )
            time.sleep(30)
    summary = (
        read(summary_path)
        if summary_path.exists()
        else {"status": "failed", "current_stage": "initialization"}
    )
    if summary["status"] != "complete":
        save(
            args.operator / "failure.json",
            {
                "returncode": child.returncode,
                "current_stage": summary.get("current_stage"),
                "preserve_completed_outputs": True,
            },
        )
        summary["status"] = "failed"
        save(summary_path, summary)
        if "settings" in summary:
            snapshot(args.root, args.name, args.operator, environment)
        raise RuntimeError("The pilot failed; native outputs are preserved.")
    result = decision(summary, read(summary_path.parent / "selection.json"))
    result["stopping_reasons"] = {
        arm: read(summary_path.parent / f"{arm}_ratings_trace.json")["stop_reason"]
        for arm in ("ratings", "evidence")
    }
    save(args.operator / "pilot_decision.json", result)
    save(
        args.operator / "generation_queue.json",
        {
            "status": "queued" if result["positive"] else "not_queued",
            "trigger": result,
            "dataset_revision": "jep-csts-v1",
        },
    )
    for attempt in range(10):
        try:
            snapshot(args.root, args.name, args.operator, environment, result)
            break
        except (OSError, ValueError, subprocess.SubprocessError) as error:
            save(
                args.operator / "publication_error.json",
                {"error": str(error), "attempt": attempt, "checked_unix": time.time()},
            )
            time.sleep(30)
    else:
        raise RuntimeError(
            "Final publication failed; the deadline watchdog retains responsibility."
        )
    save(
        args.operator / "heartbeat.json",
        {
            "status": "complete",
            "checked_unix": time.time(),
            "positive": result["positive"],
        },
    )


if __name__ == "__main__":
    main()
