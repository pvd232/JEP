"""Evaluate frozen prototype screens and export evidence for later human review."""

from typing import Any

import numpy as np
import torch
from pydantic import Field
from scipy.stats import spearmanr
from viper.config import EvalConfig, MetricConfig
from viper.metrics import MetricContext, metric
from viper.stages import StageContext, eval

from csts_pilot.codebook import (
    ARMS,
    check_disjoint,
    representations,
    restore_model,
    scored_rows,
    unique_positions,
)
from csts_pilot.condition_reference import arm_metrics, recall_cutoff
from csts_pilot.convergence import file_sha256, write_json
from csts_pilot.diagnostics import summarize
from jep_pilot.loaders import load_json, load_model


class EvaluationConfig(EvalConfig):
    """Bind the diagnostic replay to selected models and exact development features."""

    models_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    training_cache_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    validation_cache_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    bootstrap_draws: int = Field(default=2000, ge=1)
    bootstrap_seed: int = 61026


@metric(metric_id="codebook_mean_spearman_gain", mode="stateless")
def mean_spearman_gain(context: MetricContext[MetricConfig]) -> float:
    """Independently recompute the paired mean-seed gain from exported predictions."""
    import json

    import numpy as np
    from scipy.stats import spearmanr

    data = json.loads(context.artifacts["predictions"].read_text())
    y = [row["target"] for row in data["rows"]]
    changes = []
    for seed in data["seeds"]:
        a, b = (
            float(spearmanr(y, data["scores"][f"{seed}:{arm}"]).statistic)
            for arm in ("projection", "prototype")
        )
        changes.append(b - a)
    value = float(np.mean(changes))
    if not np.isfinite(value):
        raise ValueError("The paired correlation gain is undefined.")
    return value


def paired_seed_bootstrap(
    rows: list[dict[str, Any]],
    scores: dict[str, list[float]],
    seeds: list[int],
    draws: int,
    seed: int,
) -> dict[str, Any]:
    """Resample source groups jointly, averaging paired correlations across fixed seeds."""
    if not seeds or draws < 1:
        raise ValueError("Bootstrap requires declared seeds and positive draws.")
    groups: dict[str, list[int]] = {}
    for i, row in enumerate(rows):
        groups.setdefault(row["group_id"], []).append(i)
    members = [np.asarray(groups[g]) for g in sorted(groups)]
    y = np.asarray([row["target"] for row in rows])
    values = {name: np.asarray(s) for name, s in scores.items()}
    if any(len(s) != len(y) or not np.isfinite(s).all() for s in values.values()):
        raise ValueError("Bootstrap scores must exactly cover the finite cohort.")

    def difference(indices: np.ndarray) -> list[float]:
        return [
            float(spearmanr(y[indices], values[f"{s}:prototype"][indices]).statistic)
            - float(spearmanr(y[indices], values[f"{s}:projection"][indices]).statistic)
            for s in seeds
        ]

    rng = np.random.default_rng(seed)
    samples = []
    for _ in range(draws):
        indices = np.concatenate(
            [members[i] for i in rng.integers(len(members), size=len(members))]
        )
        if len(np.unique(y[indices])) < 2:
            continue
        result = difference(indices)
        if np.isfinite(result).all():
            samples.append(float(np.mean(result)))
    if not samples:
        raise ValueError("No valid source-group bootstrap draws.")
    observed = difference(np.arange(len(rows)))
    return {
        "mean_seed_spearman_gain": float(np.mean(observed)),
        "paired_seed_gains": dict(zip(map(str, seeds), observed, strict=True)),
        "seed_gain_sample_sd": float(np.std(observed, ddof=1))
        if len(seeds) > 1
        else None,
        "percentile_95": np.percentile(samples, [2.5, 97.5]).tolist(),
        "requested_draws": draws,
        "valid_draws": len(samples),
        "groups": len(members),
        "seed": seed,
        "scope": "Source-sample uncertainty conditional on fixed training seeds and selected checkpoints; validation partition. Validation selection is not accounted for.",
    }


def review_candidates(
    saved: dict[str, Any], training: dict[str, Any], evaluation: dict[str, Any]
) -> dict[str, Any]:
    """Keep original conditions/texts with nearest training and held-out exemplars."""
    model = restore_model(saved)
    result = {"seed": saved["seed"], "arm": saved["arm"], "codes": []}
    populations = {}
    with torch.no_grad():
        for name, cache in (("training", training), ("evaluation", evaluation)):
            z = representations(model, cache)
            q, ids = model.quantize(z)
            distances = (z - q).square().sum(1)
            populations[name] = (cache, ids, distances)
    for code in range(len(model.dictionary)):
        entry: dict[str, Any] = {
            "code_id": code,
            "expert_label": "",
            "definition": "",
            "review_notes": "",
        }
        for name, (cache, ids, distances) in populations.items():
            selected = unique_positions(cache)
            selected = selected[ids[selected] == code]
            nearest = sorted(selected.tolist(), key=lambda i: (float(distances[i]), i))[
                :3
            ]
            entry[name] = [
                {
                    "condition": cache["keys"][i][0],
                    "passage": cache["keys"][i][1],
                    "distance": float(distances[i]),
                }
                for i in nearest
            ]
        if entry["training"] or entry["evaluation"]:
            result["codes"].append(entry)
    return result


@eval(config=EvaluationConfig)
def evaluate_codebooks(context: StageContext[EvaluationConfig]) -> None:
    """Evaluate every frozen arm/seed once, without further checkpoint selection."""
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
    for name in ("training", "validation"):
        if bundle["config"][name + "_cache_sha256"] != getattr(
            config, name + "_cache_sha256"
        ):
            raise ValueError("The frozen model refers to different fitting caches.")
    caches = {
        name: load_model(context.inputs[name]) for name in ("training", "validation")
    }
    check_disjoint(*caches.values())
    evaluation = caches["validation"]
    if load_json(context.inputs["test"]) != evaluation["rows"]:
        raise ValueError("Published evaluation rows differ from the development cache.")
    if load_json(context.inputs["holdout"]) != list(range(len(evaluation["rows"]))):
        raise ValueError("Evaluation indices differ from the complete frozen cohort.")
    seeds = bundle["config"]["seeds"]
    scores, metrics = {}, {}
    for seed in seeds:
        for arm in ARMS:
            key = f"{seed}:{arm}"
            saved = bundle["models"][key]
            model = restore_model(saved)
            dev = scored_rows(
                caches["validation"], representations(model, caches["validation"])
            )
            measured = summarize(dev)
            if measured != saved["validation"]:
                raise ValueError(
                    "Selected checkpoint does not reproduce its validation scores."
                )
            cutoff = recall_cutoff(
                caches["validation"]["rows"], np.asarray([r["prediction"] for r in dev])
            )
            scores[key] = [row["prediction"] for row in dev]
            metrics[key] = {
                "selected_epoch": saved["epoch"],
                "validation": arm_metrics(
                    caches["validation"]["rows"],
                    np.asarray([r["prediction"] for r in dev]),
                    cutoff,
                ),
                "codes_training": saved["codes_training"],
                "codes_validation": saved["codes_validation"],
            }
    bootstrap = paired_seed_bootstrap(
        evaluation["rows"], scores, seeds, config.bootstrap_draws, config.bootstrap_seed
    )
    write_json(
        context.outputs["predictions"],
        {
            "rows": evaluation["rows"],
            "seeds": seeds,
            "scores": scores,
            "evaluation_split": "validation",
        },
    )
    write_json(
        context.outputs["report"],
        {
            "status": "complete",
            "config": bundle["config"],
            "models_sha256": config.models_sha256,
            "evaluation_split": "validation",
            "metrics": metrics,
            "bootstrap": bootstrap,
            "backbone_updates": 0,
            "hyperparameter_search": False,
            "interpretation": "Exploratory English C-STS mechanism screen. No JEP code definitions, human semantic coherence scores, rare-demand recall, expert effort, or certified edit evaluation are measured.",
        },
    )
    write_json(
        context.outputs["review"],
        {
            "status": "unreviewed_candidates",
            "scope": "English benchmark exemplars, first predeclared seed. Numeric prototypes are not approved JEP codes; whole JEP passages may require multiple claim-level assignments.",
            "evaluation_split": "validation",
            "methods": [
                review_candidates(
                    bundle["models"][f"{seeds[0]}:{arm}"],
                    caches["training"],
                    evaluation,
                )
                for arm in ARMS
            ],
        },
    )
    context.metrics["codebook_mean_spearman_gain"].record(
        bootstrap["mean_seed_spearman_gain"]
    )
