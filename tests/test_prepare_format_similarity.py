"""Bindings and isolation checks for fresh matched batch evidence."""

import copy
import json
from pathlib import Path
import tempfile
import unittest

from csts_pilot.extraction_formats import canonical_text
from scripts.prepare_format_similarity import prepare, sha, verify_capture


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, sort_keys=True) + "\n")


def fixture(root):
    sources, pairs, groups = [], [], {}
    for i in range(120):
        group = "g" + str(i // 2 if i < 20 else i - 10)
        ids = []
        for side in range(2):
            if i == 1 and side == 0:
                identity = "s000"
            else:
                identity = "s" + str(len(sources)).zfill(3)
                sources.append({"id": identity, "passage": "Brown dog " + identity + ".",
                                "condition": "color " + identity,
                                "status": "BAD_OLD_CACHE", "evidence_text": "DO NOT USE OLD PROPOSITIONS"})
            ids.append(identity)
            groups[identity] = group
        pairs.append({"id": "p" + str(i), "source_a": ids[0], "source_b": ids[1], "group_id": group})
    # Real source pairs share a condition. Different source groups have distinct conditions.
    for source in sources:
        source["condition"] = "color " + groups[source["id"]]
    by_id = {s["id"]: s for s in sources}
    baseline = root / "baseline.json"
    write(baseline, {"sources": sources, "pairs": pairs})
    write(root / "protocol.json", {"experiment": "csts-gpt-format-batches-20261028-v1",
                                   "model": "gpt-6.1-sol", "reasoning_effort": "max"})
    buckets, seen = {}, {}
    for source in sources:
        group = groups[source["id"]]
        index = seen.get(group, 0)
        seen[group] = index + 1
        buckets.setdefault(index, []).append(source["id"])
    records = []
    for arm in ("gpt_propositions", "gpt_json", "gpt_python"):
        for number, ids in buckets.items():
            batch_id = "batch-" + str(number)
            job_id = arm + "--" + batch_id
            folder = root / "captures" / job_id
            request = {"items": [{key: by_id[identity][key] for key in ("id", "passage", "condition")} for identity in ids],
                       "arm": arm, "batch_id": batch_id, "job_id": job_id,
                       "source_ids": ids, "protocol_sha256": sha(root / "protocol.json")}
            write(folder / "request.json", request)
            parsed = {}
            payloads = {}
            for identity in ids:
                if arm == "gpt_propositions":
                    value = {"status": "answered", "reason": "", "propositions": [
                        {"text": "The dog is brown.", "source_quote": "Brown dog", "support_status": "explicit", "reason": ""}]}
                    payload = json.dumps(value)
                else:
                    value = {"status": "answered", "reason": "", "entities": [
                        {"id": "dog1", "type": "dog", "source_quote": "dog", "count": 1}], "facts": [
                        {"entity_id": "dog1", "predicate": "color", "value": "brown", "source_quote": "Brown", "support_status": "explicit", "reason": ""}]}
                    payload = json.dumps(value) if arm == "gpt_json" else (
                        'Evidence(status="answered", reason="", entities=[Entity(id="dog1", type="dog", source_quote="dog", count=1)], '
                        'facts=[Fact(entity_id="dog1", predicate="color", value="brown", source_quote="Brown", support_status="explicit", reason="")])')
                parsed[identity] = value
                payloads[identity] = {"payload": payload}
            write(folder / "response.json", {"records": payloads})
            write(folder / "result.json", {"valid": True})
            raw = {name: sha(folder / name) for name in ("request.json", "response.json")}
            for identity in ids:
                import hashlib
                payload = payloads[identity]["payload"]
                records.append({"arm": arm, "id": identity, "job_id": job_id, "batch_id": batch_id,
                                "original_valid": True, "amended_valid": True, "valid": True,
                                "parsed": parsed[identity], "canonical_text": canonical_text(parsed[identity]),
                                "payload_sha256": hashlib.sha256(payload.encode()).hexdigest(),
                                "capture_path": str(folder), "result_sha256": sha(folder / "result.json"),
                                "request_sha256": raw["request.json"], "response_sha256": raw["response.json"],
                                "raw_artifacts": raw})
    records_path = root / "records.json"
    write(records_path, records)
    return baseline, records_path, sources, groups


class PreparationTests(unittest.TestCase):
    def test_matched_trio_uses_fresh_propositions_and_exact_complete_schedule(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            baseline, records, _, _ = fixture(root)
            receipt = prepare(baseline, records, root / "prepared")
            inputs = json.loads((root / "prepared/inputs.json").read_text())
            self.assertEqual(receipt["pairs"], 120)
            self.assertEqual(len(inputs["sources"]), 239)
            self.assertEqual(inputs["protocol"]["matched_generation"]["fresh_proposition_records"], 239)
            self.assertEqual(inputs["protocol"]["experiment"], "csts-gpt-format-batched-comparison-20261028-v1")
            self.assertTrue(all(source["arms"]["propositions"]["text"] == "The dog is brown." for source in inputs["sources"]))
            self.assertTrue(all(source["arms"]["propositions"]["failure"] is None for source in inputs["sources"]))

    def test_batch_connected_group_collision_is_rejected_independently(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            baseline, records_path, sources, groups = fixture(root)
            records = json.loads(records_path.read_text())
            row = copy.deepcopy(records[0])
            capture = Path(row["capture_path"])
            request = json.loads((capture / "request.json").read_text())
            source = next(s for s in sources if s["id"] == row["id"])
            companion = next(s for s in sources if s["id"] != source["id"] and groups[s["id"]] == groups[source["id"]])
            request["items"].append({key: companion[key] for key in ("id", "passage", "condition")})
            request["source_ids"].append(companion["id"])
            write(capture / "request.json", request)
            row["request_sha256"] = row["raw_artifacts"]["request.json"] = sha(capture / "request.json")
            with self.assertRaisesRegex(ValueError, "repeats a connected group or condition"):
                verify_capture(row, source, {s["id"]: s for s in sources}, groups, {}, set())

    def test_changed_source_payload_cannot_hide_behind_updated_raw_file_hash(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            baseline, records_path, _, _ = fixture(root)
            records = json.loads(records_path.read_text())
            row = records[0]
            capture = Path(row["capture_path"])
            response = json.loads((capture / "response.json").read_text())
            response["records"][row["id"]]["payload"] += " "
            write(capture / "response.json", response)
            for other in records:
                if other["capture_path"] == str(capture):
                    other["response_sha256"] = other["raw_artifacts"]["response.json"] = sha(capture / "response.json")
            write(records_path, records)
            with self.assertRaisesRegex(ValueError, "Validated payload changed"):
                prepare(baseline, records_path, root / "prepared")


if __name__ == "__main__":
    unittest.main()
