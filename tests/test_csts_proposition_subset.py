"""Verify subset identities, frozen audit binding and provisional-only decisions."""

import copy
import json
from types import SimpleNamespace

import pytest

from csts_pilot import proposition_subset as module
from csts_pilot.answers import answer_id
from csts_pilot.convergence import file_sha256


def comparison(index):
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


def inputs(row):
    return [
        {
            "id": answer_id(row[side], row["condition"]),
            "passage": row[side],
            "condition": row["condition"],
        }
        for side in ("sentence1", "sentence2")
    ]


def record(item, answered=True):
    return {
        "id": item["id"],
        "status": "answered" if answered else "not_specified",
        "target": "car",
        "attribute": "color",
        "answer": "The car is red." if answered else "",
        "evidence": ["red"] if answered else [],
    }


def records(row):
    a, b = inputs(row)
    return [record(a), record(b, False)]


def test_selects_only_complete_pair_identities_and_keeps_abstentions():
    training, validation = [comparison(0), comparison(1)], [comparison(2)]
    captured = records(training[0]) + [record(inputs(training[1])[0])]
    a, b = inputs(validation[0])
    train, dev, chosen = module.select_rows(
        training, validation, captured, [a], [b], records(validation[0])
    )
    assert train == training[:1] and dev == validation
    assert len(chosen) == 4
    transformed, coverage = module.transform_rows(
        train, {item["id"]: item for item in chosen}
    )
    assert transformed[0]["sentence2"] == training[0]["sentence2"]
    assert coverage["comparison_coverage"] == {"both": 0, "one": 1, "neither": 0}


def test_selection_does_not_depend_on_similarity_labels():
    training, dev = [comparison(0)], [comparison(1)]
    a, b = inputs(dev[0])
    captured, fresh = records(training[0]), records(dev[0])
    first = module.select_rows(training, dev, captured, [a], [b], fresh)
    changed = [dict(training[0], rating=5.0, target=1.0)]
    second = module.select_rows(changed, dev, captured, [a], [b], fresh)
    assert [row["row_id"] for row in first[0]] == [row["row_id"] for row in second[0]]


def test_rejects_duplicate_or_unsupported_captured_records():
    train, dev = [comparison(0)], [comparison(1)]
    a, b = inputs(dev[0])
    for bad in (
        records(train[0]) * 2,
        [dict(records(train[0])[0], evidence=["invented"]), records(train[0])[1]],
    ):
        with pytest.raises(ValueError):
            module.select_rows(train, dev, bad, [a], [b], records(dev[0]))


def test_fresh_quotes_use_actual_raw_generation_input():
    train, dev = [comparison(0)], [comparison(1)]
    a, b = inputs(dev[0])
    a["passage"] = a["passage"].replace("red car", "red  car")
    fresh = records(dev[0])
    fresh[0]["evidence"] = ["red  car"]
    _, chosen, _ = module.select_rows(train, dev, records(train[0]), [a], [b], fresh)
    assert chosen == dev


def test_rejects_fresh_passage_bound_to_wrong_identity():
    train, dev = [comparison(0)], [comparison(1)]
    a, b = inputs(dev[0])
    a["passage"] = "A red bus."
    with pytest.raises(ValueError, match="canonical identity"):
        module.select_rows(train, dev, records(train[0]), [a], [b], records(dev[0]))


def test_rejects_missing_audited_pair_or_split_overlap():
    train, dev = [comparison(0)], [comparison(1)]
    a, b = inputs(dev[0])
    with pytest.raises(ValueError):
        module.select_rows(train, [], records(train[0]), [a], [b], records(dev[0]))
    overlapping = [dict(dev[0], group_id=train[0]["group_id"])]
    with pytest.raises(ValueError):
        module.select_rows(
            train, overlapping, records(train[0]), [a], [b], records(dev[0])
        )


def metrics(rank, fpr):
    return {
        "spearman": rank,
        "operating_point": {"false_positive_rate": fpr},
        "condition_changes": {"n": 0, "accuracy_ties_half": None},
    }


def test_promising_is_provisional_and_never_test_eligible():
    result = module.promising(metrics(0.81, 0.0), metrics(0.8, 0.0))
    assert result["promising_for_full_generation"]
    assert not result["test_eligible"] and not result["condition_ordering_measured"]
    assert not module.promising(metrics(0.79, 0.0), metrics(0.8, 0.0))[
        "promising_for_full_generation"
    ]
    assert not module.promising(metrics(0.82, 0.1), metrics(0.8, 0.0))[
        "promising_for_full_generation"
    ]
    assert not module.promising(metrics(None, 0.0), metrics(0.8, 0.0))[
        "promising_for_full_generation"
    ]


@pytest.fixture
def preparation(tmp_path):
    train, dev = [comparison(0)], [comparison(1)]
    a, b = inputs(dev[0])
    policy = {
        "generation_template_sha256": "a" * 64,
        "schema_sha256": "b" * 64,
        "model_alias": "gpt-6.1-sol",
        "reasoning_effort": "high",
    }
    values = {
        "training": train,
        "validation": dev,
        "training_records": records(train[0]),
        "left": [a],
        "right": [b],
        "fresh_records": records(dev[0]),
    }
    paths = {
        key: tmp_path / f"{key}.json"
        for key in (*values, "training_manifest", "fresh_manifest", "gate")
    }

    def write(key, value):
        paths[key].write_text(json.dumps(value))

    for key, value in values.items():
        write(key, value)
    capture_hash = "c" * 64
    write(
        "training_manifest",
        {
            **policy,
            "records_sha256": file_sha256(paths["training_records"]),
            "items": 2,
            "source_training_sha256": file_sha256(paths["training"]),
            "capture_source_sha256": capture_hash,
        },
    )
    write(
        "fresh_manifest",
        {
            "prompt_template_sha256": policy["generation_template_sha256"],
            "schema_content_sha256": policy["schema_sha256"],
            "model_alias": policy["model_alias"],
            "reasoning_effort": policy["reasoning_effort"],
            "capture_source_sha256": capture_hash,
            "source_validation_sha256": file_sha256(paths["validation"]),
        },
    )
    audit_files = {
        filename: file_sha256(paths[key])
        for key, filename in (
            ("left", "proposition_fresh60_left.json"),
            ("right", "proposition_fresh60_right.json"),
            ("fresh_records", "proposition_fresh60_records.json"),
            ("fresh_manifest", "proposition_fresh60_manifest.json"),
        )
    }
    write(
        "gate",
        {
            **policy,
            "passed": True,
            "generation_frozen": True,
            "capture_source_sha256": capture_hash,
            "audit_files": audit_files,
        },
    )
    return SimpleNamespace(
        config=module.SubsetPreparationConfig(
            input_sha256={key: file_sha256(path) for key, path in paths.items()},
            expected_validation_pairs=1,
        ),
        inputs=paths,
        outputs={
            key: tmp_path / f"out_{key}.json"
            for key in (
                "training",
                "validation",
                "original_training",
                "original_validation",
                "audit",
            )
        },
    )


def test_preparation_retains_all_frozen_audit_records_without_review_filter(
    preparation,
):
    module.prepare_subset(preparation)
    audit = json.loads(preparation.outputs["audit"].read_text())
    assert audit["coverage"]["validation"]["comparisons"] == 1
    assert not audit["test_inputs_opened"]
    assert "no judgment-based" in audit["validation_selection"]


@pytest.mark.parametrize("key", ("training_manifest", "fresh_records", "gate"))
def test_preparation_rejects_rebound_policy_or_audit_records(preparation, key):
    value = json.loads(preparation.inputs[key].read_text())
    if key == "training_manifest":
        value["model_alias"] = "other-model"
    elif key == "gate":
        value["passed"] = False
    else:
        value = copy.deepcopy(value)
        value[0]["answer"] = "A new answer."
    preparation.inputs[key].write_text(json.dumps(value))
    preparation.config = preparation.config.model_copy(
        update={
            "input_sha256": {
                name: file_sha256(path) for name, path in preparation.inputs.items()
            }
        }
    )
    with pytest.raises(ValueError):
        module.prepare_subset(preparation)
