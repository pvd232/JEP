"""Check source identities, fidelity bindings and frozen proposition scoring."""

import copy
import json
from types import SimpleNamespace

import pytest
import torch
from torch import nn

from csts_pilot import proposition_inputs as module
from csts_pilot.answers import answer_id
from csts_pilot.baseline_models import FitConfig
from csts_pilot.convergence import file_sha256
from jep_pilot.loaders import load_json


def row(index):
    return {
        "row_id": f"row-{index}",
        "pair_id": f"pair-{index}",
        "group_id": f"group-{index}",
        "sentence1": f"A red car {index}.",
        "sentence2": f"A blue car {index}.",
        "condition": "color of car",
        "rating": 1.0,
        "target": 0.0,
    }


def record(item, answered=True):
    return {
        "id": item["id"],
        "status": "answered" if answered else "not_specified",
        "target": "car",
        "attribute": "color",
        "answer": "The car is red." if answered else "",
        "evidence": ["red"] if answered else [],
    }


def write(path, value):
    path.write_text(json.dumps(value))


@pytest.fixture
def preparation(tmp_path, monkeypatch):
    training, validation = [row(0), row(1)], [row(2)]
    items, _ = module.source_inventory(training, validation)
    records = [record(item, answered="red" in item["passage"]) for item in items]
    inputs = {
        name: tmp_path / f"{name}.json"
        for name in (
            "training",
            "validation",
            "answers",
            "capture_manifest",
            "audit_gate",
            "provenance",
        )
    }
    write(inputs["training"], training)
    write(inputs["validation"], validation)
    write(inputs["answers"], records)
    manifest = {
        "records_sha256": file_sha256(inputs["answers"]),
        "generation_template_sha256": "a" * 64,
        "schema_sha256": "b" * 64,
        "model_alias": "gpt-6.1-sol",
        "reasoning_effort": "high",
        "partitions": {"training": {}, "validation": {}},
    }
    write(inputs["capture_manifest"], manifest)
    write(
        inputs["audit_gate"],
        {
            "passed": True,
            "generation_template_sha256": "a" * 64,
            "schema_sha256": "b" * 64,
            "model_alias": "gpt-6.1-sol",
            "reasoning_effort": "high",
        },
    )
    write(inputs["provenance"], {})
    monkeypatch.setattr(module, "TRAINING_SHA256", file_sha256(inputs["training"]))
    monkeypatch.setattr(module, "VALIDATION_SHA256", file_sha256(inputs["validation"]))
    # These tests isolate replacement contracts; full frozen-audit/raw evidence
    # replay is exercised independently in test_csts_proposition_provenance.py.
    monkeypatch.setattr(module, "validate_bank", lambda *_args: None)
    config = module.PropositionPreparationConfig(
        **{f"{name}_sha256": file_sha256(path) for name, path in inputs.items()}
    )
    return SimpleNamespace(
        config=config,
        inputs=inputs,
        outputs={
            name: tmp_path / f"out_{name}.json"
            for name in ("training", "validation", "audit")
        },
    )


def refresh(context):
    context.config = context.config.model_copy(
        update={
            f"{name}_sha256": file_sha256(path) for name, path in context.inputs.items()
        }
    )


def test_preparation_accepts_grounded_paraphrases_and_preserves_all_metadata(
    preparation,
):
    original = load_json(preparation.inputs["training"])
    module.prepare(preparation)
    changed = load_json(preparation.outputs["training"])
    assert len(changed) == len(original)
    for before, after in zip(original, changed, strict=True):
        assert after == dict(before, sentence1="The car is red.")
    audit = load_json(preparation.outputs["audit"])
    assert audit["coverage"]["training"]["comparison_coverage"] == {
        "both": 0,
        "one": 2,
        "neither": 0,
    }
    assert audit["coverage"]["training"]["accepted_count_per_row"] == [1, 1]
    assert not audit["expert_verified"]


@pytest.mark.parametrize("change", ("missing", "duplicate", "evidence"))
def test_preparation_rejects_incomplete_or_wrong_source_banks_even_after_rehash(
    preparation, change
):
    records = load_json(preparation.inputs["answers"])
    if change == "missing":
        records.pop()
    elif change == "duplicate":
        records.append(copy.deepcopy(records[0]))
    else:
        answered = next(item for item in records if item["status"] == "answered")
        answered["evidence"] = ["a fabricated quotation"]
    write(preparation.inputs["answers"], records)
    manifest = load_json(preparation.inputs["capture_manifest"])
    manifest["records_sha256"] = file_sha256(preparation.inputs["answers"])
    write(preparation.inputs["capture_manifest"], manifest)
    refresh(preparation)
    with pytest.raises(ValueError):
        module.prepare(preparation)


@pytest.mark.parametrize(
    "change",
    ("failed_gate", "template", "schema", "records", "partitions", "model", "effort"),
)
def test_preparation_requires_bound_passing_gate_and_complete_manifest(
    preparation, change
):
    gate = load_json(preparation.inputs["audit_gate"])
    manifest = load_json(preparation.inputs["capture_manifest"])
    if change == "failed_gate":
        gate["passed"] = False
    elif change == "template":
        gate["generation_template_sha256"] = "c" * 64
    elif change == "schema":
        gate["schema_sha256"] = "c" * 64
    elif change == "records":
        manifest["records_sha256"] = "c" * 64
    elif change == "model":
        gate["model_alias"] = "different-model"
    elif change == "effort":
        gate["reasoning_effort"] = "low"
    else:
        manifest["partitions"].pop("validation")
    write(preparation.inputs["audit_gate"], gate)
    write(preparation.inputs["capture_manifest"], manifest)
    refresh(preparation)
    with pytest.raises(ValueError):
        module.prepare(preparation)


def test_first_canonical_representative_and_all_raw_variants_are_bound():
    first, alias = row(0), row(1)
    alias.update(
        sentence1="Ａ  RED CAR 0.", condition="COLOR of CAR", group_id=first["group_id"]
    )
    items, audit = module.source_inventory([first, alias], [row(2)])
    identity = answer_id(first["sentence1"], first["condition"])
    representative = next(item for item in items if item["id"] == identity)
    assert representative["passage"] == first["sentence1"]
    assert representative["condition"] == first["condition"]
    variants = next(
        item for item in audit["raw_variant_groups"] if item["id"] == identity
    )
    assert variants["group_id"] == first["group_id"]
    assert len(variants["variants"]) == 2 and audit["aliased_identities"] == 1
    alias["group_id"] = "wrong-source-group"
    with pytest.raises(ValueError, match="changes source semantics or group"):
        module.source_inventory([first, alias], [row(2)])


def test_unknown_and_ambiguous_statuses_keep_original_passages_and_conditions():
    original = row(0)
    items, _ = module.source_inventory([original], [])
    records = {item["id"]: record(item, answered=False) for item in items}
    records[items[0]["id"]]["status"] = "ambiguous"
    transformed, audit = module.transform_rows([original], records)
    assert transformed == [original]
    assert audit["accepted_count_per_row"] == [0]
    assert audit["comparison_coverage"]["neither"] == 1


@pytest.mark.parametrize("change", ("order", "condition", "target", "extra"))
def test_replacement_validation_rejects_changed_order_labels_or_metadata(change):
    original = [row(0), row(1)]
    transformed = [dict(item, sentence1="red") for item in original]
    if change == "order":
        transformed.reverse()
    elif change == "condition":
        transformed[0]["condition"] = "activity"
    elif change == "target":
        transformed[0]["target"] = 1.0
        transformed[0]["rating"] = 5.0
    else:
        transformed[0]["extra"] = True
    with pytest.raises(ValueError):
        module.validate_replacements(original, transformed)


class FakeModel(nn.Module):
    def __init__(self):
        super().__init__()
        self.lora_weight = nn.Parameter(torch.zeros(2))


@pytest.mark.parametrize("mutate", (False, True))
def test_frozen_inference_filters_saved_full_baseline_and_never_updates_adapters(
    tmp_path, monkeypatch, mutate
):
    original = [row(0), dict(row(1), rating=5.0, target=1.0)]
    transformed = [dict(item, sentence1="red") for item in original]
    inputs = {
        name: tmp_path / f"{name}.json"
        for name in ("original_rows", "transformed_rows", "baseline_predictions")
    }
    write(inputs["original_rows"], original)
    write(inputs["transformed_rows"], transformed)
    write(
        inputs["baseline_predictions"],
        [
            dict(row(3), prediction=0.3),
            dict(original[1], prediction=0.9),
            dict(original[0], prediction=0.1),
        ],
    )
    inputs["model"] = tmp_path / "parent.pt"
    fit = FitConfig(kind="lora", device="cpu", embedding_dimension=2)
    torch.save(
        {
            "kind": "lora",
            "config": fit.model_dump(),
            "state": {"lora_weight": torch.tensor([3.0, 4.0])},
        },
        inputs["model"],
    )
    context = SimpleNamespace(
        config=module.PropositionInferenceConfig(
            device="cpu",
            embedding_dimension=2,
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

    class Pairs:
        def __init__(self, rows, config, tokenizer):
            self.nonpadding_tokens = 0
            assert rows == transformed

        def scores(self, model, indices):
            if mutate:
                model.lora_weight.fill_(1)
            self.nonpadding_tokens += len(indices)
            return torch.tensor([0.2, 0.8])[indices]

    monkeypatch.setattr(module, "TokenPairs", Pairs)
    monkeypatch.setattr(module, "load_tokenizer", lambda config: None)
    monkeypatch.setattr(module, "load_backbone", lambda config, adapters: FakeModel())
    if mutate:
        with pytest.raises(ValueError, match="Adapter bytes changed"):
            module.infer(context)
    else:
        module.infer(context)
        scored = load_json(context.outputs["predictions"])
        assert [
            {key: value for key, value in item.items() if key != "prediction"}
            for item in scored
        ] == original
        result = load_json(context.outputs["result"])
        assert result["metrics"]["saved_qwen"]["mse_0_1"] == pytest.approx(0.01)
        assert result["metrics"]["propositions"]["mse_0_1"] == pytest.approx(0.04)
        assert result["optimizer_updates"] == 0 and not result["baseline_rerun"]
