"""Matched full-dimensional residual learning with optional prototype training."""

import json
import math
import time
from typing import Any

import numpy as np
import torch
from pydantic import Field, model_validator
from torch import nn
from torch.nn import functional as F
from viper.config import TrainConfig
from viper.randomness import capture_main_process_rng
from viper.resume import (
    DataLoaderConfiguration,
    DataLoaderResumeState,
    ResumeState,
    save_resume_state,
)
from viper.stages import StageContext, train

from csts_pilot.baseline_models import state_digest
from csts_pilot.codebook import (
    ARMS,
    PrototypeEncoder,
    check_disjoint,
    code_diagnostics,
    objective,
    representations,
    scored_rows,
    spherical_kmeans,
    unique_positions,
)
from csts_pilot.convergence import file_sha256, reset_rng, write_json
from csts_pilot.diagnostics import summarize
from csts_pilot.iterative_codebook import tensor_sha256
from jep_pilot.loaders import load_model


class ResidualConfig(TrainConfig):
    """Freeze one paired screen over the already captured Qwen features."""

    seeds: tuple[int, ...] = (7, 8, 9)
    rank: int = Field(default=32, ge=1)
    codes: int = Field(default=128, ge=2)
    learning_rate: float = Field(default=0.001, gt=0, allow_inf_nan=False)
    weight_decay: float = Field(default=0.01, ge=0, allow_inf_nan=False)
    batch_size: int = Field(default=32, ge=1)
    max_epochs: int = Field(default=12, ge=1)
    patience: int = Field(default=5, ge=1)
    kmeans_iterations: int = Field(default=10, ge=1)
    auxiliary_weight: float = Field(default=0.1, gt=0, allow_inf_nan=False)
    commitment_weight: float = Field(default=0.25, ge=0, allow_inf_nan=False)
    seconds_per_pair: float = Field(default=1200, gt=0, allow_inf_nan=False)
    expected_baseline_spearman: float = Field(default=0.782575, ge=-1, le=1)
    baseline_tolerance: float = Field(default=0.000001, gt=0, allow_inf_nan=False)
    training_cache_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    validation_cache_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")

    @model_validator(mode="after")
    def validate_seeds(self) -> "ResidualConfig":
        if (
            not self.seeds
            or min(self.seeds) < 0
            or len(set(self.seeds)) != len(self.seeds)
        ):
            raise ValueError("Seeds must be unique nonnegative integers.")
        return self


class ResidualProjection(nn.Module):
    """Keep every input coordinate and initialize the added correction to zero."""

    def __init__(self, width: int, rank: int) -> None:
        super().__init__()
        if not 1 <= rank <= width:
            raise ValueError("Residual rank must lie between one and feature width.")
        self.down = nn.Linear(width, rank, bias=False)
        self.up = nn.Linear(rank, width, bias=False)
        nn.init.zeros_(self.up.weight)

    def forward(self, features: torch.Tensor) -> torch.Tensor:
        return features + self.up(self.down(features))


class ResidualEncoder(PrototypeEncoder):
    """Reuse prototype scoring with a full-width identity-initialized mapping."""

    def __init__(self, input_dim: int, rank: int, codes: int) -> None:
        nn.Module.__init__(self)
        self.projection = ResidualProjection(input_dim, rank)
        self.dictionary = nn.Parameter(torch.zeros(codes, input_dim))


def restore_residual(saved: dict[str, Any]) -> ResidualEncoder:
    """Restore each arm's own complete selected or terminal state."""
    state = saved["state"]
    down = state["projection.down.weight"]
    model = ResidualEncoder(down.shape[1], down.shape[0], len(state["dictionary"]))
    model.load_state_dict(state, strict=True)
    return model


def matched_group_metrics(
    model: ResidualEncoder, cache: dict[str, Any], requested_recall: float = 0.9
) -> dict[str, Any]:
    """Compare quantized scores at equal expected recall using fractional ties."""
    with torch.no_grad():
        quantized, _ = model.quantize(representations(model, cache))
    return fixed_recall_metrics(scored_rows(cache, quantized), requested_recall)


def fixed_recall_metrics(
    rows: list[dict[str, Any]], requested_recall: float = 0.9
) -> dict[str, Any]:
    """Recompute the equal-coverage diagnostic from sealed prediction rows."""
    if not 0 < requested_recall <= 1:
        raise ValueError("Requested recall must lie in (0, 1].")
    scores = np.asarray([row["prediction"] for row in rows])
    targets = np.asarray([row["target"] for row in rows])
    positive, negative = scores[targets >= 0.75], scores[targets <= 0.25]
    if (
        not len(positive)
        or not len(negative)
        or not np.isfinite(scores).all()
        or not np.isfinite(targets).all()
        or np.any((targets < 0) | (targets > 1))
    ):
        raise ValueError(
            "Matched group rates require finite positive and negative pairs."
        )
    target = requested_recall * len(positive)
    threshold = float(np.sort(positive)[::-1][math.ceil(target) - 1])
    above = int(np.sum(positive > threshold))
    ties = int(np.sum(positive == threshold))
    fraction = (target - above) / ties
    false_positives = int(np.sum(negative > threshold)) + fraction * int(
        np.sum(negative == threshold)
    )
    return {
        "requested_recall": requested_recall,
        "achieved_recall": (above + fraction * ties) / len(positive),
        "threshold": threshold,
        "tie_acceptance_probability": fraction,
        "false_positive_rate": false_positives / len(negative),
        "positives": len(positive),
        "negatives": len(negative),
        "scope": "Expected rates with uniform randomized acceptance at the boundary score.",
    }


def gradient_diagnostics(
    model: ResidualEncoder,
    features: torch.Tensor,
    ratings: torch.Tensor,
    config: ResidualConfig,
    arm: str = "prototype",
) -> dict[str, float | None]:
    """Measure actual rating and weighted-group gradients on the shared mapping."""
    rating, _ = objective(model, features, ratings, "projection", 0.0, 0.0)
    combined = rating
    if arm != "projection":
        combined, _ = objective(
            model,
            features,
            ratings,
            arm,
            config.auxiliary_weight,
            config.commitment_weight,
        )
    parameters = tuple(model.projection.parameters())

    def flattened(loss: torch.Tensor) -> torch.Tensor:
        values = torch.autograd.grad(
            loss, parameters, allow_unused=True, retain_graph=True
        )
        return torch.cat(
            [
                (torch.zeros_like(parameter) if value is None else value).reshape(-1)
                for parameter, value in zip(parameters, values, strict=True)
            ]
        )

    rating_gradient = flattened(rating)
    auxiliary_gradient = flattened(combined - rating)
    rating_norm = float(rating_gradient.norm())
    auxiliary_norm = float(auxiliary_gradient.norm())
    return {
        "rating_grad_norm": rating_norm,
        "weighted_aux_grad_norm": auxiliary_norm,
        "cosine": float(torch.dot(rating_gradient, auxiliary_gradient))
        / (rating_norm * auxiliary_norm)
        if rating_norm > 0 and auxiliary_norm > 0
        else None,
        "aux_to_rating_norm_ratio": auxiliary_norm / rating_norm
        if rating_norm > 0
        else None,
    }


def fit_pair(
    training: dict[str, Any],
    validation: dict[str, Any],
    config: ResidualConfig,
    seed: int,
    observer: Any = lambda *_: None,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    """Train the two objectives with identical exposure and shared patience."""
    started = time.monotonic()

    def check_budget() -> None:
        if time.monotonic() - started > config.seconds_per_pair:
            raise TimeoutError("Residual pair budget ended; preserve this attempt.")

    check_disjoint(training, validation)
    reset_rng(seed)
    initial = ResidualEncoder(training["vectors"].shape[1], config.rank, config.codes)
    baseline = scored_rows(validation, F.normalize(validation["vectors"], dim=1))
    initial_rows = scored_rows(validation, representations(initial, validation))
    difference = max(
        abs(a["prediction"] - b["prediction"])
        for a, b in zip(baseline, initial_rows, strict=True)
    )
    baseline_metrics = summarize(baseline)
    baseline_score = baseline_metrics["spearman"]
    if baseline_score is None or not math.isfinite(baseline_score):
        raise ValueError("Frozen baseline Spearman is undefined.")
    if (
        difference > 1e-7
        or abs(baseline_score - config.expected_baseline_spearman)
        > config.baseline_tolerance
    ):
        raise ValueError("Epoch zero does not reproduce the frozen Qwen baseline.")
    initial.dictionary.data.copy_(
        spherical_kmeans(
            representations(initial, training)[unique_positions(training)],
            config.codes,
            config.kmeans_iterations,
            seed,
        )
    )
    initial_hash = state_digest(initial.state_dict())
    models = {arm: restore_residual({"state": initial.state_dict()}) for arm in ARMS}
    optimizers = {
        arm: torch.optim.AdamW(
            [
                {
                    "params": list(model.projection.parameters()),
                    "weight_decay": config.weight_decay,
                },
                {"params": [model.dictionary], "weight_decay": 0.0},
            ],
            lr=config.learning_rate,
        )
        for arm, model in models.items()
    }
    selected: dict[str, Any] = {}
    histories: dict[str, list[dict[str, Any]]] = {arm: [] for arm in ARMS}
    generator = torch.Generator().manual_seed(seed + 100)
    left, right = torch.tensor(training["left"]), torch.tensor(training["right"])
    ratings = torch.tensor([row["target"] for row in training["rows"]])

    def checkpoint(arm: str, epoch: int) -> tuple[dict[str, Any], bool]:
        measured = summarize(
            scored_rows(validation, representations(models[arm], validation))
        )
        score = measured["spearman"]
        if score is None:
            raise ValueError("Residual validation Spearman is undefined.")
        improved = (
            arm not in selected or score > selected[arm]["validation"]["spearman"]
        )
        if improved:
            selected[arm] = {
                "state": {
                    name: value.detach().clone()
                    for name, value in models[arm].state_dict().items()
                },
                "epoch": epoch,
                "validation": measured,
                "seed": seed,
                "arm": arm,
                "initial_state_sha256": initial_hash,
                "dictionary_origin": "joint_rating_vq"
                if arm == "prototype"
                else "posthoc_training_kmeans",
            }
        return measured, improved

    for arm in ARMS:
        checkpoint(arm, 0)
    stale, updates, reason = 0, 0, "epoch_budget"
    check_budget()
    for epoch in range(1, config.max_epochs + 1):
        order = torch.randperm(len(ratings), generator=generator)
        totals: dict[str, dict[str, float]] = {arm: {} for arm in ARMS}
        gradients = {}
        for batch_index, batch in enumerate(order.split(config.batch_size)):
            check_budget()
            features = training["vectors"][torch.cat((left[batch], right[batch]))]
            for arm in ARMS:
                model, optimizer = models[arm], optimizers[arm]
                if batch_index == 0:
                    gradients[arm] = gradient_diagnostics(
                        model, features, ratings[batch], config, arm
                    )
                optimizer.zero_grad(set_to_none=True)
                loss, parts = objective(
                    model,
                    features,
                    ratings[batch],
                    arm,
                    config.auxiliary_weight,
                    config.commitment_weight,
                )
                if not torch.isfinite(loss):
                    raise ValueError("Nonfinite residual-codebook objective.")
                loss.backward()
                nn.utils.clip_grad_norm_(
                    model.parameters(), 1.0, error_if_nonfinite=True
                )
                optimizer.step()
                for name, value in {"objective": float(loss.detach()), **parts}.items():
                    totals[arm][name] = totals[arm].get(name, 0.0) + value * len(batch)
            updates += 1
        improved = False
        for arm in ARMS:
            measured, better = checkpoint(arm, epoch)
            improved = improved or better
            record = {
                "epoch": epoch,
                "training": {
                    name: value / len(ratings) for name, value in totals[arm].items()
                },
                "validation": measured,
                "batch_order_sha256": tensor_sha256(order),
                "updates": updates,
                "gradient_diagnostics": gradients[arm],
                "elapsed_seconds": time.monotonic() - started,
            }
            histories[arm].append(record)
            observer(seed, arm, record)
        stale = 0 if improved else stale + 1
        check_budget()
        if stale >= config.patience:
            reason = "paired_validation_patience"
            break
    traces, terminal = {}, {}
    for arm in ARMS:
        chosen = restore_residual(selected[arm])
        if arm == "projection" and selected[arm]["epoch"] > 0:
            chosen.dictionary.data.copy_(
                spherical_kmeans(
                    representations(chosen, training)[unique_positions(training)],
                    config.codes,
                    config.kmeans_iterations,
                    seed,
                )
            )
            selected[arm]["state"] = {
                name: value.detach().clone()
                for name, value in chosen.state_dict().items()
            }
        selected[arm]["codes_training"] = code_diagnostics(chosen, training)
        selected[arm]["codes_validation"] = code_diagnostics(chosen, validation)
        selected[arm]["group_metrics_validation"] = matched_group_metrics(
            chosen, validation
        )
        traces[arm] = {
            "epochs": histories[arm],
            "selected_epoch": selected[arm]["epoch"],
            "initial_state_sha256": initial_hash,
            "updates": updates,
            "stop_reason": reason,
            "paired_stale_epochs": stale,
            "baseline": baseline_metrics,
            "baseline_max_prediction_difference": difference,
        }
        terminal[arm] = {
            "state": {
                name: value.detach().clone()
                for name, value in models[arm].state_dict().items()
            },
            "optimizer": optimizers[arm].state_dict(),
            "batch_generator": generator.get_state(),
            "updates": updates,
        }
    check_budget()
    return selected, traces, terminal


@train(config=ResidualConfig)
def fit_residual_codebooks(context: StageContext[ResidualConfig]) -> None:
    """Keep native selected, terminal, optimizer and trace artifacts together."""
    torch.set_num_threads(1)
    config = context.config
    caches = {}
    for split in ("training", "validation"):
        if file_sha256(context.inputs[split]) != getattr(
            config, split + "_cache_sha256"
        ):
            raise ValueError(f"Changed residual fitting cache: {split}.")
        caches[split] = load_model(context.inputs[split])
    selected, traces, terminal = {}, {}, {}
    seed_index = 0

    def observe(seed: int, arm: str, record: dict[str, Any]) -> None:
        step = 2 * (
            seed_index * (config.max_epochs + 1) + record["epoch"]
        ) + ARMS.index(arm)
        for name, value in (
            ("training_objective", record["training"]["objective"]),
            ("validation_mse", record["validation"]["mse_0_1"]),
            ("validation_spearman", record["validation"]["spearman"]),
        ):
            context.metrics[name].record(value, step=step)
        write_json(
            context.outputs["trace"],
            {
                "status": "running",
                "completed": traces,
                "current": {"seed": seed, "arm": arm, **record},
            },
        )
        print(
            json.dumps(
                {
                    "event": "residual_codebook_epoch",
                    "seed": seed,
                    "arm": arm,
                    "epoch": record["epoch"],
                }
            ),
            flush=True,
        )

    for seed_index, seed in enumerate(config.seeds):
        chosen, trace, end = fit_pair(
            caches["training"], caches["validation"], config, seed, observe
        )
        for arm in ARMS:
            key = f"{seed}:{arm}"
            selected[key], traces[key], terminal[key] = (
                chosen[arm],
                trace[arm],
                end[arm],
            )
    torch.save(
        {"config": config.model_dump(mode="json"), "models": selected},
        context.outputs["model"],
    )
    write_json(
        context.outputs["trace"],
        {
            "status": "complete",
            "fits": traces,
            "test_accessed": False,
            "backbone_updates": 0,
        },
    )
    save_resume_state(
        context.outputs["resume_state"],
        ResumeState(
            optimizer_state={"terminal_runs": terminal},
            main_process_rng=capture_main_process_rng(
                context.numpy_generators, capture_legacy_global=True
            ),
            dataloader=DataLoaderResumeState(
                configuration=DataLoaderConfiguration(workers=0),
                state_dict={
                    "completed_runs": list(selected),
                    "training_cache_sha256": config.training_cache_sha256,
                },
            ),
        ),
    )
