"""Synchronous global-batch LoRA updates and rank-local epoch recovery."""

import math
from contextlib import nullcontext
from typing import Any

import torch
import torch.distributed as dist
from torch import nn
from torch.nn import functional as F
from torch.nn.parallel import DistributedDataParallel
from transformers import get_constant_schedule, get_linear_schedule_with_warmup
from viper.randomness import capture_main_process_rng, restore_main_process_rng
from viper.resume import DataLoaderConfiguration, DataLoaderResumeState, ResumeState

from csts_pilot.baseline_models import FitConfig


def rank_microbatches(
    effective: torch.Tensor, microbatch_size: int, rank: int, world_size: int
) -> list[torch.Tensor]:
    """Assign original consecutive microbatches without padding, dropping or duplicating rows."""
    if effective.ndim != 1 or not len(effective) or microbatch_size < 1:
        raise ValueError("Require a nonempty global batch and positive microbatch size.")
    if world_size != 2 or rank not in range(world_size):
        raise ValueError("This replay requires exactly two ranks.")
    chunks = list(effective.split(microbatch_size))
    if len(chunks) % world_size:
        raise ValueError("Both ranks must have the same number of backward calls.")
    return chunks[rank::world_size]


def make_scheduler(
    optimizer: torch.optim.Optimizer, config: FitConfig, updates_per_epoch: int
) -> Any:
    """Start the declared phase without shortening its original scheduler horizon."""
    for group in optimizer.param_groups:
        group["lr"] = group["initial_lr"] = config.learning_rate
    total_updates = config.max_epochs * updates_per_epoch
    if config.schedule == "constant":
        return get_constant_schedule(optimizer)
    return get_linear_schedule_with_warmup(
        optimizer, math.ceil(config.warmup_fraction * total_updates), total_updates
    )


def distributed_optimizer_step(
    model: DistributedDataParallel,
    pairs: Any,
    targets: torch.Tensor,
    effective: torch.Tensor,
    optimizer: torch.optim.Optimizer,
    scheduler: Any,
    *,
    rank: int,
    world_size: int,
    microbatch_size: int,
) -> dict[str, Any]:
    """Average the complete global MSE gradient, clip it once, and update both replicas."""
    if not isinstance(model, DistributedDataParallel):
        raise TypeError("A real DistributedDataParallel model is required.")
    if dist.get_world_size() != world_size or dist.get_rank() != rank:
        raise ValueError("The declared rank differs from the initialized process group.")
    chunks = rank_microbatches(effective, microbatch_size, rank, world_size)
    optimizer.zero_grad(set_to_none=True)
    local_squared_error = 0.0
    for position, indices in enumerate(chunks):
        synchronize = position == len(chunks) - 1
        with nullcontext() if synchronize else model.no_sync():
            scores = pairs.scores(model, indices)
            with torch.autocast(targets.device.type, enabled=False):
                squared_error = F.mse_loss(
                    scores.float(), targets[indices].float(), reduction="sum"
                )
                loss = squared_error * world_size / len(effective)
            if not torch.isfinite(loss):
                raise ValueError("Training loss must be finite.")
            loss.backward()
            local_squared_error += float(squared_error.detach())
    parameters = [p for p in model.parameters() if p.requires_grad]
    norm = nn.utils.clip_grad_norm_(parameters, 1.0, error_if_nonfinite=True)
    optimizer.step()
    scheduler.step()
    return {
        "local_squared_error": local_squared_error,
        "gradient_norm": float(norm),
        "learning_rates": scheduler.get_last_lr(),
    }


def capture_training_state(
    optimizer: torch.optim.Optimizer,
    scheduler: Any,
    generator: torch.Generator,
    *,
    epoch: int,
    step: int,
    model_sha256: str,
) -> ResumeState:
    """Capture this rank's optimizer and complete RNG state at a finished epoch."""
    return ResumeState(
        optimizer_state={
            "optimizer": optimizer.state_dict(),
            "scheduler": scheduler.state_dict(),
        },
        main_process_rng=capture_main_process_rng({}, capture_legacy_global=True),
        dataloader=DataLoaderResumeState(
            configuration=DataLoaderConfiguration(workers=0),
            state_dict={
                "epoch": epoch,
                "step": step,
                "generator_state": generator.get_state(),
                "last_model_sha256": model_sha256,
            },
        ),
    )


def restore_training_state(
    state: ResumeState,
    optimizer: torch.optim.Optimizer,
    scheduler: Any,
    generator: torch.Generator,
) -> None:
    """Restore this rank; the caller starts a new schedule only at the phase transition."""
    optimizer.load_state_dict(state.optimizer_state["optimizer"])
    scheduler.load_state_dict(state.optimizer_state["scheduler"])
    generator.set_state(state.dataloader.state_dict["generator_state"])
    restore_main_process_rng(state.main_process_rng, {})
    if capture_main_process_rng({}, capture_legacy_global=True) != state.main_process_rng:
        raise ValueError("Rank-local random state did not restore exactly.")


def validate_checkpoint_receipts(
    receipts: list[dict[str, Any]],
    *,
    world_size: int,
    epoch: int,
    step: int,
    protocol_sha256: str,
) -> None:
    """Reject a mixed or incomplete set of durable rank states before committing an epoch."""
    if (
        world_size != 2
        or len(receipts) != world_size
        or {receipt.get("rank") for receipt in receipts} != set(range(world_size))
    ):
        raise ValueError("A checkpoint requires one durable receipt for each rank.")
    for receipt in receipts:
        if any(
            receipt.get(key) != expected
            for key, expected in (
                ("epoch", epoch),
                ("step", step),
                ("protocol_sha256", protocol_sha256),
            )
        ):
            raise ValueError("Checkpoint ranks disagree on epoch, step or protocol.")
        model_digest = receipt.get("model_state_sha256", "")
        if not isinstance(model_digest, str) or len(model_digest) != 64 or any(
            char not in "0123456789abcdef" for char in model_digest
        ):
            raise ValueError("The synchronized model state requires a SHA-256 identity.")
        directory = receipt.get("directory", "")
        if not directory.startswith("epochs/") or ".." in directory.split("/"):
            raise ValueError("Checkpoint directories must stay inside the run.")
        files = receipt.get("files", {})
        if not {"model.pt", "resume.pt", "state.json"}.issubset(files):
            raise ValueError("A rank checkpoint lacks model, optimizer/RNG or history.")
        for name, record in files.items():
            if "/" in name or name in {".", ".."}:
                raise ValueError("Checkpoint file names must be local basenames.")
            digest = record.get("sha256", "")
            if (
                len(digest) != 64
                or any(char not in "0123456789abcdef" for char in digest)
                or record.get("bytes", 0) <= 0
            ):
                raise ValueError("Checkpoint artifact identity is incomplete.")
        if receipt["rank"] == 0 and not {
            "best_model.pt", "best_validation_predictions.json"
        }.issubset(files):
            raise ValueError("Rank zero must retain its selected model and predictions.")
    state_digests = {receipt.get("model_state_sha256") for receipt in receipts}
    if len(state_digests) != 1 or None in state_digests:
        raise ValueError("The synchronized model replicas disagree at the epoch boundary.")
