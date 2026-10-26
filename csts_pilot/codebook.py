"""Compare post-hoc clustering with task-guided vector quantization on cached states."""

import hashlib
import json
import math
import time
from typing import Any, Literal

import torch
from pydantic import Field, model_validator
from torch import nn
from torch.nn import functional as F
from viper.config import BuildConfig, TrainConfig
from viper.randomness import capture_main_process_rng
from viper.resume import (
    DataLoaderConfiguration,
    DataLoaderResumeState,
    ResumeState,
    save_resume_state,
)
from viper.stages import StageContext, build, train

from csts_pilot.baseline_models import state_digest, validate_rows
from csts_pilot.condition_reference import MODEL_SHA256, native_layout
from csts_pilot.convergence import file_sha256, reset_rng, write_json
from csts_pilot.data import canonical
from csts_pilot.diagnostics import summarize
from csts_pilot.early_stopping import ValidationPatience
from jep_pilot.loaders import load_json, load_model

ARMS = ("projection", "prototype")


class CacheConfig(BuildConfig):
    """Identify one pre-existing frozen-Qwen extraction and its comparison cohort."""

    kind: Literal["matched", "condition_reference"]
    rows_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    source_cache_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    model_sha256: str = MODEL_SHA256


class CodebookConfig(TrainConfig):
    """Predeclare the entire paired screen; model selection uses validation only."""

    seeds: tuple[int, ...] = (7, 8, 9)
    output_dim: int = Field(default=128, ge=2)
    codes: int = Field(default=128, ge=2)
    learning_rate: float = Field(default=0.001, gt=0, allow_inf_nan=False)
    weight_decay: float = Field(default=0.01, ge=0, allow_inf_nan=False)
    batch_size: int = Field(default=32, ge=1)
    max_epochs: int = Field(default=48, ge=1)
    patience: int = Field(default=5, ge=1)
    kmeans_iterations: int = Field(default=10, ge=1)
    auxiliary_weight: float = Field(default=0.1, gt=0, allow_inf_nan=False)
    commitment_weight: float = Field(default=0.25, gt=0, allow_inf_nan=False)
    seconds_per_fit: float = Field(default=600, gt=0, allow_inf_nan=False)
    training_cache_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    validation_cache_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")

    @model_validator(mode="after")
    def check_seeds(self) -> "CodebookConfig":
        """Reject duplicate/empty seed declarations before fitting starts."""
        if not self.seeds or len(set(self.seeds)) != len(self.seeds):
            raise ValueError("Seeds must be a nonempty unique sequence.")
        if min(self.seeds) < 0:
            raise ValueError("Seeds must be nonnegative.")
        return self


def compact_cache(
    raw: dict[str, Any], rows: list[dict[str, Any]], config: CacheConfig
) -> dict[str, Any]:
    """Retain only normalized native states after exact occurrence/provenance checks."""
    validate_rows(rows)
    for name in ("rows_sha256", "model_sha256"):
        if raw[name] != getattr(config, name):
            raise ValueError(f"Changed source feature identity: {name}.")
    keys, left, right = native_layout(rows)
    left_key, right_key, values_key = (
        ("left", "right", "native")
        if config.kind == "matched"
        else ("row_left_indices", "row_right_indices", "raw")
    )
    if (
        [tuple(k) for k in raw["keys"]] != keys
        or raw[left_key] != left
        or raw[right_key] != right
    ):
        raise ValueError("Cached passage occurrences differ from the exact cohort.")
    vectors = raw[values_key].float()
    if (
        vectors.ndim != 2
        or len(vectors) != len(keys)
        or not torch.isfinite(vectors).all()
        or (vectors.norm(dim=1) < 1e-8).any()
    ):
        raise ValueError("Native states must have aligned finite nonzero vectors.")
    return {
        "rows": rows,
        "keys": keys,
        "left": left,
        "right": right,
        "vectors": F.normalize(vectors, dim=1),
        "provenance": config.model_dump(mode="json"),
    }


@build(config=CacheConfig)
def prepare_cache(context: StageContext[CacheConfig]) -> None:
    """Seal a compact CPU feature cache without loading or updating the backbone."""
    torch.set_num_threads(1)
    for name, expected in (
        ("rows", context.config.rows_sha256),
        ("source_cache", context.config.source_cache_sha256),
    ):
        if file_sha256(context.inputs[name]) != expected:
            raise ValueError(f"Changed cache-preparation input: {name}.")
    cache = compact_cache(
        load_model(context.inputs["source_cache"]),
        load_json(context.inputs["rows"]),
        context.config,
    )
    torch.save(cache, context.outputs["cache"])


def validate_compact(cache: dict[str, Any]) -> None:
    """Validate sealed features again at their consuming stage boundary."""
    rows, vectors = cache["rows"], cache["vectors"]
    validate_rows(rows)
    keys, left, right = native_layout(rows)
    if (
        [tuple(k) for k in cache["keys"]] != keys
        or cache["left"] != left
        or cache["right"] != right
        or vectors.dtype != torch.float32
        or vectors.ndim != 2
        or len(vectors) != len(keys)
        or not torch.isfinite(vectors).all()
        or not torch.allclose(vectors.norm(dim=1), torch.ones(len(keys)), atol=2e-5)
    ):
        raise ValueError("Compact cache identities, shape or unit vectors differ.")


def check_disjoint(*caches: dict[str, Any]) -> None:
    """Require source groups and canonical captions to stay in one partition."""
    groups: set[str] = set()
    captions: set[str] = set()
    widths = set()
    models = set()
    for cache in caches:
        validate_compact(cache)
        selected_groups = {r["group_id"] for r in cache["rows"]}
        selected_captions = {canonical(p) for _, p in cache["keys"]}
        if groups & selected_groups or captions & selected_captions:
            raise ValueError("Source groups or canonical captions overlap partitions.")
        groups.update(selected_groups)
        captions.update(selected_captions)
        widths.add(cache["vectors"].shape[1])
        models.add(cache["provenance"]["model_sha256"])
    if len(widths) != 1 or len(models) != 1:
        raise ValueError("Partitions must share one frozen encoder and feature width.")


def unique_positions(cache: dict[str, Any]) -> torch.Tensor:
    """Choose the first occurrence of each condition/passage for dictionary fitting."""
    first = {}
    for i, key in enumerate(cache["keys"]):
        first.setdefault(tuple(key), i)
    return torch.tensor(list(first.values()), dtype=torch.long)


@torch.no_grad()
def spherical_kmeans(
    vectors: torch.Tensor, codes: int, iterations: int, seed: int
) -> torch.Tensor:
    """Fit training-only spherical centers with seeded farthest-first initialization."""
    if (
        vectors.ndim != 2
        or not 2 <= codes <= len(vectors)
        or iterations < 1
        or not torch.isfinite(vectors).all()
        or (vectors.norm(dim=1) < 1e-8).any()
    ):
        raise ValueError("K-means requires enough finite nonzero training vectors.")
    x = F.normalize(vectors, dim=1)
    generator = torch.Generator().manual_seed(seed)
    first = int(torch.randint(len(x), (1,), generator=generator))
    centers = [x[first]]
    distance = torch.full((len(x),), math.inf)
    for _ in range(1, codes):
        # Coordinate differences avoid cancellation making identical unit vectors
        # appear distinct through 2 - 2 * dot(x, x) in float32.
        distance = torch.minimum(distance, (x - centers[-1]).square().sum(1))
        if float(distance.max()) < 1e-12:
            raise ValueError("Fewer distinct training directions than requested codes.")
        centers.append(x[int(distance.argmax())])
    result = torch.stack(centers)
    for _ in range(iterations):
        assignments = (x @ result.T).argmax(1)
        sums = torch.zeros_like(result).index_add_(0, assignments, x)
        occupied = sums.norm(dim=1) > 1e-8
        # Retain an unused center; frequency alone cannot justify deleting a code.
        result[occupied] = F.normalize(sums[occupied], dim=1)
    return result


class PrototypeEncoder(nn.Module):
    """Project conditioned features and look up shared unit-vector prototypes."""

    projection: nn.Module

    def __init__(self, input_dim: int, output_dim: int, codes: int) -> None:
        """Use the same projection initialization and zero-cost dictionary allocation."""
        super().__init__()
        self.projection = nn.Linear(input_dim, output_dim, bias=False)
        self.dictionary = nn.Parameter(torch.zeros(codes, output_dim))

    def forward(self, features: torch.Tensor) -> torch.Tensor:
        """Return the continuous conditional representation used for primary scoring."""
        return F.normalize(self.projection(features), dim=1)

    def quantize(self, z: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
        """Return nearest unit prototypes and their discrete identities."""
        dictionary = F.normalize(self.dictionary, dim=1)
        indices = (z @ dictionary.T).argmax(1)
        return dictionary[indices], indices


def objective(
    model: PrototypeEncoder,
    features: torch.Tensor,
    target: torch.Tensor,
    arm: str,
    weight: float,
    commitment: float,
) -> tuple[torch.Tensor, dict[str, float]]:
    """Add task distortion through a straight-through VQ bottleneck in one arm."""
    if arm not in ARMS or len(features) != 2 * len(target):
        raise ValueError("Require a named arm and left-then-right comparison features.")
    z = model(features)
    left, right = z.chunk(2)
    continuous = F.mse_loss((left * right).sum(1), target)
    loss = continuous
    values = {"continuous_mse": float(continuous.detach())}
    if arm == "prototype":
        q, _ = model.quantize(z)
        straight_through = z + (q - z).detach()
        a, b = straight_through.chunk(2)
        discrete = F.mse_loss((a * b).sum(1), target)
        dictionary = (z.detach() - q).square().sum(1).mean()
        committed = (z - q.detach()).square().sum(1).mean()
        loss = continuous + weight * (discrete + dictionary + commitment * committed)
        values.update(
            discrete_mse=float(discrete.detach()),
            dictionary_loss=float(dictionary.detach()),
            commitment_loss=float(committed.detach()),
        )
    return loss, values


@torch.no_grad()
def representations(model: PrototypeEncoder, cache: dict[str, Any]) -> torch.Tensor:
    """Use a fixed CPU batching layout during checkpointing and independent replay."""
    model.eval()
    return torch.cat([model(x) for x in cache["vectors"].split(512)])


def scored_rows(cache: dict[str, Any], z: torch.Tensor) -> list[dict[str, Any]]:
    """Preserve all comparison fields, order and multiplicity when attaching scores."""
    values = (z[cache["left"]] * z[cache["right"]]).sum(1).tolist()
    return [
        dict(row, prediction=value)
        for row, value in zip(cache["rows"], values, strict=True)
    ]


def restore_model(saved: dict[str, Any]) -> PrototypeEncoder:
    """Restore a complete selected projection and its associated dictionary."""
    weight = saved["state"]["projection.weight"]
    dictionary = saved["state"]["dictionary"]
    model = PrototypeEncoder(weight.shape[1], weight.shape[0], len(dictionary))
    model.load_state_dict(saved["state"], strict=True)
    return model


def code_diagnostics(model: PrototypeEncoder, cache: dict[str, Any]) -> dict[str, Any]:
    """Measure usage, distortion and low-rating collisions without claiming semantic codes."""
    z = representations(model, cache)
    with torch.no_grad():
        q, indices = model.quantize(z)
    unique = unique_positions(cache)
    counts = torch.bincount(indices[unique], minlength=len(model.dictionary))
    probabilities = counts[counts > 0].double() / len(unique)
    same = indices[cache["left"]] == indices[cache["right"]]
    ratings = torch.tensor([row["rating"] for row in cache["rows"]])
    return {
        "unique_condition_passages": len(unique),
        "occupied_codes": int((counts > 0).sum()),
        "effective_codes": float(
            torch.exp(-(probabilities * probabilities.log()).sum())
        ),
        "largest_code_share": float(counts.max() / len(unique)),
        "usage_counts": counts.tolist(),
        "mean_squared_quantization_distance": float(
            (z[unique] - q[unique]).square().sum(1).mean()
        ),
        "negative_pairs": int((ratings <= 2).sum()),
        "negative_same_code": int(same[ratings <= 2].sum()),
        "positive_pairs": int((ratings >= 4).sum()),
        "positive_same_code": int(same[ratings >= 4].sum()),
        "quantized_similarity": summarize(scored_rows(cache, q)),
    }


def fit_one(
    training: dict[str, Any],
    validation: dict[str, Any],
    config: CodebookConfig,
    seed: int,
    arm: str,
    observer: Any,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    """Fit one paired arm, retaining cloned best weights and exact terminal resume state."""
    reset_rng(seed)
    model = PrototypeEncoder(
        training["vectors"].shape[1], config.output_dim, config.codes
    )
    unique = unique_positions(training)
    model.dictionary.data.copy_(
        spherical_kmeans(
            representations(model, training)[unique],
            config.codes,
            config.kmeans_iterations,
            seed,
        )
    )
    initial = state_digest(model.state_dict())
    groups = [
        {
            "params": list(model.projection.parameters()),
            "weight_decay": config.weight_decay,
        }
    ]
    if arm == "prototype":
        groups.append({"params": [model.dictionary], "weight_decay": 0.0})
    optimizer = torch.optim.AdamW(groups, lr=config.learning_rate)
    generator = torch.Generator().manual_seed(seed + 100)
    left, right = torch.tensor(training["left"]), torch.tensor(training["right"])
    targets = torch.tensor([row["target"] for row in training["rows"]])
    stopping = ValidationPatience(config.patience)
    selected: dict[str, Any] = {}
    history = []
    started, updates = time.monotonic(), 0

    def checkpoint(epoch: int) -> dict[str, Any]:
        measured = summarize(
            scored_rows(validation, representations(model, validation))
        )
        score = measured["spearman"]
        if score is None:
            raise ValueError("Continuous validation Spearman is undefined.")
        if not selected or score > selected["validation"]["spearman"]:
            selected.update(
                state={
                    name: tensor.detach().cpu().clone()
                    for name, tensor in model.state_dict().items()
                },
                epoch=epoch,
                validation=measured,
                seed=seed,
                arm=arm,
                initial_state_sha256=initial,
            )
        return measured

    initial_metrics = checkpoint(0)
    stopping.observe(initial_metrics["spearman"])
    reason = "epoch_budget"
    for epoch in range(1, config.max_epochs + 1):
        model.train()
        order = torch.randperm(len(targets), generator=generator)
        totals: dict[str, float] = {}
        for batch in order.split(config.batch_size):
            if time.monotonic() - started > config.seconds_per_fit:
                raise TimeoutError(
                    "Fit budget ended; preserve the failed native attempt."
                )
            features = training["vectors"][torch.cat((left[batch], right[batch]))]
            optimizer.zero_grad(set_to_none=True)
            loss, components = objective(
                model,
                features,
                targets[batch],
                arm,
                config.auxiliary_weight,
                config.commitment_weight,
            )
            if not torch.isfinite(loss):
                raise ValueError("Nonfinite codebook objective.")
            loss.backward()
            nn.utils.clip_grad_norm_(model.parameters(), 1.0, error_if_nonfinite=True)
            optimizer.step()
            updates += 1
            for name, value in {
                "objective": float(loss.detach()),
                **components,
            }.items():
                totals[name] = totals.get(name, 0.0) + value * len(batch)
        measured = checkpoint(epoch)
        record = {
            "epoch": epoch,
            "training": {name: value / len(targets) for name, value in totals.items()},
            "validation": measured,
            "batch_order_sha256": hashlib.sha256(order.numpy().tobytes()).hexdigest(),
            "elapsed_seconds": time.monotonic() - started,
        }
        history.append(record)
        observer(seed, arm, record)
        if stopping.observe(measured["spearman"]):
            reason = "validation_patience"
            break
    terminal = {
        "optimizer": optimizer.state_dict(),
        "state": model.state_dict(),
        "generator": generator.get_state(),
        "updates": updates,
    }
    chosen = restore_model(selected)
    if arm == "projection":
        chosen.dictionary.data.copy_(
            spherical_kmeans(
                representations(chosen, training)[unique],
                config.codes,
                config.kmeans_iterations,
                seed,
            )
        )
        selected["state"] = {
            name: value.detach().clone() for name, value in chosen.state_dict().items()
        }
    selected["dictionary_origin"] = (
        "post_hoc_training_kmeans" if arm == "projection" else "joint_training"
    )
    selected["codes_training"] = code_diagnostics(chosen, training)
    selected["codes_validation"] = code_diagnostics(chosen, validation)
    return (
        selected,
        {
            "seed": seed,
            "arm": arm,
            "epochs": history,
            "stop_reason": reason,
            "selected_epoch": selected["epoch"],
            "updates": updates,
            "initial_state_sha256": initial,
            "elapsed_seconds": time.monotonic() - started,
        },
        terminal,
    )


@train(config=CodebookConfig)
def fit_codebooks(context: StageContext[CodebookConfig]) -> None:
    """Run all predeclared paired seeds in one CPU stage with immutable feature inputs."""
    torch.set_num_threads(1)
    config = context.config
    caches = {}
    for name in ("training", "validation"):
        if file_sha256(context.inputs[name]) != getattr(config, name + "_cache_sha256"):
            raise ValueError(f"Changed fitting cache: {name}.")
        caches[name] = load_model(context.inputs[name])
    check_disjoint(caches["training"], caches["validation"])
    models, traces, terminal = {}, {}, {}
    run_index = 0

    def observe(seed: int, arm: str, record: dict[str, Any]) -> None:
        step = run_index * (config.max_epochs + 1) + record["epoch"]
        context.metrics["training_objective"].record(
            record["training"]["objective"], step=step
        )
        context.metrics["validation_mse"].record(
            record["validation"]["mse_0_1"], step=step
        )
        context.metrics["validation_spearman"].record(
            record["validation"]["spearman"], step=step
        )
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
                    "event": "codebook_epoch",
                    "seed": seed,
                    "arm": arm,
                    "epoch": record["epoch"],
                    "spearman": record["validation"]["spearman"],
                }
            ),
            flush=True,
        )

    for seed in config.seeds:
        for arm in ARMS:
            key = f"{seed}:{arm}"
            models[key], traces[key], terminal[key] = fit_one(
                caches["training"], caches["validation"], config, seed, arm, observe
            )
            run_index += 1
        a, b = (traces[f"{seed}:{arm}"] for arm in ARMS)
        if a["initial_state_sha256"] != b["initial_state_sha256"] or any(
            x["batch_order_sha256"] != y["batch_order_sha256"]
            for x, y in zip(a["epochs"], b["epochs"])
        ):
            raise ValueError(
                "Paired initialization or shared-epoch batch orders differ."
            )
    torch.save(
        {"config": config.model_dump(mode="json"), "models": models},
        context.outputs["model"],
    )
    write_json(
        context.outputs["trace"],
        {
            "status": "complete",
            "fits": traces,
            "backbone_updates": 0,
            "test_accessed": False,
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
                    "completed_runs": list(models),
                    "training_cache_sha256": config.training_cache_sha256,
                },
            ),
        ),
    )
