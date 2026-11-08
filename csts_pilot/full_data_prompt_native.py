"""Draft native VIPER plan builders. No provisioning or execution side effects.

One scientific training phase is sealed in resumable epoch-sized native segments.
Each continuation restores the same optimizer, scheduler, RNG and best incumbent.
The full-data curriculum, seed and prompt never change between segments.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

from csts_pilot.full_data_prompt_protocol import (
    PROMPTS, digest_object, require_complete_selections, validate_protocol,
)


def fit_arguments(protocol: dict[str, Any], arm: str, seed: int,
                  completed_epochs: int = 0) -> dict[str, Any]:
    """Specify a single full-data epoch without introducing a new training phase."""
    validate_protocol(protocol)
    if arm not in PROMPTS or seed not in protocol["seeds"]:
        raise ValueError("Unregistered arm/seed.")
    if type(completed_epochs) is not int or not 0 <= completed_epochs < protocol["training"]["max_epochs"]:
        raise ValueError("Epoch cap reached or invalid continuation counter.")
    spec = protocol["model"]
    train = protocol["training"]
    return {
        "model_id": spec["id"], "revision": spec["revision"],
        "max_length": spec["max_length"], "embedding_dimension": spec["width"],
        "encode_batch_size": 4, "device": "cuda", "kind": "lora", "seed": seed,
        "prompt_template": PROMPTS[arm],
        "trial_id": f"{arm}_seed{seed}",
        "data_contract": {name: protocol["splits"][name] for name in ("training", "validation")},
        "learning_rate": train["learning_rate"], "weight_decay": train["weight_decay"],
        "batch_size": train["batch_size"], "microbatch_size": train["microbatch_size"],
        "schedule": "constant", "warmup_fraction": 0,
        "lora_rank": train["lora_rank"], "lora_alpha": train["lora_alpha"],
        "lora_dropout": train["lora_dropout"], "patience": train["patience"],
        "train_until_patience": False, "max_epochs": completed_epochs + 1,
        "start_epoch": completed_epochs, "max_seconds": 36000,
    }


def next_epoch_from_trace(trace: dict[str, Any]) -> int:
    """Return a sealed continuation boundary; never resume a running partial write."""
    history = trace.get("epochs", [])
    if trace.get("status") != "complete" or trace.get("stop_reason") != "epoch_budget":
        raise ValueError("Parent is partial, failed, or already stopped by validation.")
    if not history or [e.get("epoch") for e in history] != list(range(1, len(history) + 1)):
        raise ValueError("Noncontiguous epoch history.")
    if trace.get("actual_updates") != 190 * len(history):
        raise ValueError("Continuation did not train on the full 6051 comparisons.")
    return len(history)


def epoch_stage(protocol: dict[str, Any], arm: str, seed: int,
                parent: dict[str, Any] | None = None,
                parent_trace: dict[str, Any] | None = None) -> Any:
    """Construct a native training stage, requiring the installed pinned environment.

    Calling this constructs a graph only. The existing fit_lora/fit_neural code
    handles gradient computation and exact state restoration, without new losses.
    """
    from viper.authoring import input, stage
    from viper.metrics import max as maximize, measure
    from csts_pilot.baseline_models import FitConfig
    from csts_pilot.baseline_stages import fit_lora
    from csts_pilot.convergence import training_objective, validation_mse, validation_spearman
    from csts_pilot.convergence_run import artifact_source
    from csts_pilot.evidence_run import evidence_training_outputs

    if (parent is None) != (parent_trace is None):
        raise ValueError("Parent reference and trace must be supplied together.")
    completed = 0 if parent is None else next_epoch_from_trace(parent_trace)
    config = FitConfig.model_validate(fit_arguments(protocol, arm, seed, completed))
    inputs = [input(name, path=protocol["splits"][name]["path"], data_role="training")
              for name in ("training", "validation")]
    if parent is not None:
        bindings = {"parent_model": "model", "parent_last_model": "last_model",
                    "parent_resume": "resume_state", "parent_trace": "trace",
                    "parent_validation_predictions": "validation_predictions"}
        for name, artifact in bindings.items():
            # Never pass data_role a second time for a bound source input.
            inputs.append(input(name, source=artifact_source(parent, "train", artifact)))
    metrics = tuple(measure(m) for m in (training_objective, validation_mse, validation_spearman))
    return stage(fit_lora, stage_id="train", config=config, inputs=tuple(inputs),
                 outputs=evidence_training_outputs(), metrics=metrics,
                 objective=maximize(metrics[-1]), reuse="never")


def epoch_plan(root: Path, protocol: dict[str, Any], arm: str, seed: int,
               gpu_model: str, parent: dict[str, Any] | None = None,
               parent_trace: dict[str, Any] | None = None) -> Any:
    """Build a source-bound local VIPER plan; never allocate or execute a worker."""
    from viper.authoring import experiment, plan, replicate, variant
    from viper.references import GitFileRef
    from viper.repository import read_source
    from viper.runtime import CUDAComputeSpec, LocalEnvSpec, observe_python_env

    source = read_source(root)
    configured = epoch_stage(protocol, arm, seed, parent, parent_trace)
    epoch = 1 if parent_trace is None else len(parent_trace["epochs"]) + 1
    trial = experiment(
        experiment_id=f"full_prompt_{source.commit[:8]}_{arm.lower()}_s{seed}_e{epoch}",
        variants=(variant(arm.lower(), stages=(configured,), estimator=configured.outputs["model"]),),
        replicates=(replicate(seed=seed),),
    )
    environment = LocalEnvSpec(
        compute=CUDAComputeSpec(model=gpu_model, count=1),
        lockfile=GitFileRef(repository=source.repository, commit=source.commit,
                           path="tranche2_requirements.txt"),
        python_env=observe_python_env(),
    )
    return plan(experiment=trial, source=source, env=environment)


def prediction_stage(protocol: dict[str, Any], arm: str, seed: int,
                     selections: list[dict[str, Any]], selected_run: dict[str, Any],
                     model_sha256: str, selection_path: str, selection_sha256: str,
                     holdout_path: str, matrix_path: str, matrix_sha256: str,
                     protocol_path: str) -> Any:
    """Construct test capture only after the entire 15-fit selection is frozen.

    The controller must verify the source-bound selected_run/model digest before
    invoking this builder, and write per-trial selection plus holdout manifests.
    """
    require_complete_selections(protocol, selections)
    trial_id = f"{arm}_seed{seed}"
    chosen = [s for s in selections if s["trial_id"] == trial_id]
    if len(chosen) != 1 or chosen[0]["model_sha256"] != model_sha256:
        raise ValueError("Model does not match its frozen matrix selection.")
    from viper.authoring import input, stage
    from viper.outputs import StageOutputs, output
    from csts_pilot.baseline_models import ScoreConfig
    from csts_pilot.baseline_stages import capture_predictions
    from csts_pilot.convergence_run import artifact_source
    from jep_pilot.loaders import load_json

    model = protocol["model"]
    config = ScoreConfig.model_validate({
        "kind": "lora", "model_id": model["id"], "revision": model["revision"],
        "max_length": model["max_length"], "embedding_dimension": model["width"],
        "encode_batch_size": 4, "device": "cuda", "prompt_template": PROMPTS[arm],
        "expected_seed": seed, "expected_trial_id": trial_id,
        "matrix_sha256": matrix_sha256, "protocol_sha256": digest_object(protocol),
        "model_sha256": model_sha256, "selection_sha256": selection_sha256,
        "test_sha256": protocol["splits"]["test"]["sha256"],
    })
    return stage(capture_predictions, stage_id="capture", config=config, inputs=(
        input("test", path=protocol["splits"]["test"]["path"], data_role="eval"),
        input("holdout", path=holdout_path, data_role="eval"),
        input("selection", path=selection_path, data_role="training"),
        input("matrix", path=matrix_path, data_role="training"),
        input("protocol", path=protocol_path, data_role="training"),
        input("model", source=artifact_source(selected_run, "train", "model")),
    ), outputs=StageOutputs(
        predictions=output(path="predictions.json", loader=load_json, data_role="eval"),
        timing=output(path="timing.json", loader=load_json, data_role="eval"),
    ), reuse="never")
