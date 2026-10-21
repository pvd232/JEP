"""Protect cached facts, acceptance coverage and source-validation boundaries."""

import json
from collections import defaultdict
from types import SimpleNamespace

import pytest
import torch
from transformers import T5Config, T5ForConditionalGeneration

from csts_pilot import joint
from csts_pilot.annotation_formats import prepare_targets, render_target
from csts_pilot.joint import JointConfig, selection_score


def accepted_record():
    return {
        "id": "example",
        "passage": "A person wears a red shirt.",
        "condition": "shirt color",
        "valid": True,
        "target": "shirt",
        "attribute": "color",
        "answer": "red",
        "response": json.dumps(
            {"target": "shirt", "attribute": "color", "evidence": "red"}
        ),
        "review_response": '{"accept":true}',
    }


def test_record_and_prose_preserve_identical_unescaped_facts():
    row = accepted_record()
    row.update(
        target='a "quoted" entity', attribute="acción", answer="line one\nline two"
    )
    fields = json.loads(render_target(row, "record"))
    assert fields == {
        "target": row["target"],
        "attribute": row["attribute"],
        "evidence": row["answer"],
    }
    prose = render_target(row, "prose")
    assert all(
        json.dumps(value, ensure_ascii=False) in prose for value in fields.values()
    )
    assert render_target(row, "evidence") == row["answer"]


def test_unaccepted_examples_stay_maskable_and_missing_metadata_fails():
    row = accepted_record()
    for style in ("evidence", "prose", "record"):
        assert render_target(dict(row, valid=False), style) == ""
    with pytest.raises(ValueError, match="target or attribute"):
        render_target(dict(row, target=""), "record")


def test_preparation_preserves_coverage_and_refuses_changed_evidence(tmp_path):
    source = tmp_path / "cache.jsonl"
    row = accepted_record()
    rejected = dict(row, id="rejected", valid=False, answer="")
    source.write_text("\n".join(json.dumps(item) for item in (row, rejected)) + "\n")
    destination = tmp_path / "targets"
    manifest = prepare_targets(source, destination, expected_count=2)
    assert manifest["accepted"] == 1 and manifest["new_teacher_calls"] == 0
    for style in ("evidence", "prose", "record"):
        targets = [
            json.loads(line)
            for line in (destination / f"{style}.jsonl").read_text().splitlines()
        ]
        assert [item["id"] for item in targets] == ["example", "rejected"]
        assert targets[1]["valid"] is False and targets[1]["answer"] == ""
    row["answer"] = "blue"
    source.write_text(json.dumps(row) + "\n")
    with pytest.raises(ValueError, match="original checks"):
        prepare_targets(source, tmp_path / "invalid", expected_count=1)
    assert not (tmp_path / "invalid").exists()


def test_ranking_checkpoint_selection_handles_improving_ranks_with_worse_mse():
    earlier = {"mse_0_1": 0.070098, "spearman": 0.5208}
    later = {"mse_0_1": 0.070156, "spearman": 0.5421}
    ranking = JointConfig(objective="ratings", checkpoint_metric="spearman")
    historical = JointConfig(objective="ratings")
    assert selection_score(ranking, later, None) < selection_score(
        ranking, earlier, None
    )
    assert selection_score(historical, earlier, None) < selection_score(
        historical, later, None
    )
    annotation = JointConfig(objective="answers", checkpoint_metric="spearman")
    assert selection_score(annotation, earlier, 0.3) == 0.3
    with pytest.raises(ValueError, match="finite"):
        selection_score(ranking, dict(later, spearman=None), None)


@pytest.mark.parametrize(("fixed_budget", "expected_epochs"), [(True, 3), (False, 2)])
def test_training_budget_survives_a_worsening_selection_curve(
    tmp_path, monkeypatch, fixed_budget, expected_epochs
):
    """Exercise the actual training loop while controlling development quality."""
    tiny = T5Config(
        vocab_size=20,
        d_model=16,
        d_ff=32,
        num_layers=1,
        num_decoder_layers=1,
        num_heads=2,
        d_kv=8,
        dropout_rate=0,
        pad_token_id=0,
        eos_token_id=1,
        decoder_start_token_id=0,
    )
    monkeypatch.setattr(
        joint.T5ForConditionalGeneration,
        "from_pretrained",
        lambda *args, **kwargs: T5ForConditionalGeneration(tiny),
    )
    monkeypatch.setattr(
        joint.AutoTokenizer, "from_pretrained", lambda *args, **kwargs: None
    )
    monkeypatch.setattr(torch.cuda, "reset_peak_memory_stats", lambda: None)
    token_ids = torch.tensor([[2, 3, 1], [4, 5, 1], [6, 7, 1], [8, 9, 1]])
    monkeypatch.setattr(
        joint,
        "prepare_tokens",
        lambda *args, **kwargs: {
            "input_ids": token_ids,
            "attention_mask": torch.ones_like(token_ids),
            "pool_mask": token_ids.ne(1),
        },
    )
    monkeypatch.setattr(
        joint, "answer_labels", lambda *args, **kwargs: torch.tensor([[3, 1]] * 4)
    )
    scores = iter([0.4, 0.6, 0.5, 0.4])
    monkeypatch.setattr(
        joint, "summarize", lambda rows: {"mse_0_1": 0.1, "spearman": next(scores)}
    )
    rows = [{"target": 0.2}, {"target": 0.8}]
    for name in ("training", "development"):
        (tmp_path / f"{name}.json").write_text(json.dumps(rows))
    (tmp_path / "answers.jsonl").write_text("")
    config = JointConfig(
        objective="ratings",
        device="cpu",
        projection_dimension=8,
        batch_size=2,
        max_epochs=3,
        patience=1,
        checkpoint_metric="spearman",
        fixed_epoch_budget=fixed_budget,
    )
    context = SimpleNamespace(
        config=config,
        inputs={
            name: tmp_path / filename
            for name, filename in {
                "training": "training.json",
                "development": "development.json",
                "answers": "answers.jsonl",
            }.items()
        },
        outputs={
            name: tmp_path / filename
            for name, filename in {
                "model": "model.pt",
                "trace": "trace.json",
                "resume_state": "resume.pt",
                "development_predictions": "predictions.json",
            }.items()
        },
        metrics=defaultdict(
            lambda: SimpleNamespace(record=lambda *args, **kwargs: None)
        ),
        numpy_generators={},
    )
    joint.fit(context)
    trace = json.loads((tmp_path / "trace.json").read_text())
    assert len(trace["epochs"]) == expected_epochs
    assert trace["best_epoch"] == 1
    assert trace["selection_metric"] == "spearman"
    assert trace["best_selection_value"] == 0.6
