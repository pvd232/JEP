"""Report frozen proposition-supervision experiments using CPU-only analysis."""

import hashlib
import json
import math
import re
from pathlib import Path
from typing import Any

import numpy as np
from scipy.stats import spearmanr

from csts_pilot.baseline_report import same_comparisons
from csts_pilot.convergence_analysis import calibration

ARMS = ("ratings", "evidence")
COHORTS_PATH = "datasets/csts-proposition-evidence-report-cohorts.json"
APPEARANCE = "appearance-and-sensory-attributes"


def read_json(path: Path) -> Any:
    """Load exact report inputs."""
    return json.loads(path.read_text())


def file_sha256(path: Path) -> str:
    """Hash checkpoint files in bounded memory."""
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def write_json(path: Path, value: Any) -> None:
    """Publish finite analysis results."""
    path.write_text(json.dumps(value, indent=2, allow_nan=False) + "\n")


def aligned_predictions(
    candidates: dict[str, list[dict[str, Any]]], source: list[dict[str, Any]]
) -> None:
    """Require identical ordered sources, labels and groups for every arm."""
    same_comparisons({"source": source, **candidates})
    for rows in candidates.values():
        if any(
            not math.isfinite(float(row["prediction"]))
            or abs(float(row["target"]) - (float(row["rating"]) - 1) / 4) > 1e-12
            for row in rows
        ):
            raise ValueError("Prediction values or normalized ratings are invalid.")


def score_rows(rows: list[dict[str, Any]], fitted: dict[str, Any]) -> dict[str, Any]:
    """Keep rank scores raw and compute rating errors with validation calibration."""
    if not rows:
        return {"n": 0, "groups": 0, "spearman": None}
    raw = np.array([r["prediction"] for r in rows], dtype=float)
    target = np.array([r["target"] for r in rows], dtype=float)
    error = 4 * (raw - target)
    calibrated = fitted["a"] * raw + fitted["c"]
    adjusted_error = 4 * (calibrated - target)
    rho = (
        float(spearmanr(raw, target).statistic)
        if np.ptp(raw) > 0 and np.ptp(target) > 0
        else None
    )
    return {
        "n": len(rows),
        "groups": len({r["group_id"] for r in rows}),
        "spearman": rho,
        "mse_0_1": float(np.mean((raw - target) ** 2)),
        "mae_1_5": float(np.mean(np.abs(error))),
        "rmse_1_5": float(np.sqrt(np.mean(error**2))),
        "calibrated_mae_1_5": float(np.mean(np.abs(adjusted_error))),
        "calibrated_rmse_1_5": float(np.sqrt(np.mean(adjusted_error**2))),
        "calibrated_bias_1_5": float(np.mean(adjusted_error)),
        "calibrated_prediction_range_1_5": [
            float(1 + 4 * calibrated.min()),
            float(1 + 4 * calibrated.max()),
        ],
    }


def fit_validation_calibration(rows: list[dict[str, Any]]) -> dict[str, Any]:
    """Add rating-scale group-held-out calibration errors to the existing fit."""
    fitted = calibration(rows)
    held_out = np.array(
        [
            fitted["fold_coefficients"][fitted["group_folds"][row["group_id"]]]["a"]
            * row["prediction"]
            + fitted["fold_coefficients"][fitted["group_folds"][row["group_id"]]]["c"]
            for row in rows
        ]
    )
    error = 4 * (held_out - np.array([row["target"] for row in rows]))
    fitted["validation_oof_mae_1_5"] = float(np.abs(error).mean())
    fitted["validation_oof_rmse_1_5"] = float(np.sqrt(np.mean(error**2)))
    return fitted


def bootstrap_differences(
    candidates: dict[str, list[dict[str, Any]]],
    fitted: dict[str, dict[str, Any]],
    draws: int,
    seed: int,
) -> dict[str, Any]:
    """Resample source components with paired arms and fixed calibration."""
    if set(candidates) != set(ARMS) or draws < 1:
        raise ValueError("Require both arms and a positive bootstrap draw count.")
    same_comparisons(candidates)
    reference = candidates["ratings"]
    groups = sorted({r["group_id"] for r in reference})
    if not reference:
        return {"draws": draws, "groups": 0, "contrasts": {}, "status": "empty"}
    members = [
        np.array([i for i, row in enumerate(reference) if row["group_id"] == group])
        for group in groups
    ]
    fields = ("spearman", "mse_0_1", "calibrated_mae_1_5", "calibrated_rmse_1_5")
    samples: dict[str, list[float]] = {field: [] for field in fields}
    rng = np.random.default_rng(seed)
    for _ in range(draws):
        indices = np.concatenate(
            [members[i] for i in rng.integers(0, len(groups), len(groups))]
        )
        scores = {
            arm: score_rows([rows[i] for i in indices], fitted[arm])
            for arm, rows in candidates.items()
        }
        for field in fields:
            a, b = scores["evidence"][field], scores["ratings"][field]
            if a is not None and b is not None:
                samples[field].append(a - b)
    full = {arm: score_rows(rows, fitted[arm]) for arm, rows in candidates.items()}
    return {
        "draws": draws,
        "seed": seed,
        "groups": len(groups),
        "unit": "connected source-caption component",
        "calibration": "Fixed coefficients fitted on selected validation predictions.",
        "contrast": "evidence_minus_ratings",
        "contrasts": {
            field: {
                "difference": full["evidence"][field] - full["ratings"][field]
                if full["evidence"][field] is not None
                and full["ratings"][field] is not None
                else None,
                "ci95": np.percentile(samples[field], [2.5, 97.5]).tolist()
                if samples[field]
                else None,
                "defined_draws": len(samples[field]),
            }
            for field in fields
        },
    }


def cohort_rows(
    candidates: dict[str, list[dict[str, Any]]], spec: dict[str, Any], split: str
) -> dict[str, dict[str, list[dict[str, Any]]]]:
    """Use frozen raw-condition families and an explicit lexical colour rule."""
    mapping = spec["splits"][split]["condition_families"]
    colour = re.compile(spec["colour_regex"], re.IGNORECASE)
    return {
        "all": candidates,
        "appearance": {
            arm: [r for r in rows if mapping.get(r["condition"]) == APPEARANCE]
            for arm, rows in candidates.items()
        },
        "colour": {
            arm: [r for r in rows if colour.search(r["condition"])]
            for arm, rows in candidates.items()
        },
    }


def verified_source(root: Path, expected: dict[str, Any]) -> list[dict[str, Any]]:
    """Bind report cohorts to the same immutable split files used by training."""
    path = root / expected["path"]
    if file_sha256(path) != expected["sha256"]:
        raise ValueError("Report source split bytes changed.")
    rows = read_json(path)
    if len(rows) != expected["rows"] or len({r["group_id"] for r in rows}) != expected["groups"]:
        raise ValueError("Report source split coverage changed.")
    return rows


def verify_checkpoint(directory: Path, arm: str, candidate: dict[str, Any]) -> None:
    """Verify the selected model locally or through its native artifact location."""
    local = directory / f"{arm}_selected_model.pt"
    native = Path(candidate["run"]["path"]).parent / "artifacts/train/model/model.pt"
    path = local if local.exists() else native
    if not path.exists() or file_sha256(path) != candidate["sha256"]:
        raise ValueError("The selected checkpoint bytes differ or are unavailable.")


def build_report(root: Path, directory: Path) -> dict[str, Any]:
    """Check frozen selection and compute paired validation/test/cohort reports."""
    summary = read_json(directory / "summary.json")
    selection = read_json(directory / "selection.json")
    if (
        summary["status"] != "complete"
        or selection["status"] != "checkpoints_frozen"
        or selection.get("test_scores_used_for_selection") is not False
        or file_sha256(directory / "selection.json") != summary["selection_sha256"]
        or set(selection["candidates"]) != set(ARMS)
    ):
        raise ValueError("Report requires the completed, frozen two-arm selection.")
    settings = summary["settings"]
    taxonomy_setting = settings.get("report_cohorts", {"path": COHORTS_PATH})
    taxonomy_path = root / taxonomy_setting["path"]
    if taxonomy_setting.get("sha256") and file_sha256(taxonomy_path) != taxonomy_setting["sha256"]:
        raise ValueError("Frozen cohort definitions changed.")
    taxonomy = read_json(taxonomy_path)
    predictions = {
        split: {
            arm: read_json(directory / f"{arm}{suffix}")
            for arm in ARMS
        }
        for split, suffix in (
            ("validation", "_validation_predictions.json"),
            ("test", "_predictions.json"),
        )
    }
    sources = {
        split: verified_source(root, settings["splits"][split])
        for split in predictions
    }
    for split, candidates in predictions.items():
        aligned_predictions(candidates, sources[split])
    if {r["group_id"] for r in sources["validation"]} & {r["group_id"] for r in sources["test"]}:
        raise ValueError("Validation and test source groups overlap.")
    traces = {
        arm: {
            phase: read_json(directory / f"{arm}_{phase}_trace.json")
            for phase in ("pretrain", "ratings")
        }
        for arm in ARMS
    }
    fitted = {}
    for arm in ARMS:
        candidate = selection["candidates"][arm]
        verify_checkpoint(directory, arm, candidate)
        if traces[arm]["ratings"]["selected"]["sha256"] != candidate["sha256"]:
            raise ValueError("Selected trace and checkpoint selection disagree.")
        validation = predictions["validation"][arm]
        fitted[arm] = fit_validation_calibration(validation)
        actual = score_rows(validation, fitted[arm])["spearman"]
        recorded = candidate["validation"]["spearman"]
        if actual is None or abs(actual - recorded) > 1e-12:
            raise ValueError("Selected validation predictions disagree with selection.")
        test_score = score_rows(predictions["test"][arm], fitted[arm])["spearman"]
        if test_score is None or abs(test_score - summary["live_scores"][arm]["spearman"]) > 1e-12:
            raise ValueError("Independent test ranking differs from native scoring.")
    cohorts = {}
    for split, values in predictions.items():
        cohorts[split] = {}
        for name, selected in cohort_rows(values, taxonomy, split).items():
            cohorts[split][name] = {
                "scores": {arm: score_rows(rows, fitted[arm]) for arm, rows in selected.items()},
                "paired_intervals": bootstrap_differences(
                    selected, fitted, settings["bootstrap_draws"], settings["bootstrap_seed"]
                ),
            }
    result = {
        "source_commit": summary["source_commit"],
        "selection_sha256": summary["selection_sha256"],
        "selection": selection,
        "preparation": summary["preparation"],
        "training_traces": traces,
        "calibration": fitted,
        "cohorts": cohorts,
        "cohort_definitions": {"path": taxonomy_setting["path"], "sha256": file_sha256(taxonomy_path), **taxonomy},
        "runs": summary["runs"],
        "gpu_stage_seconds": summary["gpu_stage_seconds"],
        "scope": {
            "training_seed": settings["training"]["seed"],
            "teacher_bank": "Existing partial source-only assistant-generated training bank, frozen before fitting.",
            "quality_review": "Model-assisted selected-sample fidelity review.",
            "uncertainty": "Paired source-component sampling conditional on this one training seed and frozen validation calibration.",
            "validation": "Current audit labels and fixed exclusions were used for checkpoint selection.",
            "test": "Tu human-reannotated test labels and source-caption text remain fixed.",
            "calibration": "Positive affine fit on selected validation predictions, identity fallback for a nonpositive slope; unclipped rating estimates.",
            "cohorts": "Descriptive appearance family and lexical colour subsets; exploratory subgroup uncertainty.",
        },
        "publication": "asynchronous",
    }
    output = root / "training_outputs"
    output.mkdir(exist_ok=True)
    write_json(output / "csts_proposition_evidence_results.json", result)
    lines = ["# Qwen proposition supervision followed by ratings", "", "| Split / cohort | n | Groups | Ratings Spearman | Proposition Spearman | Difference [95% CI] |", "|---|---:|---:|---:|---:|---|"]
    for split, split_cohorts in cohorts.items():
        for name, value in split_cohorts.items():
            a, b = value["scores"]["ratings"], value["scores"]["evidence"]
            difference = value["paired_intervals"]["contrasts"].get("spearman", {})
            interval = difference.get("ci95")
            formatted = f"{difference['difference']:+.6f} [{interval[0]:+.6f}, {interval[1]:+.6f}]" if interval else "undefined"
            fmt = lambda number: f"{number:.6f}" if number is not None else "undefined"
            lines.append(f"| {split} / {name} | {a['n']} | {a['groups']} | {fmt(a['spearman'])} | {fmt(b['spearman'])} | {formatted} |")
    lines += ["", "Both arms share first-phase comparison exposure, initialization and update counts. The proposition arm receives generation supervision from the frozen partial training bank. Both arms then train on the full ratings training partition with the same learning rate and validation patience. The selected checkpoints were frozen before test scoring.", "", "Rating errors use a separate positive affine calibration fitted on each arm's selected validation predictions. The JSON records raw and calibrated rating errors, group-held-out validation calibration error, exact cohort definitions and paired source-group intervals. Spearman uses the original scores and tie structure.", "", "This experiment uses one training seed. The teacher fidelity assessment was model assisted and sampled. Results describe the available training targets and the fixed C-STS partitions.", ""]
    (output / "csts_proposition_evidence_report.md").write_text("\n".join(lines))
    return result
