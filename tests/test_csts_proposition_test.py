"""Keep candidate test access bound to validation selection and operating points."""

import copy
import json
from types import SimpleNamespace

import pytest
import torch
from torch import nn

from csts_pilot import proposition_inputs as inputs_module
from csts_pilot import proposition_test as module
from csts_pilot.baseline_models import FitConfig
from csts_pilot.convergence import file_sha256
from jep_pilot.loaders import load_json


def selection(model_sha256="a" * 64):
    return {
        "selected_arm": "adapted",
        "test_scores_used_for_selection": False,
        "selected_model": {"sha256": model_sha256},
        "eligibility": {"adapted": {"eligible": True}},
        "thresholds": {"saved_qwen": 0.7, "epoch_zero": 0.6, "adapted": 0.4},
        "generation_policy": {
            "generation_template_sha256": "b" * 64,
            "schema_sha256": "c" * 64,
            "model_alias": "gpt-6.1-sol",
            "reasoning_effort": "high",
        },
    }


@pytest.mark.parametrize(
    "change", ["ineligible", "test_used", "model", "missing_cutoff", "nan_cutoff"]
)
def test_frozen_test_thresholds_rejects_unreleased_or_changed_decisions(change):
    value = selection()
    if change == "ineligible":
        value["eligibility"]["adapted"]["eligible"] = False
    elif change == "test_used":
        value["test_scores_used_for_selection"] = True
    elif change == "model":
        value["selected_model"]["sha256"] = "d" * 64
    elif change == "missing_cutoff":
        del value["thresholds"]["adapted"]
    else:
        value["thresholds"]["saved_qwen"] = float("nan")
    with pytest.raises(ValueError):
        inputs_module.frozen_test_thresholds(value, "a" * 64)


def test_test_configuration_cannot_silently_use_validation_cutoff_fitting():
    values = {
        "parent_model_sha256": "a" * 64,
        "original_rows_sha256": "b" * 64,
        "transformed_rows_sha256": "c" * 64,
        "baseline_sha256": "d" * 64,
    }
    with pytest.raises(ValueError, match="frozen selection SHA"):
        inputs_module.PropositionInferenceConfig(**values, evaluation_split="test")
    with pytest.raises(ValueError, match="frozen selection SHA"):
        inputs_module.PropositionInferenceConfig(**values, selection_sha256="e" * 64)


@pytest.mark.parametrize("field", module.POLICY_FIELDS)
def test_test_capture_cannot_change_frozen_generation_policy(field):
    frozen = selection()
    manifest = copy.deepcopy(frozen["generation_policy"])
    manifest[field] += "changed"
    with pytest.raises(ValueError, match=field):
        module.require_policy(manifest, frozen)


def test_ineligible_selection_is_rejected_before_opening_any_test_rows(
    tmp_path, monkeypatch
):
    path = tmp_path / "selection.json"
    value = selection()
    value["eligibility"]["adapted"]["eligible"] = False
    path.write_text(json.dumps(value))
    config = inputs_module.PropositionInferenceConfig(
        device="cpu",
        evaluation_split="test",
        selection_sha256=file_sha256(path),
        parent_model_sha256="a" * 64,
        original_rows_sha256="b" * 64,
        transformed_rows_sha256="c" * 64,
        baseline_sha256="d" * 64,
    )
    opened = []
    original_load = inputs_module.load_json

    def tracked_load(source):
        opened.append(source)
        return original_load(source)

    monkeypatch.setattr(inputs_module, "load_json", tracked_load)
    with pytest.raises(ValueError, match="eligible validation-frozen model"):
        inputs_module.infer(SimpleNamespace(config=config, inputs={"selection": path}))
    assert opened == [path]


def test_test_inference_uses_frozen_cutoffs_even_when_test_has_no_positives(
    tmp_path, monkeypatch
):
    original = [
        {
            "row_id": "r0",
            "pair_id": "p0",
            "group_id": "g0",
            "sentence1": "A red car.",
            "sentence2": "A blue car.",
            "condition": "color of car",
            "rating": 1.0,
            "target": 0.0,
        }
    ]
    transformed = [dict(original[0], sentence1="Red.", sentence2="Blue.")]
    inputs = {
        name: tmp_path / f"{name}.json"
        for name in (
            "original_rows",
            "transformed_rows",
            "baseline_predictions",
            "selection",
        )
    }
    for name, value in (
        ("original_rows", original),
        ("transformed_rows", transformed),
        ("baseline_predictions", [dict(original[0], prediction=0.6)]),
    ):
        inputs[name].write_text(json.dumps(value))
    fit = FitConfig(kind="lora", device="cpu", embedding_dimension=2)
    inputs["model"] = tmp_path / "model.pt"
    torch.save(
        {
            "kind": "lora",
            "config": fit.model_dump(),
            "state": {"lora_weight": torch.tensor([3.0, 4.0])},
        },
        inputs["model"],
    )
    inputs["selection"].write_text(json.dumps(selection(file_sha256(inputs["model"]))))

    class Model(nn.Module):
        def __init__(self):
            super().__init__()
            self.lora_weight = nn.Parameter(torch.tensor([0.0, 0.0]))

    class Pairs:
        nonpadding_tokens = 2

        def __init__(self, rows, config, tokenizer):
            assert rows == transformed

        def scores(self, model, indices):
            return torch.tensor([0.5])[indices]

    def reject_refit(*args, **kwargs):
        raise AssertionError("Test rows must never fit a recall threshold.")

    monkeypatch.setattr(inputs_module, "TokenPairs", Pairs)
    monkeypatch.setattr(inputs_module, "load_tokenizer", lambda config: None)
    monkeypatch.setattr(
        inputs_module, "load_backbone", lambda config, adapters: Model()
    )
    monkeypatch.setattr(inputs_module, "recall_cutoff", reject_refit)
    context = SimpleNamespace(
        config=inputs_module.PropositionInferenceConfig(
            device="cpu",
            embedding_dimension=2,
            evaluation_split="test",
            selection_sha256=file_sha256(inputs["selection"]),
            parent_model_sha256=file_sha256(inputs["model"]),
            original_rows_sha256=file_sha256(inputs["original_rows"]),
            transformed_rows_sha256=file_sha256(inputs["transformed_rows"]),
            baseline_sha256=file_sha256(inputs["baseline_predictions"]),
        ),
        inputs=inputs,
        outputs={
            name: tmp_path / f"out_{name}.json"
            for name in ("predictions", "result", "timing")
        },
    )
    inputs_module.infer(context)
    result = load_json(context.outputs["result"])
    assert result["metrics"]["saved_qwen"]["operating_point"]["cutoff"] == 0.7
    assert result["metrics"]["propositions"]["operating_point"]["cutoff"] == 0.4
    assert (
        result["metrics"]["propositions"]["operating_point"]["false_positive_rate"]
        == 1.0
    )
    assert result["test_cutoffs_refitted"] is False
