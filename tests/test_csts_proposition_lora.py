"""Check weight-only initialization and binding of changed answer inputs."""

import json
from types import SimpleNamespace

import pytest
import torch
from pydantic import ValidationError
from torch import nn

from csts_pilot import proposition_lora as module
from csts_pilot.baseline_models import FitConfig, state_digest, trainable_state
from csts_pilot.convergence import file_sha256
from jep_pilot.loaders import load_json, load_model


def comparison(index):
    return {
        "row_id": f"row-{index}",
        "pair_id": f"pair-{index}",
        "group_id": f"group-{index}",
        "sentence1": "red car",
        "sentence2": "blue car",
        "condition": "color of car",
        "rating": 1.0,
        "target": 0.0,
    }


class AdapterModel(nn.Module):
    def __init__(self):
        super().__init__()
        self.lora_weight = nn.Parameter(torch.zeros(2))


@pytest.fixture
def context(tmp_path):
    parent = FitConfig(kind="lora", device="cpu", embedding_dimension=2)
    inputs = {name: tmp_path / f"{name}.json" for name in ("training", "validation")}
    inputs["training"].write_text(json.dumps([comparison(0)]))
    inputs["validation"].write_text(json.dumps([comparison(1)]))
    inputs["model"] = tmp_path / "parent.pt"
    torch.save(
        {
            "kind": "lora",
            "config": parent.model_dump(),
            "state": {"lora_weight": torch.tensor([3.0, 4.0])},
        },
        inputs["model"],
    )
    config = module.PropositionLoraConfig(
        device="cpu",
        embedding_dimension=2,
        parent_model_sha256=file_sha256(inputs["model"]),
        training_sha256=file_sha256(inputs["training"]),
        validation_sha256=file_sha256(inputs["validation"]),
    )
    return SimpleNamespace(
        config=config,
        inputs=inputs,
        outputs={
            name: tmp_path / filename
            for name, filename in {
                "model": "selected.pt",
                "last_model": "last.pt",
                "trace": "trace.json",
                "warm_start": "warm_start.json",
            }.items()
        },
        metrics={},
        numpy_generators={},
    )


@pytest.mark.parametrize(
    "change", ({"kind": "projection"}, {"start_epoch": 1}, {"schedule": "linear"})
)
def test_config_rejects_other_scorers_and_optimizer_continuation(change):
    values = {
        "parent_model_sha256": "1" * 64,
        "training_sha256": "2" * 64,
        "validation_sha256": "3" * 64,
        **change,
    }
    with pytest.raises(ValidationError):
        module.PropositionLoraConfig(**values)


def test_saved_weights_reach_fresh_trainer_without_provenance_fields_in_checkpoint(
    context, monkeypatch
):
    parent_bytes = context.inputs["model"].read_bytes()
    events = []
    monkeypatch.setattr(module, "load_tokenizer", lambda config: None)
    monkeypatch.setattr(module, "TokenPairs", lambda rows, config, tokenizer: rows)
    monkeypatch.setattr(
        module, "load_backbone", lambda config, adapters: AdapterModel()
    )

    def fit(inner, model, training, validation):
        assert type(inner.config) is FitConfig
        assert inner.config.start_epoch == 0
        assert "parent_model_sha256" not in inner.config.model_dump()
        torch.testing.assert_close(model.lora_weight, torch.tensor([3.0, 4.0]))
        assert training == [comparison(0)] and validation == [comparison(1)]
        assert set(inner.inputs) == {"model", "training", "validation"}
        initial = state_digest(trainable_state(model))
        with torch.no_grad():
            model.lora_weight.add_(1)
        torch.save(
            {
                "kind": "lora",
                "config": inner.config.model_dump(),
                "state": trainable_state(model),
            },
            inner.outputs["model"],
        )
        digest = file_sha256(inner.outputs["model"])
        inner.outputs["trace"].write_text(
            json.dumps(
                {
                    "status": "complete",
                    "config": inner.config.model_dump(),
                    "initial_trainable_sha256": initial,
                    "selected": {"sha256": digest},
                    "actual_updates": 1,
                }
            )
        )
        events.append(digest)

    monkeypatch.setattr(module, "fit_neural", fit)
    module.fit_proposition_lora(context)
    assert context.inputs["model"].read_bytes() == parent_bytes
    assert file_sha256(context.outputs["model"]) == events[0]
    saved = load_model(context.outputs["model"])
    FitConfig.model_validate(saved["config"])
    assert saved["state"]["lora_weight"].tolist() == [4, 5]
    audit = load_json(context.outputs["warm_start"])
    assert audit["fresh_optimizer"] and not audit["restored_optimizer_state"]
    assert audit["optimizer_updates_at_start"] == 0 and audit["actual_updates"] == 1
    assert load_json(context.outputs["trace"])["warm_start"] == audit


@pytest.mark.parametrize("input_name", ("model", "training", "validation"))
def test_changed_inputs_fail_before_model_allocation(context, monkeypatch, input_name):
    context.inputs[input_name].write_bytes(b"changed")
    monkeypatch.setattr(
        module,
        "load_backbone",
        lambda *args, **kwargs: pytest.fail("Model allocated for changed input"),
    )
    with pytest.raises(ValueError, match="Changed proposition-LoRA input"):
        module.fit_proposition_lora(context)


@pytest.mark.parametrize(
    "setting,value",
    (
        ("lora_rank", 1),
        ("lora_alpha", 1),
        ("lora_dropout", 0.2),
        ("embedding_dimension", 3),
    ),
)
def test_changed_adapter_or_encoder_settings_fail_before_loading(
    context, monkeypatch, setting, value
):
    context.config = context.config.model_copy(update={setting: value})
    monkeypatch.setattr(
        module,
        "load_backbone",
        lambda *args, **kwargs: pytest.fail("Incompatible model allocated"),
    )
    with pytest.raises(ValueError, match="Parent adapter or encoder setting differs"):
        module.fit_proposition_lora(context)


def test_token_preflight_fails_before_model_allocation(context, monkeypatch):
    monkeypatch.setattr(module, "load_tokenizer", lambda config: None)

    def too_long(*args):
        raise ValueError("token ceiling")

    monkeypatch.setattr(module, "TokenPairs", too_long)
    monkeypatch.setattr(
        module,
        "load_backbone",
        lambda *args, **kwargs: pytest.fail("Model allocated before token preflight"),
    )
    with pytest.raises(ValueError, match="token ceiling"):
        module.fit_proposition_lora(context)


def test_shared_source_group_fails_before_model_allocation(context, monkeypatch):
    changed = comparison(1)
    changed["group_id"] = "group-0"
    context.inputs["validation"].write_text(json.dumps([changed]))
    context.config = context.config.model_copy(
        update={"validation_sha256": file_sha256(context.inputs["validation"])}
    )
    monkeypatch.setattr(
        module,
        "load_backbone",
        lambda *args, **kwargs: pytest.fail("Overlapping data allocated a model"),
    )
    with pytest.raises(ValueError, match="share group_id"):
        module.fit_proposition_lora(context)


def test_non_lora_parent_is_rejected_before_allocation(context, monkeypatch):
    saved = load_model(context.inputs["model"])
    saved["kind"] = "projection"
    torch.save(saved, context.inputs["model"])
    context.config = context.config.model_copy(
        update={"parent_model_sha256": file_sha256(context.inputs["model"])}
    )
    monkeypatch.setattr(
        module,
        "load_backbone",
        lambda *args, **kwargs: pytest.fail("Wrong parent allocated a model"),
    )
    with pytest.raises(ValueError, match="saved LoRA checkpoint"):
        module.fit_proposition_lora(context)


def test_actual_cpu_trainer_saves_selected_and_terminal_checkpoints(
    context, monkeypatch
):
    """Exercise real AdamW, patience, native resume serialization and selected replay."""
    from viper.resume import load_resume_state

    from csts_pilot import baseline_stages
    from csts_pilot.baseline_models import restore_parameters
    from csts_pilot.diagnostics import summarize

    parent_bytes = context.inputs["model"].read_bytes()
    for split, offset in (("training", 0), ("validation", 10)):
        rows = []
        for index, rating in enumerate((1.0, 2.0, 4.0, 5.0)):
            row = comparison(offset + index)
            row.update(rating=rating, target=(rating - 1) / 4)
            rows.append(row)
        context.inputs[split].write_text(json.dumps(rows))
    context.config = context.config.model_copy(
        update={
            "training_sha256": file_sha256(context.inputs["training"]),
            "validation_sha256": file_sha256(context.inputs["validation"]),
            "learning_rate": 0.1,
            "weight_decay": 0.0,
            "batch_size": 2,
            "microbatch_size": 1,
            "max_epochs": 3,
            "patience": 2,
            "max_seconds": 30,
        }
    )
    context.outputs["resume_state"] = context.outputs["trace"].with_name("resume.pt")
    context.outputs["validation_predictions"] = context.outputs["trace"].with_name(
        "predictions.json"
    )

    class Pairs:
        def __init__(self, rows, _config, _tokenizer):
            self.rows = rows
            self.features = torch.linspace(-1, 1, len(rows))
            self.nonpadding_tokens = 0

        def scores(self, model, indices):
            self.nonpadding_tokens += 4 * len(indices)
            return (
                model.lora_weight[0] * self.features[indices] + model.lora_weight[1]
            ) / 10

    class Recorder:
        def __init__(self):
            self.steps = []

        def record(self, value, step):
            assert torch.isfinite(torch.tensor(value))
            self.steps.append(step)

    optimizer_observations = []
    real_adamw = torch.optim.AdamW

    class ObservedAdamW(real_adamw):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            assert not self.state
            torch.testing.assert_close(
                self.param_groups[0]["params"][0], torch.tensor([3.0, 4.0])
            )
            optimizer_observations.append(self)

        def load_state_dict(self, _state):
            pytest.fail("Changed-input adaptation restored old optimizer state")

    assert module.fit_neural is baseline_stages.fit_neural
    monkeypatch.setattr(module, "load_tokenizer", lambda _config: None)
    monkeypatch.setattr(module, "TokenPairs", Pairs)
    monkeypatch.setattr(
        module, "load_backbone", lambda _config, adapters: AdapterModel()
    )
    monkeypatch.setattr(baseline_stages.torch.optim, "AdamW", ObservedAdamW)
    context.metrics = {
        name: Recorder()
        for name in ("training_objective", "validation_mse", "validation_spearman")
    }
    module.fit_proposition_lora(context)

    trace = load_json(context.outputs["trace"])
    selected = load_model(context.outputs["model"])
    terminal = load_model(context.outputs["last_model"])
    resume = load_resume_state(context.outputs["resume_state"])
    assert context.inputs["model"].read_bytes() == parent_bytes
    assert len(optimizer_observations) == 1
    assert trace["config"] == context.config.fit_config().model_dump(mode="json")
    assert FitConfig.model_validate(selected["config"]) == context.config.fit_config()
    assert trace["initial_trainable_sha256"] == state_digest(
        {"lora_weight": torch.tensor([3.0, 4.0])}
    )
    assert trace["stop_reason"] == "validation_patience"
    assert trace["actual_updates"] == terminal["step"] == 6
    assert selected["epoch"] == trace["selected"]["epoch"] == 1
    assert terminal["epoch"] == 3
    assert trace["selected"]["sha256"] == file_sha256(context.outputs["model"])
    assert not torch.equal(
        selected["state"]["lora_weight"], terminal["state"]["lora_weight"]
    )
    assert all(recorder.steps == [1, 2, 3] for recorder in context.metrics.values())
    optimizer_state = resume.optimizer_state["optimizer"]
    assert len(optimizer_state["state"]) == 1
    assert int(next(iter(optimizer_state["state"].values()))["step"]) == 6
    assert resume.optimizer_state["scheduler"]["last_epoch"] == 6
    assert resume.dataloader.state_dict["epoch"] == 3
    assert resume.dataloader.state_dict["step"] == 6
    assert resume.dataloader.state_dict["last_model_sha256"] == file_sha256(
        context.outputs["last_model"]
    )
    restored = AdapterModel()
    restore_parameters(restored, selected["state"])
    validation = Pairs(load_json(context.inputs["validation"]), None, None)
    replay = baseline_stages.predict_pairs(restored, validation, 1)
    assert replay == load_json(context.outputs["validation_predictions"])
    assert summarize(replay) == trace["selected"]["validation"]
    assert trace["warm_start"] == load_json(context.outputs["warm_start"])
    assert trace["warm_start"]["status"] == "complete"
