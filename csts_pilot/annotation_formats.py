"""Render existing teacher facts as matched annotation training targets."""

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Literal

AnnotationFormat = Literal["evidence", "prose", "record"]
FORMATS: tuple[AnnotationFormat, ...] = ("evidence", "prose", "record")


def render_target(record: dict[str, Any], style: AnnotationFormat) -> str:
    """Preserve cached field values without introducing types or new facts."""
    if style not in FORMATS:
        raise ValueError(f"Unknown annotation format: {style}")
    if record.get("valid") is not True:
        return ""
    evidence = record.get("answer")
    if not isinstance(evidence, str) or not evidence.strip():
        raise ValueError("Accepted record has no evidence answer.")
    if style == "evidence":
        return evidence
    fields = {"target": record.get("target"), "attribute": record.get("attribute")}
    if any(
        not isinstance(value, str) or not value.strip() for value in fields.values()
    ):
        raise ValueError("Accepted record lacks nonempty cached target or attribute.")
    fields["evidence"] = evidence
    if style == "record":
        return json.dumps(fields, ensure_ascii=False)
    quoted = {
        key: json.dumps(value, ensure_ascii=False) for key, value in fields.items()
    }
    return (
        f"The target is {quoted['target']} and the attribute is {quoted['attribute']}. "
        f"The supporting evidence is {quoted['evidence']}."
    )


def prepare_targets(
    source: Path, destination: Path, expected_count: int
) -> dict[str, Any]:
    """Validate the original cache and preserve acceptance and input identities."""
    from csts_pilot.answers import parse_response, review_accepts

    raw = source.read_bytes()
    rows = [json.loads(line) for line in raw.splitlines() if line.strip()]
    if len(rows) != expected_count:
        raise ValueError(
            f"Expected {expected_count} cached records, found {len(rows)}."
        )
    identities = [row["id"] for row in rows]
    if len(set(identities)) != len(identities):
        raise ValueError("Duplicate cached annotation identities.")
    for row in rows:
        if type(row.get("valid")) is not bool:
            raise ValueError("Every cached record must retain its acceptance decision.")
        if row["valid"]:
            parsed = parse_response(row["passage"], row.get("response", ""))
            if (
                not parsed["valid"]
                or parsed["answer"] != row["answer"]
                or parsed.get("target") != row.get("target")
                or parsed.get("attribute") != row.get("attribute")
                or not review_accepts(row.get("review_response", ""))
            ):
                raise ValueError(f"Cached record fails original checks: {row['id']}")
    rendered = {
        style: [dict(row, answer=render_target(row, style)) for row in rows]
        for style in FORMATS
    }
    # Validate all variants before writing any target files.
    if destination.exists() and any(destination.iterdir()):
        raise ValueError("Target destination must be empty; preserve prior artifacts.")
    destination.mkdir(parents=True, exist_ok=True)
    manifest: dict[str, Any] = {
        "source_sha256": hashlib.sha256(raw).hexdigest(),
        "records": len(rows),
        "accepted": sum(row["valid"] for row in rows),
        "new_teacher_calls": 0,
        "new_semantic_fields": [],
        "formats": {},
        "validation_scope": "Original source-span and teacher-review checks; metadata semantic audit remains separate.",
    }
    for style, targets in rendered.items():
        content = "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in targets)
        artifact = destination / f"{style}.jsonl"
        artifact.write_text(content)
        manifest["formats"][style] = {
            "file": artifact.name,
            "sha256": hashlib.sha256(content.encode()).hexdigest(),
            "identity_order_preserved": [row["id"] for row in targets] == identities,
            "acceptance_preserved": all(
                target["valid"] == original["valid"]
                for original, target in zip(rows, targets, strict=True)
            ),
        }
    (destination / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    return manifest


def main() -> None:
    """Prepare targets only; this command never starts training or generation."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--destination", type=Path, required=True)
    parser.add_argument("--expected-count", type=int, default=17334)
    args = parser.parse_args()
    print(
        json.dumps(prepare_targets(args.source, args.destination, args.expected_count))
    )


if __name__ == "__main__":
    main()
