"""Fit validation calibration and quantify paired test-set uncertainty."""

import hashlib
from collections import defaultdict
from typing import Any

import numpy as np
from scipy.stats import rankdata


def affine_fit(scores: np.ndarray, targets: np.ndarray) -> dict[str, Any]:
    """Fit a positive slope and offset, falling back to the identity map."""
    x, y = np.asarray(scores, dtype=float), np.asarray(targets, dtype=float)
    if x.shape != y.shape or x.size < 2 or not np.isfinite([x, y]).all():
        raise ValueError("Calibration requires aligned finite scores and targets.")
    centered = x - x.mean()
    variance = float(centered @ centered)
    slope = float(centered @ (y - y.mean()) / variance) if variance > 0 else 0.0
    if slope <= 0:
        return {"a": 1.0, "c": 0.0, "identity_fallback": True}
    return {
        "a": slope,
        "c": float(y.mean() - slope * x.mean()),
        "identity_fallback": False,
    }


def calibration(rows: list[dict[str, Any]]) -> dict[str, Any]:
    """Estimate five-fold validation error with whole caption groups held out."""
    groups = sorted(
        {r["group_id"] for r in rows},
        key=lambda g: hashlib.sha256(("calibration-61021:" + g).encode()).hexdigest(),
    )
    if len(groups) < 5:
        raise ValueError("Five calibration folds require at least five caption groups.")
    assignment = {group: i % 5 for i, group in enumerate(groups)}
    folds = np.array([assignment[r["group_id"]] for r in rows])
    x = np.array([r["prediction"] for r in rows])
    y = np.array([r["target"] for r in rows])
    held_out = np.empty_like(x)
    coefficients = []
    for fold in range(5):
        keep = folds != fold
        fitted = affine_fit(x[keep], y[keep])
        held_out[~keep] = fitted["a"] * x[~keep] + fitted["c"]
        coefficients.append(fitted)
    return {
        **affine_fit(x, y),
        "validation_oof_mse_0_1": float(np.mean((held_out - y) ** 2)),
        "fold_coefficients": coefficients,
        "group_folds": assignment,
        "fit_split": "validation",
    }


def correlation(x: np.ndarray, y: np.ndarray) -> float:
    """Compute Spearman from average ranks independently of the metric worker."""
    rx, ry = rankdata(x), rankdata(y)
    if np.ptp(rx) == 0 or np.ptp(ry) == 0:
        raise ValueError("Spearman requires variation in predictions and targets.")
    return float(np.corrcoef(rx, ry)[0, 1])


def metrics(rows: list[dict[str, Any]], field: str = "prediction") -> dict[str, Any]:
    """Recompute raw score errors, ranking and conditional ordering."""
    x = np.array([r[field] for r in rows], dtype=float)
    y = np.array([r["target"] for r in rows], dtype=float)
    if not len(rows) or not np.isfinite([x, y]).all():
        raise ValueError("Metrics require finite, nonempty predictions.")
    pairs: dict[str, list[int]] = defaultdict(list)
    for i, row in enumerate(rows):
        pairs[row["pair_id"]].append(i)
    ordering = []
    for members in pairs.values():
        for j, a in enumerate(members):
            for b in members[j + 1 :]:
                if rows[a]["condition"] == rows[b]["condition"] or y[a] == y[b]:
                    continue
                difference = x[a] - x[b]
                ordering.append(
                    0.5
                    if abs(difference) < 1e-7
                    else float(difference * (y[a] - y[b]) > 0)
                )
    mse = float(np.mean((x - y) ** 2))
    return {
        "n": len(rows),
        "spearman": correlation(x, y),
        "mse_0_1": mse,
        "mse_1_5": 16 * mse,
        "prediction_mean": float(x.mean()),
        "prediction_std": float(x.std()),
        "target_mean": float(y.mean()),
        "target_std": float(y.std()),
        "score_min": float(x.min()),
        "score_max": float(x.max()),
        "condition_ordering_accuracy": float(np.mean(ordering)) if ordering else None,
        "condition_ordering_comparisons": len(ordering),
    }


def paired_intervals(
    candidates: dict[str, list[dict[str, Any]]], draws: int = 2000, seed: int = 61021
) -> dict[str, Any]:
    """Reuse each component bootstrap sample across all four frozen candidates."""
    names = list(candidates)
    reference = candidates[names[0]]
    identity = [(r["row_id"], r["target"], r["group_id"]) for r in reference]
    if len({r[0] for r in identity}) != len(identity):
        raise ValueError("Repeated test row identities.")
    for rows in candidates.values():
        if [(r["row_id"], r["target"], r["group_id"]) for r in rows] != identity:
            raise ValueError(
                "Test row IDs, targets or groups differ across candidates."
            )
    groups: dict[str, list[int]] = defaultdict(list)
    for i, row in enumerate(reference):
        groups[row["group_id"]].append(i)
    members = [np.array(groups[g]) for g in sorted(groups)]
    target = np.array([r["target"] for r in reference])
    predictions = {
        name: np.array([r["prediction"] for r in candidates[name]]) for name in names
    }
    contrasts = {
        "pearson_full_minus_mse_full": ("pearson_full", "mse_full"),
        "mse_full_minus_prefix": ("mse_full", "mse_prefix"),
        "pearson_full_minus_prefix": ("pearson_full", "pearson_prefix"),
    }
    samples: dict[str, list[list[float]]] = {key: [] for key in contrasts}
    rng = np.random.default_rng(seed)
    for _ in range(draws):
        indices = np.concatenate(
            [members[i] for i in rng.integers(len(members), size=len(members))]
        )
        y = target[indices]
        scores = {
            name: (correlation(x[indices], y), float(np.mean((x[indices] - y) ** 2)))
            for name, x in predictions.items()
        }
        for key, (a, b) in contrasts.items():
            samples[key].append([scores[a][i] - scores[b][i] for i in (0, 1)])
    full = {name: metrics(rows) for name, rows in candidates.items()}
    return {
        "draws": draws,
        "seed": seed,
        "groups": len(members),
        "unit": "connected source-caption component",
        "scope": "Test-sample uncertainty conditional on seed 7.",
        "contrasts": {
            key: {
                metric: {
                    "difference": full[a][metric] - full[b][metric],
                    "ci95": np.percentile(
                        np.array(samples[key])[:, i], [2.5, 97.5]
                    ).tolist(),
                }
                for i, metric in enumerate(("spearman", "mse_0_1"))
            }
            for key, (a, b) in contrasts.items()
        },
    }
