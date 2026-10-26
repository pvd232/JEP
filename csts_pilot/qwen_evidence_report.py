"""Report the locally verified Qwen comparison without waiting for cloud storage."""

from pathlib import Path
from typing import Any

from csts_pilot.baseline_report import same_comparisons
from csts_pilot.convergence import file_sha256, write_json
from csts_pilot.convergence_analysis import metrics, paired_intervals
from jep_pilot.loaders import load_json


def build_report(root: Path, directory: Path) -> dict[str, Any]:
    """Check the exact cohort and independently recompute the paired gain."""
    summary = load_json(directory / "summary.json")
    selection = load_json(directory / "selection.json")
    if (
        summary["status"] != "complete"
        or selection["status"] != "checkpoints_frozen"
        or file_sha256(directory / "selection.json") != summary["selection_sha256"]
    ):
        raise ValueError("Only a completed, frozen comparison can be reported.")
    predictions = {
        arm: load_json(directory / f"{arm}_predictions.json")
        for arm in ("ratings", "evidence")
    }
    same_comparisons(predictions)
    expected = summary["settings"]["splits"]["test"]
    if any(
        len(rows) != expected["rows"]
        or len({r["group_id"] for r in rows}) != expected["groups"]
        for rows in predictions.values()
    ):
        raise ValueError("Incomplete test cohort.")
    scores = {arm: metrics(rows) for arm, rows in predictions.items()}
    for arm, score in scores.items():
        if abs(score["spearman"] - summary["live_scores"][arm]["spearman"]) > 1e-12:
            raise ValueError(
                "Independent score disagrees with native prediction capture."
            )
    result = {
        "training_traces": {
            arm: {
                phase: load_json(directory / f"{arm}_{phase}_trace.json")
                for phase in ("pretrain", "ratings")
            }
            for arm in ("ratings", "evidence")
        },
        "source_commit": summary["source_commit"],
        "scores": scores,
        "paired_intervals": paired_intervals(
            predictions,
            draws=summary["settings"]["bootstrap_draws"],
            seed=summary["settings"]["bootstrap_seed"],
            contrasts={"evidence_minus_ratings": ("evidence", "ratings")},
        ),
        "selection": selection,
        "preparation": summary["preparation"],
        "runs": summary["runs"],
        "gpu_stage_seconds": summary["gpu_stage_seconds"],
        "scope": "One seed on the existing examined C-STS split; teacher-checked evidence; no Spanish transfer claim.",
        "publication": "asynchronous",
    }
    output = root / "training_outputs"
    output.mkdir(exist_ok=True)
    write_json(output / "csts_qwen_evidence_results.json", result)
    lines = [
        "# Qwen evidence pretraining followed by rating training",
        "",
        "| Sequence | Test Spearman | MSE, 0–1 |",
        "|---|---:|---:|",
    ]
    for arm, label in (
        ("ratings", "Ratings → ratings"),
        ("evidence", "Evidence → ratings"),
    ):
        lines.append(
            f"| {label} | {scores[arm]['spearman']:.6f} | {scores[arm]['mse_0_1']:.6f} |"
        )
    lines += [
        "",
        "Both arms use two fixed first-phase epochs, then the same constant-rate rating training with patience five and a 24-epoch ceiling. Updates and comparison exposure are matched in phase A; evidence training processes additional answer tokens. Both selected checkpoints were frozen before test scoring.",
        "",
        "The JSON contains the paired source-group bootstrap interval. It does not measure training-seed variation. Cloud publication runs separately.",
        "",
    ]
    (output / "csts_qwen_evidence_report.md").write_text("\n".join(lines))
    return result
