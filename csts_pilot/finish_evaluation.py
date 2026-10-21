"""Finish the reserved evaluation using the existing selected checkpoints."""

import argparse
import shutil
from pathlib import Path

import numpy as np
from viper import execution
from viper.artifacts import StageArtifactRef
from viper.authoring import (
    experiment,
    input,
    plan,
    replicate,
    run_artifact,
    stage,
    variant,
)
from viper.cloud import ViperCloudDestination
from viper.config import EvalConfig
from viper.metrics import FloatComparator, MetricDependency, measure
from viper.metrics import min as minimize
from viper.outputs import EvalOutputs, output
from viper.references import GitFileRef, ResolvedRunRef
from viper.repository import read_source, resolve_root
from viper.runtime import CUDAComputeSpec, LocalEnvSpec, observe_python_env

from csts_pilot.diagnostics import summarize
from csts_pilot.training import evaluate, write_json
from jep_pilot.loaders import load_json
from jep_pilot.metrics import evaluation_mse, evaluation_spearman


def main() -> None:
    """Promote frozen training runs and evaluate six models in one native plan."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--baseline-root", type=Path, required=True)
    args = parser.parse_args()
    baseline = args.baseline_root
    result_dir = baseline / "csts_results"
    summary = load_json(result_dir / "summary.json")
    root = resolve_root()
    source = read_source(root)
    if summary["source_commit"] != "344207017dc36a4fe243fa15ae84bcf00bc6f165":
        raise RuntimeError("Unexpected training source.")
    summary["evaluation_source_commit"] = source.commit
    summary["status"] = "promoting"
    write_json(result_dir / "summary.json", summary)
    # Original frozen plans retain local publication. Promotion adds cloud graphs.
    marker = baseline / "viper.toml"
    if "[viper_cloud]" not in marker.read_text():
        with marker.open("a") as stream:
            stream.write(
                '\n[viper_cloud]\nprovider = "gcs"\nbucket = "mantra-mlfg-prod-uscentral1-8e7a"\nprefix = "viper"\n'
            )
    destination = ViperCloudDestination(owner="pvd232", workspace="jep_csts_20261021")
    promoted_path = result_dir / "promoted_runs.json"
    promoted = load_json(promoted_path) if promoted_path.exists() else {}
    for run in summary["runs"]:
        name = run["name"]
        if name in promoted:
            continue
        reference = execution.promote_run_to_cloud(
            baseline, Path(run["path"]), destination
        )
        promoted[name] = reference.model_dump(mode="json")
        write_json(promoted_path, promoted)
        print(f"Promoted {name}", flush=True)
    published = ResolvedRunRef.model_validate(promoted["publish_evaluation"])
    test = run_artifact(
        published,
        StageArtifactRef(stage_id="publish", artifact_name="test"),
        path="inputs/evaluation.json",
        data_role="eval",
    )
    indices = run_artifact(
        published,
        StageArtifactRef(stage_id="publish", artifact_name="holdout"),
        path="inputs/indices.json",
        data_role="eval",
    )
    selection = load_json(result_dir / "selection.json")
    metrics_dependencies = (
        MetricDependency(source="artifact", name="predictions", data_role="eval"),
    )
    comparator = FloatComparator(mode="absolute", tolerance=1e-12)
    mse = measure(
        evaluation_mse, dependencies=metrics_dependencies, comparator=comparator
    )
    correlation = measure(
        evaluation_spearman, dependencies=metrics_dependencies, comparator=comparator
    )
    stages = []
    for arm in ("conditioned", "without_question"):
        rate_tag = f"{selection[arm]['encoder_learning_rate']:.0e}".replace("-", "_")
        for seed in (7, 8, 9):
            name = f"{arm}_lr{rate_tag}_seed7" if seed == 7 else f"{arm}_seed{seed}"
            reference = ResolvedRunRef.model_validate(promoted[name])
            model = run_artifact(
                reference,
                StageArtifactRef(stage_id="train", artifact_name="model"),
                path=f"inputs/{name}.pt",
                data_role="training",
            )
            stage_id = f"{arm}_seed{seed}"
            evaluation = stage(
                evaluate,
                stage_id=stage_id,
                eval_id=stage_id,
                config=EvalConfig(),
                inputs=(
                    input("model", source=model),
                    input("test", source=test),
                    input("holdout", source=indices),
                ),
                split_inputs=("holdout",),
                outputs=EvalOutputs(
                    predictions=output(
                        path="predictions.json", loader=load_json, data_role="eval"
                    )
                ),
                metrics=(mse, correlation),
                objective=minimize(mse),
                reuse="never",
            )
            stages.append((arm, seed, evaluation))
    env = LocalEnvSpec(
        compute=CUDAComputeSpec(model="NVIDIA L4", count=1),
        lockfile=GitFileRef(
            repository=source.repository,
            commit=source.commit,
            path="pilot_requirements.txt",
        ),
        python_env=observe_python_env(),
    )
    study = experiment(
        experiment_id=f"csts_finish_{source.commit[:7]}",
        variants=(
            variant(
                "selected_models",
                stages=tuple(row[2] for row in stages),
                estimator=stages[0][2].outputs["predictions"],
            ),
        ),
        replicates=(replicate(seed=7),),
    )
    summary["status"] = "evaluating"
    write_json(result_dir / "summary.json", summary)
    result = execution.run(
        plan(experiment=study, source=source, env=env),
        timeout_seconds=7200,
        trusted_source_repositories=frozenset({str(source.repository)}),
    )
    summary["evaluation"] = []
    for arm, seed, definition in stages:
        path = (
            Path(result.path).parent
            / f"artifacts/{definition.stage_id}/predictions/predictions.json"
        )
        rows = load_json(path)
        summary["evaluation"].append(
            {"arm": arm, "seed": seed, "metrics": summarize(rows)}
        )
        shutil.copyfile(path, result_dir / f"{arm}_seed{seed}_predictions.json")
    mean = float(
        np.mean([row["target"] for row in load_json(baseline / "csts_data/train.json")])
    )
    reference_rows = [
        dict(row, prediction=mean)
        for row in load_json(baseline / "csts_data/evaluation.json")
    ]
    summary["mean_predictor"] = {
        "prediction": mean,
        "metrics": summarize(reference_rows),
    }
    summary["evaluation_run"] = result.reference.model_dump(mode="json")
    summary["status"] = "complete"
    write_json(result_dir / "summary.json", summary)
    print("Reserved evaluation complete", flush=True)


if __name__ == "__main__":
    main()
