"""Check the approved loss math, matched training and pre-test selection rules."""

import json
from collections import defaultdict
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest
import torch
from transformers import T5Config, T5ForConditionalGeneration

from csts_pilot import convergence, convergence_run
from csts_pilot.convergence_analysis import (
    affine_fit,
    calibration,
    metrics,
    paired_intervals,
)
from csts_pilot.joint import AnswerEncoder, rating_loss
from jep_pilot.loaders import load_model, load_state


def tiny_backbone():
    """Exercise real T5 gradients without downloading model weights."""
    return T5ForConditionalGeneration(
        T5Config(
            vocab_size=24,
            d_model=16,
            d_ff=32,
            num_layers=1,
            num_decoder_layers=1,
            num_heads=2,
            d_kv=8,
            dropout_rate=0.1,
            pad_token_id=0,
            eos_token_id=1,
            decoder_start_token_id=0,
        )
    )


def test_mse_values_and_gradients():
    scores = torch.tensor([0.1, 0.4, 0.8], requires_grad=True)
    targets = torch.tensor([0.0, 0.5, 1.0])
    loss = rating_loss(scores, targets, "mse")
    torch.testing.assert_close(loss, torch.tensor(0.02))
    (gradient,) = torch.autograd.grad(loss, scores)
    torch.testing.assert_close(gradient, 2 * (scores - targets) / 3)


def test_pearson_values_and_analytic_gradients():
    scores = torch.tensor([0.0, 1.0, 2.0], requires_grad=True)
    targets = torch.tensor([2.0, 0.0, 1.0])
    loss = rating_loss(scores, targets, "pearson")
    torch.testing.assert_close(loss, torch.tensor(1.5))
    u, v = scores.detach() - 1, targets - 1
    numerator, score_variance = (u * v).sum(), u.square().sum() + 1e-8
    denominator = score_variance.sqrt() * (v.square().sum() + 1e-8).sqrt()
    expected = -(v / denominator - numerator * u / (score_variance * denominator))
    (gradient,) = torch.autograd.grad(loss, scores)
    torch.testing.assert_close(gradient, expected)


@pytest.mark.parametrize("objective", ["mse", "pearson"])
def test_loss_uses_float32_for_bfloat16_inputs(objective):
    scores = torch.tensor([0.2, 0.8, 0.4], dtype=torch.bfloat16, requires_grad=True)
    targets = torch.tensor([0.0, 1.0, 0.5], dtype=torch.bfloat16)
    loss = rating_loss(scores, targets, objective)
    assert loss.dtype == torch.float32
    loss.backward()
    assert torch.isfinite(scores.grad).all()


def test_constant_targets_have_zero_pearson_data_gradient():
    scores = torch.tensor([0.1, 0.7, 0.3, 0.2], requires_grad=True)
    loss = rating_loss(scores, torch.full((4,), 0.5), "pearson")
    loss.backward()
    assert loss.item() == 1
    torch.testing.assert_close(scores.grad, torch.zeros(4))


def test_constant_predictions_have_finite_pearson_gradient():
    scores = torch.full((4,), 0.5, requires_grad=True)
    rating_loss(scores, torch.tensor([0.0, 0.2, 0.8, 1.0]), "pearson").backward()
    assert torch.isfinite(scores.grad).all()
    assert scores.grad.norm() > 0


@pytest.mark.parametrize("objective", ["mse", "pearson"])
def test_rating_losses_reach_encoder_and_projection(monkeypatch, objective):
    monkeypatch.setattr(
        "csts_pilot.joint.T5ForConditionalGeneration.from_pretrained",
        lambda *args, **kwargs: tiny_backbone(),
    )
    model = AnswerEncoder(
        convergence.ConvergenceConfig(device="cpu", projection_dimension=8)
    )
    ids = torch.arange(2, 18).reshape(8, 2)
    vectors, _ = model.encode(
        {
            "input_ids": ids,
            "attention_mask": torch.ones_like(ids),
            "pool_mask": torch.ones_like(ids, dtype=torch.bool),
        }
    )
    left, right = vectors.chunk(2)
    loss = rating_loss(
        (left * right).sum(-1), torch.tensor([0.0, 0.25, 0.5, 1.0]), objective
    )
    shared = model.t5.encoder.block[0].layer[0].SelfAttention.q.weight
    encoder_gradient, projection_gradient = torch.autograd.grad(
        loss, [shared, model.projection.weight]
    )
    assert encoder_gradient.norm() > 0
    assert projection_gradient.norm() > 0


def exercise_training(tmp_path, monkeypatch, arm, curve, **settings):
    """Run the actual CPU training loop with a controlled validation curve."""
    parent = settings.pop("parent", None)
    monkeypatch.setattr(
        "csts_pilot.joint.T5ForConditionalGeneration.from_pretrained",
        lambda *args, **kwargs: tiny_backbone(),
    )
    monkeypatch.setattr(
        convergence.AutoTokenizer, "from_pretrained", lambda *args, **kwargs: None
    )

    def tokens(rows, *_args):
        ids = torch.tensor([[2 + i % 18, 3, 1] for i in range(2 * len(rows))])
        return {
            "input_ids": ids,
            "attention_mask": torch.ones_like(ids),
            "pool_mask": ids.ne(1),
        }

    monkeypatch.setattr(convergence, "prepare_tokens", tokens)
    values = iter(curve)
    monkeypatch.setattr(
        convergence,
        "summarize",
        lambda _rows: {"mse_0_1": 0.2, "spearman": next(values)},
    )
    monkeypatch.setattr(
        AnswerEncoder,
        "answer_loss",
        lambda *args: pytest.fail("Rating-only training called the decoder."),
    )
    directory = tmp_path / arm
    directory.mkdir(parents=True)
    training = [{"target": (i % 3) / 2} for i in range(9)]
    for name in ("training", "validation"):
        (directory / f"{name}.json").write_text(json.dumps(training))
    initial_path = tmp_path / "initial.pt"
    if parent is None and not initial_path.exists():
        convergence.initialize(
            SimpleNamespace(
                config=convergence.InitializationConfig(projection_dimension=8),
                outputs={"model": initial_path},
            )
        )
    outputs = {
        name: directory / filename
        for name, filename in {
            "model": "model.pt",
            "prefix_model": "prefix.pt",
            "last_model": "last.pt",
            "resume_state": "resume.pt",
            "trace": "trace.json",
            "validation_predictions": "validation.json",
            "prefix_validation_predictions": "prefix-validation.json",
        }.items()
    }
    context = SimpleNamespace(
        config=convergence.ConvergenceConfig(
            device="cpu",
            projection_dimension=8,
            max_epochs=settings.pop("max_epochs", 3),
            prefix_epochs=settings.pop("prefix_epochs", 1),
            batch_size=4,
            rating_objective=arm,
            **settings,
        ),
        inputs={
            "training": directory / "training.json",
            "validation": directory / "validation.json",
            "initial_model": initial_path,
        },
        outputs=outputs,
        numpy_generators={},
        metrics=defaultdict(
            lambda: SimpleNamespace(record=lambda *args, **kwargs: None)
        ),
    )
    if parent is not None:
        _parent_trace, parent_paths = parent
        context.inputs.update(
            initial_model=parent_paths["last_model"],
            parent_resume=parent_paths["resume_state"],
            parent_trace=parent_paths["trace"],
            incumbent_model=parent_paths["model"],
            incumbent_validation_predictions=parent_paths["validation_predictions"],
            incumbent_prefix_model=parent_paths["prefix_model"],
            incumbent_prefix_validation_predictions=parent_paths[
                "prefix_validation_predictions"
            ],
        )
    convergence.fit(context)
    return json.loads(outputs["trace"].read_text()), outputs


def test_continuation_restores_moments_rng_orders_and_new_constant_rates(
    tmp_path, monkeypatch
):
    """A continuation starts after terminal weights and retains a stronger incumbent."""
    import hashlib

    parent, paths = exercise_training(
        tmp_path / "parent",
        monkeypatch,
        "mse",
        [0.1, 0.3, 0.8, 0.7],
        patience=None,
    )
    original = {name: path.read_bytes() for name, path in paths.items()}
    trace, continued = exercise_training(
        tmp_path / "continued",
        monkeypatch,
        "mse",
        [0.7] * 6,
        parent=(parent, paths),
        start_epoch=3,
        max_epochs=10,
        prefix_epochs=1,
        schedule="constant",
        warmup_fraction=0.0,
        encoder_learning_rate=3e-6,
        projection_learning_rate=1e-4,
    )
    assert len(trace["epochs"]) == 8
    assert trace["stop_reason"] == "validation_patience"
    assert trace["actual_updates"] == 24
    assert trace["selected"]["full"]["epoch"] == 2
    assert continued["model"].read_bytes() == original["model"]
    assert load_model(continued["last_model"])["epoch"] == 8
    assert trace["continuation"]["rng_restored_and_verified"] is True
    for epoch in trace["epochs"][3:]:
        assert epoch["learning_rates"] == [3e-6, 1e-4]
    saved = load_state(paths["resume_state"])
    generator = torch.Generator().set_state(
        saved.dataloader.state_dict["generator_state"]
    )
    expected = hashlib.sha256(
        torch.randperm(9, generator=generator).numpy().tobytes()
    ).hexdigest()
    assert trace["epochs"][3]["batch_order_sha256"] == expected
    final = load_state(continued["resume_state"])
    assert all(
        float(s["step"]) == 24
        for s in final.optimizer_state["optimizer"]["state"].values()
    )
    assert all(path.read_bytes() == original[name] for name, path in paths.items())


def test_continuation_can_improve_and_freeze_a_new_checkpoint(tmp_path, monkeypatch):
    """The new stage can replace its incumbent using validation alone."""
    parent, paths = exercise_training(
        tmp_path / "parent",
        monkeypatch,
        "pearson",
        [0.1, 0.3, 0.8, 0.7],
        patience=None,
    )
    trace, continued = exercise_training(
        tmp_path / "continued",
        monkeypatch,
        "pearson",
        [0.7, 0.85, 0.9, 0.89],
        parent=(parent, paths),
        start_epoch=3,
        max_epochs=6,
        prefix_epochs=1,
        schedule="constant",
        warmup_fraction=0.0,
        encoder_learning_rate=3e-6,
        projection_learning_rate=1e-4,
    )
    assert trace["selected"]["full"]["epoch"] == 5
    assert load_model(continued["model"])["epoch"] == 5
    assert trace["epochs"][-1]["epochs_without_improvement"] == 1


def test_continuation_rejects_misaligned_epoch_state(tmp_path, monkeypatch):
    """Reject a resume request whose epoch differs from the frozen parent."""
    parent, paths = exercise_training(
        tmp_path / "parent",
        monkeypatch,
        "mse",
        [0.1, 0.3, 0.8, 0.7],
        patience=None,
    )
    with pytest.raises(ValueError, match="completed epoch disagree"):
        exercise_training(
            tmp_path / "continued",
            monkeypatch,
            "mse",
            [0.7],
            parent=(parent, paths),
            start_epoch=4,
            max_epochs=10,
            prefix_epochs=1,
            schedule="constant",
            warmup_fraction=0.0,
        )


def test_patience_five_stops_after_five_checks_and_keeps_best_checkpoint(
    tmp_path, monkeypatch
):
    """Exercise the real training loop through a plateau and terminal state save."""
    trace, paths = exercise_training(
        tmp_path,
        monkeypatch,
        "mse",
        [0.1, 0.8, 0.7, 0.7, 0.6, 0.6, 0.5],
        max_epochs=12,
    )
    assert len(trace["epochs"]) == 6
    assert trace["stop_reason"] == "validation_patience"
    assert trace["selected"]["full"]["epoch"] == 1
    assert load_model(paths["model"])["epoch"] == 1
    assert load_model(paths["last_model"])["epoch"] == 6
    state = load_state(paths["resume_state"]).dataloader.state_dict
    assert state["step"] == 18
    assert state["early_stopping"]["stale_epochs"] == 5


def test_prefix_window_finishes_even_when_patience_expires_earlier(
    tmp_path, monkeypatch
):
    """Keep the complete required prefix without extending the scheduler horizon."""
    trace, _paths = exercise_training(
        tmp_path,
        monkeypatch,
        "mse",
        [0.1, 0.8] + [0.7] * 7,
        max_epochs=12,
        prefix_epochs=8,
    )
    assert len(trace["epochs"]) == 8
    assert trace["actual_updates"] == 24
    assert trace["total_updates"] == 36


def test_individual_patience_counts_allow_different_valid_stopping_epochs(
    tmp_path, monkeypatch
):
    """Distinguish shared schedules from equal realized training budgets."""
    traces = {}
    for arm, curve in {
        "mse": [0.1, 0.8] + [0.7] * 5,
        "pearson": [0.1, 0.7, 0.8] + [0.7] * 5,
    }.items():
        traces[arm], _paths = exercise_training(
            tmp_path, monkeypatch, arm, curve, max_epochs=12
        )
    convergence_run.verify_matched_arms(traces)
    assert traces["mse"]["actual_updates"] == 18
    assert traces["pearson"]["actual_updates"] == 21
    traces["mse"]["epochs"].pop()
    traces["mse"]["actual_updates"] -= 3
    with pytest.raises(ValueError, match="stop rule"):
        convergence_run.verify_matched_arms(traces)


def test_matched_training_preserves_orders_updates_and_both_windows(
    tmp_path, monkeypatch
):
    traces, paths = {}, {}
    for arm in ("mse", "pearson"):
        traces[arm], paths[arm] = exercise_training(
            tmp_path, monkeypatch, arm, [0.1, 0.3, 0.8, 0.7]
        )
        trace = traces[arm]
        assert (
            trace["actual_updates"] == 9
        )  # Three updates, including the final one-pair batch, per epoch.
        assert trace["selected"]["prefix"]["epoch"] == 1
        assert trace["selected"]["full"]["epoch"] == 2
        assert load_model(paths[arm]["last_model"])["epoch"] == 3
        assert load_state(paths[arm]["resume_state"]).dataloader.state_dict["step"] == 9
    convergence_run.verify_matched_arms(traces)
    altered = json.loads(json.dumps(traces))
    altered["pearson"]["epochs"][1]["batch_order_sha256"] = "changed"
    with pytest.raises(ValueError, match="pair orders"):
        convergence_run.verify_matched_arms(altered)
    altered = json.loads(json.dumps(traces))
    altered["pearson"]["config"]["encoder_learning_rate"] *= 2
    with pytest.raises(ValueError, match="shared training configuration"):
        convergence_run.verify_matched_arms(altered)

    # Selection uses saved validation predictions, with the test set absent.
    monkeypatch.setattr(
        convergence_run,
        "artifact_path",
        lambda record, _stage, name, _filename: paths[record["arm"]][name],
    )
    for arm in paths:
        for name in ("validation_predictions", "prefix_validation_predictions"):
            paths[arm][name].write_text(json.dumps(prediction_rows()))
    selection_path = tmp_path / "selection.json"
    records = {arm: {"arm": arm} for arm in paths}
    selection = convergence_run.freeze_selection(records, selection_path)
    assert selection["provisional_loss"] == "mse"  # Exact validation tie.
    assert len(selection["candidates"]) == 4
    assert selection["test_scores_used_for_selection"] is False
    selection["provisional_loss"] = "pearson"
    selection_path.write_text(json.dumps(selection))
    with pytest.raises(ValueError, match="existing frozen selection"):
        convergence_run.freeze_selection(records, selection_path)


def test_validation_ties_keep_earlier_epoch_and_identical_checkpoint_bytes(
    tmp_path, monkeypatch
):
    trace, paths = exercise_training(tmp_path, monkeypatch, "mse", [0.1, 0.6, 0.6, 0.5])
    assert trace["selected"]["full"]["epoch"] == 1
    assert paths["prefix_model"].read_bytes() == paths["model"].read_bytes()


def test_test_scoring_rejects_changed_selection_before_loading_model(tmp_path):
    selection = tmp_path / "selection.json"
    selection.write_text('{"status":"checkpoints_frozen"}')
    context = SimpleNamespace(
        config=convergence.TestConfig(
            model_sha256="0" * 64, selection_sha256="1" * 64, test_sha256="2" * 64
        ),
        inputs={"selection": selection},
    )
    with pytest.raises(ValueError, match="selection document"):
        convergence.test_checkpoint(context)


def test_test_scoring_rechecks_test_bytes_before_loading_weights(tmp_path, monkeypatch):
    model = tmp_path / "model.pt"
    model.write_bytes(b"fixture checkpoint")
    identity = convergence.file_sha256(model)
    selection = tmp_path / "selection.json"
    selection.write_text(
        json.dumps(
            {
                "status": "checkpoints_frozen",
                "candidates": {"mse_full": {"sha256": identity}},
            }
        )
    )
    test_input = tmp_path / "test.json"
    test_input.write_text("[]")
    monkeypatch.setattr(
        convergence,
        "load_model",
        lambda *_args: pytest.fail("Model loading preceded the test identity check."),
    )
    context = SimpleNamespace(
        config=convergence.TestConfig(
            model_sha256=identity,
            selection_sha256=convergence.file_sha256(selection),
            test_sha256="0" * 64,
        ),
        inputs={"selection": selection, "model": model, "test": test_input},
    )
    with pytest.raises(ValueError, match="Test bytes"):
        convergence.test_checkpoint(context)


def prediction_rows():
    """Keep multiple target values in each component for small bootstrap tests."""
    return [
        {
            "row_id": f"r{i}",
            "group_id": f"g{i // 2}",
            "pair_id": f"p{i // 2}",
            "condition": f"q{i % 2}",
            "rating": 1 + 4 * (i % 2),
            "target": float(i % 2),
            "prediction": 0.3 + 0.4 * (i % 2),
        }
        for i in range(12)
    ]


def test_positive_affine_fit_corrects_scale_and_preserves_rank():
    x, y = np.array([0.3, 0.5, 0.7]), np.array([0.0, 0.5, 1.0])
    fitted = affine_fit(x, y)
    np.testing.assert_allclose(fitted["a"] * x + fitted["c"], y, atol=1e-15)
    rows = prediction_rows()
    fitted = calibration(rows)
    for row in rows:
        row["calibrated_prediction"] = fitted["a"] * row["prediction"] + fitted["c"]
    assert (
        metrics(rows)["spearman"] == metrics(rows, "calibrated_prediction")["spearman"]
    )
    assert fitted["validation_oof_mse_0_1"] < 1e-20
    assert set(fitted["group_folds"]) == {row["group_id"] for row in rows}
    for scores in (np.ones(3), -y):
        assert affine_fit(scores, y)["identity_fallback"] is True


def test_paired_intervals_reuse_samples_and_require_identical_row_labels():
    rows = prediction_rows()
    candidates = {
        name: rows
        for name in ("mse_prefix", "mse_full", "pearson_prefix", "pearson_full")
    }
    intervals = paired_intervals(candidates, draws=30)
    for contrast in intervals["contrasts"].values():
        assert contrast["spearman"]["ci95"] == [0.0, 0.0]
        assert contrast["mse_0_1"]["ci95"] == [0.0, 0.0]
    changed = [dict(row) for row in rows]
    changed[0]["target"] = 0.5
    with pytest.raises(ValueError, match="IDs, targets or groups"):
        paired_intervals(dict(candidates, pearson_full=changed), draws=1)


def test_default_command_only_shows_review_settings(monkeypatch, capsys):
    root = Path(__file__).parents[1]
    monkeypatch.setattr(convergence_run, "resolve_root", lambda: root)
    monkeypatch.setattr("sys.argv", ["convergence_run"])
    monkeypatch.setattr(
        convergence_run,
        "run_study",
        lambda *args, **kwargs: pytest.fail("The review command executed training."),
    )
    convergence_run.main()
    assert json.loads(capsys.readouterr().out)["status"] == "review"


def test_checkpoint_handoff_preserves_bytes_and_rejects_changed_input(tmp_path):
    source, destination = tmp_path / "prefix.pt", tmp_path / "model.pt"
    source.write_bytes(b"frozen checkpoint weights")
    config = convergence.CheckpointConfig(model_sha256=convergence.file_sha256(source))
    context = SimpleNamespace(
        config=config, inputs={"checkpoint": source}, outputs={"model": destination}
    )
    convergence.promote_checkpoint(context)
    assert destination.read_bytes() == source.read_bytes()
    source.write_bytes(b"changed checkpoint")
    with pytest.raises(ValueError, match="frozen identity"):
        convergence.promote_checkpoint(context)
    assert destination.read_bytes() == b"frozen checkpoint weights"


def test_prefix_handoff_satisfies_native_stored_eval_model_contract():
    from viper.artifacts import StageArtifactRef
    from viper.evidence import VerificationError
    from viper.inputs import StoredInputRef
    from viper.stages import EvalSpec
    from viper.verification import verify_stored_input_selections

    reference = {
        "sha256": "a" * 64,
        "bytes": 1,
        "stored_at": {
            "kind": "gcs",
            "bucket": "fixture",
            "owner": "owner",
            "workspace": "study",
            "revision": "b" * 64,
            "path": "experiments/fixture/resolved.yaml",
        },
    }
    original = {"name": "train_mse", "reference": reference}
    candidate = {
        "run": original,
        "artifact_name": "prefix_model",
        "sha256": "c" * 64,
        "arm": "mse",
        "window": "prefix",
    }
    configured_stages = []

    def execute(_name, configured, _estimator, gpu):
        assert gpu is False
        configured_stages.append(configured)
        return {"name": "checkpoint_mse_prefix", "reference": reference}

    promoted, stage_id = convergence_run.canonical_checkpoint(candidate, execute)
    configured = convergence_run.evaluation_stage(
        candidate["sha256"],
        promoted,
        stage_id,
        original,
        {"splits": {"test": {"sha256": "d" * 64}}},
        "e" * 64,
    )
    model = configured.spec.inputs["model"]
    assert model.artifact.artifact_name == "model"
    assert model.artifact.stage_id == "checkpoint"
    assert (
        configured_stages[0].spec.inputs["checkpoint"].artifact.artifact_name
        == "prefix_model"
    )

    # Exercise the exact native verifier that rejected the first test run.
    spec = EvalSpec.model_construct(inputs={"model": StoredInputRef.model_construct()})
    pointer = SimpleNamespace(
        artifact=StageArtifactRef(stage_id="train", artifact_name="prefix_model")
    )
    with pytest.raises(VerificationError, match="must select model"):
        verify_stored_input_selections("test", spec, {"model": pointer})
    pointer.artifact = model.artifact
    verify_stored_input_selections("test", spec, {"model": pointer})

    full = dict(candidate, artifact_name="model")
    assert convergence_run.canonical_checkpoint(full, execute) == (original, "train")
    assert len(configured_stages) == 1


def test_evaluation_recovery_preserves_failed_evidence_and_blocks_live_state(tmp_path):
    from csts_pilot.convergence_evaluate import reconcile_failure

    path = tmp_path / "experiments/fixture/runs/test_mse_prefix/run/resolved.yaml"
    path.parent.mkdir(parents=True)
    failed = "status: failed\nattempts: []\nsuccessful_attempt_id: null\n"
    path.write_text(failed)
    summary = {
        "status": "failed",
        "in_flight": {"stage": "test_mse_prefix", "experiment_id": "fixture"},
        "gpu_stage_seconds": 1240.0,
    }
    reconcile_failure(tmp_path, summary)
    assert summary["in_flight"] is None
    assert summary["failed_evaluations"][0]["resolved"]["status"] == "failed"
    assert summary["gpu_stage_seconds"] == 1240.0
    assert path.read_text() == failed
    summary["in_flight"] = {"stage": "test_mse_prefix", "experiment_id": "fixture"}
    path.write_text("status: running\n")
    with pytest.raises(ValueError, match="unresolved native status"):
        reconcile_failure(tmp_path, summary)
