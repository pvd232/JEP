"""Prepare blinded raw-output review and merge a fourth extraction arm.

    python scripts/instructuie_review.py prepare DIRECTORY --outputs OUTPUTS.jsonl
    python scripts/instructuie_review.py summarize DIRECTORY --review-a A.json --review-b B.json

References and existing reviews are read-only. Only summarize replaces results.json.
"""

import argparse
import hashlib
import json
import os
import random
import tempfile
from collections import Counter
from pathlib import Path

MODEL = "ZWK/InstructUIE"
REVISION = "48f45b25a01df1798f8c1c31751a973adb7e8647"
ARM = "instructuie"
ORIGINAL_ARMS = ("assistant_structured", "archived_qwen_spans", "archived_generated_v1")
ISSUES = ("wrong_entity", "omitted_relevant_values", "unsupported_fact", "inference_issue")
PACKET = "additional_blind_candidates.json"
IDENTITIES = "additional_candidate_identity_map.json"
MANIFEST = "instructuie_review_manifest.json"
SEED = 61038
PROTECTED = (
    "source_inputs.json", "sampling_manifest.json", "reference_a.json", "reference_b.json",
    "review_a.json", "review_b.json", "candidate_identity_map.json", "instructuie_inputs.json",
)


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path, value, replace=False):
    content = (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    if path.exists():
        if path.read_bytes() == content:
            return
        if not replace:
            raise ValueError(f"Preserve existing review preparation: {path.name}")
    with tempfile.NamedTemporaryFile(dir=path.parent, prefix=".review-", delete=False) as stream:
        temporary = Path(stream.name)
        try:
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        except BaseException:
            temporary.unlink(missing_ok=True)
            raise
    temporary.replace(path)


def index(rows, key, label, expected=None):
    if not isinstance(rows, list):
        raise ValueError(f"{label} must be a JSON list")
    result = {}
    for row in rows:
        value = row.get(key) if isinstance(row, dict) else None
        if not isinstance(value, str) or not value or value in result:
            raise ValueError(f"{label} requires unique nonempty {key} values")
        result[value] = row
    if expected is not None and result.keys() != set(expected):
        raise ValueError(f"{label} ID coverage differs: expected {len(expected)}, got {len(result)}")
    return result


def reviews(path, expected):
    result = index(read(path), "candidate_id", path.name, expected)
    for row in result.values():
        if any(type(row.get(key)) is not bool for key in ("faithful", *ISSUES)):
            raise ValueError(f"{path.name} review flags must be JSON booleans")
        if not isinstance(row.get("reason"), str) or not row["reason"].strip():
            raise ValueError(f"{path.name} requires a reason for each judgment")
        if row["faithful"] and any(row[key] for key in ISSUES):
            raise ValueError(f"{path.name} marks a faithful candidate as containing an issue")
    return result


def counts(candidate_ids, reader_a, reader_b):
    candidate_ids = list(candidate_ids)
    return {
        "n": len(candidate_ids),
        "reader_a_faithful": sum(reader_a[key]["faithful"] for key in candidate_ids),
        "reader_b_faithful": sum(reader_b[key]["faithful"] for key in candidate_ids),
        "both_faithful": sum(reader_a[key]["faithful"] and reader_b[key]["faithful"] for key in candidate_ids),
        "reader_disagreements": sum(reader_a[key]["faithful"] != reader_b[key]["faithful"] for key in candidate_ids),
    }


def context(directory):
    sources = index(read(directory / "source_inputs.json"), "id", "Source inputs")
    if len(sources) != 108:
        raise ValueError("This sealed pilot requires exactly 108 source inputs")
    for source in sources.values():
        if any(not isinstance(source.get(key), str) or not source[key].strip() for key in ("passage", "condition")):
            raise ValueError("Source passages and conditions must be nonempty strings")
    sampling = read(directory / "sampling_manifest.json")
    metadata = sampling["metadata"]
    if metadata.keys() != sources.keys() or sampling["total"] != len(sources):
        raise ValueError("Sampling metadata must cover every source exactly")
    cohort_counts = Counter(value["cohort"] for value in metadata.values())
    if dict(cohort_counts) != {"color_diagnostic": sampling["color_inputs"], "evidence_helped_control": sampling["matched_helped_control_inputs"]}:
        raise ValueError("Sampling cohort counts differ from the sealed manifest")
    result = read(directory / "results.json")
    for reader in ("a", "b"):
        path = directory / f"reference_{reader}.json"
        index(read(path), "id", path.name, sources)
        if result["reference_sha256"][reader] != sha256(path):
            raise ValueError(f"Sealed reference {reader} changed")
    identities = read(directory / "candidate_identity_map.json")
    if not isinstance(identities, dict) or any(not isinstance(key, str) or not key for key in identities):
        raise ValueError("Original candidate map must contain nonempty candidate IDs")
    arm_sources = {arm: set() for arm in ORIGINAL_ARMS}
    for value in identities.values():
        arm, source = value["arm"], value["source_id"]
        if arm not in arm_sources or source not in sources or source in arm_sources[arm]:
            raise ValueError("Original map has duplicate or unknown arm/source identities")
        arm_sources[arm].add(source)
    if arm_sources[ORIGINAL_ARMS[0]] != sources.keys() or any(len(arm_sources[arm]) != 30 for arm in ORIGINAL_ARMS[1:]):
        raise ValueError("Original arm coverage must remain 108/30/30")
    matched = set.intersection(*arm_sources.values())
    if len(matched) != 30 or sampling["original_cached_targets_available"] != 30:
        raise ValueError("The original archive-matched cohort must remain exactly 30 sources")
    reader_a, reader_b = (reviews(directory / f"review_{key}.json", identities) for key in ("a", "b"))
    for scope, selected in (("all_available", sources.keys()), ("matched", matched)):
        for arm in ORIGINAL_ARMS:
            keys = [key for key, value in identities.items() if value["arm"] == arm and value["source_id"] in selected]
            if result[scope][arm] != counts(keys, reader_a, reader_b):
                raise ValueError(f"Original {scope} summary differs from its sealed reviews")
    return sources, sampling, result, identities, reader_a, reader_b, matched


def outputs(directory, path, sources):
    records = index([json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()], "id", "InstructUIE outputs", sources)
    for key, record in records.items():
        if any(record.get(field) != sources[key][field] for field in ("passage", "condition")):
            raise ValueError(f"Output source text differs for {key}")
        if not isinstance(record.get("raw_output"), str):
            raise ValueError("Every output must retain its raw text, including empty outputs")
        if record.get("model_id") != MODEL or record.get("revision") != REVISION:
            raise ValueError("Output checkpoint identity differs from pinned InstructUIE")
    manifest_path = path.with_suffix(path.suffix + ".manifest.json")
    manifest = read(manifest_path)
    if any(manifest.get(key) != value for key, value in {"status": "complete", "model_id": MODEL, "revision": REVISION, "items": 108, "outputs_generated": 108, "input_sha256": sha256(directory / "instructuie_inputs.json")}.items()):
        raise ValueError("Generation manifest is incomplete or has different input/checkpoint identity")
    inputs = index(read(directory / "instructuie_inputs.json"), "id", "Generation inputs", sources)
    if any(inputs[key].get(field) != source[field] for key, source in sources.items() for field in ("passage", "condition")):
        raise ValueError("Generation inputs differ from source-only pilot inputs")
    return records, manifest_path


def prepare(directory, output_path):
    sources, _, _, original_map, _, _, _ = context(directory)
    records, generation_manifest = outputs(directory, output_path, sources)
    rng = random.Random(SEED)
    source_ids = sorted(sources)
    rng.shuffle(source_ids)
    packet, mapping = [], {}
    for source_id in source_ids:
        candidate_id = f"candidate_{rng.getrandbits(128):032x}"
        if candidate_id in original_map or candidate_id in mapping:
            raise ValueError("Randomized candidate ID collision")
        source = sources[source_id]
        packet.append({"candidate_id": candidate_id, "source_id": source_id, "passage": source["passage"], "condition": source["condition"], "content": records[source_id]["raw_output"]})
        mapping[candidate_id] = {"source_id": source_id, "arm": ARM}
    write(directory / PACKET, packet)
    write(directory / IDENTITIES, mapping)
    manifest = {
        "schema_version": 1, "source_inputs": 108, "seed": SEED,
        "outputs_path": os.path.relpath(output_path.resolve(), directory.resolve()),
        "outputs_sha256": sha256(output_path),
        "generation_manifest_sha256": sha256(generation_manifest),
        "protected_sha256": {name: sha256(directory / name) for name in PROTECTED},
        "packet_sha256": sha256(directory / PACKET), "identity_map_sha256": sha256(directory / IDENTITIES),
        "review_fields": ["candidate_id", "faithful", *ISSUES, "reason"],
        "review_scope": "Compare raw candidate content with the unchanged source-only reference and its inference criteria; model identity and similarity ratings are withheld.",
    }
    write(directory / MANIFEST, manifest)
    return {"status": "prepared", "candidates": 108, "packet": str(directory / PACKET), "identity_map": str(directory / IDENTITIES)}


def summarize(directory, review_a, review_b):
    sources, sampling, result, identities, original_a, original_b, matched = context(directory)
    manifest = read(directory / MANIFEST)
    if manifest["source_inputs"] != 108 or manifest["seed"] != SEED:
        raise ValueError("Review preparation scope changed")
    for name, expected in manifest["protected_sha256"].items():
        if name not in PROTECTED or sha256(directory / name) != expected:
            raise ValueError(f"Protected review input changed: {name}")
    if set(manifest["protected_sha256"]) != set(PROTECTED):
        raise ValueError("Preparation lacks complete protected input identities")
    for name, key in ((PACKET, "packet_sha256"), (IDENTITIES, "identity_map_sha256")):
        if sha256(directory / name) != manifest[key]:
            raise ValueError(f"Prepared review input changed: {name}")
    output_path = directory / manifest["outputs_path"]
    records, generation_manifest = outputs(directory, output_path, sources)
    if sha256(output_path) != manifest["outputs_sha256"] or sha256(generation_manifest) != manifest["generation_manifest_sha256"]:
        raise ValueError("Generation output or provenance changed after blinding")
    additional = read(directory / IDENTITIES)
    packet = index(read(directory / PACKET), "candidate_id", "Blinded packet", additional)
    additional_sources = []
    for key, value in additional.items():
        source_id = value["source_id"]
        if key in identities or value["arm"] != ARM or source_id not in sources:
            raise ValueError("Additional candidate map contains invalid identities")
        expected = {"candidate_id": key, "source_id": source_id, "passage": sources[source_id]["passage"], "condition": sources[source_id]["condition"], "content": records[source_id]["raw_output"]}
        if packet[key] != expected:
            raise ValueError("Blinded packet differs from source/raw output or contains extra fields")
        additional_sources.append(source_id)
    if len(additional_sources) != 108 or set(additional_sources) != sources.keys():
        raise ValueError("Additional candidates require exactly one candidate per source")
    new_a, new_b = reviews(review_a, additional), reviews(review_b, additional)
    all_identities = {**identities, **additional}
    all_a, all_b = {**original_a, **new_a}, {**original_b, **new_b}
    arms = (*ORIGINAL_ARMS, ARM)

    def summaries(selected):
        return {arm: counts([key for key, value in all_identities.items() if value["arm"] == arm and value["source_id"] in selected], all_a, all_b) for arm in arms}

    result["all_available"] = summaries(sources)
    result["matched"] = summaries(matched)
    result["by_cohort"] = {}
    for cohort in sorted({value["cohort"] for value in sampling["metadata"].values()}):
        selected = {key for key, value in sampling["metadata"].items() if value["cohort"] == cohort}
        result["by_cohort"][cohort] = {"all_available": summaries(selected), "matched": summaries(selected & matched)}
    result["instructuie_by_cohort"] = {cohort: value["all_available"][ARM] for cohort, value in result["by_cohort"].items()}
    result["instructuie_issue_counts"] = {label: {issue: sum(values[key][issue] for key in additional) for issue in ISSUES} for label, values in (("reader_a", new_a), ("reader_b", new_b))}
    result["instructuie_review"] = {"model_id": MODEL, "revision": REVISION, "outputs_sha256": manifest["outputs_sha256"], "preparation_sha256": sha256(directory / MANIFEST), "review_a_sha256": sha256(review_a), "review_b_sha256": sha256(review_b), "reference_sha256": result["reference_sha256"], "matched_source_ids": sorted(matched)}
    result.update(status="structured_and_instructuie_review_complete", instructuie_predictions=108)
    write(directory / "results.json", result, replace=True)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    preparation = commands.add_parser("prepare")
    preparation.add_argument("directory", type=Path)
    preparation.add_argument("--outputs", type=Path, required=True)
    summary = commands.add_parser("summarize")
    summary.add_argument("directory", type=Path)
    summary.add_argument("--review-a", type=Path, required=True)
    summary.add_argument("--review-b", type=Path, required=True)
    args = parser.parse_args()
    if args.command == "prepare":
        result = prepare(args.directory, args.outputs)
    else:
        result = summarize(args.directory, args.review_a, args.review_b)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
