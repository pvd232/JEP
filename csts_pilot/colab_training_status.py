"""Show delegated training progress while preserving the native publication acknowledgment."""

import copy
import json
from pathlib import Path


def decorate(report: dict, migration_path: Path) -> dict:
    """Expose the observed Colab stage without changing the native report object."""
    result = copy.deepcopy(report)
    if not migration_path.exists():
        return result
    migration = json.loads(migration_path.read_text())
    stage = result.get("stages", {}).get("evidence_ratings", {})
    if stage.get("trace_available") and stage.get("trace_status") in (
        "running",
        "complete",
    ):
        stage["hardware"] = migration["hardware"]
        if stage.get("status") == "pending":
            stage["status"] = "running"
    result["training_migration"] = migration
    return result


def markdown(body: str, report: dict) -> str:
    """State the actual training devices beside the existing proposition epoch history."""
    migration = report.get("training_migration")
    stage = report.get("stages", {}).get("evidence_ratings", {})
    if not migration or not stage.get("trace_available"):
        return body
    heading = "## Proposition model: ratings on the full training set\n"
    if heading not in body:
        return body
    before, after = body.split(heading, 1)
    if stage.get("status") == "running":
        after = after.replace("Status: **pending**.", "Status: **running**.", 1)
    detail = (
        f"\nTraining hardware: **{migration['hardware']}**. Overall batch: **{migration['batch_size']}**; "
        f"microbatch: **{migration['microbatch_size']}**. Ratings control continues on the Asian L4. "
        "Both models keep patience 1 and their best validation checkpoints.\n"
    )
    return before + heading + detail + after
