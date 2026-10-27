"""Time disposable ratings updates from a sealed checkpoint and preserve experiment artifacts."""

import argparse
import json
import statistics
import time
from pathlib import Path
from typing import Any

import torch
from torch.nn import functional as F

from csts_pilot.baseline_models import (
    FitConfig,
    TokenPairs,
    load_backbone,
    load_tokenizer,
    restore_parameters,
)
from csts_pilot.convergence import file_sha256, reset_rng
from jep_pilot.loaders import load_json, load_model


def benchmark(inputs: Path, output: Path, microbatch: int, steps: int) -> None:
    """Keep the checkpoint, optimizer batch, rows and backbone fixed during timing."""
    manifest = load_json(inputs / "manifest.json")
    for name, digest in manifest["files"].items():
        if file_sha256(inputs / name) != digest:
            raise ValueError(f"Changed benchmark input: {name}")
    checkpoint = inputs / "checkpoint.pt"
    saved = load_model(checkpoint)
    config = FitConfig.model_validate(saved["config"]).model_copy(
        update={"microbatch_size": microbatch}
    )
    if not 1 <= microbatch <= config.batch_size:
        raise ValueError("The microbatch must fit inside the fixed optimizer batch.")
    rows = load_json(inputs / "prepared.json")["training"]
    reset_rng(config.seed)
    tokenizer = load_tokenizer(config)
    started = time.monotonic()
    model = load_backbone(config, adapters=config)
    restore_parameters(model, saved["state"])
    load_seconds = time.monotonic() - started
    training = TokenPairs(rows, config, tokenizer)
    parameters = [p for p in model.parameters() if p.requires_grad]
    optimizer = torch.optim.AdamW(
        parameters, lr=config.learning_rate, weight_decay=config.weight_decay
    )
    targets = torch.tensor([r["target"] for r in rows], device=config.device)
    generator = torch.Generator().manual_seed(config.seed + 100)
    order = torch.arange(len(rows))
    for _ in range(saved["epoch"] + 1):
        order = torch.randperm(len(rows), generator=generator)
    reset_rng(config.seed + 1000)
    model.train()
    timings: list[float] = []
    losses: list[float] = []
    torch.cuda.reset_peak_memory_stats()
    for index in range(steps + 2):
        indices = order[index * config.batch_size : (index + 1) * config.batch_size]
        if len(indices) != config.batch_size:
            raise ValueError("Benchmark requires complete optimizer batches.")
        torch.cuda.synchronize()
        started = time.monotonic()
        optimizer.zero_grad(set_to_none=True)
        total_loss = 0.0
        for offset in range(0, len(indices), microbatch):
            selected = indices[offset : offset + microbatch]
            loss = F.mse_loss(
                training.scores(model, selected).float(),
                targets[selected].float(),
                reduction="sum",
            ) / len(indices)
            if not torch.isfinite(loss):
                raise ValueError("Nonfinite benchmark loss.")
            loss.backward()
            total_loss += float(loss.detach())
        torch.nn.utils.clip_grad_norm_(parameters, 1.0, error_if_nonfinite=True)
        optimizer.step()
        torch.cuda.synchronize()
        elapsed = time.monotonic() - started
        if index >= 2:
            timings.append(elapsed)
            losses.append(total_loss)
        print(json.dumps({"update": index, "seconds": elapsed}), flush=True)
    receipt: dict[str, Any] = {
        "purpose": "Disposable device timing; weights are excluded from scientific results.",
        "gpu": torch.cuda.get_device_name(),
        "source_commit": manifest["source_commit"],
        "checkpoint_sha256": file_sha256(checkpoint),
        "checkpoint_epoch": saved["epoch"],
        "checkpoint_step": saved["step"],
        "prepared_sha256": manifest["files"]["prepared.json"],
        "batch_size": config.batch_size,
        "microbatch_size": microbatch,
        "warmup_updates": 2,
        "timed_updates": len(timings),
        "seconds_per_update": statistics.mean(timings),
        "median_seconds_per_update": statistics.median(timings),
        "update_seconds": timings,
        "training_loss": losses,
        "model_load_seconds": load_seconds,
        "peak_cuda_memory_bytes": torch.cuda.max_memory_allocated(),
        "torch_version": torch.__version__,
    }
    if receipt["checkpoint_sha256"] != manifest["files"]["checkpoint.pt"]:
        raise ValueError("Benchmark changed the saved checkpoint.")
    with output.open("x") as stream:
        json.dump(receipt, stream, indent=2)
        stream.write("\n")
    print(json.dumps(receipt), flush=True)


def main() -> None:
    """Run the requested fixed-input timing test in the owning project environment."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--inputs", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--microbatch", type=int, default=32)
    parser.add_argument("--steps", type=int, default=12)
    args = parser.parse_args()
    benchmark(args.inputs, args.output, args.microbatch, args.steps)


if __name__ == "__main__":
    main()
