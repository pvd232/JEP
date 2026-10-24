"""Report Tranche 3 scores and paired contrasts without waiting for publication."""

import argparse
from pathlib import Path
from typing import Any

from csts_pilot.baseline_report import same_comparisons
from csts_pilot.convergence import file_sha256, write_json
from csts_pilot.convergence_analysis import metrics, paired_intervals
from jep_pilot.loaders import load_json


def build_report(root: Path, directory: Path) -> dict[str, Any]:
    """Independently remeasure the completed, prospectively frozen comparison."""
    summary = load_json(directory / "summary.json")
    selection = load_json(directory / "selection.json")
    if summary["status"] != "complete" or selection["status"] != "checkpoints_frozen":
        raise ValueError("Only completed, frozen comparisons can be reported.")
    if file_sha256(directory / "selection.json") != summary["selection_sha256"]:
        raise ValueError("Changed frozen selection.")
    candidates = {
        arm: load_json(directory / f"{arm}_predictions.json")
        for arm in ("ratings", "evidence", "shuffled")
    }
    same_comparisons(candidates)
    expected = summary["settings"]["splits"]["test"]
    rows = candidates["ratings"]
    if (
        len(rows) != expected["rows"]
        or len({r["group_id"] for r in rows}) != expected["groups"]
    ):
        raise ValueError("Incomplete test cohort.")
    scores = {arm: metrics(rows) for arm, rows in candidates.items()}
    for arm, score in scores.items():
        if abs(score["spearman"] - summary["live_scores"][arm]["spearman"]) > 1e-12:
            raise ValueError("Independent ranking disagrees with the native result.")
    result = {
        "source_commit": summary["source_commit"],
        "evaluation_source_commit": summary.get(
            "evaluation_source_commit", summary["source_commit"]
        ),
        "scores": scores,
        "paired_intervals": paired_intervals(
            candidates,
            draws=summary["settings"]["bootstrap_draws"],
            seed=summary["settings"]["bootstrap_seed"],
            contrasts={
                "evidence_minus_ratings": ("evidence", "ratings"),
                "evidence_minus_shuffled": ("evidence", "shuffled"),
            },
        ),
        "preparation": summary["preparation"],
        "checkpoints": selection["candidates"],
        "gpu_stage_seconds": summary["gpu_stage_seconds"],
        "native_runs": summary["runs"],
        "scope": "Seed-7 follow-up on an already examined benchmark; teacher-checked evidence, not expert validation.",
        "publication": "Local native measurements are complete; cloud publication is asynchronous.",
    }
    output = root / "training_outputs"
    write_json(output / "csts_tranche3_results.json", result)
    lines = [
        "# Tranche 3: matched evidence-supervision controls",
        "",
        (
            "All three rating checkpoints were selected with validation and frozen before test scoring. "
            "Native CPU EVAL and independent metric workers verified the saved predictions. "
            "Cloud publication runs separately."
        ),
        "",
        "| Training sequence | Test Spearman | MSE, 0–1 | Condition ordering |",
        "|---|---:|---:|---:|",
    ]
    names = {
        "ratings": "Ratings → ratings",
        "evidence": "Aligned evidence → ratings",
        "shuffled": "Shuffled evidence → ratings",
    }
    for arm, score in scores.items():
        lines.append(
            f"| {names[arm]} | {score['spearman']:.6f} | {score['mse_0_1']:.6f} | {score['condition_ordering_accuracy']:.2%} |"
        )
    lines += [
        "",
        (
            "The first phase uses the same comparison subset and answer mask. "
            "Every arm completes six epochs and transitions from its terminal weights. "
            "The rating phases share the original 24-epoch schedule and lower constant-rate continuation, "
            "with a 40-epoch ceiling and patience five in the continuation."
        ),
        "",
        (
            "The JSON report includes both predeclared paired source-group bootstrap contrasts, "
            "retained evidence coverage, selected epochs, actual updates and native references. "
            "These are exploratory one-seed results. Independent Spanish JEP confirmation remains open."
        ),
        "",
    ]
    (output / "csts_tranche3_report.md").write_text("\n".join(lines))
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    args = parser.parse_args()
    build_report(args.root, args.directory)


if __name__ == "__main__":
    main()
