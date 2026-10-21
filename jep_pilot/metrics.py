"""Recompute comparison metrics in VIPER's independent metric worker."""

import json

import numpy as np
from scipy.stats import spearmanr
from viper.config import MetricConfig
from viper.metrics import MetricContext, metric


@metric(metric_id="training_mse", mode="stateless")
def training_mse(_context: MetricContext[MetricConfig], value: float) -> float:
    """Record the observed pair-rating error during optimization."""
    return value


@metric(metric_id="evaluation_mse", mode="stateless")
def evaluation_mse(context: MetricContext[MetricConfig]) -> float:
    """Recompute MSE from the saved prediction artifact."""
    rows = json.loads(context.artifacts["predictions"].read_text())
    return float(np.mean([(r["prediction"] - r["target"]) ** 2 for r in rows]))


@metric(metric_id="evaluation_spearman", mode="stateless")
def evaluation_spearman(context: MetricContext[MetricConfig]) -> float:
    """Recompute rank correlation from the saved prediction artifact."""
    rows = json.loads(context.artifacts["predictions"].read_text())
    value = float(
        spearmanr(
            [r["prediction"] for r in rows], [r["target"] for r in rows]
        ).statistic
    )
    return value if np.isfinite(value) else 0.0
