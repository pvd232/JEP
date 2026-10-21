"""Run answer annotation, sequential training and matched joint training."""

import argparse
from pathlib import Path
from typing import Any

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
from viper.config import EvalConfig
from viper.metrics import FloatComparator, MetricDependency, measure
from viper.metrics import min as minimize
from viper.outputs import EvalOutputs, StageOutputs, TrainOutputs, output
from viper.references import GitFileRef
from viper.repository import read_source, resolve_root
from viper.runtime import CUDAComputeSpec, LocalEnvSpec, observe_python_env

from csts_pilot.answers import AnswerConfig, annotate
from csts_pilot.diagnostics import summarize
from csts_pilot.joint import JointConfig, evaluate, fit
from csts_pilot.metrics import (
    development_answer_ce,
    development_mse,
    training_answer_ce,
)
from csts_pilot.training import write_json
from jep_pilot.loaders import load_answers, load_json, load_model, load_state
from jep_pilot.metrics import evaluation_mse, evaluation_spearman, training_mse
from jep_pilot.stages import publish_evaluation_inputs


def main() -> None:
    """Freeze all checkpoints before reading reserved similarity evaluation."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--annotation-limit", type=int)
    parser.add_argument("--annotation-offset", type=int, default=0)
    args = parser.parse_args()
    root = resolve_root()
    source = read_source(root)
    trusted = frozenset({str(source.repository)})
    env = LocalEnvSpec(
        compute=CUDAComputeSpec(model="NVIDIA L4", count=1),
        lockfile=GitFileRef(
            repository=source.repository,
            commit=source.commit,
            path="pilot_requirements.txt",
        ),
        python_env=observe_python_env(),
    )
    result_dir = root / "csts_results"
    result_dir.mkdir(exist_ok=True)
    summary: dict[str, Any] = {
        "source_commit": source.commit,
        "status": "annotating",
        "runs": [],
        "selected": {},
        "evaluation": [],
        "data_manifest": load_json(root / "csts_data/manifest.json"),
    }

    def execute(name: str, stages: tuple, estimator: Any, seed: int = 7) -> Any:
        study = experiment(
            experiment_id=f"csts_natural_20261021_{source.commit[:7]}_{name}",
            variants=(variant(name, stages=stages, estimator=estimator),),
            replicates=(replicate(seed=seed),),
        )
        result = execution.run(
            plan(experiment=study, source=source, env=env),
            timeout_seconds=14400,
            trusted_source_repositories=trusted,
        )
        if result.status != "succeeded":
            raise RuntimeError(f"Trial {name} failed: {result.path}")
        # execution.run already verifies the complete run graph.
        summary["runs"].append({"name": name, "path": str(result.path)})
        write_json(result_dir / "summary.json", summary)
        return result

    annotation = stage(
        annotate,
        stage_id="annotate",
        config=AnswerConfig(limit=args.annotation_limit, offset=args.annotation_offset),
        inputs=(
            input("training", path="csts_data/train.json", data_role="training"),
            input("development", path="csts_data/dev.json", data_role="training"),
        ),
        outputs=StageOutputs(
            answers=output(
                path="answers.jsonl", loader=load_answers, data_role="training"
            ),
            manifest=output(
                path="manifest.json", loader=load_json, data_role="training"
            ),
        ),
        reuse="never",
    )
    annotated = execute(
        "annotation_pilot" if args.annotation_limit else "annotations",
        (annotation,),
        annotation.outputs["answers"],
    )
    answer_ref = run_artifact(
        annotated.reference,
        StageArtifactRef(stage_id="annotate", artifact_name="answers"),
        path="inputs/answers.jsonl",
        data_role="training",
    )
    annotation_manifest = load_json(
        Path(annotated.path).parent / "artifacts/annotate/manifest/manifest.json"
    )
    summary["annotation"] = annotation_manifest
    if args.annotation_limit:
        summary["status"] = "annotation_pilot_complete"
        write_json(result_dir / "summary.json", summary)
        return
    if annotation_manifest["accepted_fraction"] < 0.5:
        raise RuntimeError(
            "Fewer than half of teacher answers passed the source-span check. Review annotations before training."
        )
    summary["status"] = "training"
    metrics = (
        measure(training_mse),
        measure(development_mse),
        measure(training_answer_ce),
        measure(development_answer_ce),
    )

    def train_run(name: str, config: JointConfig, initial: Any = None) -> Any:
        inputs = [
            input("training", path="csts_data/train.json", data_role="training"),
            input("development", path="csts_data/dev.json", data_role="training"),
            input("answers", source=answer_ref),
        ]
        if initial is not None:
            inputs.append(
                input(
                    "initial_model",
                    source=run_artifact(
                        initial.reference,
                        StageArtifactRef(stage_id="train", artifact_name="model"),
                        path="inputs/initial.pt",
                        data_role="training",
                    ),
                )
            )
        training = stage(
            fit,
            stage_id="train",
            config=config,
            inputs=tuple(inputs),
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
            metrics=metrics,
            objective=minimize(
                metrics[3] if config.objective == "answers" else metrics[1]
            ),
            reuse="never",
        )
        result = execute(name, (training,), training.outputs["model"], config.seed)
        trace = load_json(Path(result.path).parent / "artifacts/train/trace/trace.json")
        summary["runs"][-1].update(
            best_development_mse=trace["best_development_mse"],
            best_epoch=trace["best_epoch"],
        )
        write_json(result_dir / "summary.json", summary)
        return result

    selected: dict[str, list[tuple[int, Any]]] = {
        name: [] for name in ("ratings", "sequential", "joint", "shuffled")
    }
    selected["ratings"].append(
        (7, train_run("ratings_seed7", JointConfig(objective="ratings")))
    )
    pretrained = train_run("answers_seed7", JointConfig(objective="answers"))
    selected["sequential"].append(
        (7, train_run("sequential_seed7", JointConfig(objective="ratings"), pretrained))
    )
    candidates = []
    for weight in (0.05, 0.2):
        result = train_run(
            f"joint_w{str(weight).replace('.', 'p')}_seed7",
            JointConfig(annotation_weight=weight),
        )
        candidates.append((summary["runs"][-1]["best_development_mse"], weight, result))
    _, weight, chosen = min(candidates, key=lambda row: (row[0], row[1]))
    selected["joint"].append((7, chosen))
    summary["selected"]["annotation_weight"] = weight
    write_json(result_dir / "selection.json", summary["selected"])
    selected["shuffled"].append(
        (
            7,
            train_run(
                "shuffled_seed7",
                JointConfig(annotation_weight=weight, shuffle_answers=True),
            ),
        )
    )
    for seed in (8, 9):
        selected["ratings"].append(
            (
                seed,
                train_run(
                    f"ratings_seed{seed}", JointConfig(objective="ratings", seed=seed)
                ),
            )
        )
        pretrained = train_run(
            f"answers_seed{seed}", JointConfig(objective="answers", seed=seed)
        )
        selected["sequential"].append(
            (
                seed,
                train_run(
                    f"sequential_seed{seed}",
                    JointConfig(objective="ratings", seed=seed),
                    pretrained,
                ),
            )
        )
        selected["joint"].append(
            (
                seed,
                train_run(
                    f"joint_seed{seed}",
                    JointConfig(annotation_weight=weight, seed=seed),
                ),
            )
        )
        selected["shuffled"].append(
            (
                seed,
                train_run(
                    f"shuffled_seed{seed}",
                    JointConfig(
                        annotation_weight=weight, shuffle_answers=True, seed=seed
                    ),
                ),
            )
        )

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
    published = execute(
        "publish_evaluation", (preparation,), preparation.outputs["test"]
    )
    eval_input = run_artifact(
        published.reference,
        StageArtifactRef(stage_id="publish", artifact_name="test"),
        path="inputs/evaluation.json",
        data_role="eval",
    )
    indices = run_artifact(
        published.reference,
        StageArtifactRef(stage_id="publish", artifact_name="holdout"),
        path="inputs/indices.json",
        data_role="eval",
    )
    dependencies = (
        MetricDependency(source="artifact", name="predictions", data_role="eval"),
    )
    comparator = FloatComparator(mode="absolute", tolerance=1e-12)
    mse = measure(evaluation_mse, dependencies=dependencies, comparator=comparator)
    correlation = measure(
        evaluation_spearman, dependencies=dependencies, comparator=comparator
    )
    summary["status"] = "evaluating"
    for arm, runs in selected.items():
        for seed, trained in runs:
            model = run_artifact(
                trained.reference,
                StageArtifactRef(stage_id="train", artifact_name="model"),
                path="inputs/model.pt",
                data_role="training",
            )
            evaluation = stage(
                evaluate,
                stage_id="eval",
                eval_id="joint_csts",
                config=EvalConfig(),
                inputs=(
                    input("model", source=model),
                    input("test", source=eval_input),
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
            result = execute(
                f"evaluate_{arm}_seed{seed}",
                (evaluation,),
                evaluation.outputs["predictions"],
                seed,
            )
            rows = load_json(
                Path(result.path).parent / "artifacts/eval/predictions/predictions.json"
            )
            summary["evaluation"].append(
                {
                    "arm": arm,
                    "seed": seed,
                    "diagnostics": summarize(rows),
                    "path": str(result.path),
                }
            )
            write_json(result_dir / "summary.json", summary)
    summary["status"] = "complete"
    write_json(result_dir / "summary.json", summary)


if __name__ == "__main__":
    main()
