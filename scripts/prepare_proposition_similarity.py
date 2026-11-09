"""Bind the paired embedding comparison to retained GPT captures; no inference."""

import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

from csts_pilot.extraction_formats import canonical_text, parse_payload
from csts_pilot.transport_revalidation import validate_completed_capture


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    return json.loads(Path(path).read_text())


def write(path, value):
    Path(path).write_text(json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False, allow_nan=False) + "\n")


def prepare(cohort, origin, audit_path, output):
    cohort, origin, output = map(Path, (cohort, origin, output))
    output.mkdir(parents=True, exist_ok=False)
    manifest, audit = read(cohort / "manifest.json"), read(audit_path)
    names = ("pairs.json", "sources.json", "labels.json", "protocol.json")
    for name in names:
        if sha(cohort / name) != manifest["artifacts"][name]:
            raise ValueError("Frozen cohort changed: " + name)
    executed_manifest = read(origin / "manifest.json")
    executed_protocol = read(origin / "protocol.json")
    executed_identity = {
        "manifest_sha256": sha(origin / "manifest.json"),
        "protocol_sha256": sha(origin / "protocol.json"),
    }
    if (audit.get("frozen_origin_verified") is not True
            or audit.get("status") != "parser_amendment"
            or audit.get("original_manifest_sha256") != executed_identity["manifest_sha256"]
            or audit.get("original_protocol_sha256") != executed_identity["protocol_sha256"]):
        raise ValueError("The parser audit does not bind this executed GPT origin.")
    for name in names:
        if sha(origin / name) != executed_manifest["artifacts"][name]:
            raise ValueError("Executed GPT origin changed: " + name)
    for name in names[:3]:
        if (cohort / name).read_bytes() != (origin / name).read_bytes():
            raise ValueError("Cohort differs from the executed GPT source inputs: " + name)
    executed_identity["cohort_sha256"] = {name: sha(origin / name) for name in names[:3]}
    pairs, sources, labels = [read(cohort / name) for name in names[:3]]
    by_label = {row["row_id"]: row for row in labels}
    by_source = {row["id"]: row for row in sources}
    if len(by_label) != 120 or len(by_source) != 239 or len(pairs) != 120:
        raise ValueError("Unexpected cohort")
    reviewed = {(row["arm"], row["id"]): row for row in audit["records"]}
    expected_records = ({("gpt_direct", row["row_id"]) for row in pairs}
                        | {("gpt_propositions", row["id"]) for row in sources})
    if len(audit["records"]) != 359 or set(reviewed) != expected_records:
        raise ValueError("Incomplete or duplicated retained audit")
    parsed, hashes = {}, {}
    for (arm, identity), row in reviewed.items():
        folder = origin / "captures" / arm / identity
        if not row["amended_valid"] or sha(folder / "result.json") != row["original_result_sha256"]:
            raise ValueError("Original response identity changed")
        for name, digest in row["raw_artifacts"].items():
            if sha(folder / name) != digest:
                raise ValueError("Original raw artifact changed")
        request = read(folder / "request.json")
        expected = ({key: by_source[identity][key] for key in ("id", "passage", "condition")}
                    if arm == "gpt_propositions" else
                    {key: next(p for p in pairs if p["row_id"] == identity)[key]
                     for key in ("row_id", "sentence1", "sentence2", "condition")})
        if (request["item"] != expected or request["arm"] != arm
                or request.get("protocol_sha256") != executed_identity["protocol_sha256"]):
            raise ValueError("Source/request mismatch")
        events = [json.loads(line) for line in (folder / "events.jsonl").read_text().splitlines() if line.strip()]
        payload = validate_completed_capture(events, read(folder / "response.json"))
        if hashlib.sha256(payload.encode()).hexdigest() != row["payload_sha256"]:
            raise ValueError("Response payload changed")
        value = (parse_payload(payload, "propositions", by_source[identity]["passage"])
                 if arm == "gpt_propositions" else {"score": float(payload)})
        if value != row["parsed"]:
            raise ValueError("Retained parsed response differs")
        parsed[arm, identity] = value
        hashes[arm + "/" + identity] = {"payload_sha256": row["payload_sha256"], "raw_artifacts": row["raw_artifacts"]}
    protocol = {
        "experiment": "csts-proposition-similarity-120-20261028-v1",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "model_id": "Qwen/Qwen3-Embedding-8B",
        "revision": "c90816d848505624c2434128dfc61132162a0ee9",
        "max_length": 512, "batch_size": 4, "seed": 42,
        "prompt": "Instruct: Represent the passage for semantic similarity with respect to this condition: {condition}\nQuery: {passage}",
        "pooling": "last_attended_explicit_endoftext_float32_unit_norm",
        "dtype": "bfloat16", "attention": "sdpa", "truncation": "reject",
        "scorer": "unclipped_cosine", "training": "none", "calibration": "none",
        "fallback": "both_raw_when_either_source_not_answered_or_empty",
        "primary_metric": "spearman", "secondary_metric": "uncalibrated_mse_target_0_1",
        "bootstrap": {"unit": "connected_source_group", "draws": 2000, "seed": 42, "interval": "percentile_95"},
        "cohort": "existing_120_validation_pairs_110_groups_not_fresh_blind_holdout",
        "selection": "all_original_pairs_no_semantic_acceptance_filter",
        "cohort_sha256": {name: sha(cohort / name) for name in names},
        "origin_audit_sha256": sha(audit_path),
        "prepare_code_sha256": sha(__file__),
    }
    inputs = {"protocol": protocol, "sources": [], "pairs": []}
    for row in sources:
        record = parsed["gpt_propositions", row["id"]]
        inputs["sources"].append({key: row[key] for key in ("id", "passage", "condition")} |
                                  {"status": record["status"], "evidence_text": canonical_text(record)})
    for row in pairs:
        label = by_label[row["row_id"]]
        left, right = [by_source[s] for s in row["source_ids"]]
        if (left["passage"], right["passage"], left["condition"], right["condition"]) != (
                row["sentence1"], row["sentence2"], row["condition"], row["condition"]):
            raise ValueError("Pair/source identity differs")
        inputs["pairs"].append({"id": row["row_id"], "source_a": left["id"], "source_b": right["id"], "group_id": label["group_id"]})
    write(output / "inputs.json", inputs)
    write(output / "labels.json", labels)
    write(output / "direct.json", {row["row_id"]: parsed["gpt_direct", row["row_id"]]["score"] for row in pairs})
    write(output / "origin.json", {
        "captures": hashes, "parser_amendment": audit,
        "preflight_manifest": manifest, "executed_manifest": executed_manifest,
        "executed_protocol": executed_protocol, "executed_identity": executed_identity,
    })
    receipt = {"status": "prepared_before_embedding_inference", "source_status": dict(Counter(s["status"] for s in inputs["sources"])),
               "pairs": len(pairs), "sources": len(sources), "groups": len({p["group_id"] for p in inputs["pairs"]}),
               "sha256": {n: sha(output / n) for n in ("inputs.json", "labels.json", "direct.json", "origin.json")}}
    write(output / "preparation.json", receipt)
    return receipt


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    for key in ("cohort", "origin", "audit", "output"):
        parser.add_argument("--" + key, required=True)
    args = parser.parse_args()
    print(json.dumps(prepare(args.cohort, args.origin, args.audit, args.output), indent=2))
