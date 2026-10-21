"""Protect cached facts, acceptance coverage and source-validation boundaries."""

import json

import pytest

from csts_pilot.annotation_formats import prepare_targets, render_target


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
