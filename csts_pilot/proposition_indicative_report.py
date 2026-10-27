"""Summarize a fixed short Qwen continuation on the current validation split."""

from pathlib import Path
from typing import Any

from csts_pilot.proposition_evidence_report import (
    ARMS,
    COHORTS_PATH,
    aligned_predictions,
    bootstrap_differences,
    cohort_rows,
    file_sha256,
    fit_validation_calibration,
    read_json,
    score_rows,
    verified_source,
    write_json,
)


def _number(value: float | None) -> str:
    """Keep undefined subgroup ranks explicit in the readable report."""
    return f"{value:.6f}" if value is not None else "undefined"


def _difference(value: dict[str, Any]) -> str:
    """Format a paired point estimate and its available interval."""
    estimate, interval = value.get("difference"), value.get("ci95")
    if estimate is None or interval is None:
        return "undefined"
    return f"{estimate:+.6f} [{interval[0]:+.6f}, {interval[1]:+.6f}]"


def build_indicative_report(root: Path, directory: Path) -> dict[str, Any]:
    """Check shared sources and report short-run validation changes from baseline.

    The input is ``directory/results.json`` with list-valued ``arms.ratings``,
    ``arms.evidence``, ``baseline``, plus ``protocol`` and ``traces``. Protocol
    binds ``validation`` to path/sha256/rows/groups and may bind report_cohorts.
    """
    input_path = directory / "results.json"
    raw = read_json(input_path)
    if set(raw["arms"]) != set(ARMS):
        raise ValueError("Indicative reporting requires ratings and evidence arms.")
    if not isinstance(raw["protocol"], dict) or not isinstance(raw["traces"], dict):
        raise TypeError("Protocol and training traces must be explicit objects.")
    protocol = raw["protocol"]
    source = verified_source(root, protocol["validation"])
    predictions = {"baseline": raw["baseline"], **raw["arms"]}
    if any(not isinstance(rows, list) for rows in predictions.values()):
        raise ValueError("All prediction inputs must be ordered comparison lists.")
    aligned_predictions(predictions, source)
    taxonomy_setting = protocol.get("report_cohorts", {"path": COHORTS_PATH})
    taxonomy_path = root / taxonomy_setting["path"]
    taxonomy_sha = file_sha256(taxonomy_path)
    if taxonomy_setting.get("sha256") and taxonomy_setting["sha256"] != taxonomy_sha:
        raise ValueError("Frozen indicative cohort definitions changed.")
    taxonomy = read_json(taxonomy_path)
    fitted = {
        arm: fit_validation_calibration(rows)
        for arm, rows in predictions.items()
    }
    draws = protocol.get("bootstrap_draws", 1000)
    seed = protocol.get("bootstrap_seed", 61027)
    if not isinstance(draws, int) or isinstance(draws, bool) or draws < 1:
        raise ValueError("The bootstrap draw count must be a positive integer.")
    cohorts = {}
    for name, selected in cohort_rows(predictions, taxonomy, "validation").items():
        scores = {arm: score_rows(rows, fitted[arm]) for arm, rows in selected.items()}
        contrasts = {}
        for label, left, right in (
            ("evidence_minus_ratings", "evidence", "ratings"),
            ("ratings_minus_baseline", "ratings", "baseline"),
            ("evidence_minus_baseline", "evidence", "baseline"),
        ):
            interval = bootstrap_differences(
                {"ratings": selected[right], "evidence": selected[left]},
                {"ratings": fitted[right], "evidence": fitted[left]},
                draws=draws,
                seed=seed,
            )
            interval["contrast"] = label
            contrasts[label] = interval
        cohorts[name] = {"scores": scores, "paired_intervals": contrasts}
    result = {
        "status": "early_validation_diagnostic_complete",
        "input_sha256": file_sha256(input_path),
        "report_code_sha256": file_sha256(Path(__file__)),
        "evaluation_split": "validation",
        "protocol": protocol,
        "training_traces": raw["traces"],
        "calibration": fitted,
        "cohorts": cohorts,
        "cohort_definitions": {
            "path": taxonomy_setting["path"],
            "sha256": taxonomy_sha,
            "colour_regex": taxonomy["colour_regex"],
            "validation": taxonomy["splits"]["validation"],
        },
        "scope": {
            "experiment": "Fixed short continuation from the selected Qwen adapter; early validation diagnostic.",
            "uncertainty": "Paired source-component sampling conditional on one training seed and fixed fitted validation calibration.",
            "errors": "Raw errors use the released target scale. Calibrated validation errors are in-sample; separate group-held-out calibration errors are also supplied.",
            "ranking": "Spearman uses raw predictions and their existing ties.",
            "cohorts": "Appearance and colour are exploratory descriptive validation subsets.",
            "held_out_test": "Held-out test scoring remains pending.",
            "full_comparison": "The full matched-budget comparison remains a separate queued experiment.",
        },
    }
    write_json(directory / "indicative_report.json", result)
    lines = [
        "# Qwen proposition supervision: early validation diagnostic",
        "",
        "This is a fixed short continuation from the selected Qwen adapter. The full matched-budget comparison is queued separately. The reported predictions use the current validation split.",
        "",
        "| Cohort | n | Groups | Baseline Spearman | Ratings continuation | Proposition continuation | Proposition − ratings [95% CI] |",
        "|---|---:|---:|---:|---:|---:|---|",
    ]
    for name, value in cohorts.items():
        scores = value["scores"]
        estimate = value["paired_intervals"]["evidence_minus_ratings"]["contrasts"].get("spearman", {})
        lines.append(
            f"| {name} | {scores['baseline']['n']} | {scores['baseline']['groups']} | "
            f"{_number(scores['baseline']['spearman'])} | "
            f"{_number(scores['ratings']['spearman'])} | "
            f"{_number(scores['evidence']['spearman'])} | {_difference(estimate)} |"
        )
    lines += [
        "",
        "| Cohort | Arm | Raw MAE, 1–5 | Raw RMSE, 1–5 | Calibrated MAE, 1–5 | Calibrated RMSE, 1–5 |",
        "|---|---|---:|---:|---:|---:|",
    ]
    for name, value in cohorts.items():
        for arm, score in value["scores"].items():
            if score["n"]:
                lines.append(
                    f"| {name} | {arm} | {score['mae_1_5']:.6f} | {score['rmse_1_5']:.6f} | "
                    f"{score['calibrated_mae_1_5']:.6f} | {score['calibrated_rmse_1_5']:.6f} |"
                )
    lines += [
        "",
        "The JSON includes both continuation changes from the unchanged baseline, paired source-group intervals, exact protocol and source identities, and five-fold group-held-out calibration errors. Calibrated scores in the table use coefficients fitted on the same overall validation predictions. Spearman uses raw scores. Sampling intervals are conditional on this one seed and fixed calibration. Appearance and colour results are exploratory.",
        "",
    ]
    (directory / "indicative_report.md").write_text("\n".join(lines))
    return result
