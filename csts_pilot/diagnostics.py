"""Evaluate ratings and score changes under different comparison conditions."""

from collections import defaultdict
from itertools import combinations
from typing import Any

import numpy as np
from scipy.stats import spearmanr


def summarize(rows: list[dict[str, Any]]) -> dict[str, Any]:
    """Measure calibration, ranking and condition differences on fixed predictions."""
    target = np.asarray([row["target"] for row in rows], dtype=float)
    prediction = np.asarray([row["prediction"] for row in rows], dtype=float)
    if not np.isfinite(prediction).all():
        raise ValueError("Predictions must be finite.")
    correlation = (
        float(spearmanr(target, prediction).statistic)
        if np.std(target) > 0 and np.std(prediction) > 0
        else None
    )
    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    by_rating: dict[float, list[float]] = defaultdict(list)
    for row in rows:
        groups[row["pair_id"]].append(row)
        by_rating[row["rating"]].append(row["prediction"])
    changes = []
    correct = ties = 0
    for pair in groups.values():
        for a, b in combinations(pair, 2):
            if a["condition"] == b["condition"] or a["target"] == b["target"]:
                continue
            difference = a["prediction"] - b["prediction"]
            expected = a["target"] - b["target"]
            changes.append((difference - expected) ** 2)
            ties += abs(difference) < 1e-7
            correct += difference * expected > 0 and abs(difference) >= 1e-7
    return {
        "n": len(rows),
        "mse_0_1": float(np.mean((prediction - target) ** 2)),
        "mse_1_5": float(16 * np.mean((prediction - target) ** 2)),
        "spearman": correlation,
        "prediction_mean": float(np.mean(prediction)),
        "target_mean": float(np.mean(target)),
        "prediction_std": float(np.std(prediction)),
        "target_std": float(np.std(target)),
        "mean_prediction_by_rating": {
            str(rating): {"n": len(values), "mean": float(np.mean(values))}
            for rating, values in sorted(by_rating.items())
        },
        "condition_changes": {
            "n": len(changes),
            "correct": int(correct),
            "ties": int(ties),
            "accuracy_ties_half": (correct + 0.5 * ties) / len(changes)
            if changes
            else None,
            "difference_mse": float(np.mean(changes)) if changes else None,
            "unit": "Within-pair comparisons. These reuse captions and are dependent.",
        },
    }
