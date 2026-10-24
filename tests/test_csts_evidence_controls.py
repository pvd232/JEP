"""Check evidence alignment, equal exposure, phase transitions and test isolation."""

import json
from collections import Counter
from types import SimpleNamespace

import pytest
import torch
from torch import nn
from transformers import T5Config, T5ForConditionalGeneration

from csts_pilot import evidence_controls as controls
from csts_pilot.answers import answer_id
from csts_pilot.convergence import file_sha256, write_json
from csts_pilot.evidence_run import (
    PRETEST_STAGES,
    evidence_training_outputs,
    validate_evaluation_resume,
    validate_matched_traces,
)

MODEL_CLASS = controls.AnswerEncoder


def test_native_prediction_and_eval_stage_contracts_are_both_constructible():
    from viper.authoring import input, stage
    from viper.config import BuildConfig, EvalConfig
    from viper.metrics import FloatComparator, MetricDependency, measure
    from viper.metrics import max as maximize
    from viper.outputs import EvalOutputs, StageOutputs, output

    from csts_pilot.convergence import test_spearman
    from jep_pilot.loaders import load_json

    config = controls.EvidenceTestConfig(
        arm="evidence",
        model_sha256="a" * 64,
        selection_sha256="b" * 64,
        test_sha256="c" * 64,
    )
    capture = stage(
        controls.capture_evidence_predictions,
        stage_id="predict",
        config=controls.EvidencePredictionConfig(**config.model_dump()),
        outputs=StageOutputs(
            predictions=output(
                path="predictions.json", loader=load_json, data_role="eval"
            ),
            binding=output(path="binding.json", loader=load_json, data_role="eval"),
        ),
    )
    metric = measure(
        test_spearman,
        dependencies=(
            MetricDependency(source="artifact", name="predictions", data_role="eval"),
        ),
        comparator=FloatComparator(mode="absolute", tolerance=1e-12),
    )
    evaluated = stage(
        controls.evaluate_evidence,
        stage_id="test",
        eval_id="csts_tranche3",
        config=config,
        inputs=(input("holdout", path="indices.json", data_role="eval"),),
        split_inputs=("holdout",),
        metrics=(metric,),
        objective=maximize(metric),
        outputs=EvalOutputs(
            predictions=output(
                path="predictions.json", loader=load_json, data_role="eval"
            )
        ),
    )
    assert isinstance(capture.spec.config, BuildConfig)
    assert isinstance(evaluated.spec.config, EvalConfig)
    assert capture.spec.config.model_dump() == evaluated.spec.config.model_dump()


def completed_for_evaluation(tmp_path):
    records = [{"name": name, "status": "succeeded"} for name in PRETEST_STAGES]
    selection = {
        "status": "checkpoints_frozen",
        "test_scores_used_for_selection": False,
        "candidates": {
            arm: {"run": next(r for r in records if r["name"] == f"{arm}_ratings")}
            for arm in ("ratings", "evidence", "shuffled")
        },
    }
    path = tmp_path / "selection.json"
    write_json(path, selection)
    return {"runs": records, "selection_sha256": file_sha256(path)}


def test_evaluation_recovery_accepts_complete_training_and_partial_scoring(tmp_path):
    summary = completed_for_evaluation(tmp_path)
    original = json.loads(json.dumps(summary))
    validate_evaluation_resume(tmp_path, summary)
    assert summary == original
    summary["runs"].append({"name": "predict_ratings", "status": "succeeded"})
    validate_evaluation_resume(tmp_path, summary)


@pytest.mark.parametrize(
    "fault", ["missing", "failed", "duplicate", "reordered", "unknown"]
)
def test_evaluation_recovery_rejects_incomplete_or_ambiguous_training(tmp_path, fault):
    summary = completed_for_evaluation(tmp_path)
    records = summary["runs"]
    if fault == "missing":
        records.pop(3)
    elif fault == "failed":
        records[3]["status"] = "failed"
    elif fault == "duplicate":
        records.append(dict(records[3]))
    elif fault == "reordered":
        records[2], records[3] = records[3], records[2]
    else:
        records.append({"name": "unreviewed_training", "status": "succeeded"})
    with pytest.raises(ValueError, match="all completed native training"):
        validate_evaluation_resume(tmp_path, summary)


@pytest.mark.parametrize("rehash", [False, True])
def test_evaluation_recovery_rejects_changed_frozen_candidates(tmp_path, rehash):
    summary = completed_for_evaluation(tmp_path)
    path = tmp_path / "selection.json"
    selection = json.loads(path.read_text())
    selection["candidates"]["evidence"]["run"]["name"] = "different_training"
    write_json(path, selection)
    if rehash:
        summary["selection_sha256"] = file_sha256(path)
    with pytest.raises(ValueError, match="frozen selection|Frozen candidates"):
        validate_evaluation_resume(tmp_path, summary)


def test_review_gate_rejects_unmatched_exposure_and_best_instead_of_terminal_transition():
    import copy

    a = {
        "initial_sha256": "initial",
        "updates": 6,
        "training_rows": 2,
        "completed_epoch": 6,
        "initial_rng": {"seed": 7},
        "terminal_sha256": "terminal",
        "epochs": [{"batch_order_sha256": "same"}],
    }
    b = {
        "initial_sha256": "terminal",
        "initial_rng": {"seed": 7},
        "epochs": [{"batch_order_sha256": "same"}],
    }
    traces = {
        k: {"pretrain": copy.deepcopy(a), "ratings": copy.deepcopy(b)}
        for k in ("ratings", "evidence", "shuffled")
    }
    validate_matched_traces(traces)
    traces["evidence"]["pretrain"]["updates"] = 5
    with pytest.raises(ValueError, match="Unmatched phase-A"):
        validate_matched_traces(traces)
    traces["evidence"]["pretrain"]["updates"] = 6
    traces["evidence"]["ratings"]["initial_sha256"] = "selected earlier epoch"
    with pytest.raises(ValueError, match="terminal phase-A"):
        validate_matched_traces(traces)


def record(passage, condition, answer, valid=True):
    return {
        "id": answer_id(passage, condition),
        "passage": passage,
        "condition": condition,
        "answer": answer,
        "valid": valid,
        "response": json.dumps(
            {"target": "shirt", "attribute": "color", "evidence": answer}
        ),
        "review_response": '{"accept":true}',
    }


def test_shuffling_is_training_only_and_changes_every_supervised_answer():
    rows = [
        record("A red shirt.", "shirt color", "red"),
        record("A blue shirt.", "shirt color", "blue"),
        record("A green shirt.", "shirt color", "green"),
        record("A black dog.", "animal color", "black"),
    ]
    cache = {r["id"]: r for r in rows}
    train = set(cache) - {rows[2]["id"]}
    a, b, donors = controls.aligned_and_shuffled(train, cache, 7)
    assert set(a) == set(b) == set(donors) == {rows[0]["id"], rows[1]["id"]}
    assert all(a[k] != b[k] and k != donors[k] for k in a)
    assert Counter(a.values()) == Counter(b.values())
    assert controls.aligned_and_shuffled(train, cache, 7) == (a, b, donors)


def test_unshuffleable_and_duplicate_answer_keys_share_one_exclusion_mask():
    rows = [record(f"{i} red shirt.", "shirt color", "red") for i in range(3)]
    rows.append(record("A blue shirt.", "shirt color", "blue"))
    cache = {r["id"]: r for r in rows}
    a, b, _ = controls.aligned_and_shuffled(set(cache), cache, 7)
    assert len(a) == 2 and set(a) == set(b)
    assert all(a[k] != b[k] for k in a)
    assert Counter(a.values()) == Counter(b.values())


def test_cache_rejects_duplicates_and_missing_verification(tmp_path):
    r = record("A red shirt.", "shirt color", "red")
    path = tmp_path / "cache.jsonl"
    path.write_text(json.dumps(r) + "\n" + json.dumps(r) + "\n")
    with pytest.raises(ValueError, match="uniqueness"):
        controls.checked_cache(path)
    r["review_response"] = '{"accept":false}'
    path.write_text(json.dumps(r) + "\n")
    with pytest.raises(ValueError, match="source checks"):
        controls.checked_cache(path)


def config(**overrides):
    return controls.EvidenceConfig(
        arm="ratings",
        phase="ratings",
        training_sha256="a" * 64,
        validation_sha256="b" * 64,
        prepared_sha256="c" * 64,
        initial_sha256="d" * 64,
        **overrides,
    )


def test_schedule_keeps_the_original_prefix_and_reduces_rates_without_new_warmup():
    c = config(max_epochs=40, linear_epochs=24, warmup_fraction=0.1)
    assert controls.phase_rates(c, 1, 0, 10) == (0, 0)
    assert controls.phase_rates(c, 3, 24, 10) == (
        c.encoder_learning_rate,
        c.projection_learning_rate,
    )
    rates = controls.phase_rates(c, 25, 240, 10)
    assert rates == (3e-6, 1e-4)
    assert controls.phase_rates(c, 26, 250, 10) == rates


def tiny_model():
    model = MODEL_CLASS.__new__(MODEL_CLASS)
    nn.Module.__init__(model)
    c = T5Config(
        vocab_size=20,
        d_model=8,
        d_ff=16,
        num_layers=1,
        num_decoder_layers=1,
        num_heads=2,
        d_kv=4,
        dropout_rate=0,
        pad_token_id=0,
        eos_token_id=1,
        decoder_start_token_id=0,
    )
    model.t5 = T5ForConditionalGeneration(c)
    model.projection = nn.Linear(8, 4, bias=False)
    return model


@pytest.mark.parametrize("arm", ["ratings", "evidence", "shuffled"])
@pytest.mark.parametrize("phase,completed", [("pretrain", 6), ("ratings", 3)])
def test_phase_exposure_terminal_weights_and_continuation_patience(
    tmp_path, monkeypatch, arm, phase, completed
):
    rows = [
        {
            "id": "a",
            "sentence1": "red",
            "sentence2": "blue",
            "condition": "color",
            "target": 0.0,
            "rating": 1.0,
            "pair_id": "p",
            "group_id": "g",
        },
        {
            "id": "b",
            "sentence1": "blue",
            "sentence2": "red",
            "condition": "color",
            "target": 1.0,
            "rating": 5.0,
            "pair_id": "q",
            "group_id": "h",
        },
    ]
    inputs = {
        k: tmp_path / f"{k}.json"
        for k in ("training", "validation", "prepared", "initial_model")
    }
    write_json(inputs["training"], rows)
    write_json(inputs["validation"], rows)
    a = {answer_id("red", "color"): "red", answer_id("blue", "color"): "blue"}
    b = {k: ("blue" if v == "red" else "red") for k, v in a.items()}
    write_json(
        inputs["prepared"], {"training": rows, "aligned": a, "shuffled": b, "audit": {}}
    )
    factory = tiny_model
    torch.save({"state": factory().state_dict()}, inputs["initial_model"])
    monkeypatch.setattr(controls, "AnswerEncoder", lambda _: factory())
    monkeypatch.setattr(
        controls.AutoTokenizer, "from_pretrained", lambda *a, **k: object()
    )

    def tokens(rows, config, tokenizer):
        ids = torch.tensor([[2, 3, 1], [4, 5, 1], [4, 5, 1], [2, 3, 1]])
        return {
            "input_ids": ids,
            "attention_mask": torch.ones_like(ids),
            "pool_mask": torch.tensor([[1, 1, 0]] * 4, dtype=torch.bool),
        }

    monkeypatch.setattr(controls, "prepare_tokens", tokens)
    monkeypatch.setattr(
        controls,
        "targets_for_rows",
        lambda *args: torch.tensor([[3, 1], [5, 1], [5, 1], [3, 1]]),
    )
    monkeypatch.setattr(
        controls,
        "predictions",
        lambda model, rows, *a: ([dict(r, prediction=r["target"]) for r in rows], None),
    )
    declared = evidence_training_outputs()
    outputs = {name: tmp_path / name / draft.path for name, draft in declared.items()}
    for path in outputs.values():
        path.parent.mkdir(parents=True)
    values = {
        f"{k}_sha256": file_sha256(v) for k, v in inputs.items() if k != "initial_model"
    }
    c = controls.EvidenceConfig(
        arm=arm,
        phase=phase,
        max_epochs=6,
        linear_epochs=2,
        batch_size=2,
        device="cpu",
        patience=1,
        initial_sha256=file_sha256(inputs["initial_model"]),
        **values,
    )
    metrics = {
        k: SimpleNamespace(record=lambda *a, **k: None)
        for k in ("training_objective", "validation_mse", "validation_spearman")
    }
    controls.fit_evidence(
        SimpleNamespace(
            config=c,
            inputs=inputs,
            outputs=outputs,
            metrics=metrics,
            numpy_generators={},
        )
    )
    trace = json.loads(outputs["trace"].read_text())
    assert trace["completed_epoch"] == completed and trace["updates"] == completed
    assert trace["selected"]["epoch"] == 1
    assert torch.load(outputs["last_model"], weights_only=True)["epoch"] == completed
    assert torch.load(outputs["model"], weights_only=True)["epoch"] == 1
    # Exercise the real runner declarations and every native artifact loader.
    loaded = {name: draft.loader(outputs[name]) for name, draft in declared.items()}
    resume = loaded["resume_state"]
    assert resume.dataloader.state_dict["completed_epochs"] == completed
    assert resume.dataloader.state_dict["step"] == completed
    assert resume.dataloader.state_dict["terminal_model_sha256"] == file_sha256(
        outputs["last_model"]
    )
    assert resume.optimizer_state["optimizer"]["param_groups"]
    assert resume.optimizer_state["config"]["arm"] == arm
    assert resume.optimizer_state["config"]["phase"] == phase
    assert len({r["batch_order_sha256"] for r in trace["epochs"]}) <= 2


def test_preparation_excludes_validation_answers_from_the_shuffle(tmp_path):
    training = [
        {
            "sentence1": "A red shirt.",
            "sentence2": "A blue shirt.",
            "condition": "shirt color",
        }
    ]
    validation = [
        {
            "sentence1": "A green shirt.",
            "sentence2": "A black shirt.",
            "condition": "shirt color",
        }
    ]
    rows = [
        record(f"A {color} shirt.", "shirt color", color)
        for color in ("red", "blue", "green", "black")
    ]
    inputs = {k: tmp_path / k for k in ("training", "validation", "answers")}
    write_json(inputs["training"], training)
    write_json(inputs["validation"], validation)
    inputs["answers"].write_text("\n".join(json.dumps(r) for r in rows) + "\n")
    config = controls.PreparationConfig(
        **{k + "_sha256": file_sha256(p) for k, p in inputs.items()}
    )
    output = tmp_path / "prepared.json"
    controls.prepare_evidence(
        SimpleNamespace(config=config, inputs=inputs, outputs={"prepared": output})
    )
    prepared = json.loads(output.read_text())
    assert set(prepared["aligned"]) == controls.passage_keys(training)
    assert not set(prepared["donors"].values()) & controls.passage_keys(validation)
    assert prepared["training"] == training


def test_test_scoring_rejects_a_changed_checkpoint_or_selection(tmp_path):
    model = tmp_path / "model.pt"
    torch.save({"config": {"arm": "evidence", "phase": "ratings"}}, model)
    selection = tmp_path / "selection.json"
    write_json(
        selection,
        {
            "status": "checkpoints_frozen",
            "candidates": {"evidence": {"sha256": file_sha256(model)}},
        },
    )
    cohort = tmp_path / "test.json"
    write_json(cohort, [])
    c = controls.EvidenceTestConfig(
        arm="evidence",
        model_sha256=file_sha256(model),
        selection_sha256=file_sha256(selection),
        test_sha256=file_sha256(cohort),
    )
    context = SimpleNamespace(
        config=c, inputs={"model": model, "selection": selection, "test": cohort}
    )
    assert controls.verify_evidence_test(context)["config"]["arm"] == "evidence"
    model.write_bytes(b"changed")
    with pytest.raises(ValueError, match="Changed checkpoint"):
        controls.verify_evidence_test(context)
