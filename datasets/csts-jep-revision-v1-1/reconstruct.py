"""Reconstruct the JEP C-STS revision from the exact upstream CSVs (Python 3.9+)."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path

from source_partition import HASHES, REVISION, canonical, digest, partition


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def encoded(value):
    return (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def require(condition, message):
    if not condition:
        raise ValueError(message)


def reconstruct(source, package):
    manifest = read(package / "manifest.json")
    require(manifest["source"]["revision"] == REVISION, "Source revision mismatch")
    for name, expected in manifest["package_sha256"].items():
        require(hashlib.sha256((package / name).read_bytes()).hexdigest() == expected,
                "Package hash mismatch: " + name)
    raw = {}
    for split, expected in HASHES.items():
        path = source / ("csts_" + split + "_reannotated.csv")
        require(hashlib.sha256(path.read_bytes()).hexdigest() == expected,
                "Source hash mismatch: " + split)
        with path.open(encoding="utf-8", newline="") as handle:
            raw[split] = list(csv.DictReader(handle))
    prepared, partition_manifest = partition(raw["train"], raw["validation"])
    require(partition_manifest["overlapping_training_rows_removed"] == 2532,
            "Original partition changed")
    source_rows = {"training": prepared["train"], "validation": prepared["dev"], "test": []}
    for index, row in enumerate(raw["validation"]):
        source_rows["test"].append({
            "row_id": "evaluation_" + str(index),
            "sentence1": row["sentence1"], "sentence2": row["sentence2"],
            "condition": row["condition"], "rating": float(row["label"]),
            "pair_id": digest(json.dumps(sorted((canonical(row["sentence1"]),
                                                  canonical(row["sentence2"]))))),
        })
    result = {}
    filenames = {"training": "training.base.labels.json", "validation": "validation.labels.json",
                 "test": "test.base.labels.json"}
    changes = read(package / "changes.json")["changes"]
    overrides = {change["row_id"]: change for change in changes}
    require(len(overrides) == len(changes), "Duplicate revision changes")
    applied = set()
    for split, rows in source_rows.items():
        records = read(package / filenames[split])["labels"]
        labels = {row["row_id"]: dict(row) for row in records}
        require(len(labels) == len(records) == len(rows), split + ": duplicate/missing IDs")
        require(set(labels) == {row["row_id"] for row in rows}, split + ": ID coverage")
        for row_id, label in labels.items():
            if row_id not in overrides:
                continue
            require(split != "validation", "Validation V4.2 must stay unchanged")
            change = overrides[row_id]
            require(change["project_split"] == split, row_id + ": change split")
            for key in ("status", "rating", "usable_for_split"):
                require(label[key] == change["before"][key], row_id + ": change baseline")
            label.update(change["after"])
            applied.add(row_id)
        result[split] = []
        for row in rows:
            label = labels[row["row_id"]]
            require(float(label["original_rating"]) == row["rating"], row["row_id"] + ": source rating")
            usable = label.get("usable_for_split", label["rating"] is not None)
            if not usable:
                continue
            require(label["rating"] is not None and 1 <= float(label["rating"]) <= 5,
                    row["row_id"] + ": invalid usable rating")
            require(label["pair_id"] == row["pair_id"], row["row_id"] + ": pair ID")
            rating = float(label["rating"])
            result[split].append({
                "row_id": row["row_id"], "sentence1": row["sentence1"],
                "sentence2": row["sentence2"], "condition": row["condition"],
                "rating": rating, "target": (rating - 1) / 4,
                "pair_id": row["pair_id"], "group_id": label["group_id"],
            })
        require(len(result[split]) == manifest["counts"][split]["usable"], split + ": count")
    require(applied == set(overrides), "Unapplied revision changes")
    captions = {split: {canonical(row[key]) for row in rows
                       for key in ("sentence1", "sentence2")} for split, rows in result.items()}
    for left, right in (("training", "validation"), ("training", "test"), ("validation", "test")):
        require(not captions[left] & captions[right], left + "/" + right + ": caption overlap")
    for split in ("training", "validation"):
        original = {canonical(row[key]) for row in source_rows[split]
                    for key in ("sentence1", "sentence2")}
        require(not original & captions["test"], "Test overlaps original " + split)
    for split, rows in result.items():
        require(hashlib.sha256(encoded(rows)).hexdigest() == manifest["export_sha256"][split],
                split + ": export hash")
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    package = Path(__file__).resolve().parent
    rows = reconstruct(args.source, package)
    names = {"training": "train.json", "validation": "validation.json", "test": "test.json"}
    args.output.mkdir(parents=True, exist_ok=True)
    receipt = {"revision": read(package / "manifest.json")["revision"], "passed": True, "partitions": {}}
    for split, data in rows.items():
        content = encoded(data)
        (args.output / names[split]).write_bytes(content)
        receipt["partitions"][split] = {"rows": len(data), "sha256": hashlib.sha256(content).hexdigest()}
    (args.output / "reconstruction_receipt.json").write_bytes(encoded(receipt))
    print(json.dumps(receipt, indent=2))


if __name__ == "__main__":
    main()
