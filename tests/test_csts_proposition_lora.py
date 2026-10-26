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
        "row_id": f"row-{index}", "pair_id": f"pair-{index}",
        "group_id": f"group-{index}", "sentence1": "red car",
        "sentence2": "blue car", "condition": "color of car",
        "rating": 1.0, "target": 0.0,
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
    torch.save({"kind": "lora", "config": parent.model_dump(), "state": {"lora_weight": torch.tensor([3.0, 4.0])}}, inputs["model"])
    config = module.PropositionLoraConfig(
        device="cpu", embedding_dimension=2,
        parent_model_sha256=file_sha256(inputs["model"]),
        training_sha256=file_sha256(inputs["training"]),
        validation_sha256=file_sha256(inputs["validation"]),
    )
    return SimpleNamespace(
        config=config, inputs=inputs,
        outputs={name: tmp_path / filename for name, filename in {
            "model": "selected.pt", "last_model": "last.pt",
            "trace": "trace.json", "warm_start": "warm_start.json",
        }.items()},
        metrics={}, numpy_generators={},
    )


@pytest.mark.parametrize("change", ({"kind": "projection"}, {"start_epoch": 1}, {"schedule": "linear"}))
def test_config_rejects_other_scorers_and_optimizer_continuation(change):
    values = {"parent_model_sha256": "1" * 64, "training_sha256": "2" * 64, "validation_sha256": "3" * 64, **change}
    with pytest.raises(ValidationError):
        module.PropositionLoraConfig(**values)


def test_saved_weights_reach_fresh_trainer_without_provenance_fields_in_checkpoint(context, monkeypatch):
    parent_bytes = context.inputs["model"].read_bytes()
    events = []
    monkeypatch.setattr(module, "load_tokenizer", lambda config: None)
    monkeypatch.setattr(module, "TokenPairs", lambda rows, config, tokenizer: rows)
    monkeypatch.setattr(module, "load_backbone", lambda config, adapters: AdapterModel())

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
        torch.save({"kind": "lora", "config": inner.config.model_dump(), "state": trainable_state(model)}, inner.outputs["model"])
        digest = file_sha256(inner.outputs["model"])
        inner.outputs["trace"].write_text(json.dumps({
            "status": "complete", "config": inner.config.model_dump(),
            "initial_trainable_sha256": initial,
            "selected": {"sha256": digest}, "actual_updates": 1,
        }))
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
    monkeypatch.setattr(module, "load_backbone", lambda *args, **kwargs: pytest.fail("Model allocated for changed input"))
    with pytest.raises(ValueError, match="Changed proposition-LoRA input"):
        module.fit_proposition_lora(context)


@pytest.mark.parametrize("setting,value", (("lora_rank", 1), ("lora_alpha", 1), ("lora_dropout", 0.2), ("embedding_dimension", 3)))
def test_changed_adapter_or_encoder_settings_fail_before_loading(context, monkeypatch, setting, value):
    context.config = context.config.model_copy(update={setting: value})
    monkeypatch.setattr(module, "load_backbone", lambda *args, **kwargs: pytest.fail("Incompatible model allocated"))
    with pytest.raises(ValueError, match="Parent adapter or encoder setting differs"):
        module.fit_proposition_lora(context)


def test_token_preflight_fails_before_model_allocation(context, monkeypatch):
    monkeypatch.setattr(module, "load_tokenizer", lambda config: None)

    def too_long(*args):
        raise ValueError("token ceiling")

    monkeypatch.setattr(module, "TokenPairs", too_long)
    monkeypatch.setattr(module, "load_backbone", lambda *args, **kwargs: pytest.fail("Model allocated before token preflight"))
    with pytest.raises(ValueError, match="token ceiling"):
        module.fit_proposition_lora(context)


def test_shared_source_group_fails_before_model_allocation(context, monkeypatch):
    changed = comparison(1)
    changed["group_id"] = "group-0"
    context.inputs["validation"].write_text(json.dumps([changed]))
    context.config = context.config.model_copy(update={"validation_sha256": file_sha256(context.inputs["validation"])})
    monkeypatch.setattr(module, "load_backbone", lambda *args, **kwargs: pytest.fail("Overlapping data allocated a model"))
    with pytest.raises(ValueError, match="share group_id"):
        module.fit_proposition_lora(context)


def test_non_lora_parent_is_rejected_before_allocation(context, monkeypatch):
    saved = load_model(context.inputs["model"])
    saved["kind"] = "projection"
    torch.save(saved, context.inputs["model"])
    context.config = context.config.model_copy(update={"parent_model_sha256": file_sha256(context.inputs["model"])})
    monkeypatch.setattr(module, "load_backbone", lambda *args, **kwargs: pytest.fail("Wrong parent allocated a model"))
    with pytest.raises(ValueError, match="saved LoRA checkpoint"):
        module.fit_proposition_lora(context)
