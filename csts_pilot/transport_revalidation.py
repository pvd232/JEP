"""Derive a parser amendment from retained captures without changing the run.

No network requests or model calls occur. Startup reconnection notices are
accepted only when one completed, tool-free turn has an agreeing final response.
Original validity decisions and the sealed review panel remain unchanged.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import re
import subprocess
import sys
import tempfile

WARNING = re.compile(
    r"Reconnecting\.\.\. [1-5]/5 \((?:request timed out|"
    r"stream disconnected before completion: invalid peer certificate: UnknownIssuer)\)"
)


def _object(pairs):
    """Reject repeated object keys before JSON decoding discards them."""
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("Duplicate JSON key")
        result[key] = value
    return result


def _decode(text):
    """Parse JSON without duplicate keys or nonfinite numeric constants."""
    def invalid(value):
        raise ValueError("Nonfinite JSON constant: " + value)
    return json.loads(text, object_pairs_hook=_object, parse_constant=invalid)


def _envelope(response):
    """Require exactly the common string payload envelope."""
    if not isinstance(response, dict) or set(response) != {"payload"} or not isinstance(response["payload"], str):
        raise ValueError("Invalid common output envelope")
    return response["payload"]


def validate_completed_capture(events, response):
    """Accept completed turns while narrowly recognizing two transport notices.

Errors outside the exact allowlist, failed turns, tool events, multiple final
answers, incomplete turns and disagreement with response.json remain failures.
"""
    payload = _envelope(response)
    if sum(isinstance(event, dict) and event.get("type") == "thread.started" for event in events) != 1:
        raise ValueError("Expected exactly one original thread")
    if sum(isinstance(event, dict) and event.get("type") == "turn.started" for event in events) != 1:
        raise ValueError("Expected exactly one original turn")
    completed, answers = 0, []
    for index, event in enumerate(events):
        if not isinstance(event, dict):
            raise ValueError("Malformed Codex event")
        kind = event.get("type")
        if kind not in {"thread.started", "turn.started", "item.started", "item.updated", "item.completed", "error", "turn.failed", "turn.completed"}:
            raise ValueError("Unknown Codex event type")
        if kind == "turn.failed":
            raise ValueError("Codex inference failed")
        if kind == "error":
            if set(event) != {"type", "message"} or not isinstance(event["message"], str) or not WARNING.fullmatch(event["message"]):
                raise ValueError("Codex inference failed: unrecognized error")
        if kind == "turn.completed":
            completed += 1
            if index != len(events) - 1:
                raise ValueError("Completed turn must be the final event")
        item = event.get("item", {})
        if not isinstance(item, dict) or item.get("type") not in (None, "agent_message", "reasoning"):
            raise ValueError("Closed-book violation")
        if kind == "item.completed" and item.get("type") == "agent_message":
            if not isinstance(item.get("text"), str):
                raise ValueError("Missing final agent response text")
            answers.append(_decode(item["text"]))
    if completed != 1:
        raise ValueError("Expected exactly one completed inference turn")
    if len(answers) != 1 or answers[0] != response:
        raise ValueError("Final agent response and response envelope disagree")
    return payload


def _sha(data):
    return hashlib.sha256(data).hexdigest()


def _read(path):
    return _decode(Path(path).read_text())


def _bytes(value):
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode()


def _score(payload):
    value = _decode(payload)
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or not 1 <= value <= 5:
        raise ValueError("Direct score must be a finite 1-5 number")
    return value


def _ranks(values):
    order = sorted(range(len(values)), key=values.__getitem__)
    ranks = [0.0] * len(values)
    start = 0
    while start < len(order):
        stop = start + 1
        while stop < len(order) and values[order[stop]] == values[order[start]]:
            stop += 1
        for index in order[start:stop]:
            ranks[index] = (start + stop - 1) / 2
        start = stop
    return ranks


def _correlation(left, right):
    a, b = sum(left) / len(left), sum(right) / len(right)
    numerator = sum((x-a)*(y-b) for x, y in zip(left, right))
    variance = sum((x-a)**2 for x in left) * sum((y-b)**2 for y in right)
    return numerator / math.sqrt(variance) if variance else None


def _verify_frozen_origin(run, frozen_code):
    """Use the frozen implementation to verify its protocol and every request.

    The isolated subprocess imports only the archived implementation and performs
    its read-only verification path. Bytecode writes and external Python paths
    are disabled. This reconstructs exact original prompts with their owner.
    """
    source = (
        "import sys; sys.path.insert(0, sys.argv[1]); "
        "from csts_pilot.extraction_comparison import verify_run, load_results; "
        "verify_run(sys.argv[2]); "
        "load_results(sys.argv[2], ['gpt_direct', 'gpt_propositions'])"
    )
    checked = subprocess.run(
        [sys.executable, "-I", "-B", "-c", source, str(frozen_code.resolve()), str(run.resolve())],
        cwd=frozen_code, text=True, capture_output=True, timeout=60, check=False,
    )
    if checked.returncode:
        raise ValueError("Frozen origin verifier rejected the run: " + checked.stderr[-2000:])


def derive(run, frozen_code, output):
    """Write a fresh derived audit; reject any changed original proof or label."""
    from .extraction_formats import parse_payload
    run, frozen_code, output = map(Path, (run, frozen_code, output))
    manifest = _read(run / "manifest.json")
    for name, expected in manifest["artifacts"].items():
        if _sha((run / name).read_bytes()) != expected:
            raise ValueError("Frozen run artifact changed: " + name)
    protocol = _read(run / "protocol.json")
    for name, expected in protocol["code"].items():
        if _sha((frozen_code / "csts_pilot" / name).read_bytes()) != expected:
            raise ValueError("Frozen implementation changed: " + name)
    _verify_frozen_origin(run, frozen_code)
    if _sha(Path(__file__).with_name("extraction_formats.py").read_bytes()) != protocol["code"]["extraction_formats.py"]:
        raise ValueError("Proposition validator differs from frozen format contract")
    pairs = _read(run / "pairs.json")
    sources = _read(run / "sources.json")
    labels = _read(run / "labels.json")
    records, scores, counts = [], {}, {}
    for arm, values, fields, identity_key in (
        ("gpt_direct", pairs, ("row_id", "sentence1", "sentence2", "condition"), "row_id"),
        ("gpt_propositions", sources, ("id", "passage", "condition"), "id"),
    ):
        expected = {item[identity_key] for item in values}
        paths = list((run / "captures" / arm).glob("*/result.json"))
        if len(expected) != len(values) or {path.parent.name for path in paths} != expected:
            raise ValueError("Exact capture coverage required: " + arm)
        original_valid, amended_valid = 0, 0
        by_id = {item[identity_key]: item for item in values}
        for path in sorted(paths):
            identity, folder = path.parent.name, path.parent
            original = _read(path)
            if original["id"] != identity or original["arm"] != arm or type(original["valid"]) is not bool:
                raise ValueError("Original result identity differs")
            actual = {p.name: _sha(p.read_bytes()) for p in folder.iterdir()
                      if p.is_file() and p.name != "result.json"}
            if actual != original["raw_artifacts"]:
                raise ValueError("Original raw capture changed")
            request = _read(folder / "request.json")
            item = {key: by_id[identity][key] for key in fields}
            if request["item"] != item or request["arm"] != arm or request["protocol_sha256"] != manifest["artifacts"]["protocol.json"]:
                raise ValueError("Original request identity differs")
            original_valid += original["valid"]
            audit = {"arm": arm, "id": identity, "original_valid": original["valid"],
                     "original_result_sha256": _sha(path.read_bytes()), "raw_artifacts": actual,
                     "amended_valid": False}
            events = [_decode(line) for line in (folder / "events.jsonl").read_text().splitlines() if line.strip()]
            try:
                if sum(event.get("type") == "thread.started" for event in events) != 1 or sum(event.get("type") == "turn.started" for event in events) != 1:
                    raise ValueError("Expected one original thread and turn")
                payload = validate_completed_capture(events, _read(folder / "response.json"))
                parsed = {"score": _score(payload)} if arm == "gpt_direct" else parse_payload(payload, "propositions", item["passage"])
                warnings = [event["message"] for event in events if event.get("type") == "error"]
                if original["valid"]:
                    if original["payload"] != payload or original["parsed"] != parsed:
                        raise ValueError("Original accepted payload differs from raw capture")
                elif original.get("error") != "Codex inference failed" or not warnings:
                    raise ValueError("Original failure is outside the parser amendment")
                audit.update(amended_valid=True, warnings=warnings,
                             payload_sha256=_sha(payload.encode()), parsed=parsed)
                amended_valid += 1
                if arm == "gpt_direct":
                    scores[identity] = parsed["score"]
            except (ValueError, KeyError, TypeError) as error:
                audit["rejection_reason"] = str(error)
            records.append(audit)
        counts[arm] = {"expected": len(values), "original_valid": original_valid,
                       "amended_valid": amended_valid}
    label_ids = [row["row_id"] for row in labels]
    if len(set(label_ids)) != len(labels) or set(label_ids) != {row["row_id"] for row in pairs}:
        raise ValueError("Labels must match every original pair exactly")
    metrics = {"status": "parser_amendment", "original_first_pass": counts,
               "new_model_calls": 0, "sealed_review_panel_changed": False,
               "proposition_amendment_scope": "sensitivity_only"}
    if len(scores) == len(labels):
        prediction = [scores[row["row_id"]] for row in labels]
        target = [row["rating"] for row in labels]
        for row in labels:
            _score(json.dumps(row["rating"]))
            if not math.isfinite(row["target"]) or abs(row["target"] - (row["rating"]-1)/4) > 1e-12:
                raise ValueError("Original target scale differs")
        mse = sum((x-y)**2 for x, y in zip(prediction, target)) / len(labels)
        metrics["direct_similarity"] = {"n": len(labels), "spearman": _correlation(_ranks(prediction), _ranks(target)),
                                         "mse_1_5": mse, "mse_0_1": mse / 16}
    else:
        metrics["direct_similarity"] = {"status": "incomplete_no_complete_case_score"}
    audit = {"status": "parser_amendment", "original_manifest_sha256": _sha((run / "manifest.json").read_bytes()),
             "original_protocol_sha256": manifest["artifacts"]["protocol.json"],
             "frozen_origin_verified": True,
             "parser_sha256": _sha(Path(__file__).read_bytes()), "records": records}
    if output.exists():
        raise ValueError("Derived output must be a fresh directory")
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=output.parent, prefix=".parser-amendment-") as temporary:
        stage = Path(temporary) / "audit"
        stage.mkdir()
        (stage / "audit.json").write_bytes(_bytes(audit))
        (stage / "metrics.json").write_bytes(_bytes(metrics))
        stage.rename(output)
    return metrics


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", type=Path, required=True)
    parser.add_argument("--frozen-code", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    print(json.dumps(derive(**vars(parser.parse_args())), indent=2))


if __name__ == "__main__":
    main()
