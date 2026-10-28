"""Verify joint gradients, logical batch weighting, state restoration and gating."""

import copy
from types import SimpleNamespace

import pytest
import torch
from torch import nn
from torch.nn import functional as F

from csts_pilot.baseline_models import restore_parameters, state_digest
from csts_pilot.convergence import file_sha256, reset_rng, write_json
from csts_pilot.native_comparison import (
    JointEncoder,
    NativeComparisonConfig,
    fit_joint,
    logical_batch_backward,
    optimizer_for,
    save_joint,
)
from csts_pilot.native_comparison_run import continuation_decision
from jep_pilot.loaders import load_json, load_model


class TinyAdapter(nn.Module):
    def __init__(self):
        super().__init__()
        self.base = nn.Parameter(torch.randn(4, 4), requires_grad=False)
        self.lora_a = nn.Parameter(torch.randn(4, 2) * 0.05)
        self.lora_b = nn.Parameter(torch.randn(2, 4) * 0.05)
        self.dropout = nn.Dropout(0.1)

    def forward(self, x):
        return x @ self.base + self.dropout(x) @ self.lora_a @ self.lora_b


class TinyPairs:
    def __init__(self, rows, left, right):
        self.rows, self.left, self.right = rows, left, right

    def vectors(self, model, indices):
        return (
            F.normalize(model.backbone(self.left[indices]), dim=-1),
            F.normalize(model.backbone(self.right[indices]), dim=-1),
        )

    def scores(self, model, indices):
        return model.comparison(*self.vectors(model, indices))


def fixture_data():
    reset_rng(611)
    left, right = torch.randn(7, 4), torch.randn(7, 4)
    rows = [
        {
            "row_id": str(i),
            "group_id": str(i // 2),
            "pair_id": str(i // 2),
            "condition": f"condition {i}",
            "sentence1": f"first {i}",
            "sentence2": f"second {i}",
            "rating": float(i % 5 + 1),
            "target": (i % 5) / 4,
        }
        for i in range(7)
    ]
    return TinyPairs(rows, left, right)


def config_for(tmp_path, **changes):
    data = fixture_data()
    for name in ("training", "validation"):
        write_json(tmp_path / f"{name}.json", data.rows)
    return NativeComparisonConfig(
        device="cpu",
        embedding_dimension=4,
        max_epochs=3,
        patience=10,
        batch_size=5,
        microbatch_size=2,
        encode_batch_size=3,
        autotune_microbatch=False,
        training_sha256=file_sha256(tmp_path / "training.json"),
        validation_sha256=file_sha256(tmp_path / "validation.json"),
        **changes,
    )


def test_comparison_gradient_and_checkpoint_include_both_components(tmp_path):
    cfg = config_for(tmp_path)
    data = fixture_data()
    model = JointEncoder(TinyAdapter(), 4).eval()
    ids = torch.arange(7)
    left, right = data.vectors(model, ids)
    torch.testing.assert_close(
        model.comparison(left, right), (left * right).sum(-1), rtol=0, atol=0
    )
    targets = torch.tensor([r["target"] for r in data.rows])
    logical_batch_backward(model, data, ids, targets, 2)
    assert model.backbone.base.grad is None
    assert model.backbone.lora_a.grad.norm() > 0
    assert model.backbone.lora_b.grad.norm() > 0
    assert model.comparison.residual.weight.grad.norm() > 0
    before = model.backbone.base.detach().clone()
    optimizer = optimizer_for(model, cfg)
    assert [g["lr"] for g in optimizer.param_groups] == [0.00002, 0.001]
    optimizer.step()
    torch.testing.assert_close(before, model.backbone.base, rtol=0, atol=0)
    predicted = data.scores(model, ids).detach()
    save_joint(tmp_path / "model.pt", model, cfg, 1, 1)
    restored = copy.deepcopy(model)
    with torch.no_grad():
        for parameter in restored.parameters():
            if parameter.requires_grad:
                parameter.zero_()
    restore_parameters(restored, load_model(tmp_path / "model.pt")["state"])
    torch.testing.assert_close(data.scores(restored, ids), predicted, rtol=0, atol=0)
    torch.testing.assert_close(
        restored.comparison(left, right),
        restored.comparison(right, left),
        rtol=0,
        atol=0,
    )


@pytest.mark.parametrize("count", [7, 2])
def test_partial_logical_batch_matches_unsplit_gradients(count):
    data = fixture_data()
    model = JointEncoder(TinyAdapter(), 4).eval()
    full, split = copy.deepcopy(model), copy.deepcopy(model)
    ids = torch.arange(count)
    target = torch.tensor([r["target"] for r in data.rows])
    logical_batch_backward(full, data, ids, target, count)
    logical_batch_backward(split, data, ids, target, 3)
    for (name, a), (_, b) in zip(
        full.named_parameters(), split.named_parameters(), strict=True
    ):
        if a.requires_grad:
            torch.testing.assert_close(a.grad, b.grad, atol=2e-7, rtol=2e-6, msg=name)


def context_for(path, cfg, parent=None):
    path.mkdir()
    inputs = {name: path.parent / f"{name}.json" for name in ("training", "validation")}
    if parent is not None:
        inputs.update(
            {
                "parent_" + name: parent.outputs[name]
                for name in (
                    "last_model",
                    "model",
                    "validation_predictions",
                    "initial_vectors",
                )
            }
        )
        inputs["parent_resume"] = parent.outputs["resume_state"]
    outputs = {
        name: path / filename
        for name, filename in (
            ("model", "model.pt"),
            ("last_model", "last.pt"),
            ("validation_predictions", "predictions.json"),
            ("initial_vectors", "vectors.pt"),
            ("resume_state", "resume.pt"),
            ("trace", "trace.json"),
            ("checkpoint_receipts", "receipts.json"),
        )
    }
    return SimpleNamespace(
        config=cfg,
        inputs=inputs,
        outputs=outputs,
        numpy_generators={},
        metrics={
            name: SimpleNamespace(record=lambda *a, **k: None)
            for name in ("training_objective", "validation_mse", "validation_spearman")
        },
    )


@pytest.mark.parametrize("autotune", [False, True])
def test_epoch_resume_reproduces_weights_optimizer_and_batch_order(
    tmp_path, monkeypatch, autotune
):
    cfg = config_for(tmp_path).model_copy(update={"autotune_microbatch": autotune})
    if autotune:

        def profile(*args):
            reset_rng(990)
            return cfg.microbatch_size, []

        monkeypatch.setattr("csts_pilot.native_comparison.tune_microbatch", profile)
    data = fixture_data()
    reset_rng(7)
    initial = JointEncoder(TinyAdapter(), 4)
    full_context = context_for(tmp_path / "full", cfg)
    fit_joint(full_context, copy.deepcopy(initial), data, data)
    first_context = context_for(
        tmp_path / "first", cfg.model_copy(update={"max_epochs": 1})
    )
    fit_joint(first_context, copy.deepcopy(initial), data, data)
    resumed_context = context_for(
        tmp_path / "resumed", cfg.model_copy(update={"start_epoch": 1}), first_context
    )
    fit_joint(resumed_context, copy.deepcopy(initial), data, data)
    full, resumed = (
        load_model(c.outputs["last_model"]) for c in (full_context, resumed_context)
    )
    assert state_digest(full["state"]) == state_digest(resumed["state"])
    assert full["step"] == resumed["step"] == 6
    traces = [load_json(c.outputs["trace"]) for c in (full_context, resumed_context)]
    assert [e["batch_order_sha256"] for e in traces[0]["epochs"]] == [
        e["batch_order_sha256"] for e in traces[1]["epochs"]
    ]
    assert traces[0]["selected"]["epoch"] == traces[1]["selected"]["epoch"]


def test_continuation_requires_strict_validation_improvement():
    data = fixture_data().rows
    control = [dict(r, prediction=r["target"]) for r in data]
    equal = continuation_decision(control, control, data)
    assert equal["follow_on_seeds"] == []
    weak = [dict(r, prediction=float(i)) for i, r in enumerate(data)]
    positive = continuation_decision(control, weak, data)
    assert positive["follow_on_seeds"] == [8, 9]
    assert positive["test_scores_used"] is False
    changed = copy.deepcopy(data)
    changed[0]["sentence1"] += " changed"
    with pytest.raises(ValueError, match="differs"):
        continuation_decision(control, weak, changed)
