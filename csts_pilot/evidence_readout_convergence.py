"""Native validation selected readout fits and comparison of A's final vectors."""

import copy
from typing import Any, Literal

import numpy as np
import torch
from pydantic import Field
from viper.config import EvalConfig, MetricConfig, TrainConfig
from viper.metrics import FloatComparator, MetricContext, MetricDependency, measure
from viper.metrics import metric as declare_metric
from viper.randomness import capture_main_process_rng
from viper.resume import (
    DataLoaderConfiguration,
    DataLoaderResumeState,
    ResumeState,
    save_resume_state,
)
from viper.stages import StageContext, eval, train

from csts_pilot import evidence_readout_progress as progress
from csts_pilot.convergence import write_json
from csts_pilot.evidence_readout import (
    ARMS,
    EvidenceReadout,
    SymmetricComparison,
    metric_values,
    paired_intervals,
    predict,
    validate_cache,
)
from csts_pilot.evidence_readout_stages import (
    ReadoutFitConfig,
    checked,
    condition_diagnostics,
    family_diagnostics,
    fit_comparisons,
    intervention_diagnostics,
    paired_condition_diagnostics,
    selection_diagnostics,
    train_pair,
)
from jep_pilot.loaders import load_json, load_model

REFIT_CONTRASTS = {
    "A_comparison_minus_A": {"parent_comparison": 1, "A_parent": -1},
    "D_minus_A": {"ratings_comparison": 1, "A_parent": -1},
    "E_minus_A": {"evidence_comparison": 1, "A_parent": -1},
    "B_minus_A": {"ratings": 1, "A_parent": -1},
    "C_minus_A": {"evidence": 1, "A_parent": -1},
    "C_minus_B": {"evidence": 1, "ratings": -1},
    "E_minus_D": {"evidence_comparison": 1, "ratings_comparison": -1},
    "D_minus_B": {"ratings_comparison": 1, "ratings": -1},
    "E_minus_C": {"evidence_comparison": 1, "evidence": -1},
}


@declare_metric(metric_id="readout_refit_a_comparison_gain", mode="stateless")
def refit_gain(context: MetricContext[MetricConfig]) -> float:
    return float(
        load_json(context.artifacts["report"])["contrasts"]["A_comparison_minus_A"][
            "mean"
        ]
    )


def refit_evaluation_metric():
    return measure(
        refit_gain,
        dependencies=(
            MetricDependency(source="artifact", name="report", data_role="eval"),
        ),
        comparator=FloatComparator(mode="absolute", tolerance=1e-12),
    )


class ConvergedFitConfig(TrainConfig):
    """Declare equal learning rate searches on one frozen representation."""

    device: Literal["cpu", "cuda"] = "cuda"
    progress_path: str | None = None
    seeds: tuple[int, ...] = (7, 8, 9)
    learning_rates: tuple[float, ...] = (0.00001, 0.00003, 0.0001)
    query_dim: int = Field(default=128, ge=1)
    evidence_weight: float = Field(default=0.1, gt=0)
    weight_decay: float = Field(default=0.01, ge=0)
    batch_size: int = Field(default=32, ge=1)
    max_epochs: int = Field(default=256, ge=1)
    patience: int = Field(default=10, ge=1)
    comparison_learning_rate: float = Field(default=0.001, gt=0)
    comparison_max_epochs: int = Field(default=256, ge=1)
    comparison_patience: int = Field(default=10, ge=1)
    training_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    validation_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    training_cache_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    validation_cache_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")


class ConvergedEvaluationConfig(EvalConfig):
    """Bind selected fits before opening the existing exploratory test cohort."""

    device: Literal["cpu", "cuda"] = "cuda"
    progress_path: str | None = None
    model_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    selection_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    test_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    cache_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    intervention_rows_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    intervention_cache_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    cohorts_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    bootstrap_draws: int = Field(default=2000, ge=1)
    bootstrap_seed: int = 61028


def select_rates(candidates: dict[str, Any], seeds: tuple[int, ...]) -> dict[str, Any]:
    """Select one rate per objective by mean best validation Spearman across seeds."""
    if not candidates or len(set(seeds)) != len(seeds) or not seeds:
        raise ValueError("Require a nonempty candidate grid and distinct seeds.")
    scores: dict[str, Any] = {}
    for rate in sorted(candidates, key=float):
        if not np.isfinite(float(rate)) or float(rate) <= 0:
            raise ValueError("Learning rates must be finite and positive.")
        values = candidates[rate]
        if set(values) != {str(seed) for seed in seeds}:
            raise ValueError("Each rate must have the same complete seed set.")
        if any(v["trace"]["budget_censored"] for v in values.values()):
            raise ValueError(
                "An epoch ceiling requires further fitting before selection."
            )
        scores[rate] = {
            arm: float(
                np.mean(
                    [
                        values[str(s)]["model"]["selected"][arm]["spearman"]
                        for s in seeds
                    ]
                )
            )
            for arm in ARMS
        }
        if any(not np.isfinite(v) for v in scores[rate].values()):
            raise ValueError("Validation selection requires finite Spearman values.")
    selected = {arm: max(scores, key=lambda r, arm=arm: scores[r][arm]) for arm in ARMS}
    return {
        "rates": selected,
        "mean_validation_spearman": scores,
        "tie_rule": "smallest learning rate",
    }


def fit_config(config: ConvergedFitConfig, seed: int, rate: float) -> ReadoutFitConfig:
    values = {
        k: v
        for k, v in config.model_dump().items()
        if k in ReadoutFitConfig.model_fields
    }
    return ReadoutFitConfig.model_validate(
        {
            **values,
            "seed": seed,
            "learning_rate": rate,
            "fit_comparison": False,
            "include_initial": True,
            "record_attention": True,
        }
    )


@train(config=ConvergedFitConfig)
def fit_converged_readouts(context: StageContext[ConvergedFitConfig]) -> None:
    config = context.config
    progress.configure(config.progress_path)
    if not config.learning_rates or len(set(config.learning_rates)) != len(
        config.learning_rates
    ):
        raise ValueError("Require distinct candidate learning rates.")
    for name in ("training", "validation", "training_cache", "validation_cache"):
        checked(context.inputs[name], getattr(config, name + "_sha256"))
    training, validation = (
        load_model(context.inputs["training_cache"]),
        load_model(context.inputs["validation_cache"]),
    )
    rows, heldout = (
        load_json(context.inputs["training"]),
        load_json(context.inputs["validation"]),
    )
    candidates: dict[str, Any] = {}
    traces: dict[str, Any] = {"status": "running", "candidates": {}, "comparisons": {}}
    step = 0

    def record_epoch(record):
        nonlocal step
        step += 1
        context.metrics["training_objective"].record(
            float(np.mean(list(record["training_objective"].values()))), step=step
        )
        context.metrics["validation_spearman"].record(
            float(np.mean([v["spearman"] for v in record["validation"].values()])),
            step=step,
        )
        context.metrics["validation_mse"].record(
            float(np.mean([v["mse_0_1"] for v in record["validation"].values()])),
            step=step,
        )

    def checkpoint(current):
        save_resume_state(
            context.outputs["resume_state"],
            ResumeState(
                optimizer_state=current["optimizer"],
                main_process_rng=capture_main_process_rng(
                    context.numpy_generators, capture_legacy_global=True
                ),
                dataloader=DataLoaderResumeState(
                    configuration=DataLoaderConfiguration(workers=0),
                    state_dict={k: v for k, v in current.items() if k != "optimizer"},
                ),
            ),
        )

    for rate in sorted(config.learning_rates):
        key = str(rate)
        candidates[key], traces["candidates"][key] = {}, {}
        for seed in config.seeds:
            progress.append("candidate_started", name=f"B/C rate {rate}", seed=seed)

            def save_active(current, rate=rate, seed=seed):
                checkpoint(
                    {**current, "learning_rate": rate, "seed": seed, "phase": "readout"}
                )

            model, trace, predictions, terminal = train_pair(
                training,
                validation,
                rows,
                heldout,
                fit_config(config, seed, rate),
                record_epoch,
                save_active,
            )
            candidates[key][str(seed)] = {
                "model": model,
                "trace": trace,
                "predictions": predictions,
                "terminal": terminal,
            }
            traces["candidates"][key][str(seed)] = trace
            torch.save(candidates, context.outputs["candidates"])
            write_json(context.outputs["trace"], traces)
            progress.append(
                "candidate_finished",
                name=f"B/C rate {rate}; epochs {len(trace['epochs'])}; selected {trace['selected_epoch']}",
                seed=seed,
                status=trace["stop_reason"],
            )
    selection = select_rates(candidates, config.seeds)
    write_json(context.outputs["selection"], selection)
    progress.append("rates_selected", name=str(selection))
    fitted, validation_predictions, comparison_terminal = {}, {}, {}
    for seed in config.seeds:
        b = candidates[selection["rates"]["ratings"]][str(seed)]["model"]
        c = candidates[selection["rates"]["evidence"]][str(seed)]["model"]
        selected = {
            "ratings": copy.deepcopy(b["selected"]["ratings"]),
            "evidence": copy.deepcopy(c["selected"]["evidence"]),
        }
        heads = {
            arm: EvidenceReadout(training["embedding_dimension"], config.query_dim).to(
                config.device
            )
            for arm in ARMS
        }
        comparison_config = fit_config(config, seed, config.comparison_learning_rate)
        progress.append("comparison_started", name="A with comparison, D, E", seed=seed)
        comparison, trace, predictions, terminal = fit_comparisons(
            heads,
            selected,
            training,
            validation,
            rows,
            heldout,
            comparison_config,
            record_epoch,
            include_parent=True,
        )
        if trace["budget_censored"]:
            raise ValueError(
                "Comparison hit the epoch ceiling; preserve and extend this fit."
            )
        saved = {
            "config": {"seed": seed, "query_dim": config.query_dim},
            "embedding_dimension": training["embedding_dimension"],
            "parent_model_sha256": training["model_sha256"],
            "frozen_adapter_sha256": training["adapter_before_sha256"],
            "training_groups": b["training_groups"],
            "validation_groups": b["validation_groups"],
            "selected": selected,
            "comparisons": comparison,
            "selected_learning_rates": selection["rates"],
        }
        fitted[str(seed)] = saved
        traces["comparisons"][str(seed)] = trace
        validation_predictions[str(seed)] = {
            **predictions,
            **{
                arm: candidates[selection["rates"][arm]][str(seed)]["predictions"][arm]
                for arm in ARMS
            },
        }
        comparison_terminal[str(seed)] = terminal
        torch.save({"seeds": fitted, "selection": selection}, context.outputs["model"])
        write_json(context.outputs["trace"], traces)
    traces["status"] = "complete"
    traces["config"] = config.model_dump()
    write_json(context.outputs["trace"], traces)
    write_json(context.outputs["validation_predictions"], validation_predictions)
    checkpoint(
        {
            "optimizer": {s: v["optimizer"] for s, v in comparison_terminal.items()},
            "phase": "complete",
            "comparisons": comparison_terminal,
        }
    )
    progress.append(
        "fitting_complete",
        name="Learning rates and all checkpoints selected using validation",
    )


@eval(config=ConvergedEvaluationConfig)
def evaluate_converged_readouts(
    context: StageContext[ConvergedEvaluationConfig],
) -> None:
    config = context.config
    progress.configure(config.progress_path)
    for name in (
        "model",
        "selection",
        "test",
        "cache",
        "intervention_rows",
        "intervention_cache",
        "cohorts",
    ):
        checked(context.inputs[name], getattr(config, name + "_sha256"))
    frozen = load_json(context.inputs["selection"])
    if (
        frozen.get("status") != "checkpoints_frozen"
        or frozen.get("test_scores_used_for_selection") is not False
        or frozen.get("model_sha256") != config.model_sha256
    ):
        raise ValueError("Require frozen validation selected models before evaluation.")
    saved = load_model(context.inputs["model"])
    cache, edited = (
        load_model(context.inputs["cache"]),
        load_model(context.inputs["intervention_cache"]),
    )
    rows, cases = (
        load_json(context.inputs["test"]),
        load_json(context.inputs["intervention_rows"]),
    )
    if load_json(context.inputs["holdout"]) != list(range(len(rows))):
        raise ValueError("Require complete original test row coverage.")
    validate_cache(cache, rows)
    validate_cache(edited, cases)
    cohorts = load_json(context.inputs["cohorts"])
    baseline, _, _ = predict(None, cache)
    base_edits, _, _ = predict(None, edited)
    results = {"A_parent": metric_values(rows, baseline)}
    interventions = {
        "A_parent": intervention_diagnostics(
            cases, edited, base_edits, [], np.array([])
        )
    }
    paired, families, per_condition, predictions = {}, {}, {}, {}
    for seed, model in saved["seeds"].items():
        if (
            model["parent_model_sha256"] != cache["model_sha256"]
            or edited["model_sha256"] != cache["model_sha256"]
        ):
            raise ValueError("Cached values use another frozen encoder.")
        if {r["group_id"] for r in rows} & set(
            model["training_groups"] + model["validation_groups"]
        ):
            raise ValueError("Test groups overlap fitting groups.")
        predictions[seed] = {"A_parent": baseline.tolist()}
        (
            results[seed],
            interventions[seed],
            paired[seed],
            families[seed],
            per_condition[seed],
        ) = {}, {}, {}, {}, {}
        for arm in (
            "ratings",
            "evidence",
            "ratings_comparison",
            "evidence_comparison",
            "parent_comparison",
        ):
            readout_arm = arm.removesuffix("_comparison")
            head = None
            if readout_arm != "parent":
                head = EvidenceReadout(
                    model["embedding_dimension"], model["config"]["query_dim"]
                ).to(config.device)
                head.load_state_dict(
                    model["selected"][readout_arm]["state"], strict=True
                )
            comparator = None
            if arm.endswith("_comparison"):
                comparator = SymmetricComparison(model["embedding_dimension"]).to(
                    config.device
                )
                comparator.load_state_dict(
                    model["comparisons"]["selected"][readout_arm]["state"], strict=True
                )
            values, weights, null = predict(head, cache, config.device, comparator)
            predictions[seed][arm] = values.tolist()
            results[seed][arm] = {
                **metric_values(rows, values),
                **(selection_diagnostics(weights, null) if weights else {}),
                "readout_selected_epoch": model["selected"][readout_arm]["epoch"]
                if head is not None
                else None,
                "comparison_selected_epoch": model["comparisons"]["selected"][
                    readout_arm
                ]["epoch"]
                if comparator is not None
                else None,
                "prediction_range": [float(values.min()), float(values.max())],
            }
            paired[seed][arm] = paired_condition_diagnostics(rows, values)
            families[seed][arm] = family_diagnostics(rows, values, cohorts)
            per_condition[seed][arm] = condition_diagnostics(rows, values)
            values, weights, null = predict(head, edited, config.device, comparator)
            interventions[seed][arm] = intervention_diagnostics(
                cases, edited, values, weights, null
            )
    contrasts = {}
    for name, coefficients in REFIT_CONTRASTS.items():
        deltas, mses = [], []
        for seed in predictions:

            def score(arm, metric, seed=seed):
                return (
                    results["A_parent"][metric]
                    if arm == "A_parent"
                    else results[seed][arm][metric]
                )

            deltas.append(
                sum(w * score(a, "spearman") for a, w in coefficients.items())
            )
            mses.append(sum(w * score(a, "mse_0_1") for a, w in coefficients.items()))
        contrasts[name] = {
            "per_seed": deltas,
            "mean": float(np.mean(deltas)),
            "sample_std": float(np.std(deltas, ddof=1)),
            "mse_delta_per_seed": mses,
            "mse_delta_mean": float(np.mean(mses)),
            "group_bootstrap_95": paired_intervals(
                rows,
                predictions,
                config.bootstrap_draws,
                config.bootstrap_seed,
                coefficients,
            ),
        }
    report = {
        "results": results,
        "contrasts": contrasts,
        "primary_C_minus_B": contrasts["C_minus_B"],
        "learning_rate_selection": saved["selection"],
        "interventions": interventions,
        "paired_condition": paired,
        "families": families,
        "per_condition": per_condition,
        "interpretation": "Exploratory evaluation on the existing test. Learning rates and checkpoints were frozen using validation. Each objective received the same candidate grid. Three head seeds share one frozen backbone.",
        "primary_evaluation_contrast": "A_comparison_minus_A",
    }
    write_json(context.outputs["report"], report)
    write_json(
        context.outputs["predictions"],
        {"row_ids": [r["row_id"] for r in rows], "seeds": predictions},
    )
    progress.append(
        "readout_final_scores",
        results=results,
        primary_C_minus_B=report["primary_C_minus_B"],
        primary_A_comparison_minus_A=contrasts["A_comparison_minus_A"],
        contrasts=contrasts,
    )
