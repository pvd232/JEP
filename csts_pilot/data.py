"""Prepare partitions with disjoint connected sets of source captions."""

import argparse
import csv
import hashlib
import json
import unicodedata
from collections import Counter
from pathlib import Path
from typing import Any

REVISION = "058ac842f5f19d27b08ad54f6d4a2c50b3f9578b"
HASHES = {
    "train": "118ef935443531a60f3dd5652afd946869f47b134c83fd8da38779912167b652",
    "validation": "84602c1bcbbe1e6410a78c9cb1cb0f3dac4bf48c0c55ad42dc19558370e4821f",
}


def canonical(text: str) -> str:
    """Use one identity for differences in whitespace, case and Unicode form."""
    return " ".join(unicodedata.normalize("NFKC", text).casefold().split())


def digest(value: str) -> str:
    """Create a stable identifier independent of process hash randomization."""
    return hashlib.sha256(value.encode()).hexdigest()


def normalize_rating(rating: float) -> float:
    """Map the released 1–5 scale to the model's 0–1 score range."""
    if not 1 <= rating <= 5:
        raise ValueError("Expected a valid rating between 1 and 5.")
    return (rating - 1.0) / 4.0


def partition(
    training: list[dict[str, Any]], validation: list[dict[str, Any]]
) -> tuple[dict[str, list[dict[str, Any]]], dict[str, Any]]:
    """Reserve released validation, remove overlapping training and split by group."""
    parent: dict[str, str] = {}

    def root(text: str) -> str:
        parent.setdefault(text, text)
        if parent[text] != text:
            parent[text] = root(parent[text])
        return parent[text]

    valid: dict[str, list[dict[str, Any]]] = {}
    invalid: dict[str, int] = {}
    for name, rows in (("train", training), ("evaluation", validation)):
        invalid[name] = sum(float(row["label"]) == -1 for row in rows)
        valid[name] = []
        for index, row in enumerate(rows):
            rating = float(row["label"])
            if rating == -1:
                continue
            target = normalize_rating(rating)
            left, right = str(row["sentence1"]), str(row["sentence2"])
            a, b = root(canonical(left)), root(canonical(right))
            parent[max(a, b)] = min(a, b)
            valid[name].append(
                {
                    "row_id": f"{name}_{index}",
                    "sentence1": left,
                    "sentence2": right,
                    "condition": str(row["condition"]),
                    "rating": rating,
                    "target": target,
                    "pair_id": digest(
                        json.dumps(sorted((canonical(left), canonical(right))))
                    ),
                }
            )
    for rows in valid.values():
        for row in rows:
            row["group_id"] = digest(root(canonical(row["sentence1"])))
    evaluation_groups = {row["group_id"] for row in valid["evaluation"]}
    result: dict[str, list[dict[str, Any]]] = {
        "train": [],
        "dev": [],
        "evaluation": valid["evaluation"],
    }
    excluded = 0
    for row in valid["train"]:
        if row["group_id"] in evaluation_groups:
            excluded += 1
            continue
        bucket = int(digest("csts-split-20261021:" + row["group_id"])[:8], 16)
        result["dev" if bucket / 2**32 < 0.2 else "train"].append(row)
    captions = {
        name: {
            canonical(row[key]) for row in rows for key in ("sentence1", "sentence2")
        }
        for name, rows in result.items()
    }
    for a, b in (("train", "dev"), ("train", "evaluation"), ("dev", "evaluation")):
        if captions[a] & captions[b]:
            raise RuntimeError("Source captions crossed partitions.")
    manifest: dict[str, Any] = {
        "dataset": "LivNLP/C-STS-Reannotated",
        "revision": REVISION,
        "labels": "Authors combine LLM reannotations and original human labels.",
        "invalid_rows_removed": invalid,
        "overlapping_training_rows_removed": excluded,
        "split": "Connected canonical caption components. Released validation is evaluation.",
        "normalization": "target = (rating - 1) / 4; rating_prediction = 1 + 4 * score",
        "partitions": {
            name: {
                "rows": len(rows),
                "groups": len({row["group_id"] for row in rows}),
                "pairs": len({row["pair_id"] for row in rows}),
                "ratings": dict(
                    sorted(Counter(str(row["rating"]) for row in rows).items())
                ),
            }
            for name, rows in result.items()
        },
    }
    return result, manifest


def main() -> None:
    """Verify downloaded bytes and write explicit data inputs for VIPER snapshots."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=Path("csts_data"))
    args = parser.parse_args()
    raw: dict[str, list[dict[str, Any]]] = {}
    for name, expected in HASHES.items():
        path = args.source / f"csts_{name}_reannotated.csv"
        if hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            raise ValueError(f"Downloaded {name} bytes differ from the pinned release.")
        with path.open(newline="") as handle:
            raw[name] = list(csv.DictReader(handle))
    parts, manifest = partition(raw["train"], raw["validation"])
    args.output.mkdir(parents=True, exist_ok=True)
    for name, rows in parts.items():
        path = args.output / f"{name}.json"
        path.write_text(json.dumps(rows, ensure_ascii=False, indent=2) + "\n")
        manifest["partitions"][name]["sha256"] = hashlib.sha256(
            path.read_bytes()
        ).hexdigest()
    (args.output / "evaluation_indices.json").write_text(
        json.dumps(list(range(len(parts["evaluation"])))) + "\n"
    )
    (args.output / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
