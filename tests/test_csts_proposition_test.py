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
        config=module.TestEvaluationConfig(
            inference=inputs_module.PropositionInferenceConfig(
                device="cpu",
                embedding_dimension=2,
                evaluation_split="test",
                selection_sha256=file_sha256(inputs["selection"]),
                parent_model_sha256=file_sha256(inputs["model"]),
                original_rows_sha256=file_sha256(inputs["original_rows"]),
                transformed_rows_sha256=file_sha256(inputs["transformed_rows"]),
                baseline_sha256=file_sha256(inputs["baseline_predictions"]),
            )
        ),
        inputs=inputs,
        outputs={
            name: tmp_path / f"out_{name}.json"
            for name in ("predictions", "result", "timing")
        },
    )
    inputs["test"] = inputs["original_rows"]
    inputs["holdout"] = tmp_path / "indices.json"
    inputs["holdout"].write_text("[0]")
    context.run_id, context.attempt_id, context.stage_id = "fixture", 1, "infer"
    context.metrics, context.numpy_generators = {}, {}
    module.evaluate_frozen_test(context)
    result = load_json(context.outputs["result"])
    assert result["metrics"]["saved_qwen"]["operating_point"]["cutoff"] == 0.7
    assert result["metrics"]["propositions"]["operating_point"]["cutoff"] == 0.4
    assert (
        result["metrics"]["propositions"]["operating_point"]["false_positive_rate"]
        == 1.0
    )
    assert result["test_cutoffs_refitted"] is False


def test_native_eval_rejects_selection_before_opening_test_or_holdout(
    tmp_path, monkeypatch
):
    path = tmp_path / "selection.json"
    value = selection()
    value["eligibility"]["adapted"]["eligible"] = False
    path.write_text(json.dumps(value))
    config = module.TestEvaluationConfig(
        inference=inputs_module.PropositionInferenceConfig(
            device="cpu",
            evaluation_split="test",
            selection_sha256=file_sha256(path),
            parent_model_sha256="a" * 64,
            original_rows_sha256="b" * 64,
            transformed_rows_sha256="c" * 64,
            baseline_sha256="d" * 64,
        )
    )
    opened = []
    real_load = module.load_json

    def tracked_load(source):
        opened.append(source)
        return real_load(source)

    monkeypatch.setattr(module, "load_json", tracked_load)
    with pytest.raises(ValueError, match="eligible validation-frozen model"):
        module.evaluate_frozen_test(
            SimpleNamespace(config=config, inputs={"selection": path})
        )
    assert opened == [path]


def test_native_eval_requires_complete_published_holdout_and_recomputes_metrics(
    tmp_path, monkeypatch
):
    from scipy.stats import spearmanr

    rows = [
        {"row_id": f"r{i}", "target": target}
        for i, target in enumerate([0.0, 0.25, 0.75, 1.0])
    ]
    values = [0.1, 0.5, 0.4, 0.9]
    inputs = {
        name: tmp_path / f"{name}.json" for name in ("test", "holdout", "selection")
    }
    for name, data in (
        ("test", rows),
        ("holdout", list(range(4))),
        ("selection", selection()),
    ):
        inputs[name].write_text(json.dumps(data))
    config = module.TestEvaluationConfig(
        inference=inputs_module.PropositionInferenceConfig(
            device="cpu",
            evaluation_split="test",
            selection_sha256=file_sha256(inputs["selection"]),
            parent_model_sha256="a" * 64,
            original_rows_sha256=file_sha256(inputs["test"]),
            transformed_rows_sha256="c" * 64,
            baseline_sha256="d" * 64,
        )
    )
    outputs = {"predictions": tmp_path / "predictions.json"}
    delegated = []

    def frozen_scorer(context):
        assert context.config is config.inference
        assert context.inputs["original_rows"] == inputs["test"]
        delegated.append(True)
        context.outputs["predictions"].write_text(
            json.dumps(
                [
                    dict(row, prediction=score)
                    for row, score in zip(rows, values, strict=True)
                ]
            )
        )

    monkeypatch.setattr(module, "infer", frozen_scorer)
    context = SimpleNamespace(config=config, inputs=inputs, outputs=outputs, metrics={})
    inputs["holdout"].write_text("[0]")
    context.run_id, context.attempt_id, context.stage_id = "fixture", 1, "infer"
    context.metrics, context.numpy_generators = {}, {}
    with pytest.raises(ValueError, match="complete released cohort"):
        module.evaluate_frozen_test(context)
    assert not delegated
    inputs["holdout"].write_text(json.dumps(list(range(4))))
    module.evaluate_frozen_test(context)
    assert delegated == [True]
    artifact_context = SimpleNamespace(artifacts=outputs)
    expected_mse = sum(
        (score - row["target"]) ** 2 for row, score in zip(rows, values, strict=True)
    ) / len(rows)
    assert module.artifact_test_mse(artifact_context) == pytest.approx(
        expected_mse, abs=1e-12
    )
    assert module.artifact_test_spearman(artifact_context) == pytest.approx(
        float(spearmanr(values, [row["target"] for row in rows]).statistic), abs=1e-12
    )


def test_frozen_native_stage_and_plan_use_canonical_producer_bindings(tmp_path):
    from pathlib import Path

    from viper.authoring import experiment, plan, replicate, variant
    from viper.references import GitFileRef
    from viper.repository import read_source
    from viper.runtime import CPUComputeSpec, LocalEnvSpec, observe_python_env

    record = {
        "reference": {
            "kind": "resolved_run",
            "sha256": "1" * 64,
            "bytes": 1,
            "stored_at": {
                "kind": "local",
                "workspace": str(tmp_path),
                "store": ".viper/store",
                "store_id": "2" * 32,
                "commit": "3" * 64,
                "path": "experiments/example/runs/example/run/resolved.yaml",
            },
        }
    }
    config = module.TestEvaluationConfig(
        inference=inputs_module.PropositionInferenceConfig(
            device="cpu",
            evaluation_split="test",
            selection_sha256="e" * 64,
            parent_model_sha256="a" * 64,
            original_rows_sha256="b" * 64,
            transformed_rows_sha256="c" * 64,
            baseline_sha256="d" * 64,
        )
    )
    configured = module.frozen_test_stage(
        config, record, record, record, record, "selection.json"
    )
    assert configured.spec.kind == "eval"
    assert configured.spec.split_inputs == ("holdout",)
    bindings = configured.spec.inputs
    assert set(bindings) == {
        "model",
        "test",
        "holdout",
        "selection",
        "transformed_rows",
        "baseline_predictions",
    }
    assert bindings["model"].artifact.stage_id == "train"
    assert bindings["model"].artifact.artifact_name == "model"
    assert bindings["model"].data_role == "training"
    for name in ("test", "holdout"):
        assert bindings[name].artifact.stage_id == "publish"
        assert bindings[name].artifact.artifact_name == name
        assert bindings[name].data_role == "eval"
    assert bindings["transformed_rows"].artifact.stage_id == "prepare"
    assert bindings["transformed_rows"].data_role == "eval"
    assert set(configured.outputs.keys()) == {"predictions", "result", "timing"}
    for metric in configured.spec.metrics:
        assert metric.dependencies[0].source == "artifact"
        assert metric.dependencies[0].name == "predictions"
        assert metric.dependencies[0].data_role == "eval"
    source = read_source(Path(__file__).resolve().parents[1])
    declared = plan(
        experiment=experiment(
            experiment_id="frozen_proposition_test_fixture",
            variants=(
                variant(
                    "test",
                    stages=(configured,),
                    estimator=configured.outputs.predictions,
                ),
            ),
            replicates=(replicate(seed=7),),
        ),
        source=source,
        env=LocalEnvSpec(
            compute=CPUComputeSpec(),
            python_env=observe_python_env(),
            lockfile=GitFileRef(
                repository=source.repository,
                commit=source.commit,
                path="tranche2_requirements.txt",
            ),
        ),
    )
    assert declared is not None  # Native declaration only: no model, data or execution.


def test_native_eval_config_rejects_validation_cutoff_fitting():
    with pytest.raises(ValueError, match="requires frozen test inference"):
        module.TestEvaluationConfig(
            inference=inputs_module.PropositionInferenceConfig(
                device="cpu",
                parent_model_sha256="a" * 64,
                original_rows_sha256="b" * 64,
                transformed_rows_sha256="c" * 64,
                baseline_sha256="d" * 64,
            )
        )


def test_full_test_preparation_and_controller_fail_closed_without_any_input_access(
    tmp_path, monkeypatch
):
    def reject_access(*args, **kwargs):
        raise AssertionError(
            "Deferred full-test workflow must not open any input or load a release."
        )

    monkeypatch.setattr(module, "load_json", reject_access)
    monkeypatch.setattr(module, "file_sha256", reject_access)
    monkeypatch.setattr(module, "frozen_context", reject_access)
    with pytest.raises(
        NotImplementedError, match="raw-provenance capture/import producer"
    ):
        module.prepare_test(SimpleNamespace())
    with pytest.raises(
        NotImplementedError, match="raw-provenance capture/import producer"
    ):
        module.evaluate_test(
            tmp_path / "missing",
            tmp_path / "also-missing",
            "validation",
            "test",
            tmp_path / "answers.json",
            tmp_path / "manifest.json",
        )
