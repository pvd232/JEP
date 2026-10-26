"""Independently replay selected expert-coding heads on the development partition."""

import math
from typing import Any

import torch
from pydantic import Field
from viper.config import EvalConfig, MetricConfig
from viper.metrics import MetricContext, metric
from viper.stages import StageContext, eval

from csts_pilot.convergence import file_sha256, write_json
from csts_pilot.multiple_codebook import (
    ARMS,
    MultipleCodebookConfig,
    MultiplePrototypeHead,
    evaluate,
    predict,
    prepare_data,
)
from jep_pilot.loaders import load_json, load_model


class MultipleEvaluationConfig(EvalConfig):
    """Bind replay to the exact selected bundle and reviewed fitting inputs."""

    models_sha256: str = Field(pattern=r"^[a-f0-9]{64}$")
    fitting: MultipleCodebookConfig


def paired_macro_f1_gain(predictions: dict[str, Any]) -> dict[str, Any]:
    """Recompute primary paired gains from exported values without TRAIN metrics."""
    seeds, labels, mask = (predictions[name] for name in ("seeds", "labels", "mask"))
    if (
        not seeds
        or len(set(seeds)) != len(seeds)
        or not labels
        or len(labels) != len(mask)
    ):
        raise ValueError("Invalid paired development prediction dimensions.")
    codes = len(labels[0])
    if not codes or any(len(row) != codes for row in labels + mask):
        raise ValueError("Every prediction row must cover the frozen expert codes.")
    for truth, observed in zip(labels, mask, strict=True):
        if any(type(y) not in (int, float) or y not in (0, 1) for y in truth):
            raise ValueError("Exported gold labels must be zero or one.")
        if any(type(value) is not bool for value in observed):
            raise ValueError("Exported observation mask must be boolean.")
    expected = {f"{seed}:{arm}" for seed in seeds for arm in ARMS}
    if (
        set(predictions["probabilities"]) != expected
        or set(predictions["thresholds"]) != expected
    ):
        raise ValueError(
            "Predictions must contain every paired arm and seed exactly once."
        )
    measured = {}
    for key in sorted(expected):
        probabilities = predictions["probabilities"][key]
        threshold = predictions["thresholds"][key]
        if not math.isfinite(threshold) or not 0 < threshold < 1:
            raise ValueError(
                "Exported selection threshold must be finite and inside (0,1)."
            )
        if len(probabilities) != len(labels) or any(
            len(row) != codes for row in probabilities
        ):
            raise ValueError(
                "Exported probabilities must cover the exact development cohort."
            )
        if any(
            not math.isfinite(p) or not 0 <= p <= 1
            for row in probabilities
            for p in row
        ):
            raise ValueError("Exported probabilities must be finite and inside [0,1].")
        f1s = []
        for j in range(codes):
            known = [i for i in range(len(labels)) if mask[i][j]]
            if not any(labels[i][j] == 1 for i in known) or not any(
                labels[i][j] == 0 for i in known
            ):
                raise ValueError(
                    "Every evaluated code requires observed positive and negative development labels."
                )
            tp = sum(
                probabilities[i][j] >= threshold and labels[i][j] == 1 for i in known
            )
            fp = sum(
                probabilities[i][j] >= threshold and labels[i][j] == 0 for i in known
            )
            fn = sum(
                probabilities[i][j] < threshold and labels[i][j] == 1 for i in known
            )
            f1s.append(2 * tp / (2 * tp + fp + fn))
        measured[key] = sum(f1s) / len(f1s)
    changes = {
        str(seed): measured[f"{seed}:multiple_prototype"] - measured[f"{seed}:centroid"]
        for seed in seeds
    }
    return {
        "paired_seed_gains": changes,
        "mean_macro_f1_gain": sum(changes.values()) / len(changes),
        "macro_f1_by_fit": measured,
        "evaluation_split": "selected_development",
        "scope": "Development diagnostics after checkpoint/threshold selection; no fresh-test inference.",
    }


@metric(metric_id="multiple_codebook_mean_macro_f1_gain", mode="stateless")
def mean_macro_f1_gain(context: MetricContext[MetricConfig]) -> float:
    """Read sealed predictions and independently calculate the primary comparison."""
    return paired_macro_f1_gain(load_json(context.artifacts["predictions"]))[
        "mean_macro_f1_gain"
    ]


@eval(config=MultipleEvaluationConfig)
def evaluate_multiple_codebooks(
    context: StageContext[MultipleEvaluationConfig],
) -> None:
    """Restore every selected model and score frozen development labels without selection."""
    torch.set_num_threads(1)
    config = context.config
    if file_sha256(context.inputs["model"]) != config.models_sha256:
        raise ValueError("Changed selected model bundle.")
    for name in ("annotations", "training", "validation"):
        if file_sha256(context.inputs[name]) != getattr(
            config.fitting, name + "_sha256"
        ):
            raise ValueError(f"Changed replay input: {name}.")
    bundle = load_model(context.inputs["model"])
    if bundle["config"] != config.fitting.model_dump(mode="json"):
        raise ValueError(
            "Selected bundle has different fitting settings or input pins."
        )
    prepared = prepare_data(
        load_json(context.inputs["annotations"]),
        {name: load_model(context.inputs[name]) for name in ("training", "validation")},
        config.fitting,
    )
    validation = prepared["splits"]["validation"]
    if load_json(context.inputs["test"]) != validation["rows"]:
        raise ValueError("Published development rows differ from frozen annotations.")
    if load_json(context.inputs["holdout"]) != list(range(len(validation["rows"]))):
        raise ValueError(
            "Development indices must cover the complete frozen validation cohort."
        )
    if bundle["codes"] != prepared["codes"] or bundle["validation_claim_ids"] != [
        row["claim_id"] for row in validation["rows"]
    ]:
        raise ValueError("Selected bundle code definitions or claim alignment differs.")
    expected = {f"{seed}:{arm}" for seed in config.fitting.seeds for arm in ARMS}
    if set(bundle["models"]) != expected:
        raise ValueError(
            "Selected bundle must contain all paired arms/seeds exactly once."
        )
    probabilities, thresholds, measured = {}, {}, {}
    for seed in config.fitting.seeds:
        for arm in ARMS:
            key = f"{seed}:{arm}"
            selected = bundle["models"][key]
            if (
                selected["seed"] != seed
                or selected["arm"] != arm
                or selected["threshold"] not in config.fitting.thresholds
            ):
                raise ValueError(
                    "Selected model identity or threshold differs from preregistered choices."
                )
            model = MultiplePrototypeHead(
                validation["vectors"].shape[1], len(prepared["codes"]), config.fitting
            )
            model.load_state_dict(selected["state"], strict=True)
            p = predict(model, validation, arm)
            if not torch.isfinite(p).all() or not torch.equal(
                p, selected["validation_probabilities"]
            ):
                raise ValueError(
                    "Selected checkpoint does not reproduce its development predictions."
                )
            report = evaluate(validation, p, selected["threshold"])
            if report != selected["validation"]:
                raise ValueError(
                    "Selected checkpoint does not reproduce its development metrics."
                )
            probabilities[key], thresholds[key] = p.tolist(), selected["threshold"]
            measured[key] = {
                "selected_epoch": selected["epoch"],
                "threshold": selected["threshold"],
                "parameter_count": selected["parameter_count"],
                "validation": report,
            }
    exported = {
        "rows": validation["rows"],
        "codes": prepared["codes"],
        "seeds": list(config.fitting.seeds),
        "labels": validation["labels"].tolist(),
        "mask": validation["mask"].tolist(),
        "probabilities": probabilities,
        "thresholds": thresholds,
    }
    comparison = paired_macro_f1_gain(exported)
    if any(
        comparison["macro_f1_by_fit"][key] != item["validation"]["macro_f1"]
        for key, item in measured.items()
    ):
        raise ValueError(
            "Independent confusion-count replay differs from selected macro-F1."
        )
    write_json(context.outputs["predictions"], exported)
    write_json(
        context.outputs["report"],
        {
            "status": "complete",
            "comparison": comparison,
            "metrics": measured,
            "models_sha256": config.models_sha256,
            "backbone_updates": 0,
            "test_accessed": False,
            "hyperparameter_search": False,
            "passage_or_scope": "supplied_claims_only",
        },
    )
    # Artifact-derived metrics are evaluated by VIPER after sealing, without a recorder here.
