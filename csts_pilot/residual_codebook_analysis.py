"""Replay full-dimensional residual models and independently score paired gains."""

import math
from statistics import mean, stdev
from typing import Any

import torch
from scipy.stats import spearmanr
from viper.authoring import stage
from viper.config import MetricConfig
from viper.metrics import (
    FloatComparator,
    MetricContext,
    MetricDependency,
    measure,
    metric,
)
from viper.metrics import max as maximize
from viper.outputs import EvalOutputs, output
from viper.stages import StageContext, eval

from csts_pilot.codebook import check_disjoint, representations, scored_rows
from csts_pilot.codebook_run import evaluation_inputs
from csts_pilot.convergence import file_sha256, write_json
from csts_pilot.diagnostics import summarize
from csts_pilot.iterative_codebook_analysis import ReplayConfig
from csts_pilot.residual_codebook import ARMS, fixed_recall_metrics, restore_residual
from jep_pilot.loaders import load_json, load_model


def paired_summary(predictions: dict[str, Any]) -> dict[str, Any]:
    """Recompute every gate from exported scores on the identical development rows."""
    rows = predictions["rows"]
    targets = [row["target"] for row in rows]

    def correlation(values: list[float]) -> float:
        if len(values) != len(rows) or not all(math.isfinite(x) for x in values):
            raise ValueError("Predictions must cover the exact finite cohort.")
        result = float(spearmanr(targets, values).statistic)
        if not math.isfinite(result):
            raise ValueError("Undefined development correlation.")
        return result

    seeds = predictions["seeds"]
    if not seeds or len(set(seeds)) != len(seeds):
        raise ValueError("Require distinct paired seeds.")
    baseline = correlation(predictions["baseline"])
    expected_keys = {f"{seed}:{arm}" for seed in seeds for arm in ARMS}
    if (
        set(predictions["scores"]) != expected_keys
        or set(predictions["group_scores"]) != expected_keys
    ):
        raise ValueError("Incomplete paired arms.")
    correlations, groups, gains, parent_gains, fpr_gains = {}, {}, {}, {}, {}
    for seed in seeds:
        for arm in ARMS:
            key = f"{seed}:{arm}"
            correlations[key] = correlation(predictions["scores"][key])
            group_scores = predictions["group_scores"][key]
            if len(group_scores) != len(rows) or not all(
                math.isfinite(x) for x in group_scores
            ):
                raise ValueError(
                    "Group predictions must cover the exact finite cohort."
                )
            groups[key] = fixed_recall_metrics(
                [
                    dict(row, prediction=score)
                    for row, score in zip(rows, group_scores, strict=True)
                ]
            )
        control, candidate = (f"{seed}:{arm}" for arm in ARMS)
        gains[str(seed)] = correlations[candidate] - correlations[control]
        parent_gains[str(seed)] = correlations[candidate] - baseline
        fpr_gains[str(seed)] = (
            groups[candidate]["false_positive_rate"]
            - groups[control]["false_positive_rate"]
        )
    gain, parent_gain, fpr_gain = (
        mean(gains.values()),
        mean(parent_gains.values()),
        mean(fpr_gains.values()),
    )
    return {
        "baseline_spearman": baseline,
        "spearman": correlations,
        "group_metrics": groups,
        "paired_seed_gains": gains,
        "mean_seed_spearman_gain": gain,
        "seed_gain_sample_sd": stdev(gains.values()) if len(gains) > 1 else None,
        "candidate_minus_baseline": parent_gains,
        "mean_candidate_minus_baseline": parent_gain,
        "paired_group_fpr_gains": fpr_gains,
        "mean_group_fpr_gain": fpr_gain,
        "eligible": gain >= 0.005 and parent_gain >= 0.005 and fpr_gain < 0,
        "scope": "Development-selected mechanism screen; three paired seeds, exact 90% positive coverage through fractional boundary ties.",
    }


@metric(metric_id="residual_codebook_mean_spearman_gain", mode="stateless")
def mean_spearman_gain(context: MetricContext[MetricConfig]) -> float:
    """Compute the primary metric from sealed predictions in a separate worker."""
    return paired_summary(load_json(context.artifacts["predictions"]))[
        "mean_seed_spearman_gain"
    ]


@eval(config=ReplayConfig)
def evaluate_residual_codebooks(context: StageContext[ReplayConfig]) -> None:
    """Restore each selected state and recompute its continuous and group scores."""
    torch.set_num_threads(1)
    config = context.config
    for name, expected in (
        ("model", config.models_sha256),
        ("training", config.training_cache_sha256),
        ("validation", config.validation_cache_sha256),
    ):
        if file_sha256(context.inputs[name]) != expected:
            raise ValueError(f"Changed replay input: {name}.")
    bundle = load_model(context.inputs["model"])
    caches = {
        name: load_model(context.inputs[name]) for name in ("training", "validation")
    }
    for name in caches:
        if bundle["config"][name + "_cache_sha256"] != getattr(
            config, name + "_cache_sha256"
        ):
            raise ValueError("Model was fitted with different caches.")
    check_disjoint(*caches.values())
    validation = caches["validation"]
    if load_json(context.inputs["test"]) != validation["rows"] or load_json(
        context.inputs["holdout"]
    ) != list(range(len(validation["rows"]))):
        raise ValueError("Published development rows or indices changed.")
    seeds = bundle["config"]["seeds"]
    if set(bundle["models"]) != {f"{seed}:{arm}" for seed in seeds for arm in ARMS}:
        raise ValueError("Frozen paired models are incomplete.")
    baseline_rows = scored_rows(
        validation, torch.nn.functional.normalize(validation["vectors"], dim=1)
    )
    scores, group_scores, metrics = {}, {}, {}
    for key, saved in bundle["models"].items():
        model = restore_residual(saved)
        vectors = representations(model, validation)
        dev = scored_rows(validation, vectors)
        measured = summarize(dev)
        if measured != saved["validation"]:
            raise ValueError("Selected state failed exact prediction replay.")
        quantized, _ = model.quantize(vectors)
        group_rows = scored_rows(validation, quantized)
        scores[key] = [row["prediction"] for row in dev]
        group_scores[key] = [row["prediction"] for row in group_rows]
        metrics[key] = {
            "selected_epoch": saved["epoch"],
            "validation": measured,
            "groups": fixed_recall_metrics(group_rows),
        }
    predictions = {
        "rows": validation["rows"],
        "seeds": seeds,
        "baseline": [row["prediction"] for row in baseline_rows],
        "scores": scores,
        "group_scores": group_scores,
    }
    paired = paired_summary(predictions)
    if (
        abs(
            paired["baseline_spearman"] - bundle["config"]["expected_baseline_spearman"]
        )
        > bundle["config"]["baseline_tolerance"]
    ):
        raise ValueError("Unchanged Qwen baseline failed replay.")
    write_json(context.outputs["predictions"], predictions)
    write_json(
        context.outputs["report"],
        {
            "status": "complete",
            "config": bundle["config"],
            "models_sha256": config.models_sha256,
            "metrics": metrics,
            "paired": paired,
            "test_accessed": False,
            "backbone_updates": 0,
        },
    )


def residual_replay_stage(
    prepared: dict[str, Any],
    trained: dict[str, Any],
    published: dict[str, Any],
    config: ReplayConfig,
) -> Any:
    """Use the established native EVAL bindings and independent metric worker."""
    primary = measure(
        mean_spearman_gain,
        dependencies=(
            MetricDependency(source="artifact", name="predictions", data_role="eval"),
        ),
        comparator=FloatComparator(mode="absolute", tolerance=1e-12),
    )
    return stage(
        evaluate_residual_codebooks,
        stage_id="evaluate",
        eval_id="residual_codebook_validation",
        config=config,
        inputs=evaluation_inputs(prepared, trained, published),
        split_inputs=("holdout",),
        outputs=EvalOutputs(
            predictions=output(
                path="predictions.json", loader=load_json, data_role="eval"
            ),
            report=output(path="report.json", loader=load_json, data_role="eval"),
        ),
        metrics=(primary,),
        objective=maximize(primary),
        reuse="never",
    )
