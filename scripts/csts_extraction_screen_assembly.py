"""Read-only multi-origin evidence publication, preserving every original capture.

prepare --spec origins.json --output ANALYSIS
summarize --output ANALYSIS --reviews REVIEW_A.json REVIEW_B.json

Spec: {"arms": {"gpt_propositions": {"run": "...", "code": "...",
"protocol_sha256": "..."}, "knowcoder": {...}, "gollie": {...}},
"expected_sources": 239, "review_kind": "model_assisted", "amendment": {...}}
Each origin is verified in an isolated Python subprocess using its own frozen code.
This helper never invokes inference or modifies any origin artifact.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import random
import subprocess
import sys
import tempfile

FIELDS = ("faithful", "complete", "scope_correct", "binding_correct",
          "multiplicity_correct", "abstention_correct", "inference_correct")
ARM_NAMES = ("gpt_propositions", "knowcoder", "gollie")
SOURCE_FILES = ("sources.json", "pairs.json", "labels.json", "references.json")

# Trusted project source, selected by the operator and checked against protocol.json.
CHILD = r"""
import hashlib,json,sys
from pathlib import Path
spec=json.load(sys.stdin)
sys.path.insert(0,spec["code"])
from csts_pilot import extraction_comparison as m
run=Path(spec["run"])
config=m.verify_run(run)
protocol_bytes=(run/"protocol.json").read_bytes()
if hashlib.sha256(protocol_bytes).hexdigest()!=spec["protocol_sha256"]:
    raise ValueError("Origin protocol differs from declared identity")
if hashlib.sha256((run/"references.json").read_bytes()).hexdigest()!=m.read(run/"references-seal.json")["sha256"]:
    raise ValueError("Origin references differ from pre-generation seal")
results=m.load_results(run,[spec["arm"]])[spec["arm"]]
sources=m.read(run/"sources.json")
print(json.dumps({
 "protocol":m.read(run/"protocol.json"),"manifest":m.read(run/"manifest.json"),
 "sources":sources,"pairs":m.read(run/"pairs.json"),"labels":m.read(run/"labels.json"),
 "references":m.read(run/"references.json"),"results":results,
 "artifacts":{name:hashlib.sha256((run/name).read_bytes()).hexdigest()
              for name in ("sources.json","pairs.json","labels.json","references.json",
                           "protocol.json","manifest.json","references-seal.json")},
 "request_sha256":{key:hashlib.sha256((run/"captures"/spec["arm"]/key/"request.json").read_bytes()).hexdigest() for key in results},
 "result_sha256":{key:hashlib.sha256((run/"captures"/spec["arm"]/key/"result.json").read_bytes()).hexdigest() for key in results},
 "prompt_sha256":{arm:{item["id"]:hashlib.sha256(m.prompt_for(
       {key:item[key] for key in ("id","passage","condition")},arm).encode()).hexdigest()
       for item in sources} for arm in ("gpt_propositions","knowcoder","gollie")}
},ensure_ascii=False))
"""


def encoded(value):
    """Encode deterministic publication bytes."""
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2)+"\n").encode()


def sha(data):
    """Identify exact bytes."""
    return hashlib.sha256(data).hexdigest()


def read(path):
    """Read one JSON artifact."""
    return json.loads(Path(path).read_text(encoding="utf-8"))


def publish(path, value):
    """Atomically create an immutable artifact; allow identical recovery writes."""
    path = Path(path)
    data = encoded(value)
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        if path.read_bytes() != data:
            raise ValueError("Existing publication differs: "+str(path))
        return
    handle, temporary = tempfile.mkstemp(prefix=".publication-", dir=path.parent)
    try:
        with os.fdopen(handle, "wb") as output:
            output.write(data)
            output.flush()
            os.fsync(output.fileno())
        try:
            os.link(temporary, path)
        except FileExistsError:
            if path.read_bytes() != data:
                raise ValueError("Concurrent publication differs: "+str(path))
    finally:
        Path(temporary).unlink(missing_ok=True)


def validate_origins(spec):
    """Verify complete origin captures, shared data, unchanged prompts and settings."""
    if set(spec["arms"]) != set(ARM_NAMES):
        raise ValueError("Declare exactly the three reviewed extraction arms")
    if type(spec.get("expected_sources", 239)) is not int:
        raise ValueError("Expected source count must be an integer")
    data = {}
    for arm in ARM_NAMES:
        origin = spec["arms"][arm]
        if set(origin) != {"run", "code", "protocol_sha256"}:
            raise ValueError("Origin requires exact run/code/protocol_sha256 fields")
        if not all(isinstance(origin[key], str) and origin[key] for key in origin):
            raise ValueError("Origin fields require nonempty strings")
        request = {**origin, "arm": arm}
        process = subprocess.run([sys.executable, "-B", "-I", "-c", CHILD],
                                 input=json.dumps(request), text=True,
                                 capture_output=True, timeout=120)
        if process.returncode:
            # These are trusted offline validators; their traceback identifies the failed invariant.
            raise RuntimeError("Origin verification failed for "+arm+":\n"+process.stderr)
        data[arm] = json.loads(process.stdout)
    base = data["gpt_propositions"]
    amendment = spec.get("amendment")
    allowed_prompt_changes = set()
    if amendment is not None:
        if not isinstance(amendment, dict) or not isinstance(amendment.get("reason"), str) or not amendment["reason"].strip():
            raise ValueError("Amendment requires an explicit reason")
        if amendment.get("parent_protocol_sha256") != spec["arms"]["gpt_propositions"]["protocol_sha256"]:
            raise ValueError("Amendment parent must identify the original frozen protocol")
        allowed_prompt_changes = set(amendment.get("allowed_prompt_change_arms", []))
        if allowed_prompt_changes - {"knowcoder", "gollie"}:
            raise ValueError("Only declared native-system prompts may be amended")
    for arm, observed in data.items():
        if len(observed["sources"]) != spec.get("expected_sources", 239):
            raise ValueError("Unexpected source count in "+arm)
        if len({item["id"] for item in observed["sources"]}) != len(observed["sources"]):
            raise ValueError("Duplicate source identities")
        if observed["protocol"]["config"] != base["protocol"]["config"]:
            raise ValueError("Origin scientific settings differ")
        for name in ("direct_rubric", "transport", "format_prompt_examples"):
            if observed["protocol"][name] != base["protocol"][name]:
                raise ValueError("Origin frozen instructions differ: "+name)
        changed_prompts = {name for name in ARM_NAMES
                           if observed["prompt_sha256"][name] != base["prompt_sha256"][name]}
        if changed_prompts - allowed_prompt_changes:
            raise ValueError("Source-specific prompts differ without a declared native amendment")
        for name in SOURCE_FILES:
            if observed["artifacts"][name] != base["artifacts"][name]:
                raise ValueError("Origin source/reference bytes differ: "+name)
        changed = {name for name in observed["protocol"]["code"]
                   if observed["protocol"]["code"][name] != base["protocol"]["code"].get(name)}
        if changed - {"extraction_native.py"}:
            raise ValueError("Unreviewed code changes across origin implementations")
        if changed and not spec.get("amendment"):
            raise ValueError("Changed native implementation requires an explicit amendment receipt")
    origins = {}
    for arm, observed in data.items():
        origins[arm] = {
            **spec["arms"][arm], "artifacts": observed["artifacts"],
            "code_sha256": observed["protocol"]["code"],
            "request_sha256": observed["request_sha256"],
            "result_sha256": observed["result_sha256"],
            "prompt_sha256": observed["prompt_sha256"][arm],
            "prompt_changed_from_parent": observed["prompt_sha256"][arm] != base["prompt_sha256"][arm],
        }
    required_reviewers = spec.get("required_reviewers", 2)
    if type(required_reviewers) is not int or required_reviewers < 1:
        raise ValueError("Required reviewer count must be a positive integer")
    manifest = {"arms": origins, "expected_sources": len(base["sources"]),
                "required_reviewers": required_reviewers,
                "review_kind": spec.get("review_kind", "model_assisted"),
                "amendment": spec.get("amendment"), "all_origin_captures_unchanged": True,
                "absent_response_review_transport": "An absent payload (null) is displayed as an empty string; structural validity remains false and the origin result is unchanged."}
    return data, manifest


def prepare(spec_path, output):
    """Publish a blinded three-system packet with a seal as the final commit record."""
    spec = read(spec_path)
    data, manifest = validate_origins(spec)
    output = Path(output)
    base = data["gpt_propositions"]
    sources = {item["id"]: item for item in base["sources"]}
    references = {item["id"]: item["expected_answer"] for item in base["references"]}
    entries = [(arm, identity, value) for arm in ARM_NAMES
               for identity, value in sorted(data[arm]["results"].items())]
    random.Random(base["protocol"]["config"]["review_seed"]).shuffle(entries)
    packet, mapping, template = [], [], []
    for index, (arm, identity, result) in enumerate(entries):
        candidate = f"candidate_{index:05d}"
        source = sources[identity]
        raw_output = result["payload"]
        if raw_output is None:
            if result["valid"]:
                raise ValueError("A valid result cannot have an absent response")
            raw_output = ""
        if not isinstance(raw_output, str):
            raise ValueError("A review payload must be text or an absent invalid response")
        packet.append({"candidate_id": candidate, "passage": source["passage"],
                       "condition": source["condition"], "expected_answer": references[identity],
                       "raw_output": raw_output, "structurally_valid": result["valid"]})
        mapping.append({"candidate_id": candidate, "arm": arm, "id": identity,
                        "group_id": source["group_id"]})
        template.append({"candidate_id": candidate, "reviewer_id": "",
                         **{field: None for field in FIELDS}, "rationale": ""})
    counts = {"semantic_review_completed": False, "sources_per_arm": len(sources),
              "candidates": len(packet), "arms": {
                  arm: {"expected": len(sources),
                        "valid": sum(item["valid"] for item in data[arm]["results"].values()),
                        "failed": sum(not item["valid"] for item in data[arm]["results"].values())}
                  for arm in ARM_NAMES}}
    artifacts = {
        "assembly-spec.json": spec, "origin-manifest.json": manifest,
        "references.json": base["references"], "review-packet.json": packet,
        "review-map.json": mapping, "review-template.json": template,
        "operational-counts.json": counts,
    }
    for name, value in artifacts.items():
        publish(output/name, value)
    seal = {"arms": list(ARM_NAMES),
            "artifacts": {name: sha((output/name).read_bytes()) for name in artifacts}}
    publish(output/"review-seal.json", seal)
    return {**counts, "review_seal_sha256": sha((output/"review-seal.json").read_bytes())}


def interval(groups, seed, iterations=2000):
    """Bootstrap complete source components, retaining paired arm differences."""
    values = list(groups.values())
    if len(values) < 2:
        return None
    generator = random.Random(seed)
    samples = []
    for _ in range(iterations):
        draw = [value for group in generator.choices(values, k=len(values)) for value in group]
        samples.append(sum(draw)/len(draw))
    samples.sort()
    return [samples[int(.025*iterations)], samples[min(iterations-1, int(.975*iterations))]]


def score_review(values, mapping, packet_by_id, seed):
    """Compute fixed-denominator acceptance and paired differences for one review."""
    expected = set(packet_by_id)
    if not isinstance(values, list) or len(values) != len(expected):
        raise ValueError("Review must contain every candidate exactly once")
    if {item["candidate_id"] for item in values} != expected:
        raise ValueError("Review IDs differ or are duplicated")
    by_id = {}
    for item in values:
        if not isinstance(item.get("reviewer_id"), str) or not item["reviewer_id"].strip():
            raise ValueError("Missing reviewer identity")
        if not isinstance(item.get("rationale"), str) or not item["rationale"].strip():
            raise ValueError("Missing review rationale")
        if any(type(item.get(field)) is not bool for field in FIELDS):
            raise ValueError("Every criterion requires an explicit boolean judgment")
        by_id[item["candidate_id"]] = item
    accepted, per_arm = {}, {}
    for link in mapping:
        candidate = link["candidate_id"]
        valid = packet_by_id[candidate]["structurally_valid"]
        accepted[(link["arm"], link["id"])] = valid and all(by_id[candidate][field] for field in FIELDS)
    for arm in ARM_NAMES:
        links = [item for item in mapping if item["arm"] == arm]
        per_arm[arm] = {
            "n": len(links),
            "all_criteria_accepted": sum(accepted[(arm, item["id"])] for item in links),
            "criteria": {field: sum(packet_by_id[item["candidate_id"]]["structurally_valid"]
                                   and by_id[item["candidate_id"]][field] for item in links)
                         for field in FIELDS}}
    comparisons = {}
    for arm in ("knowcoder", "gollie"):
        groups = {}
        for link in mapping:
            if link["arm"] == arm:
                identity = link["id"]
                groups.setdefault(link["group_id"], []).append(
                    int(accepted[(arm, identity)])-int(accepted[("gpt_propositions", identity)]))
        differences = [value for group in groups.values() for value in group]
        comparisons[arm] = {"mean_difference": sum(differences)/len(differences),
                            "paired_component_95_ci": interval(groups, seed),
                            "components": len(groups)}
    return {"arms": per_arm, "paired_vs_propositions": comparisons}, by_id


def summarize(output, review_paths):
    """Verify the publication and its origins before producing immutable review reports."""
    output = Path(output)
    seal = read(output/"review-seal.json")
    for name, expected in seal["artifacts"].items():
        if sha((output/name).read_bytes()) != expected:
            raise ValueError("Sealed publication changed: "+name)
    data, manifest = validate_origins(read(output/"assembly-spec.json"))
    if manifest != read(output/"origin-manifest.json"):
        raise ValueError("Origin evidence changed after packet publication")
    packet = read(output/"review-packet.json")
    mapping = read(output/"review-map.json")
    expected = {item["candidate_id"] for item in packet}
    if len(mapping) != len(packet) or {item["candidate_id"] for item in mapping} != expected:
        raise ValueError("Mapping coverage differs")
    sources = {item["id"]: item for item in data["gpt_propositions"]["sources"]}
    for arm in ARM_NAMES:
        links = [item for item in mapping if item["arm"] == arm]
        if len(links) != len(sources) or {item["id"] for item in links} != set(sources):
            raise ValueError("Mapping source coverage differs")
        if any(item["group_id"] != sources[item["id"]]["group_id"] for item in links):
            raise ValueError("Mapping source component differs")
    packet_by_id = {item["candidate_id"]: item for item in packet}
    seed = data["gpt_propositions"]["protocol"]["config"]["review_seed"]
    if len(review_paths) < manifest["required_reviewers"]:
        raise ValueError("The panel requires more separately retained reviews")
    if len({Path(path).resolve() for path in review_paths}) != len(review_paths):
        raise ValueError("Duplicate review input paths")
    reports, reviews, review_hashes, reviewer_ids = [], [], set(), set()
    for path in review_paths:
        identity = sha(Path(path).read_bytes())
        if identity in review_hashes:
            raise ValueError("Duplicate review input contents")
        values = read(path)
        report, by_id = score_review(values, mapping, packet_by_id, seed)
        identities = {item["reviewer_id"] for item in values}
        if identities & reviewer_ids:
            raise ValueError("Review inputs share reviewer identities")
        reviewer_ids.update(identities)
        review_hashes.add(identity)
        report["review_sha256"] = identity
        report["reviewer_ids"] = sorted(identities)
        report["review_kind"] = manifest["review_kind"]
        reports.append(report)
        reviews.append(by_id)
    if not reviews:
        raise ValueError("Supply at least one completed review")
    disagreements = []
    for candidate in sorted(expected):
        if any(any(review[candidate][field] != reviews[0][candidate][field] for field in FIELDS)
               for review in reviews[1:]):
            disagreements.append(candidate)
    both = []
    for candidate in sorted(expected):
        both.append({"candidate_id": candidate, "reviewer_id": "reviewer_conjunction",
                     "rationale": "Conjunction of separately retained review judgments.",
                     **{field: all(review[candidate][field] for review in reviews) for field in FIELDS}})
    conjunction, _ = score_review(both, mapping, packet_by_id, seed)
    result = {"review_kind": manifest["review_kind"],
              "review_seal_sha256": sha((output/"review-seal.json").read_bytes()),
              "individual_reviews": reports, "all_reviewers_accepted": conjunction,
              "disagreement_candidates": disagreements,
              "disagreements_require_adjudication": bool(disagreements)}
    filename = "review-summary-"+sha(encoded(result))[:16]+".json"
    publish(output/filename, result)
    return {**result, "report_path": str(output/filename)}


def main():
    """Read origins, publish packets, or score completed reviews without inference."""
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    command = commands.add_parser("prepare")
    command.add_argument("--spec", dest="spec_path", type=Path, required=True)
    command.add_argument("--output", type=Path, required=True)
    command = commands.add_parser("summarize")
    command.add_argument("--output", type=Path, required=True)
    command.add_argument("--reviews", dest="review_paths", nargs="+", type=Path, required=True)
    args = vars(parser.parse_args())
    action = args.pop("command")
    print(json.dumps({"prepare": prepare, "summarize": summarize}[action](**args), indent=2))


if __name__ == "__main__":
    main()

