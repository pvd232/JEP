#!/usr/bin/env python3
"""Export the four training-phase epoch histories without accessing test outputs."""

import argparse
import hashlib
import json
import math
import os
from datetime import UTC, datetime
from pathlib import Path

STAGES = (
    "ratings_pretrain",
    "evidence_pretrain",
    "ratings_ratings",
    "evidence_ratings",
)


def read_object(path):
    try:
        data = json.loads(path.read_text())
        if not isinstance(data, dict):
            return None, "Expected a JSON object"
        return data, None
    except FileNotFoundError:
        return None, "missing"
    except (OSError, ValueError) as error:
        return None, str(error)


def atomic_json(path, data):
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(json.dumps(data, indent=2, allow_nan=False) + "\n")
    os.replace(temporary, path)


def number(value):
    if value is None:
        return None
    value = float(value)
    if not math.isfinite(value):
        raise ValueError("Nonfinite recorded metric")
    return value


def epoch_record(record, stage):
    epoch, step = record["epoch"], record["step"]
    if type(epoch) is not int or epoch < 1 or type(step) is not int or step < 1:
        raise ValueError("Epoch and optimizer step must be positive integers")
    validation = record["validation"]
    return {
        "epoch": epoch,
        "optimizer_updates": step,
        "validation_spearman": number(validation.get("spearman")),
        "validation_mse_1_5": number(validation.get("mse_1_5")),
        "validation_rows": validation.get("n"),
        "training_loss": number(
            record.get("training_objective", record.get("training_mse_0_1"))
        ),
        "training_loss_kind": "proposition_token_cross_entropy"
        if stage == "evidence_pretrain"
        else "rating_mse_0_1",
        "epochs_without_improvement": record.get("epochs_without_improvement"),
        "fit_seconds": number(record.get("fit_seconds")),
        "validation_seconds": number(record.get("validation_seconds")),
        "observed_epoch_seconds": number(record.get("observed_epoch_seconds")),
        "elapsed_seconds": number(record.get("elapsed_seconds")),
    }


def trace_candidates(root, directory, summary, stage, overrides):
    if stage in overrides:
        return [overrides[stage]]
    candidates = [directory / (stage + "_trace.json")]
    for run in summary.get("runs", []):
        if run.get("name") == stage:
            run_path = Path(run["path"])
            if not run_path.is_absolute():
                run_path = root / run_path
            if run_path.name == "resolved.yaml":
                run_path = run_path.parent
            candidates.append(run_path / "artifacts/train/trace/trace.json")
    flight = summary.get("in_flight") or {}
    if flight.get("name") == stage:
        experiment = flight.get("experiment_id", "")
        if experiment and Path(experiment).name == experiment:
            live = sorted(
                (root / "experiments" / experiment / "runs" / stage).glob(
                    "*/artifacts/train/trace/trace.json"
                )
            )
            if len(live) > 1:
                raise ValueError(
                    "Multiple native traces require an exact --trace override"
                )
            candidates = live + candidates
    return list(dict.fromkeys(candidates))


def collect(root, name, previous=None, overrides=None):
    root = Path(root)
    directory = root / "qwen_evidence_results" / name
    summary_path = directory / "summary.json"
    summary, error = read_object(summary_path)
    if summary is None:
        raise ValueError("Cannot read full-run summary: " + str(error))
    settings = summary["settings"]
    identity = {
        "run_name": name,
        "source_commit": summary["source_commit"],
        "attempt": summary.get("attempt"),
        "validation_sha256": settings["splits"]["validation"]["sha256"],
    }
    cached = (
        (previous or {}).get("stages", {})
        if (previous or {}).get("identity") == identity
        else {}
    )
    result = {
        "schema_version": 1,
        "updated_at_utc": datetime.now(UTC).isoformat(timespec="seconds"),
        "identity": identity,
        "training_sha256": settings["splits"]["training"]["sha256"],
        "training_policy": {
            "pretrain_epochs": settings.get("phases", {})
            .get("pretrain", {})
            .get("max_epochs", 2),
            "train_until_patience": settings.get("training", {}).get(
                "train_until_patience", False
            ),
            "patience": settings.get("training", {}).get("patience", 5),
            "ratings_max_epochs": settings.get("phases", {})
            .get("ratings", {})
            .get("max_epochs", 24),
            "ratings_max_seconds": settings.get("phases", {})
            .get("ratings", {})
            .get("max_seconds"),
        },
        "validation_rows": settings["splits"]["validation"]["rows"],
        "validation_groups": settings["splits"]["validation"].get("groups"),
        "run_status": summary.get("status"),
        "current_stage": summary.get("current_stage"),
        "summary_path": str(summary_path),
        "summary_sha256": hashlib.sha256(summary_path.read_bytes()).hexdigest(),
        "scope": "Training and validation histories only; subgroup epoch scores are unavailable in native traces.",
        "stages": {},
    }
    for stage in STAGES:
        notes, trace, trace_path = [], None, None
        try:
            candidates = trace_candidates(
                root, directory, summary, stage, overrides or {}
            )
        except ValueError as error:
            candidates = []
            notes.append(str(error))
        for candidate in candidates:
            loaded, error = read_object(candidate)
            if loaded is not None:
                trace, trace_path = loaded, candidate
                break
            if error != "missing":
                notes.append(str(candidate) + ": " + str(error))
        history = {row["epoch"]: row for row in cached.get(stage, {}).get("epochs", [])}
        if trace is not None:
            if trace.get("arm") not in (None, stage.split("_", 1)[0]):
                notes.append("Trace arm identity disagrees with stage")
                trace = None
            elif trace.get("phase") not in (None, stage.split("_", 1)[1]):
                notes.append("Trace phase identity disagrees with stage")
                trace = None
        if trace is not None:
            for raw in trace.get("epochs", []):
                try:
                    row = epoch_record(raw, stage)
                    if row["epoch"] in history and history[row["epoch"]] != row:
                        raise ValueError(
                            "Conflicting observation for completed epoch "
                            + str(row["epoch"])
                        )
                    history[row["epoch"]] = row
                except (KeyError, TypeError, ValueError) as error:
                    notes.append(str(error))
        rows = [history[key] for key in sorted(history)]
        if rows and [row["epoch"] for row in rows] != list(
            range(1, rows[-1]["epoch"] + 1)
        ):
            notes.append("Completed epoch history has a gap")
        native = [run for run in summary.get("runs", []) if run.get("name") == stage]
        status = "pending"
        if summary.get("current_stage") == stage:
            status = "running"
        if native:
            status = native[-1].get("status", status)
        cached_stage = cached.get(stage, {})
        recorded_updates = (trace or {}).get(
            "actual_updates", (trace or {}).get("updates", 0)
        )
        recorded_updates = max(
            recorded_updates,
            cached_stage.get("optimizer_updates", 0),
            rows[-1]["optimizer_updates"] if rows else 0,
        )
        result["stages"][stage] = {
            "status": status,
            "trace_status": (trace or {}).get("status"),
            "trace_path": str(trace_path) if trace_path else None,
            "trace_available": trace is not None,
            "completed_epoch": rows[-1]["epoch"] if rows else 0,
            "current_epoch": (trace or {}).get(
                "current_epoch", cached_stage.get("current_epoch")
            ),
            "optimizer_updates": recorded_updates,
            "epochs_without_improvement": (trace or {}).get(
                "epochs_without_improvement"
            ),
            "stop_reason": (trace or {}).get("stop_reason"),
            "epochs": rows,
            "notes": notes,
        }
    return result


def formatted(value, digits=6):
    return (
        "—"
        if value is None
        else (f"{value:.{digits}f}" if isinstance(value, float) else str(value))
    )


def markdown(report):
    identity = report["identity"]
    lines = [
        "# Qwen proposition comparison: per-epoch validation scores",
        "",
        f"Updated: **{report['updated_at_utc']}**. Run: `{identity['run_name']}`.",
        "",
        f"Status: **{report['run_status']}**. Current stage: **{report['current_stage'] or 'none'}**.",
        "",
        f"Validation: **{report['validation_rows']:,} comparisons**, {report['validation_groups']} source groups.",
        "",
        f"Source commit: `{identity['source_commit']}`.",
        f"Validation SHA-256: `{identity['validation_sha256']}`.",
        f"Training SHA-256: `{report['training_sha256']}`.",
        "",
        (
            f"Both models start from the same pretrained weights. For the first {report.get('training_policy', {}).get('pretrain_epochs', 2)} epochs, both see the comparisons covered by existing propositions. The ratings model learns ratings; the proposition model learns to write propositions. Both then learn ratings from the full training set. "
            + (
                f"Ratings training continues until validation patience {report['training_policy']['patience']} is exhausted, with time and epoch limits disabled."
                if report.get("training_policy", {}).get("train_until_patience")
                else f"Ratings training uses validation patience {report.get('training_policy', {}).get('patience', 5)} and an epoch ceiling of {report.get('training_policy', {}).get('ratings_max_epochs', 24)}."
            )
        ),
        "",
        "Rating loss measures error in predicted ratings on the 0–1 scale. Proposition-writing loss measures error in predicted text tokens. Each table counts optimizer updates from the beginning of that training step.",
        "",
        "Appearance and colour scores are available in the final report. Native epoch traces contain overall validation scores. Values are provisional while the comparison is running.",
        "",
    ]
    names = {
        "ratings_pretrain": f"Ratings model: first {report.get('training_policy', {}).get('pretrain_epochs', 2)} epochs on the covered subset",
        "evidence_pretrain": "Proposition model: writing propositions on the covered subset",
        "ratings_ratings": "Ratings model: ratings on the full training set",
        "evidence_ratings": "Proposition model: ratings on the full training set",
    }
    for stage in STAGES:
        data = report["stages"][stage]
        lines.extend(
            [
                "## " + names[stage],
                "",
                f"Status: **{data['status']}**. Completed epochs: **{data['completed_epoch']}**. Recorded optimizer updates: **{data['optimizer_updates']}**.",
                "",
            ]
        )
        if data["epochs"]:
            lines.extend(
                [
                    "| Epoch | Optimizer updates | Validation Spearman | Validation MSE, 1–5 | Training loss | Patience counter |",
                    "|---:|---:|---:|---:|---:|---:|",
                ]
            )
            for row in data["epochs"]:
                values = [
                    row[k]
                    for k in (
                        "epoch",
                        "optimizer_updates",
                        "validation_spearman",
                        "validation_mse_1_5",
                        "training_loss",
                        "epochs_without_improvement",
                    )
                ]
                lines.append(
                    "| " + " | ".join(formatted(value) for value in values) + " |"
                )
            lines.append("")
        else:
            lines.extend(["Awaiting the first completed epoch.", ""])
        if not data["trace_available"] and data["epochs"]:
            lines.extend(
                [
                    "This snapshot preserves previously observed epochs; the live trace is temporarily unavailable.",
                    "",
                ]
            )
        if data["stop_reason"]:
            lines.extend(["Stop reason: `" + data["stop_reason"] + "`.", ""])
        for note in data["notes"]:
            lines.extend(["Trace note: " + note.replace("\n", " "), ""])
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--name", default="propositions_v41_full_after_indicative")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--trace", action="append", default=[], metavar="STAGE=PATH")
    args = parser.parse_args()
    if Path(args.name).name != args.name:
        parser.error("Run name must be one directory name")
    overrides = {}
    for item in args.trace:
        stage, separator, path = item.partition("=")
        if not separator or stage not in STAGES:
            parser.error("Trace overrides require a known training stage and path")
        overrides[stage] = Path(path)
    args.output.mkdir(parents=True, exist_ok=True)
    previous, _ = read_object(args.output / "epoch_scores.json")
    report = collect(args.root, args.name, previous, overrides)
    atomic_json(args.output / "epoch_scores.json", report)
    temporary = args.output / "epoch_scores.md.tmp"
    temporary.write_text(markdown(report))
    os.replace(temporary, args.output / "epoch_scores.md")
    print(
        json.dumps(
            {
                "status": report["run_status"],
                "current_stage": report["current_stage"],
                "epochs": {
                    stage: data["completed_epoch"]
                    for stage, data in report["stages"].items()
                },
            }
        )
    )


if __name__ == "__main__":
    main()
