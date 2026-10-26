"""Paired, train-only masked-feature cluster prediction with optional target refresh."""

import hashlib
import json
import time
from typing import Any

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
    PrototypeEncoder,
    check_disjoint,
    code_diagnostics,
    representations,
    restore_model,
    scored_rows,
    spherical_kmeans,
    unique_positions,
)
from csts_pilot.convergence import file_sha256, reset_rng, write_json
from csts_pilot.diagnostics import summarize
from jep_pilot.loaders import load_model

ARMS = ("fixed", "refreshed")


class IterativeConfig(TrainConfig):
    """Declare one equal-budget, validation-only comparison before launching it."""

    seeds: tuple[int, ...] = (7, 8, 9)
    output_dim: int = Field(default=128, ge=2)
    codes: int = Field(default=128, ge=2)
    learning_rate: float = Field(default=0.001, gt=0, allow_inf_nan=False)
    weight_decay: float = Field(default=0.01, ge=0, allow_inf_nan=False)
    batch_size: int = Field(default=32, ge=1)
    max_epochs: int = Field(default=48, ge=1)
    patience: int = Field(default=5, ge=1)
    round_epochs: int = Field(default=2, ge=1)
    kmeans_iterations: int = Field(default=10, ge=1)
    cluster_weight: float = Field(default=0.1, gt=0, allow_inf_nan=False)
    temperature: float = Field(default=0.1, gt=0, allow_inf_nan=False)
    mask_fraction: float = Field(default=0.1, gt=0, lt=1, allow_inf_nan=False)
    seconds_per_pair: float = Field(default=1200, gt=0, allow_inf_nan=False)
    training_cache_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    validation_cache_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")

    @model_validator(mode="after")
    def validate_seeds(self) -> "IterativeConfig":
        """Reject ambiguous seed declarations before any native execution."""
        if (
            not self.seeds
            or min(self.seeds) < 0
            or len(set(self.seeds)) != len(self.seeds)
        ):
            raise ValueError("Seeds must be a nonempty unique nonnegative sequence.")
        return self


def tensor_sha256(value: torch.Tensor) -> str:
    """Hash the exact CPU tensor bytes used by both arms."""
    return hashlib.sha256(
        value.detach().contiguous().cpu().numpy().tobytes()
    ).hexdigest()


def feature_mask(
    shape: torch.Size, fraction: float, generator: torch.Generator
) -> torch.Tensor:
    """Drop the same fixed number of randomly chosen coordinates in each occurrence."""
    width = shape[1]
    dropped = max(1, int(width * fraction))
    if width < 2 or dropped >= width:
        raise ValueError("Feature masking must leave at least one input coordinate.")
    positions = torch.rand(shape, generator=generator).argsort(dim=1)[:, :dropped]
    return torch.ones(shape, dtype=torch.bool).scatter_(1, positions, False)


@torch.no_grad()
def teacher_targets(
    model: PrototypeEncoder,
    training: dict[str, Any],
    config: IterativeConfig,
    seed: int,
) -> dict[str, torch.Tensor]:
    """Cluster unique unmasked TRAIN keys; broadcast their labels to occurrences."""
    z = representations(model, training)
    positions = unique_positions(training)
    centers = spherical_kmeans(
        z[positions], config.codes, config.kmeans_iterations, seed
    )
    labels = (z[positions] @ centers.T).argmax(1)
    by_key = {
        tuple(training["keys"][int(pos)]): int(label)
        for pos, label in zip(positions, labels, strict=True)
    }
    occurrences = torch.tensor(
        [by_key[tuple(key)] for key in training["keys"]], dtype=torch.long
    )
    return {"centers": centers, "labels": occurrences, "unique_labels": labels}


def partition_agreement(left: torch.Tensor, right: torch.Tensor, codes: int) -> float:
    """Measure label-permutation-invariant pair coassignment agreement (Rand index)."""
    if left.shape != right.shape or left.ndim != 1:
        raise ValueError("Partitions must describe the same unique training keys.")
    n = len(left)
    if n < 2:
        return 1.0
    table = torch.bincount(left * codes + right, minlength=codes * codes).reshape(
        codes, codes
    )
    choose_two = lambda values: int((values * (values - 1) // 2).sum())
    both_same = choose_two(table)
    left_same, right_same = choose_two(table.sum(1)), choose_two(table.sum(0))
    pairs = n * (n - 1) // 2
    return (pairs - left_same - right_same + 2 * both_same) / pairs


def objective(
    model: PrototypeEncoder,
    features: torch.Tensor,
    ratings: torch.Tensor,
    labels: torch.Tensor,
    mask: torch.Tensor,
    config: IterativeConfig,
) -> tuple[torch.Tensor, dict[str, float]]:
    """Retain unmasked rating supervision and predict train clusters from masked views."""
    if (
        len(features) != 2 * len(ratings)
        or len(labels) != len(features)
        or mask.shape != features.shape
    ):
        raise ValueError("Require aligned left-then-right features, labels and masks.")
    masked = features * mask
    if (masked.norm(dim=1) < 1e-8).any():
        raise ValueError(
            "Mask erased a complete feature vector; reduce the declared mask fraction."
        )
    a, b = model(features).chunk(2)
    continuous = F.mse_loss((a * b).sum(1), ratings)
    logits = model(masked) @ F.normalize(model.dictionary, dim=1).T / config.temperature
    cluster = F.cross_entropy(logits, labels)
    loss = continuous + config.cluster_weight * cluster
    return loss, {
        "continuous_mse": float(continuous.detach()),
        "cluster_cross_entropy": float(cluster.detach()),
    }


def _optimizer(
    model: PrototypeEncoder, config: IterativeConfig
) -> torch.optim.Optimizer:
    return torch.optim.AdamW(
        [
            {
                "params": list(model.projection.parameters()),
                "weight_decay": config.weight_decay,
            },
            {"params": [model.dictionary], "weight_decay": 0.0},
        ],
        lr=config.learning_rate,
    )


def fit_pair(
    training: dict[str, Any],
    validation: dict[str, Any],
    config: IterativeConfig,
    seed: int,
    observer: Any = lambda *_: None,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    """Fit both policies in lockstep, with equal updates and selection opportunities."""
    started = time.monotonic()

    def check_budget() -> None:
        if time.monotonic() - started > config.seconds_per_pair:
            raise TimeoutError("Pair budget ended; preserve the failed native attempt.")

    check_disjoint(training, validation)
    reset_rng(seed)
    initial = PrototypeEncoder(
        training["vectors"].shape[1], config.output_dim, config.codes
    )
    teacher = teacher_targets(initial, training, config, seed)
    initial.dictionary.data.copy_(teacher["centers"])
    initial_hash = state_digest(initial.state_dict())
    models, teachers, optimizers, selected = {}, {}, {}, {}
    histories: dict[str, list[dict[str, Any]]] = {arm: [] for arm in ARMS}
    for arm in ARMS:
        models[arm] = restore_model({"state": initial.state_dict()})
        teachers[arm] = {name: value.clone() for name, value in teacher.items()}
        optimizers[arm] = _optimizer(models[arm], config)
    batch_rng = torch.Generator().manual_seed(seed + 100)
    mask_rng = torch.Generator().manual_seed(seed + 200)
    left, right = torch.tensor(training["left"]), torch.tensor(training["right"])
    ratings = torch.tensor([row["target"] for row in training["rows"]])
    updates, stale, rounds = 0, 0, 0
    check_budget()

    def checkpoint(arm: str, epoch: int) -> tuple[dict[str, Any], bool]:
        measured = summarize(
            scored_rows(validation, representations(models[arm], validation))
        )
        score = measured["spearman"]
        if score is None:
            raise ValueError("Continuous validation Spearman is undefined.")
        improved = (
            arm not in selected or score > selected[arm]["validation"]["spearman"]
        )
        if improved:
            selected[arm] = {
                "state": {
                    key: value.detach().clone()
                    for key, value in models[arm].state_dict().items()
                },
                "teacher": {key: value.clone() for key, value in teachers[arm].items()},
                "epoch": epoch,
                "validation": measured,
                "seed": seed,
                "arm": arm,
                "initial_state_sha256": initial_hash,
                "dictionary_origin": "masked_feature_cluster_classifier",
            }
        return measured, improved

    for arm in ARMS:
        checkpoint(arm, 0)
    reason = "epoch_budget"
    for epoch in range(1, config.max_epochs + 1):
        refresh = epoch > 1 and (epoch - 1) % config.round_epochs == 0
        agreements = {arm: 1.0 for arm in ARMS}
        if refresh:
            rounds += 1
            old = teachers["refreshed"]["unique_labels"]
            teachers["refreshed"] = teacher_targets(
                models["refreshed"], training, config, seed
            )
            agreements["refreshed"] = partition_agreement(
                old, teachers["refreshed"]["unique_labels"], config.codes
            )
            # A refreshed partition may permute IDs; reset both classifiers and
            # AdamW states at identical boundaries so ID history cannot confound it.
            for arm in ARMS:
                models[arm].dictionary.data.copy_(teachers[arm]["centers"])
                optimizers[arm] = _optimizer(models[arm], config)
        order = torch.randperm(len(ratings), generator=batch_rng)
        totals: dict[str, dict[str, float]] = {arm: {} for arm in ARMS}
        mask_hash = hashlib.sha256()
        for batch in order.split(config.batch_size):
            check_budget()
            occurrences = torch.cat((left[batch], right[batch]))
            features = training["vectors"][occurrences]
            mask = feature_mask(features.shape, config.mask_fraction, mask_rng)
            mask_hash.update(mask.numpy().tobytes())
            for arm in ARMS:
                model, optimizer = models[arm], optimizers[arm]
                model.train()
                optimizer.zero_grad(set_to_none=True)
                loss, parts = objective(
                    model,
                    features,
                    ratings[batch],
                    teachers[arm]["labels"][occurrences],
                    mask,
                    config,
                )
                if not torch.isfinite(loss):
                    raise ValueError("Nonfinite iterative-codebook objective.")
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
            measured, arm_improved = checkpoint(arm, epoch)
            improved = improved or arm_improved
            record = {
                "epoch": epoch,
                "training": {
                    key: value / len(ratings) for key, value in totals[arm].items()
                },
                "validation": measured,
                "batch_order_sha256": tensor_sha256(order),
                "feature_masks_sha256": mask_hash.hexdigest(),
                "target_labels_sha256": tensor_sha256(teachers[arm]["labels"]),
                "target_usage_counts": torch.bincount(
                    teachers[arm]["unique_labels"], minlength=config.codes
                ).tolist(),
                "refreshed_boundary": refresh,
                "target_partition_rand_agreement": agreements[arm],
                "updates": updates,
                "optimizer_resets": rounds,
                "elapsed_seconds": time.monotonic() - started,
            }
            histories[arm].append(record)
            observer(seed, arm, record)
        check_budget()
        stale = 0 if improved else stale + 1
        if stale >= config.patience:
            reason = "paired_validation_patience"
            break
    terminal = {}
    traces = {}
    for arm in ARMS:
        chosen = restore_model(selected[arm])
        selected[arm]["codes_training"] = code_diagnostics(chosen, training)
        selected[arm]["codes_validation"] = code_diagnostics(chosen, validation)
        traces[arm] = {
            "epochs": histories[arm],
            "selected_epoch": selected[arm]["epoch"],
            "initial_state_sha256": initial_hash,
            "updates": updates,
            "stop_reason": reason,
            "paired_stale_epochs": stale,
        }
        terminal[arm] = {
            "state": models[arm].state_dict(),
            "optimizer": optimizers[arm].state_dict(),
            "teacher": teachers[arm],
            "batch_generator": batch_rng.get_state(),
            "mask_generator": mask_rng.get_state(),
            "updates": updates,
        }
    check_budget()
    return selected, traces, terminal


@train(config=IterativeConfig)
def fit_iterative_codebooks(context: StageContext[IterativeConfig]) -> None:
    """Consume only sealed TRAIN/dev caches and save selected plus terminal states."""
    torch.set_num_threads(1)
    config = context.config
    caches = {}
    for split in ("training", "validation"):
        if file_sha256(context.inputs[split]) != getattr(
            config, split + "_cache_sha256"
        ):
            raise ValueError(f"Changed fitting cache: {split}.")
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
                    "event": "iterative_codebook_epoch",
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
