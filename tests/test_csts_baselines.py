"""Observe scorer math, exact continuation and native Tranche 2 stage boundaries."""

import copy
import json
from collections import defaultdict
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest
import torch
from torch import nn
from torch.nn import functional as F
from transformers import Qwen3Config, Qwen3Model

from csts_pilot import baseline_models as models
from csts_pilot import baseline_run as runner
from csts_pilot import baseline_stages as stages
from csts_pilot.baseline_models import (
    EncoderConfig,
    FitConfig,
    FrozenPairs,
    ScoreConfig,
)
from csts_pilot.convergence import file_sha256
from csts_pilot.diagnostics import summarize
from jep_pilot.loaders import load_json, load_model, load_state


@pytest.fixture(autouse=True)
def small_thread_pool():
    """Bound toy-model BLAS overhead and restore the caller's thread count."""
    original = torch.get_num_threads()
    torch.set_num_threads(2)
    yield
    torch.set_num_threads(original)


class TokenizerFixture:
    """Provide attended EOD and controllable padding through an offline fixture."""

    def __init__(self, padding_side="left"):
        """Select the padding convention exercised by the fixture."""
        self.padding_side = padding_side
        self.calls = 0

    def get_vocab(self):
        """Expose the explicit document terminator required by the encoder."""
        return {models.EOD: 1}

    def __call__(self, texts, **_kwargs):
        """Map words to a bounded vocabulary before explicit EOD insertion."""
        self.calls += 1
        return {
            "input_ids": [
                [2 + sum(word.encode()) % 28 for word in text.split()] for text in texts
            ]
        }

    def pad(self, encoded, **_kwargs):
        """Pad IDs and masks together under the selected convention."""
        width = max(map(len, encoded["input_ids"]))
        result = {}
        for name, sequences in encoded.items():
            rows = []
            for sequence in sequences:
                padding = [0] * (width - len(sequence))
                rows.append(
                    padding + sequence
                    if self.padding_side == "left"
                    else sequence + padding
                )
            result[name] = torch.tensor(rows)
        return result


def comparison_rows(start=0, n=9):
    """Create complete comparison identities with several rating levels."""
    return [
        {
            "row_id": f"r{i}",
            "group_id": f"g{i // 2}",
            "pair_id": f"p{i // 2}",
            "condition": f"condition {i % 2}",
            "sentence1": f"cat number {i}",
            "sentence2": f"dog number {i + 1}",
            "rating": 1 + 2 * (i % 3),
            "target": (i % 3) / 2,
        }
        for i in range(start, start + n)
    ]


@pytest.fixture
def prepared(tmp_path):
    """Persist deterministic train/validation rows and one shared frozen cache."""
    config = FitConfig(
        kind="projection",
        model_id="fixture",
        revision="a" * 40,
        embedding_dimension=8,
        projection_dimension=4,
        device="cpu",
        batch_size=4,
        microbatch_size=4,
        max_epochs=3,
    )
    inputs = {}
    all_rows = []
    for name, start in (("training", 0), ("validation", 100)):
        rows = comparison_rows(start)
        path = tmp_path / f"{name}.json"
        path.write_text(json.dumps(rows))
        inputs[name] = path
        all_rows.extend(rows)
    keys = models.passage_keys(all_rows)
    vectors = F.normalize(
        torch.randn(len(keys), 8, generator=torch.Generator().manual_seed(77)), dim=-1
    )
    cache = {
        "encoder": models.encoder_settings(config),
        "keys": keys,
        "vectors": vectors,
        "inputs": {name: file_sha256(path) for name, path in inputs.items()},
    }
    inputs["embeddings"] = tmp_path / "features.pt"
    torch.save(cache, inputs["embeddings"])
    return config, inputs


def context_for(prepared, directory, **updates):
    """Create separate output files while sharing exact prepared input bytes."""
    config, inputs = prepared
    directory.mkdir(parents=True)
    outputs = {
        name: directory / filename
        for name, filename in {
            "model": "best.pt",
            "last_model": "last.pt",
            "resume_state": "resume.pt",
            "trace": "trace.json",
            "validation_predictions": "validation.json",
        }.items()
    }
    return SimpleNamespace(
        config=FitConfig.model_validate({**config.model_dump(), **updates}),
        inputs=dict(inputs),
        outputs=outputs,
        numpy_generators={},
        metrics=defaultdict(
            lambda: SimpleNamespace(record=lambda *_args, **_kwargs: None)
        ),
    )


def test_pooling_uses_last_attended_token_under_both_padding_conventions():
    """Padding location leaves the same final content vector selected."""
    content = torch.tensor([[1.0, 2.0, 3.0], [3.0, 2.0, 1.0]])
    hidden = torch.stack(
        [
            torch.stack([torch.zeros(3), content[0], content[1]]),
            torch.stack([content[0], content[1], torch.zeros(3)]),
        ]
    )
    mask = torch.tensor([[0, 1, 1], [1, 1, 0]])
    actual = models.last_token_pool(hidden.bfloat16(), mask)
    assert actual.dtype == torch.float32
    torch.testing.assert_close(actual, F.normalize(content[1].repeat(2, 1), dim=-1))
    with pytest.raises(ValueError, match="attended token"):
        models.last_token_pool(hidden, torch.zeros_like(mask))


def test_tokenization_appends_eod_and_rejects_silent_truncation():
    """Every conditioned passage ends in attended EOD within the declared ceiling."""
    config = EncoderConfig(device="cpu", max_length=64)
    batch = models.token_batch(
        TokenizerFixture(),
        [("animal", "cat"), ("animal", "a much longer dog passage")],
        config,
    )
    assert batch["input_ids"][:, -1].tolist() == [1, 1]
    assert batch["attention_mask"][:, -1].tolist() == [1, 1]
    with pytest.raises(ValueError, match="exceeds the token ceiling"):
        models.token_batch(TokenizerFixture(), [("animal", "word " * 80)], config)


def test_cache_keys_keep_the_condition_and_check_representation_identity(prepared):
    """Shared text under different questions remains separately addressable."""
    config, inputs = prepared
    cache = load_model(inputs["embeddings"])
    assert (
        len(
            models.passage_keys(
                [
                    dict(comparison_rows()[0], condition="q1"),
                    dict(comparison_rows()[0], condition="q2"),
                ]
            )
        )
        == 4
    )
    models.validate_cache(cache, config)
    changed = copy.deepcopy(cache)
    changed["encoder"]["revision"] = "b" * 40
    with pytest.raises(ValueError, match="settings"):
        models.validate_cache(changed, config)
    changed = copy.deepcopy(cache)
    changed["vectors"][0] *= 2
    with pytest.raises(ValueError, match="unit vectors"):
        models.validate_cache(changed, config)


def test_cache_checks_all_token_lengths_before_loading_backbone(
    prepared, tmp_path, monkeypatch
):
    """A late overlength passage stops preparation before any expensive model load."""
    config, inputs = prepared
    rows = load_json(inputs["training"])
    rows[-1]["sentence1"] = "word " * 200
    inputs["training"].write_text(json.dumps(rows))
    monkeypatch.setattr(stages, "load_tokenizer", lambda _config: TokenizerFixture())
    monkeypatch.setattr(
        stages,
        "load_backbone",
        lambda _config: pytest.fail(
            "Backbone loaded before complete token validation."
        ),
    )
    context = SimpleNamespace(
        config=EncoderConfig.model_validate(
            {key: getattr(config, key) for key in EncoderConfig.model_fields}
        ),
        inputs={"training": inputs["training"]},
        outputs={
            "embeddings": tmp_path / "unused.pt",
            "timing": tmp_path / "unused.json",
        },
    )
    with pytest.raises(ValueError, match="exceeds the token ceiling"):
        stages.cache_embeddings(context)


@pytest.mark.parametrize("shape", [(7, 3), (3, 7)])
def test_ridge_matches_independent_normal_equations_in_primal_and_dual(shape):
    """Mean-loss penalty scaling and the unpenalized intercept match direct solves."""
    rng = np.random.default_rng(7)
    x, target = rng.normal(size=shape), rng.normal(size=shape[0])
    for fitted in models.ridge_candidates(x, target, [0.01, 1.0]):
        standardized = (x - x.mean(0)) / x.std(0)
        expected = np.linalg.solve(
            standardized.T @ standardized / len(x) + fitted["alpha"] * np.eye(shape[1]),
            standardized.T @ (target - target.mean()) / len(x),
        )
        np.testing.assert_allclose(fitted["coefficients"].numpy(), expected, atol=1e-12)
        assert fitted["intercept"] == target.mean()


def test_pair_features_and_projected_cosine_are_symmetric(prepared):
    """Swapping passages preserves both scorer inputs and learned cosine scores."""
    config, inputs = prepared
    rows, cache = load_json(inputs["training"]), load_model(inputs["embeddings"])
    original = FrozenPairs(rows, cache, config)
    swapped = FrozenPairs(
        [
            dict(row, sentence1=row["sentence2"], sentence2=row["sentence1"])
            for row in rows
        ],
        cache,
        config,
    )
    np.testing.assert_array_equal(
        models.pair_features(original.left, original.right),
        models.pair_features(swapped.left, swapped.right),
    )
    model = nn.Linear(8, 4, bias=False)
    torch.testing.assert_close(
        original.scores(model, torch.arange(len(rows))),
        swapped.scores(model, torch.arange(len(rows))),
    )


def test_microbatch_accumulation_matches_full_updates_including_partial_batch(
    prepared, tmp_path
):
    """A final one-pair update receives its full mean-loss gradient."""
    results = []
    for microbatch in (1, 4):
        context = context_for(
            prepared,
            tmp_path / f"micro-{microbatch}",
            microbatch_size=microbatch,
            max_epochs=1,
        )
        stages.fit_projection(context)
        results.append(load_model(context.outputs["last_model"])["state"])
        assert (
            load_state(context.outputs["resume_state"]).dataloader.state_dict["step"]
            == 3
        )
    torch.testing.assert_close(
        results[0]["weight"], results[1]["weight"], atol=2e-7, rtol=2e-6
    )


def test_patience_and_continuation_restore_optimizer_and_next_pair_order(
    prepared, tmp_path, monkeypatch
):
    """Resume terminal epoch three, retain epoch two and stop after five new checks."""
    actual_summarize = stages.summarize
    curve = iter([0.3, 0.9, 0.8])

    def controlled(rows):
        """Change only the validation criterion to exercise a declared plateau."""
        return {**actual_summarize(rows), "spearman": next(curve)}

    monkeypatch.setattr(stages, "summarize", controlled)
    parent = context_for(prepared, tmp_path / "parent")
    stages.fit_projection(parent)
    original = {key: path.read_bytes() for key, path in parent.outputs.items()}
    continuation = context_for(
        prepared,
        tmp_path / "continued",
        start_epoch=3,
        max_epochs=12,
        learning_rate=1e-4,
    )
    continuation.inputs.update(
        {
            "parent_last_model": parent.outputs["last_model"],
            "parent_resume": parent.outputs["resume_state"],
            "parent_trace": parent.outputs["trace"],
            "parent_model": parent.outputs["model"],
            "parent_validation_predictions": parent.outputs["validation_predictions"],
        }
    )
    curve = iter([0.7] * 5)
    stages.fit_projection(continuation)
    trace = load_json(continuation.outputs["trace"])
    assert len(trace["epochs"]) == 8
    assert trace["selected"]["epoch"] == 2
    assert trace["stop_reason"] == "validation_patience"
    assert continuation.outputs["model"].read_bytes() == original["model"]
    generator = torch.Generator().set_state(
        load_state(parent.outputs["resume_state"]).dataloader.state_dict[
            "generator_state"
        ]
    )
    assert trace["epochs"][3]["batch_order_sha256"] == models.state_digest(
        {"order": torch.randperm(9, generator=generator)}
    )
    resumed = load_state(continuation.outputs["resume_state"])
    assert all(
        float(state["step"]) == 24
        for state in resumed.optimizer_state["optimizer"]["state"].values()
    )
    assert resumed.optimizer_state["optimizer"]["param_groups"][0]["lr"] == 1e-4
    assert all(
        path.read_bytes() == original[name] for name, path in parent.outputs.items()
    )


def test_patience_completion_overrides_both_training_ceilings(
    prepared, tmp_path, monkeypatch
):
    """Finish two stale checks even when the declared time and epoch limits are smaller."""
    original = stages.summarize
    curve = iter([0.9, 0.8, 0.7])
    monkeypatch.setattr(
        stages, "summarize", lambda rows: {**original(rows), "spearman": next(curve)}
    )
    context = context_for(
        prepared,
        tmp_path / "completion",
        max_epochs=1,
        max_seconds=1e-12,
        patience=2,
        train_until_patience=True,
    )
    stages.fit_projection(context)
    trace = load_json(context.outputs["trace"])
    assert trace["stop_reason"] == "validation_patience"
    assert len(trace["epochs"]) == 3
    assert trace["epochs"][-1]["epochs_without_improvement"] == 2


def test_shortened_patience_preserves_best_and_completed_epochs(
    prepared, tmp_path, monkeypatch
):
    """Resume with patience one and retain the incumbent after the first decline."""
    original = stages.summarize
    curve = iter([0.3, 0.8, 0.9])
    monkeypatch.setattr(
        stages, "summarize", lambda rows: {**original(rows), "spearman": next(curve)}
    )
    parent = context_for(prepared, tmp_path / "parent_patience_two", patience=2)
    stages.fit_projection(parent)
    retained = {key: path.read_bytes() for key, path in parent.outputs.items()}
    continued = context_for(
        prepared,
        tmp_path / "shortened_patience",
        start_epoch=3,
        max_epochs=4,
        patience=1,
        train_until_patience=True,
    )
    continued.inputs.update(
        {
            "parent_last_model": parent.outputs["last_model"],
            "parent_resume": parent.outputs["resume_state"],
            "parent_trace": parent.outputs["trace"],
            "parent_model": parent.outputs["model"],
            "parent_validation_predictions": parent.outputs["validation_predictions"],
        }
    )
    curve = iter([0.7])
    stages.fit_projection(continued)
    result = load_json(continued.outputs["trace"])
    assert result["stop_reason"] == "validation_patience"
    assert len(result["epochs"]) == 4
    assert result["epochs"][-1]["epochs_without_improvement"] == 1
    assert result["epochs"][:3] == load_json(parent.outputs["trace"])["epochs"]
    assert result["selected"]["epoch"] == 3
    assert continued.outputs["model"].read_bytes() == retained["model"]
    assert {key: path.read_bytes() for key, path in parent.outputs.items()} == retained


def test_patience_completion_restores_prior_stale_check(
    prepared, tmp_path, monkeypatch
):
    """The resumed model needs one further stale check after its parent's first stale check."""
    original = stages.summarize
    curve = iter([0.3, 0.9, 0.8])
    monkeypatch.setattr(
        stages, "summarize", lambda rows: {**original(rows), "spearman": next(curve)}
    )
    parent = context_for(prepared, tmp_path / "parent_stale", patience=2)
    stages.fit_projection(parent)
    continued = context_for(
        prepared,
        tmp_path / "finish_stale",
        start_epoch=3,
        max_epochs=4,
        max_seconds=1e-12,
        patience=2,
        train_until_patience=True,
    )
    continued.inputs.update(
        {
            "parent_last_model": parent.outputs["last_model"],
            "parent_resume": parent.outputs["resume_state"],
            "parent_trace": parent.outputs["trace"],
            "parent_model": parent.outputs["model"],
            "parent_validation_predictions": parent.outputs["validation_predictions"],
        }
    )
    curve = iter([0.7])
    stages.fit_projection(continued)
    trace = load_json(continued.outputs["trace"])
    assert len(trace["epochs"]) == 4
    assert trace["stop_reason"] == "validation_patience"
    assert trace["selected"]["epoch"] == 2
    assert trace["epochs"][-1]["epochs_without_improvement"] == 2


def test_parameter_restore_rejects_broadcastable_wrong_shape():
    """Reject a malformed one-value tensor in place of a full projection matrix."""
    with pytest.raises(ValueError, match="shapes differ"):
        models.restore_parameters(
            nn.Linear(8, 4, bias=False), {"weight": torch.ones(1)}
        )


def test_resource_budget_stops_on_a_complete_epoch_with_matching_resume_state(
    prepared, tmp_path, monkeypatch
):
    """Preserve completed weights when the next observed epoch exceeds the remaining allowance."""
    clock = iter([i * 0.01 for i in range(100)])
    monkeypatch.setattr(stages, "time", SimpleNamespace(monotonic=lambda: next(clock)))
    context = context_for(
        prepared, tmp_path / "budget", max_epochs=10, max_seconds=0.11
    )
    stages.fit_projection(context)
    trace = load_json(context.outputs["trace"])
    terminal = load_model(context.outputs["last_model"])
    resume = load_state(context.outputs["resume_state"])
    assert trace["stop_reason"] == "resource_budget"
    assert terminal["epoch"] == len(trace["epochs"]) == 1
    assert resume.dataloader.state_dict["epoch"] == terminal["epoch"]
    assert resume.dataloader.state_dict["step"] == terminal["step"] == 3


@pytest.mark.parametrize("kind", ["mean", "cosine", "ridge"])
def test_static_scorers_write_selected_model_and_validation_predictions(
    prepared, tmp_path, kind
):
    """Each static fitting path emits finite scores and a self-describing model."""
    context = context_for(prepared, tmp_path / kind, kind=kind)
    stages.fit_static(context)
    saved = load_model(context.outputs["model"])
    rows = load_json(context.outputs["validation_predictions"])
    assert saved["kind"] == kind
    assert saved["validation"] == summarize(rows)
    if kind == "mean":
        assert saved["fitted"]["mean_prediction"] == 0.5
        assert saved["validation"]["spearman"] is None


def test_selection_tie_rule_is_independent_of_mapping_order(
    prepared, tmp_path, monkeypatch
):
    """Reordering JSON object keys preserves the predeclared cosine-first tie rule."""
    contexts = {}
    for kind in ("ridge", "cosine"):
        context = context_for(prepared, tmp_path / kind, kind=kind)
        stages.fit_static(context)
        contexts[kind] = context
    original = load_model(contexts["cosine"].outputs["model"])
    ridge = load_model(contexts["ridge"].outputs["model"])
    ridge["validation"] = original["validation"]
    torch.save(ridge, contexts["ridge"].outputs["model"])
    contexts["ridge"].outputs["validation_predictions"].write_bytes(
        contexts["cosine"].outputs["validation_predictions"].read_bytes()
    )
    monkeypatch.setattr(
        runner,
        "artifact_path",
        lambda record, _stage, name, _filename: contexts[record["kind"]].outputs[name],
    )
    config = prepared[0]
    settings = {
        "encoder": {key: getattr(config, key) for key in EncoderConfig.model_fields}
    }
    records = {kind: {"kind": kind} for kind in ("ridge", "cosine")}
    first = runner.freeze_selection(records, tmp_path / "selection-1.json", settings)
    second = runner.freeze_selection(
        dict(reversed(list(records.items()))), tmp_path / "selection-2.json", settings
    )
    assert first == second
    assert first["provisional_winner"] == "cosine"


def test_real_tiny_qwen_lora_produces_adapter_gradients_with_frozen_base(monkeypatch):
    """Exercise PEFT and Qwen forwards, pooling and backpropagation through offline fixtures."""
    tiny = Qwen3Model(
        Qwen3Config(
            vocab_size=32,
            hidden_size=16,
            intermediate_size=32,
            num_hidden_layers=1,
            num_attention_heads=2,
            num_key_value_heads=1,
            head_dim=8,
            max_position_embeddings=128,
            attention_dropout=0.0,
        )
    )
    monkeypatch.setattr(
        models.AutoModel, "from_pretrained", lambda *_args, **_kwargs: tiny
    )
    config = FitConfig(
        kind="lora",
        device="cpu",
        embedding_dimension=16,
        lora_rank=2,
        lora_alpha=2,
        lora_dropout=0.0,
    )
    model = models.load_backbone(config, adapters=config)
    tokenizer = TokenizerFixture()
    pairs = models.TokenPairs(comparison_rows(n=3), config, tokenizer)
    scores = pairs.scores(model, torch.arange(3))
    assert tokenizer.calls == 1
    F.mse_loss(scores, torch.tensor([0.0, 0.5, 1.0])).backward()
    trainable = [p for p in model.parameters() if p.requires_grad]
    frozen = [p for p in model.parameters() if not p.requires_grad]
    assert any(p.grad is not None and p.grad.abs().sum() > 0 for p in trainable)
    assert all(p.grad is None for p in frozen)
    assert len(models.trainable_state(model)) == len(trainable)


@pytest.mark.parametrize("kind", ["mean", "cosine", "ridge", "projection"])
def test_native_stage_models_use_canonical_names_and_no_test_training_inputs(kind):
    """Author real VIPER TRAIN/EVAL specs with stored model and evaluation roles."""
    root = Path(__file__).parents[1]
    settings = load_json(root / "configs/csts-tranche-2.json")
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
    record = {"name": "train_projection", "reference": reference}
    trained = runner.training_stage(settings, kind, record, 30)
    assert "resume_state" in trained.outputs
    assert set(trained.spec.inputs) == {"training", "validation", "embeddings"}
    configured = runner.evaluation_stage(
        "projection",
        {"sha256": "c" * 64, "run": record},
        record,
        record,
        settings,
        "selection.json",
        "d" * 64,
    )
    assert configured.spec.inputs["model"].artifact.artifact_name == "model"
    assert configured.spec.inputs["model"].artifact.stage_id == "train"
    assert configured.spec.inputs["test"].data_role == "eval"
    assert configured.spec.split_inputs == ("holdout",)


def test_test_identity_guard_fails_before_backbone_loading(tmp_path, monkeypatch):
    """Changing test bytes prevents an expensive or unapproved model forward."""
    model, test, selection = (
        tmp_path / name for name in ("model.pt", "test.json", "selection.json")
    )
    model.write_bytes(b"frozen model")
    test.write_text("[]")
    selection.write_text(
        json.dumps(
            {
                "status": "checkpoints_frozen",
                "candidates": {"lora": {"sha256": file_sha256(model)}},
            }
        )
    )
    monkeypatch.setattr(
        stages,
        "load_backbone",
        lambda *_args, **_kwargs: pytest.fail("Model loaded before identity checks."),
    )
    context = SimpleNamespace(
        config=ScoreConfig(
            kind="lora",
            model_sha256=file_sha256(model),
            selection_sha256=file_sha256(selection),
            test_sha256="0" * 64,
        ),
        inputs={"model": model, "test": test, "selection": selection},
    )
    with pytest.raises(ValueError, match="cohort bytes differ"):
        stages.evaluate_baseline(context)


def test_default_command_validates_and_shows_plan_without_execution(
    monkeypatch, capsys
):
    """The public default command neither loads model weights nor invokes VIPER."""
    monkeypatch.setattr(runner, "resolve_root", lambda: Path(__file__).parents[1])
    monkeypatch.setattr(
        runner,
        "run_study",
        lambda *_args, **_kwargs: pytest.fail("Default command launched a study."),
    )
    monkeypatch.setattr("sys.argv", ["baseline_run"])
    runner.main()
    assert json.loads(capsys.readouterr().out)["status"] == "review"


def test_lora_phase_requires_completed_frozen_baselines(tmp_path):
    """LoRA launch rejects a still-running or mismatched frozen-phase prerequisite."""
    settings = load_json(Path(__file__).parents[1] / "configs/csts-tranche-2.json")
    path = tmp_path / "summary.json"
    value = {"status": "running", "phase": "frozen", "settings": settings}
    path.write_text(json.dumps(value))
    with pytest.raises(ValueError, match="completed frozen phase"):
        runner.require_frozen_phase(path, settings)
    value["status"] = "complete"
    path.write_text(json.dumps(value))
    assert runner.require_frozen_phase(path, settings) == file_sha256(path)


@pytest.mark.parametrize("config_type", [EncoderConfig, FitConfig, ScoreConfig])
def test_new_schema_fields_retain_machine_readable_descriptions(config_type):
    """Every owned configuration field explains its role in generated JSON Schema."""
    schema = config_type.model_json_schema()
    for name, field in schema["properties"].items():
        if name != "schema_version":
            assert field.get("description"), name
