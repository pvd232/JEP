"""Replay the scope-register join against the frozen review snapshot, offline.

All generated files stay under this review's directory. Synthetic changed scope
decisions demonstrate consistency failures; they are not research conclusions.
"""
from __future__ import annotations

import collections
import contextlib
import copy
import gzip
import importlib.util
import io
import json
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent
BASE = HERE.parents[1] / "base"


def load(name):
    """Load a frozen published JSON artifact without modifying it."""
    return json.loads((BASE / name).read_text())


def replay(promotion_only=False, conflicting_overlap=False):
    """Run the actual assembler with in-memory inputs and an isolated output."""
    spec = importlib.util.spec_from_file_location(
        "review03_assembler", BASE / "workbook_build/assemble_outputs.py"
    )
    module = importlib.util.module_from_spec(spec)
    previous_bytecode_setting = sys.dont_write_bytecode
    try:
        sys.dont_write_bytecode = True
        spec.loader.exec_module(module)
    finally:
        sys.dont_write_bytecode = previous_bytecode_setting
    inputs = {
        "scope_decisions_initial.json": load("scope_decisions.json"),
        "root_content_checks.json": load("new_content_checks.json"),
        "catalog.json": json.loads(gzip.decompress((BASE / "public_catalog.json.gz").read_bytes())),
        "memberships.json": json.loads(gzip.decompress((BASE / "public_memberships.json.gz").read_bytes())),
    }
    for name in [
        "reverse_mapping_review.json", "crawl_manifest.json", "broad_metadata_scope.json",
        "inventory.json", "summary.json", "pagination_reproduction.json",
        "live_pagination_proof.json", "standalone_replay_result.json",
    ]:
        inputs[name] = load(name)
    broad = inputs["broad_metadata_scope.json"]
    if promotion_only:
        # Synthetic fixture: a broad-only review is promoted, but the main scope
        # table was not updated. A consistency guard should reject this state.
        target = "j7YryvmCbBw"
        row = next(r for r in broad["records"] if r["video_id"] == target)
        row["scope_decision"] = "included"
        row["evidence"] = "SYNTHETIC TEST ONLY: a later review established membership."
        broad["counts"] = dict(collections.Counter(r["scope_decision"] for r in broad["records"]))
        inputs["reverse_mapping_review.json"]["videos"].append({
            "video_id": target, "transcript_ids": [],
            "coverage_status": "No supplied transcript · metadata basis",
            "evidence": [{"claim": "SYNTHETIC TEST ONLY"}],
        })
        name = "promotion"
    elif conflicting_overlap:
        # Synthetic fixture: two registers disagree about the same admitted ID.
        target = "O25PKSrxRuA"
        row = next(r for r in broad["records"] if r["video_id"] == target)
        row["scope_decision"] = "excluded"
        row["evidence"] = "SYNTHETIC TEST ONLY: conflicting later scope decision."
        broad["counts"] = dict(collections.Counter(r["scope_decision"] for r in broad["records"]))
        name = "conflict"
    else:
        target = None
        name = "baseline"
    output = HERE / "observer_outputs" / name
    output.mkdir(parents=True, exist_ok=True)
    module.OUT = output
    module.read = lambda path: copy.deepcopy(inputs[Path(path).name])
    with contextlib.redirect_stdout(io.StringIO()):
        module.main()
    rows = json.loads((output / "video_inventory.json").read_text())
    return {
        "fixture": name,
        "target_video_id": target,
        "assembler_returned_successfully": True,
        "target_video_row": next((r for r in rows if r["video_id"] == target), None),
        "main_included_count": sum(r["scope_label"] == "Included" for r in rows),
        "broad_included_count": broad["counts"]["included"],
    }


def main():
    """Record the observed behavior without pretending synthetic data is real."""
    scope = {r["video_id"]: r for r in load("scope_decisions.json")["records"]}
    broad = {r["video_id"]: r for r in load("broad_metadata_scope.json")["records"]}
    baseline_consistent = all(
        scope.get(vid, {}).get("scope_decision") == "included"
        for vid, row in broad.items() if row["scope_decision"] == "included"
    ) and all(
        scope[vid]["scope_decision"] == broad[vid]["scope_decision"]
        for vid in scope.keys() & broad.keys()
    )
    promotion = replay(promotion_only=True)
    conflict = replay(conflicting_overlap=True)
    result = {
        "reviewed_commit": "620cc5eb85860ff77a837058903321876de82b15",
        "baseline_scope_registers_consistent": baseline_consistent,
        "promoted_broad_only_candidate_silently_omitted": (
            promotion["assembler_returned_successfully"]
            and promotion["target_video_row"] is None
            and promotion["broad_included_count"] == 97
            and promotion["main_included_count"] == 128
        ),
        "conflicting_overlap_silently_accepted": (
            conflict["assembler_returned_successfully"]
            and conflict["target_video_row"]["scope_label"] == "Included"
            and conflict["broad_included_count"] == 95
        ),
        "synthetic_fixture_ids_are_not_research_reclassifications": True,
    }
    (HERE / "scope_join_observer.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
