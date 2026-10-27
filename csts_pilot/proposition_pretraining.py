"""Prepare captured propositions for matched auxiliary Qwen training."""

import copy
import hashlib
import json
import math
import re
from collections import Counter
from typing import Any

from csts_pilot.data import canonical
from csts_pilot.proposition_capture import checked_records, validate_inputs

SHA256 = re.compile(r"^[0-9a-f]{64}$")
INPUT_NAMES = {"training", "validation", "records", "provenance"}


def _answer_id(passage: str, condition: str) -> str:
    """Use the existing answers.answer_id identity without model dependencies."""
    value = json.dumps([canonical(passage), canonical(condition)])
    return hashlib.sha256(value.encode()).hexdigest()


def _inventory(
    rows: list[dict[str, Any]],
) -> tuple[
    dict[str, dict[str, str]], set[str], set[str], dict[str, set[tuple[str, str]]]
]:
    """Retain original representatives and reject inconsistent source ownership."""
    if not rows:
        raise ValueError("Both original source partitions must contain comparisons.")
    items: dict[str, dict[str, str]] = {}
    groups: dict[str, str] = {}
    variants: dict[str, set[tuple[str, str]]] = {}
    captions, row_ids = set(), set()
    for row in rows:
        for field in ("row_id", "group_id", "sentence1", "sentence2", "condition"):
            if not isinstance(row.get(field), str) or not row[field].strip():
                raise ValueError(f"A comparison needs a nonempty {field}.")
        if row["row_id"] in row_ids:
            raise ValueError("Comparison identities must be unique within a partition.")
        row_ids.add(row["row_id"])
        rating, target = row.get("rating"), row.get("target")
        if (
            isinstance(rating, bool)
            or not isinstance(rating, (int, float))
            or not math.isfinite(rating)
            or not 1 <= rating <= 5
            or isinstance(target, bool)
            or not isinstance(target, (int, float))
            or not math.isfinite(target)
            or not math.isclose(target, (rating - 1) / 4, rel_tol=0, abs_tol=1e-12)
        ):
            raise ValueError("Original ratings and normalized targets must agree.")
        for side in ("sentence1", "sentence2"):
            passage, condition = row[side], row["condition"]
            identity = _answer_id(passage, condition)
            if identity in groups and groups[identity] != row["group_id"]:
                raise ValueError("A passage-condition identity changes source group.")
            groups[identity] = row["group_id"]
            items.setdefault(
                identity, {"id": identity, "passage": passage, "condition": condition}
            )
            variants.setdefault(identity, set()).add((passage, condition))
            captions.add(canonical(passage))
    return items, set(groups.values()), captions, variants


def prepare_proposition_pretraining(
    training: list[dict[str, Any]],
    validation: list[dict[str, Any]],
    records: list[dict[str, Any]],
    source_inputs: list[dict[str, str]],
    provenance: dict[str, Any],
    *,
    input_sha256: dict[str, str],
) -> dict[str, Any]:
    """Use answered training targets and retain the same phase-A rows in both arms.

    The caller binds decoded objects to exact frozen bytes. The byte-oriented
    wrapper below performs that check directly. Literal evidence validation
    establishes quotation fidelity; semantic correctness remains the recorded
    teacher-policy/model-assisted-audit claim.
    """
    if set(input_sha256) != INPUT_NAMES or any(
        not isinstance(value, str) or SHA256.fullmatch(value) is None
        for value in input_sha256.values()
    ):
        raise ValueError("Bind all four frozen preparation input hashes.")
    train_items, train_groups, train_captions, variants = _inventory(training)
    valid_items, valid_groups, valid_captions, _ = _inventory(validation)
    if (
        train_groups & valid_groups
        or train_captions & valid_captions
        or train_items.keys() & valid_items.keys()
        or {row["row_id"] for row in training} & {row["row_id"] for row in validation}
    ):
        raise ValueError("Training and validation source identities must be disjoint.")
    validate_inputs(source_inputs)
    source_lookup = {item["id"]: item for item in source_inputs}
    for identity, item in source_lookup.items():
        if (
            _answer_id(item["passage"], item["condition"]) != identity
            or identity not in train_items
            or (item["passage"], item["condition"]) not in variants[identity]
        ):
            raise ValueError(
                "A generation source differs from its original training input."
            )
    if (
        not isinstance(records, list)
        or not records
        or any(not isinstance(record, dict) for record in records)
    ):
        raise ValueError("Provide a nonempty frozen generated-record list.")
    identities: list[str] = []
    for record in records:
        identity = record.get("id")
        if not isinstance(identity, str):
            raise TypeError("Generated records need unique string identities.")
        identities.append(identity)
    if len(set(identities)) != len(identities):
        raise ValueError("Generated records need unique string identities.")
    if not set(identities) <= source_lookup.keys():
        raise ValueError("Generated targets include a foreign or validation identity.")
    if (
        provenance.get("records_sha256") != input_sha256["records"]
        or provenance.get("source_training_sha256") != input_sha256["training"]
        or type(provenance.get("items")) is not int
        or provenance["items"] != len(records)
    ):
        raise ValueError("Captured-record or training-source provenance changed.")
    for field in (
        "capture_source_sha256",
        "generation_template_sha256",
        "schema_sha256",
        "audit_gate_sha256",
    ):
        if (
            not isinstance(provenance.get(field), str)
            or SHA256.fullmatch(provenance[field]) is None
        ):
            raise ValueError(f"Capture provenance requires a valid {field}.")
    for field in ("capture_source_commit", "model_alias", "reasoning_effort"):
        if not isinstance(provenance.get(field), str) or not provenance[field].strip():
            raise ValueError(f"Capture provenance requires a nonempty {field}.")
    batches = provenance.get("completed_batches")
    if not isinstance(batches, list) or not batches:
        raise ValueError("Preserve completed raw-capture receipt identities.")
    batch_names = set()
    for batch in batches:
        if (
            not isinstance(batch, dict)
            or not isinstance(batch.get("batch"), str)
            or not batch["batch"]
            or batch["batch"] in batch_names
            or any(
                not isinstance(batch.get(field), str)
                or SHA256.fullmatch(batch[field]) is None
                for field in ("receipt_sha256", "records_sha256")
            )
        ):
            raise ValueError("Completed capture batches need unique bound receipts.")
        batch_names.add(batch["batch"])
    chosen_inputs = [source_lookup[identity] for identity in identities]
    checked = checked_records(chosen_inputs, {"records": records})
    aligned = {
        record["id"]: record["answer"]
        for record in sorted(checked, key=lambda item: item["id"])
        if record["status"] == "answered"
    }
    eligible = [
        row
        for row in training
        if any(
            _answer_id(row[side], row["condition"]) in aligned
            for side in ("sentence1", "sentence2")
        )
    ]
    if not aligned or not eligible:
        raise ValueError("No accepted generated training target is available.")
    coverage = Counter(
        sum(
            _answer_id(row[side], row["condition"]) in aligned
            for side in ("sentence1", "sentence2")
        )
        for row in training
    )
    audit = {
        "training_rows": len(training),
        "stage_a_comparisons": len(eligible),
        "stage_b_comparisons": len(training),
        "validation_comparisons": len(validation),
        "training_unique_inputs": len(train_items),
        "captured_training_inputs": len(records),
        "uncaptured_training_inputs": len(train_items) - len(records),
        "supervised_training_keys": len(aligned),
        "status_counts": dict(
            sorted(Counter(record["status"] for record in checked).items())
        ),
        "comparison_answer_coverage": {
            "neither": coverage[0],
            "one": coverage[1],
            "both": coverage[2],
        },
        "training_source_groups": len(train_groups),
        "stage_a_source_groups": len({row["group_id"] for row in eligible}),
        "validation_source_groups": len(valid_groups),
        "validation_evidence_used_for_training": False,
        "source_groups_and_captions_disjoint": True,
        "partial_capture": len(records) < len(train_items),
        "target_selection": "Available frozen answered training records; independent of ratings and predictions.",
        "phase_a_rows": "Identical original comparisons in both arms; at least one captured answered side.",
        "phase_b_rows": "All original training comparisons in both arms.",
        "transition": "Terminal weights after the common fixed update budget.",
        "input_sha256": dict(input_sha256),
        "capture_provenance": copy.deepcopy(provenance),
        "raw_receipts_replayed_by_this_helper": False,
        "expert_verified": False,
        "answer_token_policy": "Preserve full answer text; tokenizer ceiling is checked before fitting.",
    }
    return {"training": copy.deepcopy(eligible), "aligned": aligned, "audit": audit}


def prepare_frozen_proposition_pretraining(
    inputs: dict[str, bytes], expected_sha256: dict[str, str]
) -> dict[str, Any]:
    """Bind exact raw JSON bytes before selecting any auxiliary-training targets."""
    if set(inputs) != INPUT_NAMES or set(expected_sha256) != INPUT_NAMES:
        raise ValueError("Provide training, validation, records and provenance bytes.")
    actual = {}
    values = {}
    for name, data in inputs.items():
        if not isinstance(data, bytes):
            raise TypeError("Frozen inputs must be raw bytes.")
        actual[name] = hashlib.sha256(data).hexdigest()
        if actual[name] != expected_sha256[name]:
            raise ValueError(f"Changed frozen preparation bytes: {name}.")
        values[name] = json.loads(data)
    if any(
        not isinstance(values[name], list)
        for name in ("training", "validation", "records")
    ) or not isinstance(values["provenance"], dict):
        raise ValueError("Frozen input JSON types differ from the preparation schema.")
    inventory, _, _, _ = _inventory(values["training"])
    return prepare_proposition_pretraining(
        values["training"],
        values["validation"],
        values["records"],
        list(inventory.values()),
        values["provenance"],
        input_sha256=actual,
    )
