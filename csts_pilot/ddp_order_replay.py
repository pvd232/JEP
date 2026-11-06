"""Execute an explicitly external two-rank PyTorch DDP condition-order replay.

VIPER 0.1.2 does not support distributed TRAIN execution. This command reuses
its state serialization and the existing model/math helpers, but creates no
native TRAIN receipt. Each host keeps its own persistent completed-epoch state.
"""

import argparse
import fcntl
import hashlib
import importlib.metadata
import json
import math
import os
import shutil
import socket
import subprocess
import sys
import time
import uuid
from contextlib import contextmanager
from datetime import timedelta
from pathlib import Path
from typing import Any, Callable, Iterator

import numpy as np
import torch
import torch.distributed as dist
from torch.nn.parallel import DistributedDataParallel
from viper.resume import load_resume_state, save_resume_state

from csts_pilot.baseline_models import (
    FitConfig,
    TokenPairs,
    load_backbone,
    load_tokenizer,
    restore_parameters,
    state_digest,
    trainable_state,
)
from csts_pilot.baseline_stages import predict_pairs, ranking_value, save_neural
from csts_pilot.convergence import file_sha256, reset_rng
from csts_pilot.convergence_run import check_inputs
from csts_pilot.diagnostics import summarize
from csts_pilot.distributed_lora import (
    capture_training_state,
    distributed_optimizer_step,
    make_scheduler,
    restore_training_state,
    validate_checkpoint_receipts,
)
from csts_pilot.early_stopping import ValidationPatience
from csts_pilot.lora_order_replay import replay_settings
from jep_pilot.loaders import load_json, load_model


@contextmanager
def run_directory_lock(directory: Path) -> Iterator[None]:
    """Keep one local worker responsible for this rank's outputs until it exits."""
    directory.mkdir(parents=True, exist_ok=True)
    with (directory / "worker.lock").open("a+") as stream:
        try:
            fcntl.flock(stream, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as error:
            raise RuntimeError(
                "The run directory is already owned by another worker."
            ) from error
        try:
            yield
        finally:
            fcntl.flock(stream, fcntl.LOCK_UN)


def atomic_file(path: Path, writer: Callable[[Path], Any]) -> None:
    """Flush a new file and its directory before exposing its final name."""
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{uuid.uuid4().hex}.tmp")
    try:
        writer(temporary)
        with temporary.open("rb") as stream:
            os.fsync(stream.fileno())
        os.replace(temporary, path)
        descriptor = os.open(path.parent, os.O_RDONLY)
        try:
            os.fsync(descriptor)
        finally:
            os.close(descriptor)
    finally:
        temporary.unlink(missing_ok=True)


def atomic_json(path: Path, value: Any) -> None:
    """Write exact JSON without exposing a partially written progress or commit file."""
    atomic_file(
        path,
        lambda temporary: temporary.write_text(
            json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n"
        ),
    )


def broadcast(value: Any, rank: int) -> Any:
    """Broadcast a small rank-zero control decision to both workers."""
    values = [value if rank == 0 else None]
    dist.broadcast_object_list(values, src=0)
    return values[0]


def gather(value: Any) -> list[Any]:
    """Collect one small identity or checkpoint receipt per rank."""
    values = [None] * dist.get_world_size()
    dist.all_gather_object(values, value)
    return values


def file_record(path: Path) -> dict[str, Any]:
    """Identify one durable file by bytes rather than its mutable location."""
    return {"sha256": file_sha256(path), "bytes": path.stat().st_size}


def committed_checkpoint(
    directory: Path, rank: int, protocol_sha256: str, resume: bool
) -> tuple[Path | None, dict[str, Any] | None]:
    """Select only a complete epoch whose common manifest exists identically on both hosts."""
    local = {
        path.name: file_sha256(path)
        for path in (directory / "committed").glob("epoch-*.json")
    }
    manifests = gather(local)
    if not resume and any(manifests):
        raise ValueError("Completed checkpoints already exist; inspect them and use --resume.")
    common = set(manifests[0]).intersection(manifests[1])
    for name in common:
        if manifests[0][name] != manifests[1][name]:
            raise ValueError("Rank checkpoint manifests disagree; do not resume a mixed epoch.")
    if not common:
        return None, None
    name = max(common, key=lambda value: (int(value.split("-")[1]), value))
    epoch = int(name.split("-")[1])
    manifest = load_json(directory / "committed" / name)
    if manifest["epoch"] != epoch or manifest["protocol_sha256"] != protocol_sha256:
        raise ValueError("The committed epoch identity differs from its manifest.")
    validate_checkpoint_receipts(
        manifest["receipts"],
        world_size=2,
        epoch=epoch,
        step=manifest["step"],
        protocol_sha256=protocol_sha256,
    )
    receipt = next(item for item in manifest["receipts"] if item["rank"] == rank)
    checkpoint = directory / receipt["directory"]
    for name, expected in receipt["files"].items():
        if file_record(checkpoint / name) != expected:
            raise ValueError("A committed local checkpoint artifact changed or is missing.")
    return checkpoint, manifest


def save_completed_epoch(
    directory: Path,
    rank: int,
    protocol_sha256: str,
    model: torch.nn.Module,
    config: FitConfig,
    optimizer: torch.optim.Optimizer,
    scheduler: Any,
    generator: torch.Generator,
    state: dict[str, Any],
) -> dict[str, Any]:
    """Commit an epoch only after both immutable rank snapshots are durable and agree."""
    epoch, step = state["epoch"], state["step"]
    checkpoint = directory / "epochs" / f"epoch-{epoch:04d}-{uuid.uuid4().hex}"
    checkpoint.mkdir(parents=True)
    model_path = checkpoint / "model.pt"
    atomic_file(
        model_path,
        lambda temporary: save_neural(temporary, model, config, epoch, step),
    )
    resume_state = capture_training_state(
        optimizer,
        scheduler,
        generator,
        epoch=epoch,
        step=step,
        model_sha256=file_sha256(model_path),
    )
    atomic_file(
        checkpoint / "resume.pt",
        lambda temporary: save_resume_state(temporary, resume_state),
    )
    atomic_json(checkpoint / "state.json", state)
    names = ["model.pt", "resume.pt", "state.json"]
    if rank == 0:
        for name in ("best_model.pt", "best_validation_predictions.json"):
            atomic_file(
                checkpoint / name,
                lambda temporary, name=name: shutil.copyfile(directory / name, temporary),
            )
            names.append(name)
    receipt = {
        "rank": rank,
        "epoch": epoch,
        "step": step,
        "protocol_sha256": protocol_sha256,
        "model_state_sha256": state_digest(trainable_state(model)),
        "directory": str(checkpoint.relative_to(directory)),
        "files": {name: file_record(checkpoint / name) for name in names},
    }
    receipts = gather(receipt)
    validate_checkpoint_receipts(
        receipts,
        world_size=2,
        epoch=epoch,
        step=step,
        protocol_sha256=protocol_sha256,
    )
    manifest = {
        "schema_version": 1,
        "execution": "external_pytorch_ddp",
        "native_train_receipt": False,
        "epoch": epoch,
        "step": step,
        "protocol_sha256": protocol_sha256,
        "receipts": receipts,
    }
    manifest_id = hashlib.sha256(
        json.dumps(manifest, sort_keys=True, allow_nan=False).encode()
    ).hexdigest()
    manifest_path = directory / "committed" / f"epoch-{epoch:04d}-{manifest_id}.json"
    if manifest_path.exists() and load_json(manifest_path) != manifest:
        raise ValueError("Refusing to overwrite a previously committed epoch.")
    atomic_json(manifest_path, manifest)
    dist.barrier()
    atomic_json(
        directory / "latest.json",
        {
            "epoch": epoch,
            "step": step,
            "manifest": str(manifest_path),
            "manifest_sha256": file_sha256(manifest_path),
        },
    )
    return manifest


def train(
    directory: Path,
    rank: int,
    protocol_sha256: str,
    configurations: list[FitConfig],
    model: DistributedDataParallel,
    training: TokenPairs,
    validation: TokenPairs,
    resume: bool,
) -> dict[str, Any]:
    """Retain the original two-phase optimizer protocol over one shared global permutation."""
    raw_model = model.module
    initial, continuation = configurations
    updates_per_epoch = math.ceil(len(training.rows) / initial.batch_size)
    if updates_per_epoch != 219 or len(training.rows) != 6980:
        raise ValueError("The declared replay requires the original 6,980 training rows.")
    optimizer = torch.optim.AdamW(
        [p for p in raw_model.parameters() if p.requires_grad],
        lr=initial.learning_rate,
        weight_decay=initial.weight_decay,
    )
    generator = torch.Generator().manual_seed(initial.seed + 100)
    targets = torch.tensor(
        [row["target"] for row in training.rows],
        dtype=torch.float32,
        device=initial.device,
    )
    stopping = ValidationPatience(initial.patience, 0.0)
    state: dict[str, Any] = {
        "epoch": 0,
        "step": 0,
        "phase": "initial",
        "history": [],
        "selected": None,
        "phase_seconds": {"initial": 0.0, "continuation": 0.0},
        "stale_epochs": 0,
        "initial_trainable_sha256": state_digest(trainable_state(raw_model)),
    }
    checkpoint, manifest = committed_checkpoint(
        directory, rank, protocol_sha256, resume
    )
    if checkpoint is not None:
        saved = load_model(checkpoint / "model.pt")
        state = load_json(checkpoint / "state.json")
        expected_step = state["epoch"] * updates_per_epoch
        restored = load_resume_state(checkpoint / "resume.pt")
        if (
            state["step"] != expected_step
            or saved["epoch"] != state["epoch"]
            or saved["step"] != expected_step
            or restored.dataloader.state_dict["epoch"] != state["epoch"]
            or restored.dataloader.state_dict["step"] != expected_step
            or restored.dataloader.state_dict["last_model_sha256"]
            != file_sha256(checkpoint / "model.pt")
        ):
            raise ValueError("The saved model, optimizer counters and epoch disagree.")
        restore_parameters(raw_model, saved["state"])
        scheduler = make_scheduler(
            optimizer, initial if state["epoch"] == 1 else continuation, updates_per_epoch
        )
        restore_training_state(restored, optimizer, scheduler, generator)
        steps = [
            float(item["step"]) for item in optimizer.state.values() if "step" in item
        ]
        if not steps or any(step != expected_step for step in steps):
            raise ValueError("Restored optimizer updates do not match the completed epoch.")
        selected_score = state["selected"]["validation"]["spearman"]
        stopping.best_score = selected_score if selected_score is not None else -1.0
        stopping.stale_epochs = state["stale_epochs"]
        if rank == 0:
            for name in ("best_model.pt", "best_validation_predictions.json"):
                atomic_file(
                    directory / name,
                    lambda temporary, name=name: shutil.copyfile(checkpoint / name, temporary),
                )
        if rank == 0:
            print({"event": "restored_completed_epoch", "epoch": state["epoch"],
                   "step": state["step"], "manifest": manifest["epoch"]}, flush=True)
    else:
        scheduler = make_scheduler(optimizer, initial, updates_per_epoch)
        if rank == 0:
            print({"event": "fresh_initialization", "resume_requested": resume}, flush=True)
    restored_epoch = state["epoch"]
    model_digests = gather(state_digest(trainable_state(raw_model)))
    if len(set(model_digests)) != 1:
        raise ValueError("Restored rank models differ.")
    reason = "validation_patience" if stopping.stale_epochs >= initial.patience else "replay_epoch_limit"
    for epoch in range(state["epoch"] + 1, 8):
        if stopping.stale_epochs >= initial.patience:
            break
        phase = "initial" if epoch == 1 else "continuation"
        config = initial if epoch == 1 else continuation
        if epoch == 2:
            # This occurs after restoring epoch one's optimizer and linear scheduler.
            # Preserve AdamW moments, but start the historical constant-rate phase.
            scheduler = make_scheduler(optimizer, continuation, updates_per_epoch)
            stopping.stale_epochs = 0
        model.train()
        order = torch.randperm(len(training.rows), generator=generator)
        order_sha256 = state_digest({"order": order})
        if len(set(gather(order_sha256))) != 1:
            raise ValueError("Global permutations differ across ranks.")
        epoch_started = time.monotonic()
        local_error, norms = 0.0, []
        before_tokens = training.nonpadding_tokens
        for start in range(0, len(order), config.batch_size):
            timed_out = (
                state["phase_seconds"][phase] + time.monotonic() - epoch_started
                >= config.max_seconds
            ) if rank == 0 else None
            if broadcast(timed_out, rank):
                raise TimeoutError("The phase budget ended; resume only a committed epoch.")
            effective = order[start : start + config.batch_size]
            update = distributed_optimizer_step(
                model, training, targets, effective, optimizer, scheduler,
                rank=rank, world_size=2, microbatch_size=config.microbatch_size,
            )
            state["step"] += 1
            local_error += update["local_squared_error"]
            norms.append(update["gradient_norm"])
            if rank == 0 and (
                state["step"] in {1, 220}
                or state["step"] == restored_epoch * updates_per_epoch + 1
                or state["step"] % 25 == 0
            ):
                progress = {
                    "status": "training", "event": "optimizer_step", "rank": rank,
                    "epoch": epoch, "step": state["step"],
                    "updates_per_epoch": updates_per_epoch,
                    "learning_rates": update["learning_rates"],
                    "execution": "external_pytorch_ddp", "native_train_receipt": False,
                }
                print(progress, flush=True)
                atomic_json(directory / "status.json", progress)
        torch.cuda.synchronize()
        fit_seconds = time.monotonic() - epoch_started
        totals = torch.tensor(
            [local_error, training.nonpadding_tokens - before_tokens],
            dtype=torch.float64, device=initial.device,
        )
        dist.all_reduce(totals, op=dist.ReduceOp.SUM)
        validation_started = time.monotonic()
        if rank == 0:
            rows = predict_pairs(raw_model, validation, config.microbatch_size)
            diagnostics = summarize(rows)
            validation_seconds = time.monotonic() - validation_started
        else:
            rows, diagnostics, validation_seconds = None, None, None
        diagnostics, validation_seconds = broadcast(
            (diagnostics, validation_seconds), rank
        )
        score = diagnostics["spearman"] if diagnostics["spearman"] is not None else -1.0
        exhausted = stopping.observe(score)
        if state["selected"] is None or ranking_value(diagnostics) > ranking_value(
            state["selected"]["validation"]
        ):
            if rank == 0:
                atomic_file(
                    directory / "best_model.pt",
                    lambda temporary: save_neural(
                        temporary, raw_model, config, epoch, state["step"]
                    ),
                )
                atomic_json(directory / "best_validation_predictions.json", rows)
                selected = {
                    "epoch": epoch, "step": state["step"],
                    "sha256": file_sha256(directory / "best_model.pt"),
                    "validation": diagnostics,
                }
            else:
                selected = None
            state["selected"] = broadcast(selected, rank)
        if rank == 0:
            state["phase_seconds"][phase] += time.monotonic() - epoch_started
            state["epoch"], state["phase"] = epoch, phase
            state["stale_epochs"] = stopping.stale_epochs
            state["history"].append({
                "epoch": epoch, "step": state["step"],
                "training_mse_0_1": float(totals[0]) / len(training.rows),
                "validation": diagnostics, "fit_seconds": fit_seconds,
                "validation_seconds": validation_seconds,
                "learning_rates": scheduler.get_last_lr(),
                "batch_order_sha256": order_sha256,
                "mean_preclip_gradient_norm": float(np.mean(norms)),
                "training_nonpadding_input_tokens": int(totals[1]),
                "epochs_without_improvement": stopping.stale_epochs,
            })
        state = broadcast(state, rank)
        save_completed_epoch(
            directory, rank, protocol_sha256, raw_model, config,
            optimizer, scheduler, generator, state,
        )
        if rank == 0:
            print({"event": "committed_epoch", "epoch": epoch, "step": state["step"],
                   "validation_spearman": diagnostics["spearman"]}, flush=True)
        if exhausted:
            reason = "validation_patience"
            break
    state["stop_reason"] = reason
    return state


def execute(root: Path, directory: Path, manifest_path: Path, resume: bool, timeout: int) -> None:
    """Hold exclusive ownership throughout initialization, fitting and scoring."""
    with run_directory_lock(directory):
        execute_worker(root, directory, manifest_path, resume, timeout)


def execute_worker(
    root: Path, directory: Path, manifest_path: Path, resume: bool, timeout: int
) -> None:
    """Coordinate two isolated CUDA processes without creating a native TRAIN claim."""
    rank, world_size = int(os.environ["RANK"]), int(os.environ["WORLD_SIZE"])
    if world_size != 2 or rank not in (0, 1):
        raise ValueError("This command requires RANK 0/1 and WORLD_SIZE=2.")
    if not torch.cuda.is_available() or torch.cuda.device_count() != 1:
        raise ValueError("Each host must expose exactly its one assigned CUDA GPU.")
    torch.cuda.set_device(0)
    distributed_protocol = load_json(manifest_path)
    if distributed_protocol["execution"] != "external_pytorch_ddp" or distributed_protocol["native_train_receipt"]:
        raise ValueError("The protocol must explicitly declare external distributed execution.")
    if any(
        distributed_protocol.get(key) != expected
        for key, expected in (
            ("world_size", 2), ("global_batch_size", 32),
            ("microbatch_size_per_rank", 2), ("initialization_seed", 7),
            ("global_shuffle_seed", 107),
        )
    ):
        raise ValueError("The distributed protocol changed the declared batch or seed contract.")
    protocol = load_json(root / distributed_protocol["base_protocol"])
    gpu_name = torch.cuda.get_device_name(0)
    settings = replay_settings(root, protocol, gpu_name)
    check_inputs(root, settings[0])
    if subprocess.check_output(["git", "-C", str(root), "status", "--porcelain"], text=True).strip():
        raise ValueError("Commit the reviewed source before model execution.")
    source = {
        "commit": subprocess.check_output(["git", "-C", str(root), "rev-parse", "HEAD"], text=True).strip(),
        "tree": subprocess.check_output(["git", "-C", str(root), "rev-parse", "HEAD^{tree}"], text=True).strip(),
    }
    configs = [
        FitConfig.model_validate({
            **item["encoder"], "seed": item["seed"], **item["fits"]["lora"],
            "kind": "lora", "start_epoch": index,
        })
        for index, item in enumerate(settings)
    ]
    if any(
        config.batch_size != 32 or config.microbatch_size != 2 or config.seed != 7
        for config in configs
    ):
        raise ValueError("The original global batch, microbatch and seed must be retained.")
    common = {
        "distributed_protocol": distributed_protocol,
        "replay_protocol": protocol,
        "settings": settings,
        "source": source,
        "environment_lock_sha256": file_sha256(root / protocol["environment_lockfile"]),
    }
    protocol_sha256 = hashlib.sha256(
        json.dumps(common, sort_keys=True, allow_nan=False).encode()
    ).hexdigest()
    directory.mkdir(parents=True, exist_ok=True)
    identity_path = directory / "identity.json"
    identity = {"rank": rank, "protocol_sha256": protocol_sha256, "protocol": common}
    if identity_path.exists():
        if not resume or load_json(identity_path) != identity:
            raise ValueError("An existing run requires --resume and identical source/protocol.")
    else:
        atomic_json(identity_path, identity)
    runtime = {
        "rank": rank, "hostname": socket.gethostname(), "pid": os.getpid(),
        "gpu": gpu_name, "visible_gpu_count": torch.cuda.device_count(),
        "execution": "external_pytorch_ddp", "native_train_receipt": False,
        "source": source, "protocol_sha256": protocol_sha256,
        "packages": {
            name: importlib.metadata.version(name)
            for name in ("torch", "transformers", "peft", "numpy", "scipy", "accelerate", "viper-provenance")
        },
        "python": sys.version,
        "cuda_runtime": torch.version.cuda,
        "cuda_visible_devices": os.environ.get("CUDA_VISIBLE_DEVICES"),
        "gpu_memory_bytes": torch.cuda.get_device_properties(0).total_memory,
        "gpu_uuid": str(getattr(torch.cuda.get_device_properties(0), "uuid", "") or ""),
        "rank_rng_policy": distributed_protocol["rank_rng_policy"],
    }
    atomic_json(directory / f"runtime-rank-{rank}.json", runtime)
    dist.init_process_group(
        backend="nccl", init_method="env://", rank=rank, world_size=2,
        timeout=timedelta(seconds=timeout),
    )
    try:
        runtimes = gather(runtime)
        if (
            len({item["protocol_sha256"] for item in runtimes}) != 1
            or runtimes[0]["packages"] != runtimes[1]["packages"]
            or len({item["cuda_runtime"] for item in runtimes}) != 1
            or len({item["python"] for item in runtimes}) != 1
        ):
            raise ValueError("The two workers have different source, input or runtime identities.")
        if runtimes[0]["hostname"] == runtimes[1]["hostname"]:
            first, second = runtimes
            same_gpu = (
                first["gpu_uuid"] == second["gpu_uuid"]
                if first["gpu_uuid"] and second["gpu_uuid"]
                else first["cuda_visible_devices"] == second["cuda_visible_devices"]
            )
            if same_gpu:
                raise ValueError("The two workers must use distinct physical GPUs.")
        atomic_json(directory / "workers.json", runtimes)
        reset_rng(configs[0].seed)
        tokenizer = load_tokenizer(configs[0])
        raw_model = load_backbone(configs[0], adapters=configs[0])
        training = TokenPairs(load_json(root / settings[0]["splits"]["training"]["path"]), configs[0], tokenizer)
        validation = TokenPairs(load_json(root / settings[0]["splits"]["validation"]["path"]), configs[0], tokenizer)
        model = DistributedDataParallel(
            raw_model, device_ids=[0], output_device=0,
            broadcast_buffers=False, find_unused_parameters=False,
        )
        if rank:
            reset_rng(configs[0].seed + rank)
        state = train(
            directory, rank, protocol_sha256, configs, model, training, validation, resume
        )
        if rank == 0:
            selected = load_model(directory / "best_model.pt")
            if file_sha256(directory / "best_model.pt") != state["selected"]["sha256"]:
                raise ValueError("The validation-selected checkpoint changed before test scoring.")
            restore_parameters(raw_model, selected["state"])
            test = TokenPairs(
                load_json(root / settings[0]["splits"]["test"]["path"]), configs[0], tokenizer
            )
            predictions = predict_pairs(raw_model, test, configs[0].microbatch_size)
            atomic_json(directory / "test_predictions.json", predictions)
            scores = summarize(predictions)
            result = {
                "status": "complete", "execution": "external_pytorch_ddp",
                "native_train_receipt": False, "world_size": 2,
                "protocol_sha256": protocol_sha256, "source": source,
                "completed_epochs": state["epoch"], "actual_updates": state["step"],
                "stop_reason": state["stop_reason"], "selected": state["selected"],
                "test": scores, "reference": protocol["baseline"],
                "test_spearman_difference": (
                    scores["spearman"] - protocol["baseline"]["test_spearman"]
                    if scores["spearman"] is not None else None
                ),
                "workers": runtimes,
            }
            atomic_json(directory / "results.json", result)
        else:
            result = None
        result = broadcast(result, rank)
        atomic_json(directory / "status.json", result)
        print({"status": "complete", "rank": rank, "test": result["test"]}, flush=True)
    except BaseException as error:
        atomic_json(directory / "status.json", {
            "status": "failed", "rank": rank,
            "execution": "external_pytorch_ddp", "native_train_receipt": False,
            "error_type": type(error).__name__, "error": str(error),
        })
        raise
    finally:
        dist.destroy_process_group()


def main() -> None:
    """Review by default; execute only in an explicitly configured two-host rendezvous."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--settings", default="configs/csts-lora-condition-order-ddp.json")
    parser.add_argument("--collective-timeout-seconds", type=int, default=600)
    args = parser.parse_args()
    root, directory = args.root.resolve(), args.run_dir.resolve()
    if args.collective_timeout_seconds < 30:
        parser.error("Collective timeout must be at least 30 seconds.")
    if not args.execute:
        print(json.dumps({
            "status": "review", "execution": "external_pytorch_ddp",
            "native_train_receipt": False, "protocol": load_json(root / args.settings),
            "run_dir": str(directory),
        }, indent=2))
        return
    execute(root, directory, root / args.settings, args.resume, args.collective_timeout_seconds)


if __name__ == "__main__":
    main()
