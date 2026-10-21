"""Run the cached three-format screen with native VIPER provenance."""

import argparse
import hashlib
import shutil
import tempfile
import uuid
from pathlib import Path
from typing import Any, Literal

import torch
from transformers import AutoTokenizer
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
from viper.config import BuildConfig, EvalConfig
from viper.metrics import FloatComparator, MetricDependency, measure
from viper.metrics import max as maximize
from viper.metrics import min as minimize
from viper.outputs import EvalOutputs, StageOutputs, TrainOutputs, output
from viper.references import GitFileRef
from viper.repository import read_source, resolve_root
from viper.runtime import CUDAComputeSpec, LocalEnvSpec, observe_python_env
from viper.stages import StageContext, build

from csts_pilot.annotation_formats import FORMATS, prepare_targets
from csts_pilot.answers import answer_id
from csts_pilot.diagnostics import summarize
from csts_pilot.joint import AnswerEncoder, JointConfig, evaluate, fit
from csts_pilot.metrics import (
    development_answer_ce,
    development_mse,
    development_spearman,
    training_answer_ce,
)
from csts_pilot.training import mixed_precision, prepare_tokens, write_json
from jep_pilot.loaders import load_answers, load_json, load_model, load_state
from jep_pilot.metrics import evaluation_mse, evaluation_spearman, training_mse
from jep_pilot.stages import publish_evaluation_inputs


@build(config=BuildConfig)
def prepare(context: StageContext[BuildConfig]) -> None:
    """Derive all formats from one checked cache and publish an audit sample."""
    with tempfile.TemporaryDirectory(prefix="csts-formats-") as temporary:
        destination = Path(temporary) / "derived"
        manifest = prepare_targets(context.inputs["answers"], destination, 17334)
        if manifest["accepted"] != 11312:
            raise ValueError("The cache differs from the completed annotation cohort.")
        for style in FORMATS:
            shutil.copyfile(destination / f"{style}.jsonl", context.outputs[style])
        shutil.copyfile(destination / "manifest.json", context.outputs["manifest"])
    accepted = [
        row for row in load_answers(context.inputs["answers"]).values() if row["valid"]
    ]
    accepted.sort(
        key=lambda row: hashlib.sha256(
            ("format-audit:" + row["id"]).encode()
        ).hexdigest()
    )
    write_json(context.outputs["audit"], accepted[:100])


class GenerationConfig(BuildConfig):
    """Bound deterministic development generation without changing selection."""

    count: int = 32
    max_new_tokens: int = 192


@build(config=GenerationConfig)
def generate_sample(context: StageContext[GenerationConfig]) -> None:
    """Save a common teacher-agreement sample for independent semantic review."""
    saved = load_model(context.inputs["model"])
    config = JointConfig.model_validate(saved["config"])
    answers = load_answers(context.inputs["answers"])
    unique = {}
    for row in load_json(context.inputs["development"]):
        for side in ("sentence1", "sentence2"):
            key = answer_id(row[side], row["condition"])
            if answers[key]["valid"]:
                unique[key] = answers[key]
    keys = sorted(
        unique,
        key=lambda key: hashlib.sha256(
            ("format-generation:" + key).encode()
        ).hexdigest(),
    )[: context.config.count]
    records = [unique[key] for key in keys]
    rows = [
        {
            "sentence1": row["passage"],
            "sentence2": row["passage"],
            "condition": row["condition"],
        }
        for row in records
    ]
    tokenizer = AutoTokenizer.from_pretrained(
        config.model_id, revision=config.revision, use_fast=True
    )
    model = AnswerEncoder(config).to(config.device)
    model.load_state_dict(saved["state"])
    model.eval()
    tokens = prepare_tokens(rows, config, tokenizer)
    generated = []
    with torch.no_grad():
        for start in range(0, len(rows), 8):
            selected = {
                key: value[start : min(start + 8, len(rows))]
                for key, value in tokens.items()
                if key != "pool_mask"
            }
            with mixed_precision(config):
                result = model.t5.generate(
                    **selected,
                    do_sample=False,
                    max_new_tokens=context.config.max_new_tokens,
                )
            generated.extend(tokenizer.batch_decode(result, skip_special_tokens=True))
    write_json(
        context.outputs["generations"],
        [
            {
                "id": row["id"],
                "passage": row["passage"],
                "condition": row["condition"],
                "target": row["target"],
                "attribute": row["attribute"],
                "expected": row["answer"],
                "generated": text,
            }
            for row, text in zip(records, generated, strict=True)
        ],
    )


def main() -> None:
    """Freeze all format checkpoints before any follow-up benchmark evaluation."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prepare-only", action="store_true")
    parser.add_argument("--audited-source-sha")
    parser.add_argument("--annotation-epochs", type=int, default=6)
    parser.add_argument("--rating-epochs", type=int, default=8)
    args = parser.parse_args()
    if min(args.annotation_epochs, args.rating_epochs) < 1:
        raise ValueError("Both stages require a positive common epoch budget.")
    root = resolve_root()
    result_dir = root / "format_results"
    result_dir.mkdir(exist_ok=True)
    summary_path = result_dir / "summary.json"
    if summary_path.exists() and load_json(summary_path)["status"] != "prepared":
        raise RuntimeError(
            "Prior training state exists; inspect it before any restart."
        )
    source = read_source(root)
    attempt = uuid.uuid4().hex[:8]
    env = LocalEnvSpec(
        compute=CUDAComputeSpec(model="NVIDIA L4", count=1),
        lockfile=GitFileRef(
            repository=source.repository,
            commit=source.commit,
            path="pilot_requirements.txt",
        ),
        python_env=observe_python_env(),
    )
    summary: dict[str, Any] = {
        "source_commit": source.commit,
        "status": "preparing",
        "runs": [],
        "evaluation": [],
        "settings": vars(args),
        "data_manifest": load_json(root / "csts_data/manifest.json"),
    }

    def execute(name: str, configured_stage: Any, estimator: Any) -> Any:
        summary["current_stage"] = name
        write_json(summary_path, summary)
        trial = experiment(
            experiment_id=f"csts_formats_20261021_{source.commit[:7]}_{attempt}_{name}",
            variants=(variant(name, stages=(configured_stage,), estimator=estimator),),
            replicates=(replicate(seed=7),),
        )
        result = execution.run(
            plan(experiment=trial, source=source, env=env),
            timeout_seconds=21600,
            trusted_source_repositories=frozenset({str(source.repository)}),
        )
        summary["runs"].append(
            {"name": name, "path": str(result.path), "status": result.status}
        )
        if result.status != "succeeded":
            summary["status"] = "failed"
            write_json(summary_path, summary)
            raise RuntimeError(f"Native VIPER stage failed: {name}: {result.path}")
        write_json(summary_path, summary)
        return result

    def artifact(
        result: Any,
        stage_id: str,
        name: str,
        role: Literal["training", "eval"] = "training",
    ) -> Any:
        return run_artifact(
            result.reference,
            StageArtifactRef(stage_id=stage_id, artifact_name=name),
            path=f"inputs/{name}",
            data_role=role,
        )

    preparation = stage(
        prepare,
        stage_id="prepare",
        inputs=(
            input(
                "answers", path="csts_data/answers_cached.jsonl", data_role="training"
            ),
        ),
        outputs=StageOutputs(
            **{
                **{
                    style: output(
                        path=f"{style}.jsonl", loader=load_answers, data_role="training"
                    )
                    for style in FORMATS
                },
                "manifest": output(
                    path="manifest.json", loader=load_json, data_role="training"
                ),
                "audit": output(
                    path="audit.json", loader=load_json, data_role="training"
                ),
            }
        ),
        reuse="never",
    )
    prepared = execute("prepare", preparation, preparation.outputs["manifest"])
    manifest = load_json(
        Path(prepared.path).parent / "artifacts/prepare/manifest/manifest.json"
    )
    summary["target_manifest"] = manifest
    summary["audit_path"] = str(
        Path(prepared.path).parent / "artifacts/prepare/audit/audit.json"
    )
    if args.prepare_only:
        summary["status"] = "prepared"
        write_json(summary_path, summary)
        return
    if args.audited_source_sha != manifest["source_sha256"]:
        summary["status"] = "prepared"
        write_json(summary_path, summary)
        raise ValueError(
            "Review the cached metadata audit and supply its exact source SHA before training."
        )
    summary["status"] = "training"
    selected = {}
    base_metrics = (
        measure(training_mse),
        measure(development_mse),
        measure(training_answer_ce),
        measure(development_answer_ce),
    )
    for style in FORMATS:
        answer_ref = artifact(prepared, "prepare", style)
        previous = None
        for objective, epochs in (
            ("answers", args.annotation_epochs),
            ("ratings", args.rating_epochs),
        ):
            config = JointConfig(
                objective=objective,
                seed=7,
                max_epochs=epochs,
                fixed_epoch_budget=True,
                checkpoint_metric="spearman" if objective == "ratings" else "mse",
            )
            inputs = [
                input("training", path="csts_data/train.json", data_role="training"),
                input("development", path="csts_data/dev.json", data_role="training"),
                input("answers", source=answer_ref),
            ]
            if previous is not None:
                inputs.append(
                    input("initial_model", source=artifact(previous, "train", "model"))
                )
            metrics = base_metrics + (
                (measure(development_spearman),) if objective == "ratings" else ()
            )
            training = stage(
                fit,
                stage_id="train",
                config=config,
                inputs=tuple(inputs),
                outputs=TrainOutputs(
                    model=output(
                        path="model.pt", loader=load_model, data_role="training"
                    ),
                    resume_state=output(
                        path="resume.pt", loader=load_state, data_role="training"
                    ),
                    trace=output(
                        path="trace.json", loader=load_json, data_role="training"
                    ),
                    development_predictions=output(
                        path="development_predictions.json",
                        loader=load_json,
                        data_role="training",
                    ),
                ),
                metrics=metrics,
                objective=maximize(metrics[-1])
                if objective == "ratings"
                else minimize(metrics[3]),
                reuse="never",
            )
            previous = execute(
                f"{style}_{objective}", training, training.outputs["model"]
            )
        selected[style] = (previous, answer_ref)
    summary["status"] = "checkpoints_frozen"
    summary["selected_models"] = {
        style: str(model.path) for style, (model, _) in selected.items()
    }
    write_json(result_dir / "selection.json", summary["selected_models"])
    write_json(summary_path, summary)

    publication = stage(
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
    published = execute("publish_evaluation", publication, publication.outputs["test"])
    dependencies = (
        MetricDependency(source="artifact", name="predictions", data_role="eval"),
    )
    comparator = FloatComparator(mode="absolute", tolerance=1e-12)
    mse = measure(evaluation_mse, dependencies=dependencies, comparator=comparator)
    rho = measure(evaluation_spearman, dependencies=dependencies, comparator=comparator)
    summary["status"] = "evaluating"
    for style, (trained, answer_ref) in selected.items():
        model_ref = artifact(trained, "train", "model")
        evaluation = stage(
            evaluate,
            stage_id="eval",
            eval_id="annotation_format_csts",
            config=EvalConfig(),
            inputs=(
                input("model", source=model_ref),
                input("test", source=artifact(published, "publish", "test", "eval")),
                input(
                    "holdout", source=artifact(published, "publish", "holdout", "eval")
                ),
            ),
            split_inputs=("holdout",),
            outputs=EvalOutputs(
                predictions=output(
                    path="predictions.json", loader=load_json, data_role="eval"
                )
            ),
            metrics=(mse, rho),
            objective=maximize(rho),
            reuse="never",
        )
        evaluated = execute(
            f"evaluate_{style}", evaluation, evaluation.outputs["predictions"]
        )
        scored = load_json(
            Path(evaluated.path).parent / "artifacts/eval/predictions/predictions.json"
        )
        summary["evaluation"].append(
            {
                "arm": style,
                "seed": 7,
                "diagnostics": summarize(scored),
                "path": str(evaluated.path),
            }
        )
        generation = stage(
            generate_sample,
            stage_id="generate",
            config=GenerationConfig(),
            inputs=(
                input("model", source=model_ref),
                input("answers", source=answer_ref),
                input("development", path="csts_data/dev.json", data_role="training"),
            ),
            outputs=StageOutputs(
                generations=output(
                    path="generations.json", loader=load_json, data_role="training"
                )
            ),
            reuse="never",
        )
        execute(f"generate_{style}", generation, generation.outputs["generations"])
    summary["status"] = "complete"
    summary["current_stage"] = None
    write_json(summary_path, summary)


if __name__ == "__main__":
    main()
