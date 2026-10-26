"""Independently replay selected projections and score their exported predictions."""

import math
from statistics import mean, stdev
from typing import Any

import torch
from pydantic import Field
from scipy.stats import spearmanr
from viper.config import EvalConfig, MetricConfig
from viper.metrics import MetricContext, metric
from viper.stages import StageContext, eval

from csts_pilot.codebook import (
    check_disjoint,
    representations,
    restore_model,
    scored_rows,
)
from csts_pilot.convergence import file_sha256, write_json
from csts_pilot.diagnostics import summarize
from csts_pilot.iterative_codebook import ARMS
from jep_pilot.loaders import load_json, load_model


class ReplayConfig(EvalConfig):
    """Bind development replay to exact immutable model and cache bytes."""

    models_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    training_cache_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    validation_cache_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")


def paired_summary(predictions: dict[str, Any]) -> dict[str, Any]:
    """Compute paired selected-development gains from frozen prediction arrays."""
    y = [row["target"] for row in predictions["rows"]]
    gains = {}
    if not predictions["seeds"]:
        raise ValueError("Paired comparison requires declared training seeds.")
    for seed in predictions["seeds"]:
        correlations = []
        for arm in ARMS:
            values = predictions["scores"][f"{seed}:{arm}"]
            if len(values) != len(y) or not all(
                math.isfinite(value) for value in values
            ):
                raise ValueError(
                    "Predictions must cover the exact finite development cohort."
                )
            correlations.append(float(spearmanr(y, values).statistic))
        gain = correlations[1] - correlations[0]
        if not math.isfinite(gain):
            raise ValueError("The paired correlation gain is undefined.")
        gains[str(seed)] = gain
    return {
        "paired_seed_gains": gains,
        "mean_seed_spearman_gain": mean(gains.values()),
        "seed_gain_sample_sd": stdev(gains.values()) if len(gains) > 1 else None,
        "scope": "Selected validation checkpoints; development mechanism screen without selection correction or fresh-test inference.",
    }


@metric(metric_id="iterative_codebook_mean_spearman_gain", mode="stateless")
def mean_spearman_gain(context: MetricContext[MetricConfig]) -> float:
    """Recompute the declared primary metric from the sealed prediction artifact."""
    return paired_summary(load_json(context.artifacts["predictions"]))[
        "mean_seed_spearman_gain"
    ]


@eval(config=ReplayConfig)
def evaluate_iterative_codebooks(context: StageContext[ReplayConfig]) -> None:
    """Replay selected models unmasked once; no optimization or model selection."""
    torch.set_num_threads(1)
    config = context.config
    for name, expected in (
        ("model", config.models_sha256),
        ("training", config.training_cache_sha256),
        ("validation", config.validation_cache_sha256),
    ):
        if file_sha256(context.inputs[name]) != expected:
            raise ValueError(f"Changed evaluation input: {name}.")
    bundle = load_model(context.inputs["model"])
    caches = {
        name: load_model(context.inputs[name]) for name in ("training", "validation")
    }
    for name in caches:
        if bundle["config"][name + "_cache_sha256"] != getattr(
            config, name + "_cache_sha256"
        ):
            raise ValueError("The frozen model refers to different fitting caches.")
    check_disjoint(*caches.values())
    validation = caches["validation"]
    if load_json(context.inputs["test"]) != validation["rows"]:
        raise ValueError("Published evaluation rows differ from the development cache.")
    if load_json(context.inputs["holdout"]) != list(range(len(validation["rows"]))):
        raise ValueError("Evaluation indices differ from the complete frozen cohort.")
    seeds = bundle["config"]["seeds"]
    scores, metrics = {}, {}
    if set(bundle["models"]) != {f"{seed}:{arm}" for seed in seeds for arm in ARMS}:
        raise ValueError(
            "Frozen models differ from the predeclared paired arms and seeds."
        )
    for seed in seeds:
        for arm in ARMS:
            key = f"{seed}:{arm}"
            saved = bundle["models"][key]
            dev = scored_rows(
                validation, representations(restore_model(saved), validation)
            )
            measured = summarize(dev)
            if measured != saved["validation"]:
                raise ValueError(
                    "Selected checkpoint does not reproduce its validation scores."
                )
            scores[key] = [row["prediction"] for row in dev]
            metrics[key] = {
                "selected_epoch": saved["epoch"],
                "validation": measured,
                "codes_training": saved["codes_training"],
                "codes_validation": saved["codes_validation"],
            }
    predictions = {
        "rows": validation["rows"],
        "seeds": seeds,
        "scores": scores,
        "evaluation_split": "validation",
    }
    write_json(context.outputs["predictions"], predictions)
    write_json(
        context.outputs["report"],
        {
            "status": "complete",
            "models_sha256": config.models_sha256,
            "config": bundle["config"],
            "evaluation_split": "validation",
            "metrics": metrics,
            "paired": paired_summary(predictions),
            "test_accessed": False,
            "backbone_updates": 0,
        },
    )
    # Artifact-recomputed metrics have no in-stage context.metrics recorder.
