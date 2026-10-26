"""Replay real audit evidence and offline source-only successful captures."""

import copy
import json
import subprocess
from pathlib import Path

import pytest

from csts_pilot import proposition_capture as capture
from csts_pilot import proposition_inputs as inputs
from csts_pilot import proposition_provenance as provenance
from csts_pilot.answers import answer_id
from csts_pilot.convergence import write_json

ROOT = Path(__file__).resolve().parents[1]


def rows(prefix):
    return [
        {
            "row_id": f"{prefix}{i}",
            "group_id": f"{prefix}g{i // 2}",
            "pair_id": f"{prefix}p{i // 2}",
            "condition": f"car color {i % 2}",
            "sentence1": f"{prefix} red car {i}",
            "sentence2": f"{prefix} blue car {i}",
            "rating": 1 + 2 * i,
            "target": i / 2,
        }
        for i in range(3)
    ]


def make_partition(directory, inventory, original, split):
    items, _ = inputs.source_inventory(original, [])
    groups = {
        answer_id(row[side], row["condition"]): row["group_id"]
        for row in original
        for side in ("sentence1", "sentence2")
    }
    write_json(inventory / f"{split}_inputs.json", items)
    write_json(inventory / f"{split}_groups.json", groups)
    directory.mkdir()
    receipts, records = [], []
    for index, selected in enumerate(capture.batches(items, groups, 64)):
        batch = directory / f"batch_{index:04d}"
        batch.mkdir()
        original_path = Path("/original-host/frozen-capture") / split / batch.name
        answers = [
            {
                "id": row["id"],
                "status": "answered",
                "target": "car",
                "attribute": "color",
                "answer": "red" if "red" in row["passage"] else "blue",
                "evidence": ["red" if "red" in row["passage"] else "blue"],
            }
            for row in selected
        ]
        write_json(batch / "inputs.json", selected)
        write_json(batch / "schema.json", capture.SCHEMA)
        (batch / "prompt.txt").write_text(
            capture.PROMPT + json.dumps(selected, ensure_ascii=False)
        )
        (batch / "events.jsonl").write_text(
            json.dumps(
                {
                    "type": "turn.completed",
                    "usage": {"input_tokens": 1, "output_tokens": 1},
                }
            )
            + "\n"
        )
        write_json(batch / "response.json", {"records": answers})
        write_json(batch / "records.json", answers)
        receipt = {
            "directory": str(original_path),
            "status": "complete",
            "returncode": 0,
            "source_sha256": provenance.AUDITED_CAPTURE_SHA256,
            "model_alias": capture.MODEL,
            "reasoning_effort": capture.EFFORT,
            "command": capture.cli_command(original_path, "offline-fixture-cli"),
            "items": len(selected),
            "tools_permitted": False,
            "labels_or_companion_fields_provided": False,
            "usage": capture.checked_events(batch / "events.jsonl"),
        }
        for filename, field in (
            ("prompt.txt", "prompt_sha256"),
            ("inputs.json", "input_sha256"),
            ("schema.json", "schema_sha256"),
            ("events.jsonl", "events_sha256"),
            ("response.json", "response_sha256"),
            ("records.json", "records_sha256"),
        ):
            receipt[field] = provenance.sha((batch / filename).read_bytes())
        write_json(batch / "receipt.json", receipt)
        receipts.append(receipt)
        records.extend(answers)
    records = capture.checked_records(items, {"records": records})
    write_json(directory / "records.json", records)
    manifest = {
        "status": "complete",
        "split": split,
        "items": len(items),
        "batches": len(receipts),
        "batch_size": 64,
        "input_file_sha256": provenance.sha(
            (inventory / f"{split}_inputs.json").read_bytes()
        ),
        "group_file_sha256": provenance.sha(
            (inventory / f"{split}_groups.json").read_bytes()
        ),
        "model_alias": capture.MODEL,
        "reasoning_effort": capture.EFFORT,
        "prompt_template_sha256": provenance.sha(capture.PROMPT.encode()),
        "schema_content_sha256": provenance.sha(
            json.dumps(capture.SCHEMA, ensure_ascii=False).encode()
        ),
        "maximum_one_item_per_source_group_per_request": True,
        "cli": "offline-fixture-cli",
        "receipts": receipts,
        "records_sha256": provenance.sha((directory / "records.json").read_bytes()),
    }
    write_json(directory / "manifest.json", manifest)
    return records, manifest


@pytest.fixture
def bank(tmp_path):
    audit = ROOT / "training_outputs/proposition_audit"
    evidence = provenance.audit_evidence(audit)
    gate_text = provenance.text(audit / "fresh_gate.json")
    training, validation = rows("train"), rows("dev")
    inventory = tmp_path / "inventory"
    inventory.mkdir()
    train_records, train_manifest = make_partition(
        tmp_path / "training", inventory, training, "training"
    )
    dev_records, dev_manifest = make_partition(
        tmp_path / "validation", inventory, validation, "validation"
    )
    items, _ = inputs.source_inventory(training, validation)
    records = capture.checked_records(items, {"records": train_records + dev_records})
    manifest = {
        "audit_gate_sha256": provenance.AUDIT_GATE_SHA256,
        "generation_source_sha256": provenance.AUDITED_CAPTURE_SHA256,
        "partitions": {"training": train_manifest, "validation": dev_manifest},
    }
    bundle = provenance.make_provenance(tmp_path, inventory, evidence)
    return training, validation, records, manifest, gate_text, bundle


def test_actual_frozen_audit_recomputes_counts_and_rejects_changed_evidence(bank):
    gate_text, bundle = bank[4:]
    assert (
        provenance.verify_frozen_audit(gate_text, bundle["audit_files"], capture)[
            "fully_faithful"
        ]
        == 58
    )
    changed = copy.deepcopy(bundle["audit_files"])
    changed["proposition_fresh60_judgments_left.json"] += " "
    with pytest.raises(ValueError, match="Changed frozen audit"):
        provenance.verify_frozen_audit(gate_text, changed, capture)
    with pytest.raises(ValueError, match="immutable receipt"):
        provenance.verify_frozen_audit('{"passed":true}', {}, capture)


def test_complete_canonical_bank_replays_after_archive_relocation(bank):
    provenance.validate_bank(*bank, capture)


@pytest.mark.parametrize(
    "changed_file",
    (
        "training/batch_0000/response.json",
        "training/batch_0000/events.jsonl",
        "inventory/training_inputs.json",
    ),
)
def test_native_provenance_rejects_changed_raw_evidence(bank, changed_file):
    changed = copy.deepcopy(bank[-1])
    changed["files"][changed_file] += " "
    with pytest.raises(ValueError):
        provenance.validate_bank(*bank[:-1], changed, capture)


def test_native_provenance_rejects_missing_receipts_or_unexpected_paths(bank):
    changed = copy.deepcopy(bank[-1])
    del changed["files"]["training/batch_0000/receipt.json"]
    with pytest.raises(ValueError, match="missing or unexpected"):
        provenance.validate_bank(*bank[:-1], changed, capture)
    changed = copy.deepcopy(bank[-1])
    changed["files"]["../outside"] = "not an accepted evidence file"
    with pytest.raises(ValueError, match="missing or unexpected"):
        provenance.validate_bank(*bank[:-1], changed, capture)


def test_native_provenance_rejects_foreign_generation_source(bank):
    changed = copy.deepcopy(bank[3])
    changed["generation_source_sha256"] = "0" * 64
    with pytest.raises(ValueError, match="generation source"):
        provenance.validate_bank(*bank[:3], changed, *bank[4:], capture)


def test_source_guard_rejects_untracked_shadow_module_and_staged_changes(tmp_path):
    subprocess.run(["git", "init", "--quiet", str(tmp_path)], check=True)
    provenance.require_clean_source(tmp_path)
    shadow = tmp_path / "torch.py"
    shadow.write_text("raise RuntimeError('shadow module')\n")
    with pytest.raises(ValueError, match="clean committed"):
        provenance.require_clean_source(tmp_path)
    subprocess.run(["git", "-C", str(tmp_path), "add", "torch.py"], check=True)
    with pytest.raises(ValueError, match="clean committed"):
        provenance.require_clean_source(tmp_path)


def test_native_provenance_rejects_mislabeled_partition_even_after_metadata_rehash(
    bank,
):
    changed_manifest = copy.deepcopy(bank[3])
    changed_bundle = copy.deepcopy(bank[-1])
    changed_manifest["partitions"]["training"]["split"] = "validation"
    changed_bundle["files"]["training/manifest.json"] = json.dumps(
        changed_manifest["partitions"]["training"]
    )
    with pytest.raises(ValueError, match="Partition capture manifest"):
        provenance.validate_bank(
            *bank[:3], changed_manifest, bank[4], changed_bundle, capture
        )
