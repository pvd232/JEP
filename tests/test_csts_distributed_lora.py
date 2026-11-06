"""Observe real distributed gradients, epoch-boundary recovery, and replay clocks."""

import copy
import hashlib
import json
import math
import random
from datetime import timedelta
from pathlib import Path
from typing import Any

import numpy as np
import pytest
import torch
import torch.distributed as dist
import torch.multiprocessing as mp
from torch import nn
from torch.nn import functional as F
from torch.nn.parallel import DistributedDataParallel
from viper.resume import load_resume_state, save_resume_state

from csts_pilot import ddp_order_replay as replay
from csts_pilot.baseline_models import FitConfig
from csts_pilot.distributed_lora import (
    capture_training_state,
    distributed_optimizer_step,
    make_scheduler,
    rank_microbatches,
    restore_training_state,
    validate_checkpoint_receipts,
)


class ToyPairs:
    """Expose a small differentiable score through the production pairs interface."""

    def __init__(self, features: torch.Tensor) -> None:
        self.features = features

    def scores(self, model: nn.Module, indices: torch.Tensor) -> torch.Tensor:
        return model(self.features[indices]).squeeze(-1)


@pytest.fixture(autouse=True)
def cpu_test_runtime(monkeypatch: pytest.MonkeyPatch):
    """Keep these integration checks on CPU and bound worker thread pools."""
    monkeypatch.setenv("CUDA_VISIBLE_DEVICES", "")
    monkeypatch.setenv("OMP_NUM_THREADS", "1")
    monkeypatch.setenv("MKL_NUM_THREADS", "1")
    original_threads = torch.get_num_threads()
    torch.set_num_threads(1)
    yield
    torch.set_num_threads(original_threads)


def _config(**overrides: Any) -> FitConfig:
    """Retain the original optimizer and horizon while using offline toy inputs."""
    values = {
        "kind": "lora",
        "device": "cpu",
        "seed": 7,
        "learning_rate": 2e-5,
        "batch_size": 32,
        "microbatch_size": 2,
        "max_epochs": 24,
        "stop_after_epoch": 1,
        "patience": 5,
        "weight_decay": 0.01,
        "schedule": "linear",
        "warmup_fraction": 0.1,
    }
    return FitConfig(**{**values, **overrides})


def _features_and_targets(rows: int, scale: float) -> tuple[torch.Tensor, torch.Tensor]:
    """Give alternating shards different gradient directions and magnitudes."""
    row = torch.arange(rows, dtype=torch.float64)
    features = torch.stack((row.remainder(5) - 2, row.remainder(7) - 3, row.cos()), dim=1)
    targets = 0.4 * features[:, 0] - 0.2 * features[:, 1] + row.sin()
    return scale * features, scale * targets


def _assert_nested_equal(actual: Any, expected: Any) -> None:
    """Compare tensor-valued optimizer state without weakening exact resume checks."""
    if isinstance(expected, torch.Tensor):
        torch.testing.assert_close(actual, expected, rtol=0, atol=0)
    elif isinstance(expected, dict):
        assert actual.keys() == expected.keys()
        for key in expected:
            _assert_nested_equal(actual[key], expected[key])
    elif isinstance(expected, (list, tuple)):
        assert len(actual) == len(expected)
        for actual_item, expected_item in zip(actual, expected, strict=True):
            _assert_nested_equal(actual_item, expected_item)
    else:
        assert actual == expected


def _gradient_case(rank: int, rows: int, scale: float) -> dict[str, float]:
    """Compare the actual distributed update with a separate serial mean-loss update."""
    features, targets = _features_and_targets(rows, scale)
    reference = nn.Linear(3, 1).double()
    with torch.no_grad():
        reference.weight.copy_(torch.tensor([[0.2, -0.3, 0.1]], dtype=torch.float64))
        reference.bias.fill_(0.05)
    model = DistributedDataParallel(copy.deepcopy(reference))
    optimizer = torch.optim.SGD(model.parameters(), lr=0.1)
    config = _config(learning_rate=0.1, schedule="constant", warmup_fraction=0)
    scheduler = make_scheduler(optimizer, config, updates_per_epoch=1)

    reference_optimizer = torch.optim.SGD(reference.parameters(), lr=0.1)
    reference_loss = F.mse_loss(reference(features).squeeze(-1).float(), targets.float())
    reference_loss.backward()
    reference_norm = nn.utils.clip_grad_norm_(reference.parameters(), 1.0)
    reference_gradients = [parameter.grad.clone() for parameter in reference.parameters()]
    reference_optimizer.step()

    record = distributed_optimizer_step(
        model, ToyPairs(features), targets, torch.arange(rows), optimizer, scheduler,
        rank=rank, world_size=2, microbatch_size=2,
    )
    for actual, expected, expected_gradient in zip(
        model.module.parameters(), reference.parameters(), reference_gradients, strict=True
    ):
        torch.testing.assert_close(actual, expected, rtol=1e-7, atol=1e-9)
        torch.testing.assert_close(actual.grad, expected_gradient, rtol=1e-7, atol=1e-9)
    assert record["gradient_norm"] == pytest.approx(float(reference_norm), rel=1e-7, abs=1e-9)
    squared_error = torch.tensor(record["local_squared_error"], dtype=torch.float64)
    dist.all_reduce(squared_error)
    assert float(squared_error / rows) == pytest.approx(float(reference_loss), rel=1e-6)
    return {"scale": scale, "preclip_norm": float(reference_norm)}


def _future_draws() -> dict[str, Any]:
    """Observe all process-global random streams used by the continuation state."""
    return {
        "python": [random.random() for _ in range(3)],
        "numpy": np.random.random(3).tolist(),
        "torch": torch.rand(3).tolist(),
    }


def _dropout_model() -> nn.Module:
    """Exercise rank-local random masks with a tiny offline model."""
    return nn.Sequential(nn.Linear(3, 5), nn.Tanh(), nn.Dropout(0.35), nn.Linear(5, 1)).double()


def _resume_case(rank: int, directory: Path) -> dict[str, Any]:
    """Match an interrupted continuation to its uninterrupted two-rank counterpart."""
    torch.manual_seed(7)
    model = DistributedDataParallel(_dropout_model())
    optimizer = torch.optim.AdamW(model.parameters(), lr=2e-5, weight_decay=0.01)
    initial = _config()
    scheduler = make_scheduler(optimizer, initial, updates_per_epoch=2)
    generator = torch.Generator().manual_seed(107)
    features, targets = _features_and_targets(36, 0.2)
    pairs = ToyPairs(features)
    random.seed(900 + rank)
    np.random.seed(900 + rank)
    torch.manual_seed(900 + rank)
    first_order = torch.randperm(36, generator=generator)
    for effective in first_order.split(32):
        distributed_optimizer_step(
            model, pairs, targets, effective, optimizer, scheduler,
            rank=rank, world_size=2, microbatch_size=2,
        )

    canonical = directory / "canonical_model.pt"
    if rank == 0:
        torch.save(model.module.state_dict(), canonical)
    dist.barrier()
    model_digest = hashlib.sha256(canonical.read_bytes()).hexdigest()
    state = capture_training_state(
        optimizer, scheduler, generator, epoch=1, step=2, model_sha256=model_digest
    )
    saved_path = directory / f"resume_rank_{rank}.pt"
    save_resume_state(saved_path, state)
    dist.barrier()

    continuation = _config(start_epoch=1, stop_after_epoch=7, schedule="constant", warmup_fraction=0)
    scheduler = make_scheduler(optimizer, continuation, updates_per_epoch=2)
    assert optimizer.param_groups[0]["lr"] == 2e-5
    second_order = torch.randperm(36, generator=generator)
    for effective in second_order.split(32):
        distributed_optimizer_step(
            model, pairs, targets, effective, optimizer, scheduler,
            rank=rank, world_size=2, microbatch_size=2,
        )
    reference_model = copy.deepcopy(model.module.state_dict())
    reference_optimizer = copy.deepcopy(optimizer.state_dict())
    reference_draws = _future_draws()
    reference_next_order = torch.randperm(36, generator=generator)

    restarted_model = _dropout_model()
    restarted_model.load_state_dict(torch.load(canonical, weights_only=True))
    restarted_model = DistributedDataParallel(restarted_model)
    restarted_optimizer = torch.optim.AdamW(restarted_model.parameters(), lr=2e-5, weight_decay=0.01)
    restarted_scheduler = make_scheduler(restarted_optimizer, initial, updates_per_epoch=2)
    restarted_generator = torch.Generator().manual_seed(999)
    random.random()
    np.random.random(17 + rank)
    torch.rand(17 + rank)

    restored = load_resume_state(saved_path)
    restore_training_state(restored, restarted_optimizer, restarted_scheduler, restarted_generator)
    assert all(float(item["step"]) == 2 for item in restarted_optimizer.state.values())
    restarted_scheduler = make_scheduler(restarted_optimizer, continuation, updates_per_epoch=2)
    assert restarted_optimizer.param_groups[0]["lr"] == 2e-5
    replay_order = torch.randperm(36, generator=restarted_generator)
    torch.testing.assert_close(replay_order, second_order, rtol=0, atol=0)
    for effective in replay_order.split(32):
        distributed_optimizer_step(
            restarted_model, pairs, targets, effective, restarted_optimizer, restarted_scheduler,
            rank=rank, world_size=2, microbatch_size=2,
        )
    _assert_nested_equal(restarted_model.module.state_dict(), reference_model)
    _assert_nested_equal(restarted_optimizer.state_dict(), reference_optimizer)
    assert _future_draws() == reference_draws
    torch.testing.assert_close(
        torch.randperm(36, generator=restarted_generator), reference_next_order, rtol=0, atol=0
    )
    assert all(float(item["step"]) == 4 for item in restarted_optimizer.state.values())
    return {"rank": rank, "next_order": reference_next_order.tolist(), "draws": reference_draws, "step": 4}


def _distributed_worker(rank: int, directory_name: str, mode: str, rows: int) -> None:
    """Run the production helpers under an actual two-process Gloo group."""
    directory = Path(directory_name)
    torch.set_num_threads(1)
    dist.init_process_group(
        "gloo", init_method=(directory / "rendezvous").as_uri(), rank=rank, world_size=2,
        timeout=timedelta(seconds=60),
    )
    try:
        if mode == "gradients":
            cases = [_gradient_case(rank, rows, scale) for scale in (0.02, 20.0)]
            result = {"rank": rank, "rows": rows, "cases": cases}
        else:
            result = _resume_case(rank, directory)
        (directory / f"rank_{rank}.json").write_text(json.dumps(result))
    finally:
        dist.destroy_process_group()


def _run_two_ranks(directory: Path, mode: str, rows: int = 0) -> list[dict[str, Any]]:
    """Require real collectives rather than mocking synchronization away."""
    assert dist.is_available() and dist.is_gloo_available(), "The distributed checks require Gloo."
    mp.spawn(_distributed_worker, args=(str(directory), mode, rows), nprocs=2, join=True)
    return [json.loads((directory / f"rank_{rank}.json").read_text()) for rank in range(2)]


def test_rank_microbatches_preserve_global_order_and_four_example_tail() -> None:
    """Preserve every original consecutive microbatch in its alternating rank."""
    effective = torch.tensor([7, 2, 9, 1, 0, 5, 8, 4])
    assert [batch.tolist() for batch in rank_microbatches(effective, 2, 0, 2)] == [[7, 2], [0, 5]]
    assert [batch.tolist() for batch in rank_microbatches(effective, 2, 1, 2)] == [[9, 1], [8, 4]]
    generator = torch.Generator().manual_seed(107)
    order = torch.randperm(6980, generator=generator)
    reconstructed = []
    for effective in order.split(32):
        first = rank_microbatches(effective, 2, 0, 2)
        second = rank_microbatches(effective, 2, 1, 2)
        for first_batch, second_batch in zip(first, second, strict=True):
            reconstructed.extend((first_batch, second_batch))
    torch.testing.assert_close(torch.cat(reconstructed), order, rtol=0, atol=0)
    assert [len(batch) for batch in reconstructed[-2:]] == [2, 2]


def test_rank_microbatches_reject_unequal_collective_counts() -> None:
    """Fail before a rank can enter a backward collective without its peer."""
    with pytest.raises(ValueError, match="same number"):
        rank_microbatches(torch.arange(2), 2, 0, 2)


@pytest.mark.parametrize("rows", [32, 4], ids=["full_global_batch", "four_example_tail"])
def test_real_gloo_gradients_match_serial_mean_before_and_after_clipping(tmp_path: Path, rows: int) -> None:
    """Catch wrong W/N scaling and clipping before the cross-rank reduction."""
    reports = _run_two_ranks(tmp_path, "gradients", rows)
    for report in reports:
        assert report["rows"] == rows
        assert report["cases"][0]["preclip_norm"] < 1
        assert report["cases"][1]["preclip_norm"] > 1


def test_real_gloo_resume_preserves_each_rank_rng_optimizer_and_global_sampler(tmp_path: Path) -> None:
    """Reproduce the next complete epoch after a shared completed-epoch checkpoint."""
    reports = _run_two_ranks(tmp_path, "resume")
    assert reports[0]["next_order"] == reports[1]["next_order"]
    assert reports[0]["draws"] != reports[1]["draws"]
    assert [report["step"] for report in reports] == [4, 4]


def test_initial_horizon_and_constant_continuation_keep_optimizer_clock(tmp_path: Path) -> None:
    """Retain 526 warmup updates and 5,256 planned updates despite the one-epoch cap."""
    config = _config()
    parameter = nn.Parameter(torch.tensor([0.3], dtype=torch.float64))
    optimizer = torch.optim.AdamW([parameter], lr=2e-5, weight_decay=0.01)
    updates_per_epoch = math.ceil(6980 / 32)
    scheduler = make_scheduler(optimizer, config, updates_per_epoch)
    assert updates_per_epoch == 219
    assert optimizer.param_groups[0]["lr"] == 0
    for _ in range(updates_per_epoch):
        parameter.grad = torch.ones_like(parameter)
        optimizer.step()
        scheduler.step()
    assert optimizer.param_groups[0]["lr"] == pytest.approx(2e-5 * 219 / 526)
    assert float(optimizer.state[parameter]["step"]) == 219
    generator = torch.Generator().manual_seed(107)
    path = tmp_path / "epoch_one_resume.pt"
    save_resume_state(
        path, capture_training_state(
            optimizer, scheduler, generator, epoch=1, step=219, model_sha256="a" * 64
        )
    )

    resumed_parameter = nn.Parameter(parameter.detach().clone())
    resumed_optimizer = torch.optim.AdamW([resumed_parameter], lr=2e-5, weight_decay=0.01)
    resumed_scheduler = make_scheduler(resumed_optimizer, config, updates_per_epoch)
    restore_training_state(load_resume_state(path), resumed_optimizer, resumed_scheduler, generator)
    assert float(resumed_optimizer.state[resumed_parameter]["step"]) == 219
    assert resumed_optimizer.param_groups[0]["lr"] == pytest.approx(2e-5 * 219 / 526)
    continuation = _config(start_epoch=1, stop_after_epoch=7, schedule="constant", warmup_fraction=0)
    resumed_scheduler = make_scheduler(resumed_optimizer, continuation, updates_per_epoch)
    for _ in range((7 - 1) * updates_per_epoch):
        assert resumed_optimizer.param_groups[0]["lr"] == 2e-5
        resumed_parameter.grad = torch.ones_like(resumed_parameter)
        resumed_optimizer.step()
        resumed_scheduler.step()
    assert float(resumed_optimizer.state[resumed_parameter]["step"]) == 1533
    assert resumed_optimizer.param_groups[0]["lr"] == 2e-5


def _checkpoint_receipts() -> list[dict[str, Any]]:
    """Describe two complete rank artifacts at one shared epoch boundary."""
    receipts = []
    for rank in range(2):
        files = {name: {"sha256": "b" * 64, "bytes": 128} for name in ["model.pt", "resume.pt", "state.json"]}
        if rank == 0:
            files.update({name: {"sha256": "c" * 64, "bytes": 128} for name in ["best_model.pt", "best_validation_predictions.json"]})
        receipts.append({
            "rank": rank, "epoch": 1, "step": 219, "protocol_sha256": "9" * 64,
            "model_state_sha256": "a" * 64, "directory": f"epochs/epoch-0001-rank{rank}", "files": files,
        })
    return receipts


def test_complete_checkpoint_receipts_share_one_epoch() -> None:
    """Accept a complete two-rank checkpoint including the controller's incumbent."""
    validate_checkpoint_receipts(_checkpoint_receipts(), world_size=2, epoch=1, step=219, protocol_sha256="9" * 64)


@pytest.mark.parametrize(
    "damage",
    ["missing_rank", "mixed_epoch", "mixed_step", "mixed_protocol", "missing_resume", "model_divergence", "missing_selection"],
)
def test_incomplete_or_mixed_checkpoint_cannot_commit(damage: str) -> None:
    """Reject recovery states that cannot reproduce one completed global epoch."""
    receipts = _checkpoint_receipts()
    if damage == "missing_rank":
        receipts.pop()
    elif damage == "mixed_epoch":
        receipts[1]["epoch"] = 2
    elif damage == "mixed_step":
        receipts[1]["step"] = 218
    elif damage == "mixed_protocol":
        receipts[1]["protocol_sha256"] = "8" * 64
    elif damage == "missing_resume":
        del receipts[1]["files"]["resume.pt"]
    elif damage == "model_divergence":
        receipts[1]["model_state_sha256"] = "d" * 64
    else:
        del receipts[0]["files"]["best_model.pt"]
    with pytest.raises(ValueError):
        validate_checkpoint_receipts(receipts, world_size=2, epoch=1, step=219, protocol_sha256="9" * 64)


@pytest.mark.parametrize("digest", ["", "g" * 64], ids=["empty", "non_hexadecimal"])
def test_checkpoint_receipts_require_valid_model_state_identity(digest: str) -> None:
    """Equal invalid model identities cannot certify synchronized replicas."""
    receipts = _checkpoint_receipts()
    for receipt in receipts:
        receipt["model_state_sha256"] = digest
    with pytest.raises(ValueError):
        validate_checkpoint_receipts(
            receipts, world_size=2, epoch=1, step=219, protocol_sha256="9" * 64
        )


def _write_checkpoint_fixture(
    roots: list[Path], epoch: int, label: str, committed_ranks: tuple[int, ...] = (0, 1)
) -> tuple[str, dict[str, Any]]:
    """Create real immutable files and one manifest that may reach only one host."""
    receipts = []
    model_bytes = f"model epoch={epoch} branch={label}".encode()
    for rank, root in enumerate(roots):
        directory = Path("epochs") / f"epoch-{epoch:04d}-{label}-rank{rank}"
        checkpoint = root / directory
        checkpoint.mkdir(parents=True)
        contents = {
            "model.pt": model_bytes,
            "resume.pt": f"optimizer and RNG for rank {rank}, epoch {epoch}, {label}".encode(),
            "state.json": json.dumps({"epoch": epoch, "step": epoch * 219}).encode(),
        }
        if rank == 0:
            contents.update({
                "best_model.pt": model_bytes,
                "best_validation_predictions.json": b"[]",
            })
        for name, data in contents.items():
            (checkpoint / name).write_bytes(data)
        receipts.append({
            "rank": rank,
            "epoch": epoch,
            "step": epoch * 219,
            "protocol_sha256": "9" * 64,
            "model_state_sha256": hashlib.sha256(model_bytes).hexdigest(),
            "directory": str(directory),
            "files": {name: replay.file_record(checkpoint / name) for name in contents},
        })
    manifest = {
        "schema_version": 1,
        "execution": "external_pytorch_ddp",
        "native_train_receipt": False,
        "epoch": epoch,
        "step": epoch * 219,
        "protocol_sha256": "9" * 64,
        "receipts": receipts,
    }
    digest = hashlib.sha256(
        json.dumps(manifest, sort_keys=True, allow_nan=False).encode()
    ).hexdigest()
    name = f"epoch-{epoch:04d}-{digest}.json"
    for rank in committed_ranks:
        replay.atomic_json(roots[rank] / "committed" / name, manifest)
    return name, manifest


def _manifest_inventory(root: Path) -> dict[str, str]:
    """Represent exactly the manifest identities exchanged by the two hosts."""
    return {
        path.name: hashlib.sha256(path.read_bytes()).hexdigest()
        for path in (root / "committed").glob("epoch-*.json")
    }


def _choose_checkpoint(
    roots: list[Path], rank: int, monkeypatch: pytest.MonkeyPatch
) -> tuple[Path | None, dict[str, Any] | None]:
    """Supply peer inventories while retaining production selection and byte checks."""
    def gathered(local: dict[str, str]) -> list[dict[str, str]]:
        assert local == _manifest_inventory(roots[rank])
        return [_manifest_inventory(root) for root in roots]

    monkeypatch.setattr(replay, "gather", gathered)
    return replay.committed_checkpoint(roots[rank], rank, "9" * 64, resume=True)


def test_resume_ignores_one_sided_commit_and_accepts_same_epoch_retry(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Recover the last common epoch, then retain the retry beside the orphan."""
    roots = [tmp_path / f"rank{rank}" for rank in range(2)]
    _, first = _write_checkpoint_fixture(roots, 1, "shared")
    orphan_name, _ = _write_checkpoint_fixture(roots, 2, "interrupted", (0,))
    for rank in range(2):
        checkpoint, manifest = _choose_checkpoint(roots, rank, monkeypatch)
        assert manifest == first
        assert checkpoint == roots[rank] / first["receipts"][rank]["directory"]

    retry_name, retry = _write_checkpoint_fixture(roots, 2, "retry")
    assert retry_name != orphan_name
    for rank in range(2):
        checkpoint, manifest = _choose_checkpoint(roots, rank, monkeypatch)
        assert manifest == retry
        assert checkpoint == roots[rank] / retry["receipts"][rank]["directory"]
    assert (roots[0] / "committed" / orphan_name).is_file()
    assert not (roots[1] / "committed" / orphan_name).exists()


@pytest.mark.parametrize("damage", ["manifest_bytes", "local_artifact"])
def test_resume_rejects_divergent_manifest_or_changed_local_artifact(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, damage: str
) -> None:
    """A common filename is insufficient when its bytes or rank state differ."""
    roots = [tmp_path / f"rank{rank}" for rank in range(2)]
    name, manifest = _write_checkpoint_fixture(roots, 1, "shared")
    if damage == "manifest_bytes":
        path = roots[1] / "committed" / name
        path.write_bytes(path.read_bytes() + b"\n")
        message = "manifests disagree"
    else:
        path = roots[1] / manifest["receipts"][1]["directory"] / "resume.pt"
        path.write_bytes(path.read_bytes() + b"changed")
        message = "artifact changed"
    with pytest.raises(ValueError, match=message):
        _choose_checkpoint(roots, 1, monkeypatch)


def _compete_for_run_lock(directory_name: str, replies: Any, retry: Any) -> None:
    """Try ownership while the original worker lives, then after it releases."""
    directory = Path(directory_name)
    try:
        with replay.run_directory_lock(directory):
            replies.put("acquired")
    except RuntimeError as error:
        replies.put(str(error))
    if not retry.wait(timeout=60):
        raise RuntimeError("The test owner did not release its lock.")
    with replay.run_directory_lock(directory):
        replies.put("acquired_after_release")


def test_run_directory_allows_only_one_live_worker(tmp_path: Path) -> None:
    """Reject a competing process without altering the current worker's status."""
    status = tmp_path / "status.json"
    status_bytes = b'{"status": "training", "owner": "first"}\n'
    status.write_bytes(status_bytes)
    context = mp.get_context("spawn")
    replies = context.Queue()
    retry = context.Event()
    competitor = context.Process(
        target=_compete_for_run_lock, args=(str(tmp_path), replies, retry)
    )
    try:
        with replay.run_directory_lock(tmp_path):
            competitor.start()
            assert replies.get(timeout=60) == (
                "The run directory is already owned by another worker."
            )
            assert status.read_bytes() == status_bytes
        retry.set()
        assert replies.get(timeout=30) == "acquired_after_release"
        competitor.join(timeout=30)
        assert competitor.exitcode == 0
        assert status.read_bytes() == status_bytes
    finally:
        retry.set()
        if competitor.is_alive():
            competitor.terminate()
            competitor.join(timeout=10)
        replies.close()
        replies.join_thread()
