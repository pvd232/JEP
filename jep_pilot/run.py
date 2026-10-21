"""Declare matched VIPER plans for the joint-training diagnostic."""

import argparse
import json

from viper import api, execution
from viper.authoring import experiment, input, plan, replicate, stage, variant
from viper.metrics import MetricDependency, measure, min
from viper.outputs import EvalOutputs, TrainOutputs, output
from viper.references import GitFileRef
from viper.repository import read_source, resolve_root
from viper.runtime import (
    CPUComputeSpec,
    CUDAComputeSpec,
    LocalEnvSpec,
    observe_python_env,
)

from jep_pilot.stages import (
    PilotConfig,
    evaluate,
    evaluation_mse,
    evaluation_spearman,
    fit,
    load_json,
    load_model,
    load_state,
    training_mse,
)


def main() -> None:
    """Execute and verify every requested arm without selecting on test results."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--device", choices=["cpu", "cuda"], default="cpu")
    parser.add_argument("--mode", choices=["tiny", "pretrained"], default="tiny")
    parser.add_argument("--revision", default="")
    parser.add_argument("--steps", type=int, default=8)
    parser.add_argument("--seed", type=int, default=7)
    parser.add_argument("--annotation-weight", type=float, default=0.2)
    args = parser.parse_args()
    root = resolve_root()
    source = read_source(root)
    train_metric = measure(training_mse)
    dependency = (
        MetricDependency(source="artifact", name="predictions", data_role="eval"),
    )
    mse = measure(evaluation_mse, dependencies=dependency)
    spearman = measure(evaluation_spearman, dependencies=dependency)
    variants = []
    for name, weight, shuffle in [
        ("ratings", 0.0, False),
        ("joint", args.annotation_weight, False),
        ("shuffled", args.annotation_weight, True),
    ]:
        training = stage(
            fit,
            stage_id="train",
            config=PilotConfig(
                mode=args.mode,
                revision=args.revision,
                steps=args.steps,
                seed=args.seed,
                annotation_weight=weight,
                shuffle_annotations=shuffle,
                device=args.device,
            ),
            inputs=(
                input("dataset", path="pilot_data/train.json", data_role="training"),
            ),
            outputs=TrainOutputs(
                model=output(path="model.pt", loader=load_model, data_role="training"),
                resume_state=output(
                    path="resume.pt", loader=load_state, data_role="training"
                ),
                trace=output(path="trace.json", loader=load_json, data_role="training"),
            ),
            metrics=(train_metric,),
            objective=min(train_metric),
            reuse="never",
        )
        evaluation = stage(
            evaluate,
            stage_id="eval",
            eval_id="synthetic_holdout",
            inputs=(
                training.outputs["model"],
                input("test", path="pilot_data/test.json", data_role="eval"),
                input("holdout", path="pilot_data/test_indices.json", data_role="eval"),
            ),
            split_inputs=("holdout",),
            outputs=EvalOutputs(
                predictions=output(
                    path="predictions.json", loader=load_json, data_role="eval"
                )
            ),
            metrics=(mse, spearman),
            objective=min(mse),
            reuse="never",
        )
        variants.append(
            variant(
                name, stages=(training, evaluation), estimator=training.outputs["model"]
            )
        )
    study = experiment(
        experiment_id="joint_annotation_diagnostic",
        variants=tuple(variants),
        replicates=(replicate(seed=args.seed),),
    )
    compute = (
        CUDAComputeSpec(model="NVIDIA L4", count=1)
        if args.device == "cuda"
        else CPUComputeSpec()
    )
    environment = LocalEnvSpec(
        compute=compute,
        lockfile=GitFileRef(
            repository=source.repository,
            commit=source.commit,
            path="pilot_requirements.txt",
        ),
        python_env=observe_python_env(),
    )
    outcomes = []
    for name in ("ratings", "joint", "shuffled"):
        draft = plan(experiment=study, variant=name, source=source, env=environment)
        resolved = execution.run(draft)
        verified = api.verify_run(
            api.VerifyRunRequest(
                root=root,
                path=resolved.path,
                trusted_source_repositories=frozenset({str(source.repository)}),
            )
        )
        outcome = {
            "arm": name,
            "status": resolved.status,
            "result": str(resolved.path),
            "verified_measurements": verified.measurement_count,
        }
        outcomes.append(outcome)
        print(json.dumps(outcome), flush=True)
    (root / "pilot_summary.json").write_text(
        json.dumps(
            {
                "mode": args.mode,
                "device": args.device,
                "source_commit": source.commit,
                "synthetic": True,
                "expert_labels": False,
                "runs": outcomes,
            },
            indent=2,
        )
        + "\n"
    )


if __name__ == "__main__":
    main()
