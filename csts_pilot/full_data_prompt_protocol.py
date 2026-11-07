"""Dependency-free protocol and approval checks for the full-data prompt study.

This module never provisions resources, imports a model, or starts training.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from string import Formatter
from typing import Any

PROMPTS = {
    "A_condition_first": "Instruct: Represent the passage for semantic similarity with respect to this condition: {condition}\nQuery: {passage}",
    "B_order_only": "Query: {passage}\nInstruct: Represent the passage for semantic similarity with respect to this condition: {condition}",
    "C_case_inspired": "Instruct: Retrieve semantically similar texts to a given Condition, given the Sentence: {passage}\nQuery: {condition}",
}
REVIEW_ROLES = (
    "design", "case_semantics", "lora_gradients", "data_leakage", "rng_optimizer",
    "spot_recovery", "viper_contract", "statistics", "performance", "lifecycle_security",
)
BASE_REVISION = "c90816d848505624c2434128dfc61132162a0ee9"
PINNED_SPLITS = {
    "training": (6051, 2635, "9a9eac21ee73b9b029ca6f62584891dd13c74aa78e80efd764532a87665ae6a4"),
    "validation": (1576, 680, "e42d9544b2aa6814708337d0ce38eba1d64124645b62489ed448c6784dbc71ff"),
    "test": (2430, 1222, "52a9c0d6b8d9f3fc81e698bae1e2564051cf7ec29e8dc1cb4d68167910bb968d"),
}


def digest_file(path: Path) -> str:
    """Hash a file without deserializing its content or loading it into memory."""
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def digest_object(value: Any) -> str:
    """Make manifest identity independent of indentation and dictionary order."""
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"),
                                     allow_nan=False).encode()).hexdigest()


def render_prompt(arm: str, passage: str, condition: str) -> str:
    """Render the registered experimental prompt without interpreting data braces."""
    if arm not in PROMPTS:
        raise ValueError(f"Unknown prompt arm: {arm}")
    if not isinstance(passage, str) or not passage.strip():
        raise ValueError("Passage must be nonempty text.")
    if not isinstance(condition, str) or not condition.strip():
        raise ValueError("Condition must be nonempty text.")
    return PROMPTS[arm].format(passage=passage, condition=condition)


def validate_protocol(p: dict[str, Any]) -> None:
    """Reject silent changes to the approved scientific design before plan building."""
    if p["arms"] != list(PROMPTS) or p["seeds"] != [7, 8, 9, 10, 11]:
        raise ValueError("Require three registered arms and five paired seeds.")
    if p["model"] != {"id": "Qwen/Qwen3-Embedding-8B", "revision": BASE_REVISION,
                      "width": 4096, "max_length": 160}:
        raise ValueError("Base model, pooling width or token ceiling changed.")
    expected = {"seed_policy": "paired", "kind": "lora", "learning_rate": 2e-5,
                "weight_decay": .01, "batch_size": 32, "microbatch_size": 32,
                "schedule": "constant", "warmup_fraction": 0, "lora_rank": 32,
                "lora_alpha": 32, "lora_dropout": .05, "patience": 1,
                "max_epochs": 24, "train_until_patience": False,
                "initialization": "fresh_base_and_lora", "subset_phase_epochs": 0,
                "optimizer_resets": 0}
    if p["training"] != expected:
        raise ValueError("Full-data ratings-only training configuration changed.")
    for split, (rows, groups, digest) in PINNED_SPLITS.items():
        item = p["splits"][split]
        if (item["rows"], item["groups"], item["sha256"]) != (rows, groups, digest):
            raise ValueError(f"Pinned {split} cohort changed.")
    if p["execution"]["gcp_project"] != "mantra-477901":
        raise ValueError("Training belongs to Mantra, not the CPU development project.")
    if p["execution"]["max_gcp_gpus"] != 2:
        raise ValueError("Do not exceed the authorized two-Mantra-GPU concurrency.")
    if p["analysis"]["test_release"] != "all_15_validation_selections_frozen":
        raise ValueError("Test labels must stay sealed until all selections freeze.")
    for text in PROMPTS.values():
        fields = [f for _, f, _, _ in Formatter().parse(text) if f is not None]
        if sorted(fields) != ["condition", "passage"]:
            raise ValueError("Each input appears once in each prompt.")


def trial_matrix(p: dict[str, Any]) -> list[dict[str, Any]]:
    """List 15 new fits, grouped by seed and with arm order counterbalanced."""
    validate_protocol(p)
    rows = []
    arms = list(PROMPTS)
    for index, seed in enumerate(p["seeds"]):
        order = arms[index % 3:] + arms[:index % 3]
        for arm in order:
            rows.append({"trial_id": f"{arm}_seed{seed}", "arm": arm, "seed": seed,
                         "hardware_block": f"seed{seed}", "prompt": PROMPTS[arm],
                         "training_rows": p["splits"]["training"]["rows"],
                         "fresh_initialization": True, "evidence_loss": False,
                         "subset_phase_epochs": 0})
    return rows


def load_fit_cohorts(root: Path, p: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    """Check all split bytes but deserialize only training and validation here."""
    validate_protocol(p)
    loaded = {}
    for split in ("training", "validation", "test"):
        item = p["splits"][split]
        path = root / item["path"]
        if digest_file(path) != item["sha256"]:
            raise ValueError(f"Changed {split} bytes.")
        if split == "test":
            continue
        values = json.loads(path.read_text())
        if len(values) != item["rows"] or len({r["group_id"] for r in values}) != item["groups"]:
            raise ValueError(f"Changed {split} size/groups.")
        if len({r["row_id"] for r in values}) != len(values):
            raise ValueError(f"Duplicate {split} row identity.")
        loaded[split] = values
    for field in ("row_id", "group_id"):
        if {r[field] for r in loaded["training"]} & {r[field] for r in loaded["validation"]}:
            raise ValueError(f"Training/validation share {field}.")
    return loaded


def require_launch_approval(p: dict[str, Any], source: str,
                            approval: dict[str, Any], reviews: list[dict[str, Any]]) -> None:
    """Fail closed until a user-approved exact revision has ten independent receipts.

    Provider provenance must additionally be checked by the human/controller; strings
    in a JSON object are not cryptographic proof of independent review.
    """
    validate_protocol(p)
    if approval.get("user_execution_approved") is not True:
        raise PermissionError("User requested presentation before execution.")
    if approval.get("source_commit") != source or approval.get("protocol_sha256") != digest_object(p):
        raise PermissionError("Approval must bind this exact source and protocol.")
    if len(reviews) != 10 or {r.get("role") for r in reviews} != set(REVIEW_ROLES):
        raise PermissionError("Ten completed independent reviews are required.")
    ids = {r.get("provider_run_id") for r in reviews}
    if len(ids) != 10 or None in ids or "" in ids:
        raise PermissionError("Review receipts must have ten distinct provider executions.")
    for r in reviews:
        if (r.get("status"), r.get("source_commit"), r.get("protocol_sha256")) != (
                "approved", source, digest_object(p)) or r.get("blocking_findings", 0):
            raise PermissionError("Unresolved or mismatched reviewer receipt.")


def require_complete_selections(p: dict[str, Any], selections: list[dict[str, Any]]) -> None:
    """Prevent held-out evaluation of an incomplete or budget-censored fit matrix."""
    expected = {r["trial_id"] for r in trial_matrix(p)}
    if len(selections) != 15 or {s.get("trial_id") for s in selections} != expected:
        raise ValueError("All 15 independently validation-selected models must be frozen.")
    source_commits = {s.get("training_source_commit") for s in selections}
    if len(source_commits) != 1:
        raise ValueError("Selections mix training source revisions.")
    source_commit = next(iter(source_commits))
    if (not isinstance(source_commit, str) or len(source_commit) != 40
            or any(c not in "0123456789abcdef" for c in source_commit)):
        raise ValueError("Training source revision is not bound.")
    for s in selections:
        if s.get("protocol_sha256") != digest_object(p):
            raise ValueError("Selections belong to a different protocol.")
        if s.get("selection_metric") != "validation_spearman" or s.get("test_used") is not False:
            raise ValueError("A selection used the wrong partition or selection metric.")
        if s.get("stop_reason") != "validation_patience":
            raise ValueError("Budget-censored trials cannot silently enter final evaluation.")
        digest = s.get("model_sha256", "")
        if len(digest) != 64 or any(c not in "0123456789abcdef" for c in digest):
            raise ValueError("Selected model is not hash-bound.")


def main() -> None:
    """Print the draft matrix only: never allocate compute or start training."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=Path("configs/csts-full-data-prompt-20261107.json"))
    args = parser.parse_args()
    protocol = json.loads(args.config.read_text())
    print(json.dumps({"status": "DRAFT_NO_EXECUTION", "protocol_sha256": digest_object(protocol),
                      "trials": trial_matrix(protocol)}, indent=2))


if __name__ == "__main__":
    main()
