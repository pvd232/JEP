"""Freeze source-disjoint proposition checks and render their measured progress."""

import hashlib
import json
from pathlib import Path
from typing import Any

from csts_pilot.data import canonical


def digest(data: bytes) -> str:
    """Identify immutable inputs and measurements by their exact bytes."""
    return hashlib.sha256(data).hexdigest()


def inventory(
    rows: list[dict[str, Any]],
) -> tuple[list[dict[str, str]], dict[str, str]]:
    """Extract unique passage-condition inputs with no ratings or companion text."""
    items, groups = {}, {}
    for row in rows:
        for side in ("sentence1", "sentence2"):
            identity = digest(
                json.dumps([canonical(row[side]), canonical(row["condition"])]).encode()
            )
            if identity in groups and groups[identity] != row["group_id"]:
                raise ValueError("One input crosses source groups.")
            groups[identity] = row["group_id"]
            items.setdefault(
                identity,
                {"id": identity, "passage": row[side], "condition": row["condition"]},
            )
    return [items[key] for key in sorted(items)], groups


def heldout(
    training: list[dict], validation: list[dict], count: int = 128
) -> tuple[list[dict], dict]:
    """Select one validation input per source group with a fixed label-independent hash."""
    if count < 1:
        raise ValueError("A held-out sample needs at least one input.")
    training_items, training_groups = inventory(training)
    items, groups = inventory(validation)
    if set(training_groups.values()) & set(groups.values()):
        raise ValueError("Training and validation source groups overlap.")
    if {canonical(r["passage"]) for r in training_items} & {
        canonical(r["passage"]) for r in items
    }:
        raise ValueError("Training and validation passages overlap.")
    selected, seen = [], set()
    for item in sorted(
        items, key=lambda r: digest(("proposition-validation-v1:" + r["id"]).encode())
    ):
        if groups[item["id"]] not in seen:
            selected.append(item)
            seen.add(groups[item["id"]])
        if len(selected) == count:
            break
    if len(selected) != count:
        raise ValueError("Too few held-out source groups.")
    return selected, {r["id"]: groups[r["id"]] for r in selected}


def review_metrics(candidates: list[dict], reviews: list[list[dict]]) -> dict:
    """Require complete independent reviews and report agreement plus conservative accuracy."""
    expected = {r["id"] for r in candidates}
    if len(expected) != len(candidates) or not expected or len(reviews) != 2:
        raise ValueError("Two complete reviews of unique candidates are required.")
    checked = []
    for review in reviews:
        if len(review) != len(expected) or {r["id"] for r in review} != expected:
            raise ValueError("Review identities differ from the generated sample.")
        for row in review:
            if set(row) != {
                "id",
                "supported",
                "complete",
                "unsupported_assertion",
                "notes",
            }:
                raise ValueError("Unexpected review fields.")
            if any(
                type(row[key]) is not bool
                for key in ("supported", "complete", "unsupported_assertion")
            ):
                raise ValueError("Review verdicts must be booleans.")
            if row["supported"] and row["unsupported_assertion"]:
                raise ValueError("A review contradicts its factual support verdict.")
        checked.append({r["id"]: r for r in review})
    correct = sum(
        all(
            r[key]["supported"]
            and r[key]["complete"]
            and not r[key]["unsupported_assertion"]
            for r in checked
        )
        for key in expected
    )
    supported = sum(all(r[key]["supported"] for r in checked) for key in expected)
    unsupported = sum(
        any(r[key]["unsupported_assertion"] for r in checked) for key in expected
    )
    agreement = sum(
        all(
            checked[0][key][field] == checked[1][key][field]
            for field in ("supported", "complete", "unsupported_assertion")
        )
        for key in expected
    )
    return {
        "n": len(expected),
        "fully_correct": correct,
        "accuracy": correct / len(expected),
        "supported": supported,
        "unsupported_assertion_count": unsupported,
        "review_agreement": agreement / len(expected),
        "reviewers": "Two independent GPT-6.1 Sol high calls; model-reviewed, no human adjudication.",
    }


def read_status(root: Path) -> dict:
    """Read the independent monitor without altering native training or selection state."""
    path = root / "status.json"
    state = json.loads(path.read_text()) if path.exists() else {"status": "preparing"}
    protocol = root / "protocol.json"
    if protocol.exists():
        state["protocol"] = json.loads(protocol.read_text())
    revision = root / "evaluation_source_revision.json"
    if revision.exists():
        state["evaluation_source_revision"] = json.loads(revision.read_text())
    evaluations = {row["epoch"]: row for row in state.get("evaluations", [])}
    for epoch in (2, 4):
        result = root / f"epoch_{epoch}_result.json"
        if result.exists() and epoch not in evaluations:
            evaluations[epoch] = json.loads(result.read_text())
    state["evaluations"] = [evaluations[epoch] for epoch in sorted(evaluations)]
    return state


def panel(state: dict) -> str:
    """Keep pending measurements distinct from observed proposition validation results."""
    generation = state.get("generation", {})
    lines = [
        "## Proposition validation and full-training generation",
        "",
        f"Monitor: **{state.get('status', 'preparing')}**.",
        "",
        f"Training inputs captured: **{generation.get('completed_inputs', 2496):,}/11,909**; missing inputs requested: **9,413**. The current training bank remains frozen.",
        "",
        "Held-out sample: **128 validation source groups**, one passage-condition input per group. References and generated answers are kept outside training. Evaluation uses the retained checkpoints; hardware and progress appear in the detailed status below.",
        "",
        "| Proposition checkpoint | Held-out answer loss | Model-reviewed factual accuracy | Reviewed answers |",
        "|---|---:|---:|---:|",
    ]
    failure = state.get("gpu_evaluation", {}).get("error") or state.get("retry_error")
    if failure:
        lines.insert(4, "Current evaluation/retry issue: " + str(failure) + "\n")
    evaluations = state.get("evaluations", [])
    for epoch in (2, 4):
        result = next((r for r in evaluations if r.get("epoch") == epoch), {})
        loss = result.get("mean_answer_cross_entropy")
        audit = result.get("factual_review", {})
        accuracy = audit.get("accuracy")
        lines.append(
            f"| After {epoch} proposition-writing epochs | {loss:.6f}"
            if loss is not None
            else f"| After {epoch} proposition-writing epochs | Pending"
        )
        lines[-1] += (
            f" | {accuracy:.1%} | {audit['n']} |"
            if accuracy is not None
            else " | Pending | — |"
        )
    lines += [
        "",
        "Loss averages each answer's next-token cross-entropy, then averages answers. Factual checks use free-generated answers and two independent source-only model reviews; they report support, omissions, unsupported assertions and reviewer agreement. These measurements describe proposition writing and do not change the running experiment's stopping rule.",
        "",
        "Earlier checkpoints were overwritten by the original trainer; epochs 2 and 4 have retained checkpoints. [Detailed status and results](proposition_validation.json).",
        "",
    ]
    for title, audit in [
        ("Held-out reference review", state.get("validation_reference_review", {})),
        ("Training-generation review", generation.get("factual_review", {})),
    ]:
        if audit:
            lines += [
                f"{title}: **{audit['fully_correct']}/{audit['n']}** fully correct by both model reviewers; **{audit['unsupported_assertion_count']}** flagged for unsupported assertions; reviewer agreement **{audit['review_agreement']:.1%}**.",
                "",
            ]
    return "\n".join(lines)


def insert(body: str, state: dict) -> str:
    """Replace only the monitor section while preserving every native epoch row."""
    start, end = (
        "<!-- proposition-validation:start -->",
        "<!-- proposition-validation:end -->",
    )
    if start in body:
        before, rest = body.split(start, 1)
        _, after = rest.split(end, 1)
        return before + start + "\n" + panel(state) + end + after
    return body.rstrip() + "\n\n" + start + "\n" + panel(state) + end + "\n"
