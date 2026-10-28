"""Freeze condition routes and a reserve excluding every exposed source group."""

from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path

from .schema import backend_schemas, compile_condition, implementation_identity, plan_digest


def build(screen_sources, validation_rows):
    """Use condition/source identities only; similarity labels are never consumed."""
    screen = [{key: row[key] for key in ("id", "passage", "condition", "group_id")}
              for row in screen_sources]
    validation = [{key: row[key] for key in ("row_id", "condition", "group_id", "sentence1", "sentence2")}
                  for row in validation_rows]
    exposed = {row["group_id"] for row in screen}
    captions = {" ".join(row["passage"].casefold().split()) for row in screen}
    eligible = [row for row in validation if row["group_id"] not in exposed]
    if any(" ".join(row[key].casefold().split()) in captions for row in eligible for key in ("sentence1", "sentence2")):
        raise ValueError("Fresh group reserve still overlaps an exposed source caption")
    screen_counts = Counter(row["condition"] for row in screen)
    validation_counts = Counter(row["condition"] for row in validation)
    records = []
    for condition in sorted(validation_counts.keys() | screen_counts.keys()):
        plan = compile_condition(condition)
        records.append({"condition": condition, "screen_sources": screen_counts[condition],
                        "validation_rows": validation_counts[condition], "plan": plan,
                        "backend_tasks": {model: sorted({schema["kind"] for schema in backend_schemas(plan, model)})
                                          for model in ("gollie", "knowcoder")},
                        "plan_sha256": plan_digest(plan), "production_approved": False})
    summary = {}
    for row in records:
        plan = row["plan"]
        key = plan["family"] + (":designed" if plan["supported"] else ":unsupported")
        target = summary.setdefault(key, {"unique_conditions": 0, "screen_sources": 0, "validation_rows": 0})
        target["unique_conditions"] += 1
        target["screen_sources"] += row["screen_sources"]
        target["validation_rows"] += row["validation_rows"]
    return {"version": "native-route-inventory-v1", "labels_consumed": False,
            "implementation_sha256": implementation_identity(), "family_summary": summary,
            "screen": {"sources": len(screen), "conditions": len(screen_counts), "exposed_groups": len(exposed)},
            "validation": {"rows": len(validation), "conditions": len(validation_counts)},
            "routes": records,
            "fresh_reserve": {"all_exposed_groups_excluded": sorted(exposed),
                              "rows": len(eligible), "groups": len({r["group_id"] for r in eligible}),
                              "conditions": len({r["condition"] for r in eligible}),
                              "identities": [{key: row[key] for key in ("row_id", "group_id", "condition")} for row in eligible]}}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--screen-sources", type=Path, required=True)
    parser.add_argument("--validation", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = build(json.loads(args.screen_sources.read_text()), json.loads(args.validation.read_text()))
    content = (json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode()
    with args.output.open("xb") as handle:
        handle.write(content)
    print(json.dumps({"output_sha256": hashlib.sha256(content).hexdigest(),
                      "screen": result["screen"], "validation": result["validation"],
                      "family_summary": result["family_summary"],
                      "fresh_reserve": {key: value for key, value in result["fresh_reserve"].items()
                                        if key != "identities" and key != "all_exposed_groups_excluded"}}, indent=2))


if __name__ == "__main__":
    main()
