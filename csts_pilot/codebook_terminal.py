"""Inspect already-trained terminal dictionaries after the primary selection is fixed."""

import argparse
import inspect
import sys
from pathlib import Path
from typing import Any

import torch

from csts_pilot.codebook import (
    ARMS,
    PrototypeEncoder,
    check_disjoint,
    code_diagnostics,
    representations,
    restore_model,
    scored_rows,
    spherical_kmeans,
    unique_positions,
)
from csts_pilot.convergence import file_sha256, write_json
from csts_pilot.convergence_run import artifact_path
from csts_pilot.diagnostics import summarize
from jep_pilot.loaders import load_json, load_model, load_state


def analyze(summary_path: Path) -> dict[str, Any]:
    """Compare terminal states descriptively, without selecting or updating a model."""
    torch.set_num_threads(1)
    parent = load_json(summary_path)
    records = {r["name"]: r for r in parent["runs"] if r["status"] == "succeeded"}
    fitted = records["fit"]
    model_path = artifact_path(fitted, "train", "model", "models.pt")
    resume_path = artifact_path(fitted, "train", "resume_state", "resume.pt")
    trace_path = artifact_path(fitted, "train", "trace", "trace.json")
    if file_sha256(model_path) != parent["frozen_models_sha256"]:
        raise ValueError("The selected bundle differs from its frozen identity.")
    bundle, trace = load_model(model_path), load_json(trace_path)
    config = bundle["config"]
    caches, cache_hashes = {}, {}
    for name in ("training", "validation"):
        path = artifact_path(records["prepare_" + name], "prepare", "cache", "cache.pt")
        cache_hashes[name] = file_sha256(path)
        if cache_hashes[name] != config[name + "_cache_sha256"]:
            raise ValueError("Terminal inspection received different fitting vectors.")
        caches[name] = load_model(path)
    check_disjoint(*caches.values())
    terminal = load_state(resume_path).optimizer_state["terminal_runs"]
    if set(terminal) != set(bundle["models"]):
        raise ValueError("The terminal and selected bundle model identities differ.")
    output = {}
    for seed in config["seeds"]:
        for arm in ARMS:
            key = f"{seed}:{arm}"
            model = restore_model({"state": terminal[key]["state"]})
            if arm == "projection":
                # Apply the control's declared post-hoc clustering policy to its
                # terminal projection, using training vectors only.
                centers = spherical_kmeans(
                    representations(model, caches["training"])[
                        unique_positions(caches["training"])
                    ],
                    config["codes"],
                    config["kmeans_iterations"],
                    seed,
                )
                model.dictionary.data.copy_(centers)
            output[key] = {
                "completed_epochs": len(trace["fits"][key]["epochs"]),
                "updates": terminal[key]["updates"],
                "primary_selected_epoch": bundle["models"][key]["epoch"],
                "validation": summarize(
                    scored_rows(
                        caches["validation"],
                        representations(model, caches["validation"]),
                    )
                ),
                "training": summarize(
                    scored_rows(
                        caches["training"], representations(model, caches["training"])
                    )
                ),
                "codes_training": code_diagnostics(model, caches["training"]),
                "codes_validation": code_diagnostics(model, caches["validation"]),
            }
    return {
        "status": "post_selection_terminal_diagnostic",
        "scope": "Retrospective development analysis of already-trained terminal states. No training, hyperparameter search, checkpoint reselection, test data or JEP human judgments. Control dictionaries are fitted on training vectors only.",
        "primary_result_changed": False,
        "source_summary_sha256": file_sha256(summary_path),
        "selected_models_sha256": file_sha256(model_path),
        "resume_sha256": file_sha256(resume_path),
        "trace_sha256": file_sha256(trace_path),
        "cache_sha256": cache_hashes,
        "diagnostic_code_sha256": file_sha256(Path(__file__)),
        "encoder_code_sha256": file_sha256(Path(inspect.getfile(PrototypeEncoder))),
        "python": sys.executable,
        "torch": str(torch.__version__),
        "metrics": output,
    }


def main() -> None:
    """Write one new, finite diagnostic artifact while preserving native evidence."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--summary", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError("Preserve the preceding terminal diagnostic.")
    write_json(args.output, analyze(args.summary))


if __name__ == "__main__":
    main()
