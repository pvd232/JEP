"""Freeze complete generation coverage and source-disjoint writing references for a fresh comparison."""

import argparse
import hashlib
import json
import shutil
from pathlib import Path

from csts_pilot.proposition_pretraining import prepare_frozen_proposition_pretraining


def digest(path: Path) -> str:
    """Bind preparation to the exact retained input bytes."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path: Path):
    """Read one retained JSON artifact."""
    return json.loads(path.read_text())


def save(path: Path, value) -> None:
    """Retain a frozen input and refuse to replace different existing bytes."""
    raw = (
        json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n"
    ).encode()
    if path.exists() and path.read_bytes() != raw:
        raise ValueError(f"Frozen preparation input changed: {path}")
    path.write_bytes(raw)


def prepare(root: Path, monitor: Path) -> dict:
    """Validate every generated identity and freeze the unrestricted writing protocol."""
    complete = read(monitor / "training_complete.json")
    records = monitor / "full_training_records.json"
    if (
        complete["status"] != "complete"
        or digest(records) != complete["records_sha256"]
    ):
        raise ValueError(
            "Full generation must finish with its original retained digest."
        )
    inputs = read(monitor / "all_inputs.json")
    generated = read(records)
    if len(generated) != len(inputs) or {r["id"] for r in generated} != {
        r["id"] for r in inputs
    }:
        raise ValueError("Every training input requires exactly one frozen generation.")
    output = root / "csts_data/jep-csts-v1-propositions/full_bank"
    output.mkdir(parents=True, exist_ok=True)
    save(output / "records.json", generated)
    pilot = root / "csts_data/jep-csts-v1-propositions/pilot_bank"
    provenance = read(pilot / "provenance.json")
    captures = []
    manifest = read(monitor / "training_capture/manifest.json")
    for completed_batch in manifest["receipts"]:
        receipt = Path(completed_batch["directory"]) / "receipt.json"
        captures.append(
            {
                "batch": str(receipt.parent),
                "receipt_sha256": digest(receipt),
                "records_sha256": digest(receipt.parent / "records.json"),
            }
        )
    if len(captures) != manifest["batches"]:
        raise ValueError("Every new capture batch requires its retained receipt.")
    provenance.update(
        items=len(generated),
        records_sha256=digest(output / "records.json"),
        completed_batches=provenance["completed_batches"] + captures,
        full_capture_source_sha256=digest(
            root / "scripts/capture_proposition_inputs.py"
        ),
        initial_policy_gate_applies_to="Frozen generation prompt and schema; new bank quality is recorded separately in full_generation_review.",
        full_generation=complete,
        full_generation_review=read(monitor / "training_factual_review/result.json"),
    )
    save(output / "provenance.json", provenance)
    shutil.copyfile(pilot / "audit_gate.json", output / "audit_gate.json")
    settings = read(root / "configs/csts-qwen-jep-v1-four-epoch.json")
    for key in (
        "continuation_parent_root",
        "continuation_parent_name",
        "phase1_extension",
    ):
        settings.pop(key, None)
    for name in ("answers", "provenance", "audit_gate"):
        path = output / ("records.json" if name == "answers" else name + ".json")
        settings[name] = {"path": str(path.relative_to(root)), "sha256": digest(path)}
    references = {
        r["id"]: r
        for r in read(monitor / "validated_references.json")
        if r["status"] == "answered"
    }
    heldout = [
        {**item, "answer": references[item["id"]]["answer"]}
        for item in read(monitor / "validation_inputs.json")
        if item["id"] in references
    ]
    if {r["id"] for r in heldout} & {r["id"] for r in inputs}:
        raise ValueError("Writing validation identities must remain source-disjoint.")
    save(output / "writing_validation.json", heldout)
    settings.update(
        proposition_until_patience=True,
        concurrent_ratings_control=True,
        gpu_model="NVIDIA A100-SXM4-80GB",
        proposition_validation={
            "path": str((output / "writing_validation.json").relative_to(root)),
            "sha256": digest(output / "writing_validation.json"),
        },
    )
    settings["training"].update(
        microbatch_size=32, patience=1, train_until_patience=True
    )
    settings["phases"]["pretrain"]["max_epochs"] = 1
    data = {
        "training": root / settings["splits"]["training"]["path"],
        "validation": root / settings["splits"]["validation"]["path"],
        "records": output / "records.json",
        "provenance": output / "provenance.json",
    }
    prepared = prepare_frozen_proposition_pretraining(
        {k: p.read_bytes() for k, p in data.items()},
        {k: digest(p) for k, p in data.items()},
    )
    if prepared["audit"]["uncaptured_training_inputs"] != 0:
        raise ValueError("The full-bank run cannot use partial capture.")
    save(output / "prepared_preview.json", prepared)
    save(root / "configs/csts-qwen-jep-v1-full-propositions-converged.json", settings)
    return prepared["audit"]


def main() -> None:
    """Prepare inputs without starting model forwards."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--monitor", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(prepare(args.root, args.monitor), indent=2))


if __name__ == "__main__":
    main()
