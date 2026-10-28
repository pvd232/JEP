"""Check native CPU transport using random 5D fixtures, never model accuracy."""

import importlib.util
import os
import time
import uuid
from pathlib import Path
from typing import Any

import torch
from viper import execution
from viper.authoring import experiment, input, plan, replicate, stage, variant
from viper.config import BuildConfig
from viper.metrics import max as maximize
from viper.metrics import measure
from viper.outputs import EvalOutputs, StageOutputs, TrainOutputs, output
from viper.references import GitFileRef
from viper.repository import read_source
from viper.runtime import CPUComputeSpec, LocalEnvSpec, observe_python_env

from csts_pilot.convergence import (
    CheckpointConfig,
    file_sha256,
    promote_checkpoint,
    training_objective,
    validation_mse,
    validation_spearman,
    write_json,
)
from csts_pilot.convergence_run import artifact_path
from csts_pilot.evidence_attention_run import stored_source
from csts_pilot.evidence_readout_progress import initialize as initialize_progress
from csts_pilot.evidence_readout_stages import (
    ReadoutEvaluationConfig,
    evaluate_readout,
    fit_readout,
    readout_evaluation_metric,
)
from jep_pilot.loaders import load_json, load_model, load_state
from jep_pilot.stages import publish_evaluation_inputs


def main() -> None:
    """Seal caches, fit all seed pairs, freeze selection, and evaluate on CPU."""
    root = Path(__file__).resolve().parents[1]
    os.chdir(root)

    def relative(path: Path) -> str:
        return path.relative_to(root).as_posix()

    torch.set_num_threads(1)
    spec = importlib.util.spec_from_file_location(
        "readout_fixture", root / "tests/test_csts_evidence_readout.py"
    )
    assert spec is not None and spec.loader is not None
    fixture = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(fixture)
    source = read_source(root)
    environment = observe_python_env()
    attempt = uuid.uuid4().hex[:8]
    directory = root / "qwen_evidence_results" / f"readout_native_smoke_{attempt}"
    directory.mkdir(parents=True)
    progress_path = directory / "progress.md"
    initialize_progress(progress_path, source.commit, "CPU fixture")
    records = []

    def execute(label, configured, seed=7):
        trial = experiment(
            experiment_id=f"csts_readout_smoke_{source.commit[:8]}_{attempt}_{label}",
            variants=(
                variant(
                    label,
                    stages=(configured,),
                    estimator=next(iter(configured.outputs.values())),
                ),
            ),
            replicates=(replicate(seed=seed),),
        )
        started = time.monotonic()
        result = execution.run(
            plan(
                experiment=trial,
                source=source,
                env=LocalEnvSpec(
                    compute=CPUComputeSpec(),
                    lockfile=GitFileRef(
                        repository=source.repository,
                        commit=source.commit,
                        path="tranche2_requirements.txt",
                    ),
                    python_env=environment,
                ),
            ),
            timeout_seconds=600,
            trusted_source_repositories=frozenset({str(source.repository)}),
        )
        record = {
            "name": label,
            "status": result.status,
            "path": str(result.path),
            "reference": result.reference.model_dump(mode="json"),
            "seconds": time.monotonic() - started,
        }
        records.append(record)
        write_json(
            directory / "receipt.json",
            {
                "source_commit": source.commit,
                "scope": "Random 5D native CPU transport fixture, not model accuracy.",
                "runs": records,
            },
        )
        print("NATIVE_SMOKE_STAGE", label, result.status, str(result.path), flush=True)
        if result.status != "succeeded":
            raise RuntimeError(label)
        return record

    rows = {}
    caches = {}
    for split in ("training", "validation"):
        cache, items = fixture.fixture(split)
        rows[split] = items
        write_json(directory / f"{split}.json", items)
        torch.save(cache, directory / f"{split}.pt")
        caches[split] = execute(
            f"publish_{split}",
            stage(
                promote_checkpoint,
                stage_id="publish",
                config=CheckpointConfig(
                    model_sha256=file_sha256(directory / f"{split}.pt")
                ),
                inputs=(
                    input(
                        "checkpoint",
                        path=relative(directory / f"{split}.pt"),
                        data_role="training",
                    ),
                ),
                outputs=StageOutputs(
                    model=output(
                        path="model.pt", loader=load_model, data_role="training"
                    )
                ),
                reuse="never",
            ),
        )

    metrics = tuple(
        measure(m) for m in (training_objective, validation_mse, validation_spearman)
    )
    fitted = {}
    for seed in (7, 8, 9):
        cfg = fixture.config().model_copy(
            update={
                "seed": seed,
                "progress_path": str(progress_path),
                "training_sha256": file_sha256(directory / "training.json"),
                "validation_sha256": file_sha256(directory / "validation.json"),
                "training_cache_sha256": file_sha256(directory / "training.pt"),
                "validation_cache_sha256": file_sha256(directory / "validation.pt"),
            }
        )
        bindings: list[Any] = [
            input(s, path=relative(directory / f"{s}.json"), data_role="training")
            for s in ("training", "validation")
        ]
        bindings.extend(
            input(
                f"{s}_cache",
                source=stored_source(caches[s], "publish", "model", f"{s}_cache"),
            )
            for s in ("training", "validation")
        )
        fitted[str(seed)] = execute(
            f"fit_{seed}",
            stage(
                fit_readout,
                stage_id="fit",
                config=cfg,
                inputs=tuple(bindings),
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
                    validation_predictions=output(
                        path="predictions.json", loader=load_json, data_role="training"
                    ),
                ),
                metrics=metrics,
                objective=maximize(metrics[-1]),
                reuse="never",
            ),
            seed=seed,
        )

    digests = {
        s: file_sha256(artifact_path(r, "fit", "model", "model.pt"))
        for s, r in fitted.items()
    }
    selection = directory / "selection.json"
    write_json(
        selection,
        {
            "status": "checkpoints_frozen",
            "test_scores_used_for_selection": False,
            "models": {s: {"sha256": h} for s, h in digests.items()},
        },
    )
    selection_sha = file_sha256(selection)
    for split in ("test", "interventions"):
        cache, items = fixture.fixture(split)
        cache["selection_sha256"] = selection_sha
        if split == "interventions":
            for item, edit in zip(
                items, ("base", "irrelevant", "relevant", "missing"), strict=True
            ):
                item.update(
                    case="fixture",
                    edit=edit,
                    evidence_quote="" if edit == "missing" else "red",
                )
        rows[split] = items
        write_json(directory / f"{split}.json", items)
        torch.save(cache, directory / f"{split}.pt")
        caches[split] = execute(
            f"publish_{split}",
            stage(
                promote_checkpoint,
                stage_id="publish",
                config=CheckpointConfig(
                    model_sha256=file_sha256(directory / f"{split}.pt")
                ),
                inputs=(
                    input(
                        "checkpoint",
                        path=relative(directory / f"{split}.pt"),
                        data_role="eval",
                    ),
                ),
                outputs=StageOutputs(
                    model=output(path="model.pt", loader=load_model, data_role="eval")
                ),
                reuse="never",
            ),
        )

    write_json(directory / "holdout.json", list(range(len(rows["test"]))))
    published = execute(
        "publish_evaluation",
        stage(
            publish_evaluation_inputs,
            stage_id="publish",
            config=BuildConfig(),
            inputs=(
                input("test", path=relative(directory / "test.json"), data_role="eval"),
                input(
                    "holdout",
                    path=relative(directory / "holdout.json"),
                    data_role="eval",
                ),
            ),
            outputs=StageOutputs(
                test=output(path="test.json", loader=load_json, data_role="eval"),
                holdout=output(path="holdout.json", loader=load_json, data_role="eval"),
            ),
            reuse="never",
        ),
    )
    bindings = [
        input("selection", path=relative(selection), data_role="training"),
        input(
            "test", source=stored_source(published, "publish", "test", "test", "eval")
        ),
        input(
            "holdout",
            source=stored_source(published, "publish", "holdout", "holdout", "eval"),
        ),
        input(
            "cache",
            source=stored_source(caches["test"], "publish", "model", "cache", "eval"),
        ),
        input(
            "intervention_rows",
            path=relative(directory / "interventions.json"),
            data_role="eval",
        ),
        input(
            "intervention_cache",
            source=stored_source(
                caches["interventions"],
                "publish",
                "model",
                "intervention_cache",
                "eval",
            ),
        ),
    ]
    for i, (seed, r) in enumerate(fitted.items()):
        binding = "model" if i == 0 else f"model_{seed}"
        bindings.append(
            input(binding, source=stored_source(r, "fit", "model", binding))
        )
    cohorts = directory / "cohorts.json"
    write_json(
        cohorts,
        {
            "colour_regex": "color",
            "splits": {"test": {"condition_families": {"car color": "appearance"}}},
        },
    )
    bindings.extend(
        (
            input(
                "ratings_cache",
                source=stored_source(
                    caches["test"], "publish", "model", "ratings_cache", "eval"
                ),
            ),
            input("cohorts", path=relative(cohorts), data_role="eval"),
        )
    )
    evaluated_metric = readout_evaluation_metric()
    final = execute(
        "evaluate",
        stage(
            evaluate_readout,
            stage_id="evaluate",
            eval_id="csts_evidence_readout_smoke",
            config=ReadoutEvaluationConfig(
                device="cpu",
                rows_sha256=file_sha256(directory / "test.json"),
                cache_sha256=file_sha256(directory / "test.pt"),
                intervention_rows_sha256=file_sha256(directory / "interventions.json"),
                intervention_cache_sha256=file_sha256(directory / "interventions.pt"),
                model_sha256=digests,
                selection_sha256=selection_sha,
                bootstrap_draws=40,
                ratings_cache_sha256=file_sha256(directory / "test.pt"),
                cohorts_sha256=file_sha256(cohorts),
            ),
            inputs=tuple(bindings),
            outputs=EvalOutputs(
                report=output(path="report.json", loader=load_json, data_role="eval"),
                predictions=output(
                    path="predictions.json", loader=load_json, data_role="eval"
                ),
            ),
            split_inputs=("holdout",),
            metrics=(evaluated_metric,),
            objective=maximize(evaluated_metric),
            reuse="never",
        ),
    )
    report = load_json(artifact_path(final, "evaluate", "report", "report.json"))
    assert set(report["results"]) == {"A_parent", "R_ratings_parent", "7", "8", "9"}
    assert report["primary_C_minus_B"]["group_bootstrap_95"]["defined_draws"] > 0
    assert set(report["contrasts"]) == {
        "C_minus_B",
        "E_minus_D",
        "D_minus_B",
        "E_minus_C",
        "interaction",
    }
    assert all(
        set(report["results"][s])
        == {"ratings", "evidence", "ratings_comparison", "evidence_comparison"}
        for s in ("7", "8", "9")
    )
    write_json(
        directory / "receipt.json",
        {
            "status": "passed",
            "source_commit": source.commit,
            "scope": "Random 5D native CPU transport fixture, not model accuracy.",
            "runs": records,
        },
    )
    print("NATIVE_SMOKE_PASSED", directory / "receipt.json", flush=True)


if __name__ == "__main__":
    main()
