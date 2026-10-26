"""Verify the frozen proposition audit and portable raw capture evidence.

The capture controller can load this standard-library-only module from its
pinned source. Native preparation replays the same successful request evidence;
canonical passage identities and raw representatives remain owned by inputs.
"""

import hashlib
import json
import re
import subprocess
import tempfile
from pathlib import Path
from typing import Any

AUDITED_CAPTURE_SHA256 = (
    "e8ee5293f2a77420a5fe2f69168988e7772da2b3478927f73531856827a8f462"
)
AUDIT_GATE_SHA256 = "1ed74a76ec898775199dbec28a03e5ca8df453cc65ef81a8c46954b749118af7"
TRAINING_SHA256 = "4058b7f63a5285ebdb5061f24f7f2907e76e2ddc7c99480bfd39fc69062a7d01"
VALIDATION_SHA256 = "f01ec22320c590e381ede0b378895cdd241cd8079e06b18715bc13d2921a4273"
CAPTURE_FILES = (
    "receipt.json",
    "inputs.json",
    "schema.json",
    "prompt.txt",
    "events.jsonl",
    "response.json",
    "records.json",
)
BATCH_NAME = re.compile(r"batch_[0-9]{4}(?:-attempt_[0-9]{2,})?")


def sha(data: bytes) -> str:
    """Identify exact reviewed source, audit or raw response bytes."""
    return hashlib.sha256(data).hexdigest()


def text(path: Path) -> str:
    """Retain exact newlines when transporting raw capture text."""
    return path.read_bytes().decode("utf-8")


def verify_frozen_audit(
    gate_text: str, audit_files: dict[str, str], capture: Any
) -> dict[str, Any]:
    """Pin the receipt and all evidence, then recompute judgment coverage/counts."""
    if sha(gate_text.encode()) != AUDIT_GATE_SHA256:
        raise ValueError(
            "The fidelity gate differs from the reviewed immutable receipt."
        )
    gate = json.loads(gate_text)
    if set(audit_files) != set(gate["audit_files"]):
        raise ValueError("Incomplete frozen audit evidence.")
    for name, expected in gate["audit_files"].items():
        if Path(name).name != name or sha(audit_files[name].encode()) != expected:
            raise ValueError(f"Changed frozen audit evidence: {name}.")
    expected = {
        "capture_source_sha256": AUDITED_CAPTURE_SHA256,
        "source_validation_sha256": VALIDATION_SHA256,
        "generation_template_sha256": sha(capture.PROMPT.encode()),
        "schema_sha256": sha(json.dumps(capture.SCHEMA, ensure_ascii=False).encode()),
        "model_alias": capture.MODEL,
        "reasoning_effort": capture.EFFORT,
        "generation_frozen": True,
        "expert_verified": False,
    }
    if any(gate.get(key) != value for key, value in expected.items()):
        raise ValueError("Audited source or frozen generation policy differs.")
    items = json.loads(audit_files["proposition_fresh60_left.json"]) + json.loads(
        audit_files["proposition_fresh60_right.json"]
    )
    capture.checked_records(
        items, {"records": json.loads(audit_files["proposition_fresh60_records.json"])}
    )
    judgments = json.loads(
        audit_files["proposition_fresh60_judgments_left.json"]
    ) + json.loads(audit_files["proposition_fresh60_judgments_right.json"])
    ids = [row["id"] for row in judgments]
    if (
        len(ids) != 60
        or len(set(ids)) != 60
        or set(ids) != {row["id"] for row in items}
    ):
        raise ValueError("Fresh judgment identities do not cover the audited sources.")
    if any(
        row["variant"] != "P"
        or type(row["fully_faithful"]) is not bool
        or type(row["severe_unsupported"]) is not bool
        for row in judgments
    ):
        raise ValueError("Malformed fresh fidelity judgments.")
    faithful = sum(row["fully_faithful"] for row in judgments)
    severe = sum(row["severe_unsupported"] for row in judgments)
    if (
        gate["passed"] is not True
        or faithful != gate["fully_faithful"]
        or severe != gate["severe_unsupported"]
        or gate["items"] != 60
        or gate["required_faithful"] != 57
        or faithful < 57
        or gate["allowed_severe_unsupported"] != 0
        or severe
    ):
        raise ValueError("Recomputed fidelity counts do not pass the frozen screen.")
    return gate


def audit_evidence(directory: Path) -> dict[str, str]:
    """Collect exactly the files named by the immutable review receipt."""
    gate = json.loads(text(directory / "fresh_gate.json"))
    return {name: text(directory / name) for name in gate["audit_files"]}


def make_provenance(
    root: Path, inventory: Path, audit_files: dict[str, str]
) -> dict[str, Any]:
    """Project successful raw requests without stderr or unrelated private files."""
    files = {}
    for split in ("training", "validation"):
        for suffix in ("inputs", "groups"):
            files[f"inventory/{split}_{suffix}.json"] = text(
                inventory / f"{split}_{suffix}.json"
            )
        manifest = json.loads(text(root / split / "manifest.json"))
        names = ["manifest.json", "records.json"]
        for receipt in manifest["receipts"]:
            name = Path(receipt["directory"]).name
            if BATCH_NAME.fullmatch(name) is None:
                raise ValueError("Invalid successful batch directory identity.")
            names.extend(f"{name}/{filename}" for filename in CAPTURE_FILES)
        if len(set(names)) != len(names):
            raise ValueError("Successful batch directories must be unique.")
        files.update({f"{split}/{name}": text(root / split / name) for name in names})
    return {"version": 1, "audit_files": audit_files, "files": files}


def check_partition(
    items: list[dict[str, Any]],
    groups: dict[str, str],
    directory: Path,
    declared: dict[str, Any],
    capture: Any,
) -> list[dict[str, Any]]:
    """Recheck raw evidence after relocation while preserving original command paths."""
    manifest = json.loads(text(directory / "manifest.json"))
    if (
        manifest != declared
        or manifest.get("split") != directory.name
        or manifest.get("status") != "complete"
        or manifest.get("items") != len(items)
        or manifest.get("model_alias") != capture.MODEL
        or manifest.get("reasoning_effort") != capture.EFFORT
        or manifest.get("prompt_template_sha256") != sha(capture.PROMPT.encode())
        or manifest.get("schema_content_sha256")
        != sha(json.dumps(capture.SCHEMA, ensure_ascii=False).encode())
        or manifest.get("maximum_one_item_per_source_group_per_request") is not True
    ):
        raise ValueError("Partition capture manifest differs from its frozen policy.")
    selected = capture.batches(items, groups, manifest["batch_size"])
    if len(selected) != manifest.get("batches") or len(selected) != len(
        manifest.get("receipts", [])
    ):
        raise ValueError("Successful capture batch coverage differs.")
    all_records = []
    for batch_items, archived in zip(selected, manifest["receipts"], strict=True):
        original = Path(archived["directory"])
        if BATCH_NAME.fullmatch(original.name) is None:
            raise ValueError("Invalid successful batch directory identity.")
        batch = directory / original.name
        receipt = json.loads(text(batch / "receipt.json"))
        if receipt != {
            key: value for key, value in archived.items() if key != "reused"
        }:
            raise ValueError("Manifest and immutable batch receipt differ.")
        if (
            receipt.get("status") != "complete"
            or receipt.get("returncode") != 0
            or receipt.get("source_sha256")
            not in {AUDITED_CAPTURE_SHA256, sha(Path(capture.__file__).read_bytes())}
            or receipt.get("model_alias") != capture.MODEL
            or receipt.get("reasoning_effort") != capture.EFFORT
            or receipt.get("command") != capture.cli_command(original, manifest["cli"])
            or receipt.get("items") != len(batch_items)
            or receipt.get("tools_permitted") is not False
            or receipt.get("labels_or_companion_fields_provided") is not False
        ):
            raise ValueError("Successful request settings or source binding differs.")
        if (
            json.loads(text(batch / "inputs.json")) != batch_items
            or json.loads(text(batch / "schema.json")) != capture.SCHEMA
            or text(batch / "prompt.txt")
            != capture.PROMPT + json.dumps(batch_items, ensure_ascii=False)
        ):
            raise ValueError("Source-only prompt or schema differs.")
        for filename, field in (
            ("prompt.txt", "prompt_sha256"),
            ("inputs.json", "input_sha256"),
            ("schema.json", "schema_sha256"),
            ("events.jsonl", "events_sha256"),
            ("response.json", "response_sha256"),
            ("records.json", "records_sha256"),
        ):
            if sha((batch / filename).read_bytes()) != receipt.get(field):
                raise ValueError(f"Changed successful capture bytes: {filename}.")
        if capture.checked_events(batch / "events.jsonl") != receipt.get("usage"):
            raise ValueError("Successful request usage differs from its event log.")
        records = capture.checked_records(
            batch_items, json.loads(text(batch / "response.json"))
        )
        if records != json.loads(text(batch / "records.json")):
            raise ValueError("Checked records differ from the raw response.")
        all_records.extend(records)
    records = capture.checked_records(items, {"records": all_records})
    if records != json.loads(text(directory / "records.json")) or sha(
        (directory / "records.json").read_bytes()
    ) != manifest.get("records_sha256"):
        raise ValueError(
            "Aggregate partition records differ from checked raw requests."
        )
    return records


def validate_bank(
    training: list[dict[str, Any]],
    validation: list[dict[str, Any]],
    records: list[dict[str, Any]],
    manifest: dict[str, Any],
    gate_text: str,
    provenance: dict[str, Any],
    capture: Any,
) -> None:
    """Require real source-bound capture evidence before native preparation."""
    from csts_pilot.answers import answer_id
    from csts_pilot.proposition_inputs import source_inventory

    verify_frozen_audit(gate_text, provenance["audit_files"], capture)
    if (
        provenance.get("version") != 1
        or manifest.get("audit_gate_sha256") != AUDIT_GATE_SHA256
        or manifest.get("generation_source_sha256")
        not in {AUDITED_CAPTURE_SHA256, sha(Path(capture.__file__).read_bytes())}
        or set(manifest.get("partitions", {})) != {"training", "validation"}
    ):
        raise ValueError("Full bank generation source or audit binding differs.")
    files = provenance["files"]
    if not isinstance(files, dict) or any(
        not isinstance(name, str) or not isinstance(value, str)
        for name, value in files.items()
    ):
        raise ValueError("Raw provenance must map relative filenames to exact text.")
    allowed = {
        f"inventory/{split}_{suffix}.json"
        for split in ("training", "validation")
        for suffix in ("inputs", "groups")
    }
    for split, declared in manifest["partitions"].items():
        allowed.update(f"{split}/{name}" for name in ("manifest.json", "records.json"))
        for receipt in declared["receipts"]:
            name = Path(receipt["directory"]).name
            if BATCH_NAME.fullmatch(name) is None:
                raise ValueError("Invalid successful batch directory identity.")
            allowed.update(f"{split}/{name}/{filename}" for filename in CAPTURE_FILES)
    if set(files) != allowed:
        raise ValueError("Raw provenance contains missing or unexpected files.")
    checked = []
    with tempfile.TemporaryDirectory(
        prefix="csts-proposition-provenance-"
    ) as temporary:
        directory = Path(temporary)
        for name, value in files.items():
            path = directory / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(value.encode())
        for split, rows in (("training", training), ("validation", validation)):
            items, _ = source_inventory(rows, [])
            groups = {
                answer_id(row[side], row["condition"]): row["group_id"]
                for row in rows
                for side in ("sentence1", "sentence2")
            }
            for suffix, expected in (("inputs", items), ("groups", groups)):
                source = directory / "inventory" / f"{split}_{suffix}.json"
                if (
                    json.loads(text(source)) != expected
                    or sha(source.read_bytes())
                    != manifest["partitions"][split][
                        f"{'input' if suffix == 'inputs' else 'group'}_file_sha256"
                    ]
                ):
                    raise ValueError(
                        "Captured inventory differs from its original source partition."
                    )
            checked.extend(
                check_partition(
                    items,
                    groups,
                    directory / split,
                    manifest["partitions"][split],
                    capture,
                )
            )
    all_items, _ = source_inventory(training, validation)
    if capture.checked_records(all_items, {"records": checked}) != records:
        raise ValueError("Full bank records differ from the complete checked capture.")


def require_clean_source(root: Path) -> None:
    """Reject uncommitted tracked or untracked imports before allocating work."""
    status = subprocess.run(
        ["git", "-C", str(root), "status", "--porcelain", "--untracked-files=all"],
        check=True,
        capture_output=True,
        text=True,
    )
    if status.stdout:
        raise ValueError(
            "Native execution requires a clean committed source/config tree."
        )
