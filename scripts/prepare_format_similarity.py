"""Prepare label-free inputs for the trained-model GPT format comparison."""

import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import unicodedata

from csts_pilot.extraction_formats import canonical_text, parse_payload
from csts_pilot.format_similarity import CHECKPOINT_SHA256, MODEL_ID, PROMPT, REVISION, validate_inputs


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    return json.loads(Path(path).read_text())


def write(path, value):
    Path(path).write_text(json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False, allow_nan=False) + "\n")


def unresolved_references(record, passage):
    """Conservatively flag code-style object IDs that the renderer cannot bind."""
    ids = {entity["id"] for entity in record["entities"]}
    types = {entity["type"] for entity in record["entities"]}
    code_ids = {identity for identity in ids if identity not in types and
                re.fullmatch(r"[A-Za-z_][A-Za-z_0-9]*", identity) and
                re.search(r"[0-9_]", identity) and identity not in passage}
    return sorted({identity for fact in record["facts"] for identity in code_ids
                   if re.search(r"(?<!\w)" + re.escape(identity) + r"(?!\w)", fact["value"])})


def verify_capture(row, source, source_by_id, group_by_source, batch_schedules, protocol_hashes):
    """Bind each source to its raw request; independently check matched batch isolation."""
    folder = Path(row["capture_path"])
    if sha(folder / "result.json") != row["result_sha256"]:
        raise ValueError("Captured result changed")
    for name, digest in row["raw_artifacts"].items():
        if Path(name).name != name or sha(folder / name) != digest:
            raise ValueError("Raw capture changed")
    request = read(folder / "request.json")
    if request["arm"] != row["arm"]:
        raise ValueError("Capture arm differs")
    if row.get("request_sha256") and sha(folder / "request.json") != row["request_sha256"]:
        raise ValueError("Capture request identity differs")
    if row.get("response_sha256") and sha(folder / "response.json") != row["response_sha256"]:
        raise ValueError("Capture response identity differs")
    expected = {key: source[key] for key in ("id", "passage", "condition")}
    if "items" not in request:
        if request["item"] != expected:
            raise ValueError("Capture source differs")
        return folder, False
    items = request["items"]
    ids = [item["id"] for item in items]
    if not ids or len(ids) != len(set(ids)) or any(identity not in source_by_id for identity in ids):
        raise ValueError("A batch must contain unique known sources")
    if request["source_ids"] != ids or source["id"] not in ids:
        raise ValueError("Batch/source identity differs")
    for item in items:
        if item != {key: source_by_id[item["id"]][key] for key in ("id", "passage", "condition")}:
            raise ValueError("Batch item contains changed source text or extra fields")
    groups = [group_by_source[identity] for identity in ids]
    conditions = [" ".join(unicodedata.normalize("NFKC", source_by_id[identity]["condition"]).casefold().split()) for identity in ids]
    if len(set(groups)) != len(groups) or len(set(conditions)) != len(conditions):
        raise ValueError("A batch repeats a connected group or condition")
    if request["batch_id"] != row["batch_id"] or request["job_id"] != row["job_id"]:
        raise ValueError("Batch job identity differs")
    schedule = batch_schedules.setdefault(row["arm"], {})
    batch_id = request["batch_id"]
    if batch_id in schedule and schedule[batch_id] != tuple(ids):
        raise ValueError("A batch schedule changed within an arm")
    schedule[batch_id] = tuple(ids)
    digest = request["protocol_sha256"]
    if not isinstance(digest, str) or not re.fullmatch(r"[a-f0-9]{64}", digest):
        raise ValueError("A batch lacks a valid generation protocol identity")
    protocol_hashes.add(digest)
    # The common protocol must exist as retained bytes, rather than a free-standing digest.
    candidates = [parent / "protocol.json" for parent in [folder, *list(folder.parents)[:6]]]
    retained = next((path for path in candidates if path.is_file() and sha(path) == digest), None)
    if retained is None:
        raise ValueError("Retained batch generation protocol does not match its request")
    generation = read(retained)
    if (generation.get("experiment"), generation.get("model"), generation.get("reasoning_effort")) != (
            "csts-gpt-format-batches-20261028-v1", "gpt-6.1-sol", "max"):
        raise ValueError("Unexpected matched batch generation settings")
    return folder, True


def prepare(baseline_path, records_path, output):
    baseline = read(baseline_path)
    records = read(records_path)
    expected_ids = {source["id"] for source in baseline["sources"]}
    if len(expected_ids) != 239 or len(baseline["sources"]) != 239 or len(baseline["pairs"]) != 120:
        raise ValueError("The comparison requires the original 239 sources and 120 pairs")
    source_by_id = {source["id"]: source for source in baseline["sources"]}
    group_by_source = {}
    for pair in baseline["pairs"]:
        for identity in (pair["source_a"], pair["source_b"]):
            if identity in group_by_source and group_by_source[identity] != pair["group_id"]:
                raise ValueError("A source changes connected group across comparisons")
            group_by_source[identity] = pair["group_id"]
    if set(group_by_source) != expected_ids or len(set(group_by_source.values())) != 110:
        raise ValueError("The source/component inventory differs")
    lookup = {(row["arm"], row["id"]): row for row in records}
    matched = {row["arm"] for row in records} == {"gpt_propositions", "gpt_json", "gpt_python"}
    generation_arms = ("gpt_propositions", "gpt_json", "gpt_python") if matched else ("gpt_json", "gpt_python")
    if len(records) != 239 * len(generation_arms) or len(lookup) != len(records) or set(lookup) != {
            (arm, identity) for arm in generation_arms for identity in expected_ids}:
        raise ValueError("Every generation arm must retain all 239 original sources exactly")
    protocol = {
        "experiment": "csts-gpt-format-batched-comparison-20261028-v1" if matched else "csts-gpt-format-comparison-20261028-v1",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "checkpoint_sha256": CHECKPOINT_SHA256, "model_id": MODEL_ID, "revision": REVISION,
        "max_length": 160, "prompt": PROMPT, "eod": "<|endoftext|>",
        "scorer": "incumbent_trained_lora_EOD_cosine", "optimizer_updates": 0,
        "fallback": "original_text_per_unavailable_side_including_failures_and_overflow",
        "local_reference_policy": "code_identifiers_with_digits_or_underscores_absent_from_source_and_not_an_entity_type",
        "sample": "all_original_120_validation_pairs_239_sources_110_groups",
        "base_inputs_sha256": sha(baseline_path), "generation_records_sha256": sha(records_path),
        "baseline_usage": "Source/pair identities only; all proposition evidence is fresh and matched." if matched else "Source/pair identities and retained proposition incumbent.",
        "prepare_code_sha256": sha(__file__),
        "bootstrap": {"draws": 2000, "seed": 42, "unit": "connected_source_group"},
    }
    inputs = {"protocol": protocol, "sources": [], "pairs": baseline["pairs"]}
    provenance = []
    batch_schedules, protocol_hashes = {}, set()
    kinds = set()
    for source in baseline["sources"]:
        value = {key: source[key] for key in ("id", "passage", "condition")}
        value["arms"] = {} if matched else {"propositions": {"status": source["status"], "text": source["evidence_text"], "failure": None}}
        for arm in generation_arms:
            format_name = arm.removeprefix("gpt_")
            row = lookup[arm, source["id"]]
            folder, batched = verify_capture(row, source, source_by_id, group_by_source, batch_schedules, protocol_hashes)
            kinds.add(batched)
            if matched and not batched:
                raise ValueError("Fresh matched evidence must use the shared batch protocol")
            if batched and not matched:
                raise ValueError("Batched generation requires a fresh matched proposition arm")
            failure, refs = None, []
            if row["amended_valid"]:
                response = read(folder / "response.json")
                payload = response["records"][source["id"]]["payload"] if batched else response["payload"]
                if hashlib.sha256(payload.encode()).hexdigest() != row["payload_sha256"]:
                    raise ValueError("Validated payload changed")
                parsed = parse_payload(payload, format_name, source["passage"])
                if parsed != row["parsed"] or canonical_text(parsed) != row["canonical_text"]:
                    raise ValueError("Parsed or rendered response differs")
                refs = unresolved_references(parsed, source["passage"]) if format_name != "propositions" else []
                if refs:
                    failure = "unresolved_entity_reference"
                arm_record = {"status": parsed["status"], "text": canonical_text(parsed), "failure": failure}
            else:
                arm_record = {"status": "failed", "text": "", "failure": row.get("error", "invalid_capture")}
            value["arms"][format_name] = arm_record
            provenance.append({"arm": arm, "id": source["id"], "original_valid": row.get("original_valid", row.get("valid")),
                               "amended_valid": row["amended_valid"], "unresolved_references": refs,
                               "result_sha256": row["result_sha256"], "payload_sha256": row.get("payload_sha256"),
                               "batch_id": row.get("batch_id"), "job_id": row.get("job_id")})
        inputs["sources"].append(value)
    if matched:
        if kinds != {True} or len(protocol_hashes) != 1:
            raise ValueError("The matched trio must share one retained batch generation protocol")
        schedules = [batch_schedules[arm] for arm in generation_arms]
        if any(schedule != schedules[0] for schedule in schedules[1:]):
            raise ValueError("The three formats used different source batch schedules")
        scheduled_ids = [identity for ids in schedules[0].values() for identity in ids]
        if len(scheduled_ids) != 239 or set(scheduled_ids) != expected_ids:
            raise ValueError("The shared batch schedule must cover each original source once")
        protocol["matched_generation"] = {"arms": list(generation_arms), "protocol_sha256": next(iter(protocol_hashes)),
                                           "batch_schedule": {key: list(ids) for key, ids in sorted(schedules[0].items())},
                                           "fresh_proposition_records": 239}
    validate_inputs(inputs)
    output = Path(output)
    output.mkdir(exist_ok=False, parents=True)
    write(output / "inputs.json", inputs)
    write(output / "provenance.json", provenance)
    receipt = {"status": "prepared_before_trained_scoring", "pairs": len(inputs["pairs"]),
               "sources": len(inputs["sources"]), "groups": len({pair["group_id"] for pair in inputs["pairs"]}),
               "inputs_sha256": sha(output / "inputs.json"), "provenance_sha256": sha(output / "provenance.json"),
               "statuses": {arm: dict(Counter(source["arms"][arm]["status"] for source in inputs["sources"]))
                            for arm in ("propositions", "json", "python")},
               "failures": {arm: dict(Counter(source["arms"][arm]["failure"] for source in inputs["sources"] if source["arms"][arm]["failure"]))
                            for arm in ("propositions", "json", "python")}}
    write(output / "preparation.json", receipt)
    return receipt


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    for arg in ("baseline", "records", "output"):
        parser.add_argument("--" + arg, required=True)
    args = parser.parse_args()
    print(json.dumps(prepare(args.baseline, args.records, args.output), indent=2))
