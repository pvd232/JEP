"""Run development trials, freeze settings and evaluate three matched seeds."""

import json
import shutil
from pathlib import Path
from typing import Any

import numpy as np
from viper import api, execution
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
from viper.metrics import FloatComparator, MetricDependency, measure
from viper.metrics import min as minimize
from viper.outputs import EvalOutputs, StageOutputs, TrainOutputs, output
from viper.references import GitFileRef
from viper.repository import read_source, resolve_root
from viper.runtime import CUDAComputeSpec, LocalEnvSpec, observe_python_env

from csts_pilot.diagnostics import summarize
from csts_pilot.metrics import development_mse
from csts_pilot.training import CstsConfig, evaluate, fit, write_json
from jep_pilot.loaders import load_json, load_model, load_state
from jep_pilot.metrics import evaluation_mse, evaluation_spearman, training_mse
from jep_pilot.stages import publish_evaluation_inputs


def trial_name(label: str, rate: float) -> str:
    """Encode a learning rate using VIPER's permitted identifier characters."""
    rate_tag = f"{rate:.0e}".replace("-", "_")
    return f"{label}_lr{rate_tag}_seed7"


def main() -> None:
    """Finish all development choices before reading final model scores."""
    root = resolve_root()
    source = read_source(root)
    environment = LocalEnvSpec(
        compute=CUDAComputeSpec(model="NVIDIA L4", count=1),
        lockfile=GitFileRef(
            repository=source.repository,
            commit=source.commit,
            path="pilot_requirements.txt",
        ),
        python_env=observe_python_env(),
    )
    trusted = frozenset({str(source.repository)})
    result_dir = root / "csts_results"
    result_dir.mkdir(exist_ok=True)
    summary: dict[str, Any] = {
        "source_commit": source.commit,
        "data_manifest": load_json(root / "csts_data/manifest.json"),
        "protocol": "CSTS_RUN.md",
        "status": "training",
        "runs": [],
        "selected": {},
        "evaluation": [],
    }

    def execute(name: str, stages: tuple, estimator: Any, seed: int = 7) -> Any:
        study = experiment(
            experiment_id=f"csts_natural_20261021_{source.commit[:7]}_{name}",
            variants=(variant(name, stages=stages, estimator=estimator),),
            replicates=(replicate(seed=seed),),
        )
        resolved = execution.run(
            plan(experiment=study, source=source, env=environment),
            timeout_seconds=7200,
            trusted_source_repositories=trusted,
        )
        if resolved.status != "succeeded":
            raise RuntimeError(f"Run {name} failed at {resolved.path}.")
        verified = api.verify_run(
            api.VerifyRunRequest(
                root=root,
                path=resolved.path,
                trusted_source_repositories=trusted,
            )
        )
        record = {
            "name": name,
            "path": str(resolved.path),
            "verified_measurements": verified.measurement_count,
        }
        summary["runs"].append(record)
        write_json(result_dir / "summary.json", summary)
        print(json.dumps(record), flush=True)
        return resolved

    train_metric = measure(training_mse)
    development_metric = measure(development_mse)

    def training_run(name: str, config: CstsConfig) -> Any:
        training = stage(
            fit,
            stage_id="train",
            config=config,
            inputs=(
                input("training", path="csts_data/train.json", data_role="training"),
                input("development", path="csts_data/dev.json", data_role="training"),
            ),
            outputs=TrainOutputs(
                model=output(path="model.pt", loader=load_model, data_role="training"),
                resume_state=output(
                    path="resume.pt", loader=load_state, data_role="training"
                ),
                trace=output(path="trace.json", loader=load_json, data_role="training"),
                development_predictions=output(
                    path="development_predictions.json",
                    loader=load_json,
                    data_role="training",
                ),
            ),
            metrics=(train_metric, development_metric),
            objective=minimize(development_metric),
            reuse="never",
        )
        resolved = execute(name, (training,), training.outputs["model"], config.seed)
        trace = load_json(
            Path(resolved.path).parent / "artifacts/train/trace/trace.json"
        )
        summary["runs"][-1]["best_development_mse"] = trace["best_development_mse"]
        summary["runs"][-1]["best_epoch"] = trace["best_epoch"]
        write_json(result_dir / "summary.json", summary)
        return resolved

    sanity = training_run(
        "fit_check", CstsConfig(fit_check=True, max_epochs=100, patience=100)
    )
    sanity_trace = load_json(
        Path(sanity.path).parent / "artifacts/train/trace/trace.json"
    )
    if not sanity_trace["fit_check_passed"]:
        raise RuntimeError(
            "The model failed the small-subset training check. Inspect its trace before a full run."
        )
    selected: dict[str, dict[str, Any]] = {}
    for condition, label in ((True, "conditioned"), (False, "without_question")):
        trials = []
        for rate in (1e-5, 3e-5):
            name = trial_name(label, rate)
            config = CstsConfig(condition=condition, encoder_learning_rate=rate)
            resolved = training_run(name, config)
            score = summary["runs"][-1]["best_development_mse"]
            trials.append((score, rate, resolved))
        _, rate, resolved = min(trials, key=lambda value: (value[0], value[1]))
        selected[label] = {"learning_rate": rate, "seed_runs": [(7, resolved)]}
        summary["selected"][label] = {
            "encoder_learning_rate": rate,
            "selection": "Minimum development MSE, seed 7. Lower LR breaks exact ties.",
        }
    write_json(result_dir / "selection.json", summary["selected"])
    for label, settings in selected.items():
        for seed in (8, 9):
            config = CstsConfig(
                condition=label == "conditioned",
                encoder_learning_rate=settings["learning_rate"],
                seed=seed,
            )
            resolved = training_run(f"{label}_seed{seed}", config)
            settings["seed_runs"].append((seed, resolved))

    # Publication and evaluation begin after all settings and checkpoints are fixed.
    preparation = stage(
        publish_evaluation_inputs,
        stage_id="publish",
        inputs=(
            input("test", path="csts_data/evaluation.json", data_role="eval"),
            input(
                "holdout", path="csts_data/evaluation_indices.json", data_role="eval"
            ),
        ),
        outputs=StageOutputs(
            test=output(path="evaluation.json", loader=load_json, data_role="eval"),
            holdout=output(path="indices.json", loader=load_json, data_role="eval"),
        ),
    )
    data_run = execute(
        "publish_evaluation", (preparation,), preparation.outputs["test"]
    )
    eval_input = run_artifact(
        data_run.reference,
        StageArtifactRef(stage_id="publish", artifact_name="test"),
        path="inputs/evaluation.json",
        data_role="eval",
    )
    indices = run_artifact(
        data_run.reference,
        StageArtifactRef(stage_id="publish", artifact_name="holdout"),
        path="inputs/indices.json",
        data_role="eval",
    )
    dependency = (
        MetricDependency(source="artifact", name="predictions", data_role="eval"),
    )
    comparator = FloatComparator(mode="absolute", tolerance=1e-12)
    mse = measure(evaluation_mse, dependencies=dependency, comparator=comparator)
    correlation = measure(
        evaluation_spearman, dependencies=dependency, comparator=comparator
    )
    summary["status"] = "evaluating"
    for label, settings in selected.items():
        for seed, training in settings["seed_runs"]:
            model = run_artifact(
                training.reference,
                StageArtifactRef(stage_id="train", artifact_name="model"),
                path="inputs/model.pt",
                data_role="training",
            )
            evaluation = stage(
                evaluate,
                stage_id="eval",
                eval_id="natural_csts",
                inputs=(
                    input("model", source=model),
                    input("evaluation", source=eval_input),
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
            resolved = execute(
                f"evaluate_{label}_seed{seed}",
                (evaluation,),
                evaluation.outputs["predictions"],
                seed,
            )
            path = (
                Path(resolved.path).parent
                / "artifacts/eval/predictions/predictions.json"
            )
            predictions = load_json(path)
            summary["evaluation"].append(
                {"arm": label, "seed": seed, "metrics": summarize(predictions)}
            )
            shutil.copyfile(path, result_dir / f"{label}_seed{seed}_predictions.json")
            write_json(result_dir / "summary.json", summary)
    mean = float(
        np.mean([row["target"] for row in load_json(root / "csts_data/train.json")])
    )
    reference = [
        dict(row, prediction=mean)
        for row in load_json(root / "csts_data/evaluation.json")
    ]
    summary["mean_predictor"] = {"prediction": mean, "metrics": summarize(reference)}
    summary["status"] = "complete"
    write_json(result_dir / "summary.json", summary)
    print(json.dumps(summary, indent=2), flush=True)


if __name__ == "__main__":
    main()
