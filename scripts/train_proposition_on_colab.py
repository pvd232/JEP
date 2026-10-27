"""Train the proposition ratings phase from its sealed four-epoch checkpoint on Colab."""

import argparse
import json
from pathlib import Path

import torch
from viper import execution
from viper.authoring import experiment, input, plan, replicate, stage, variant
from viper.metrics import max as maximize
from viper.metrics import measure
from viper.references import GitFileRef
from viper.repository import read_source, resolve_root
from viper.runtime import CUDAComputeSpec, LocalEnvSpec, observe_python_env

from csts_pilot.convergence import (
    file_sha256,
    training_objective,
    validation_mse,
    validation_spearman,
    write_json,
)
from csts_pilot.evidence_run import evidence_training_outputs
from csts_pilot.proposition_evidence_run import phase_config
from csts_pilot.qwen_evidence import fit_qwen_evidence


def run(root: Path, inputs: Path) -> None:
    """Preserve the original phase boundary, examples, optimizer settings and patience."""
    settings = json.loads((inputs / "settings.json").read_text())
    parent = inputs / "parent_model.pt"
    parent_trace = json.loads((inputs / "parent_trace.json").read_text())
    saved = torch.load(parent, map_location="cpu", weights_only=True)
    if (
        saved["epoch"] != 4
        or parent_trace["completed_epoch"] != 4
        or parent_trace["stop_reason"] != "fixed_update_budget"
        or file_sha256(parent) != parent_trace["terminal_model_sha256"]
    ):
        raise ValueError("Migration requires the sealed terminal fourth writing epoch.")
    config = phase_config(
        settings, "evidence", "ratings", inputs / "prepared.json", parent
    )
    if (
        config.start_epoch != 0
        or config.patience != 1
        or not config.train_until_patience
    ):
        raise ValueError("Keep the original fresh ratings optimizer and patience one.")
    source = read_source(root)
    metrics = tuple(
        measure(metric)
        for metric in (training_objective, validation_mse, validation_spearman)
    )
    paths = {
        "training": inputs / "training.json",
        "validation": inputs / "validation.json",
        "prepared": inputs / "prepared.json",
        "parent_model": parent,
    }
    configured = stage(
        fit_qwen_evidence,
        stage_id="train",
        config=config,
        inputs=tuple(
            input(name, path=str(path.relative_to(root)), data_role="training")
            for name, path in paths.items()
        ),
        outputs=evidence_training_outputs(),
        metrics=metrics,
        objective=maximize(metrics[-1]),
        reuse="never",
    )
    trial = experiment(
        experiment_id=f"csts_colab_{source.commit[:8]}_evidence_ratings",
        variants=(
            variant(
                "evidence_ratings",
                stages=(configured,),
                estimator=configured.outputs["model"],
            ),
        ),
        replicates=(replicate(seed=config.seed),),
    )
    environment = LocalEnvSpec(
        compute=CUDAComputeSpec(model="NVIDIA A100-SXM4-40GB", count=1),
        lockfile=GitFileRef(
            repository=source.repository,
            commit=source.commit,
            path="tranche2_requirements.txt",
        ),
        python_env=observe_python_env(),
    )
    receipt = {
        "status": "running",
        "source_commit": source.commit,
        "experiment_id": trial.experiment_id,
        "hardware": "NVIDIA A100-SXM4-40GB",
        "parent_sha256": config.parent_sha256,
        "config": config.model_dump(mode="json"),
        "inputs": {name: file_sha256(path) for name, path in paths.items()},
        "transition": "Terminal four-epoch writing checkpoint; fresh ratings optimizer as in the original comparison.",
    }
    write_json(root / "migration_status.json", receipt)
    result = execution.run(
        plan(experiment=trial, source=source, env=environment),
        timeout_seconds=None,
        trusted_source_repositories=frozenset({str(source.repository)}),
    )
    record = {
        "name": "evidence_ratings",
        "status": result.status,
        "path": str(result.path),
        "reference": result.reference.model_dump(mode="json"),
        "hardware": receipt["hardware"],
    }
    write_json(root / "migration_result.json", record)
    write_json(
        root / "migration_status.json",
        {**receipt, "status": result.status, "run": record},
    )
    if result.status != "succeeded":
        raise RuntimeError(
            "Preserve the native Colab attempt and its saved checkpoints."
        )


def main() -> None:
    """Run only the explicitly requested proposition ratings phase."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--inputs", type=Path, default=Path("migration_inputs"))
    args = parser.parse_args()
    root = resolve_root()
    run(root, root / args.inputs)


if __name__ == "__main__":
    main()
