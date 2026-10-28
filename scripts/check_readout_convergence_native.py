"""Exercise both convergence stages with random 5D CPU fixtures."""

import importlib.util
import os
import uuid
from pathlib import Path

import torch
from viper import execution
from viper.authoring import experiment, input, plan, replicate, stage, variant
from viper.metrics import max as maximize
from viper.metrics import measure
from viper.outputs import EvalOutputs, output
from viper.references import GitFileRef
from viper.repository import read_source
from viper.runtime import CPUComputeSpec, LocalEnvSpec, observe_python_env

from csts_pilot.convergence import (
    file_sha256,
    training_objective,
    validation_mse,
    validation_spearman,
    write_json,
)
from csts_pilot.convergence_run import artifact_path
from csts_pilot.evidence_attention_run import stored_source
from csts_pilot.evidence_readout_convergence import (
    ConvergedEvaluationConfig,
    ConvergedFitConfig,
    evaluate_converged_readouts,
    fit_converged_readouts,
    refit_evaluation_metric,
)
from csts_pilot.evidence_readout_convergence_run import fit_outputs
from jep_pilot.loaders import load_json


def main():
    root = Path(__file__).resolve().parents[1]
    os.chdir(root)
    torch.set_num_threads(1)
    spec = importlib.util.spec_from_file_location(
        "readout_fixture", root / "tests/test_csts_evidence_readout.py"
    )
    fixture = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(fixture)
    source, environment = read_source(root), observe_python_env()
    attempt = uuid.uuid4().hex[:8]
    directory = root / "qwen_evidence_results" / f"convergence_native_smoke_{attempt}"
    directory.mkdir(parents=True)
    progress_path = directory / "progress.md"
    progress_path.write_text(
        "# Random 5D CPU transport fixture\n\nScientific accuracy is measured in the separate A100 run.\n\n| UTC | Event | Seed | Step | Detail |\n| --- | --- | --- | --- | --- |\n"
    )
    receipt = {
        "source_commit": source.commit,
        "scope": "Random 5D CPU transport fixture",
        "runs": [],
    }

    def relative(path):
        return path.relative_to(root).as_posix()

    def execute(name, configured):
        trial = experiment(
            experiment_id=f"csts_refit_smoke_{source.commit[:8]}_{attempt}_{name}",
            variants=(
                variant(
                    name,
                    stages=(configured,),
                    estimator=next(iter(configured.outputs.values())),
                ),
            ),
            replicates=(replicate(seed=7),),
        )
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
            "name": name,
            "status": result.status,
            "path": str(result.path),
            "reference": result.reference.model_dump(mode="json"),
        }
        receipt["runs"].append(record)
        write_json(directory / "receipt.json", receipt)
        print("CONVERGENCE_SMOKE", name, result.status, flush=True)
        if result.status != "succeeded":
            raise RuntimeError(name)
        return record

    for split in ("training", "validation", "test", "interventions"):
        cache, rows = fixture.fixture(split)
        if split == "interventions":
            for row, edit in zip(
                rows, ("base", "irrelevant", "relevant", "missing"), strict=True
            ):
                row.update(
                    case="fixture",
                    edit=edit,
                    evidence_quote="" if edit == "missing" else "red",
                )
        write_json(directory / f"{split}.json", rows)
        torch.save(cache, directory / f"{split}.pt")
    metrics = tuple(
        measure(m) for m in (training_objective, validation_mse, validation_spearman)
    )
    fitted = execute(
        "fit",
        stage(
            fit_converged_readouts,
            stage_id="fit",
            config=ConvergedFitConfig(
                device="cpu",
                progress_path=str(progress_path),
                learning_rates=(1e-12, 2e-12),
                query_dim=3,
                max_epochs=4,
                patience=2,
                comparison_learning_rate=1e-12,
                comparison_max_epochs=4,
                comparison_patience=2,
                **{
                    f"{s}_sha256": file_sha256(directory / f"{s}.json")
                    for s in ("training", "validation")
                },
                **{
                    f"{s}_cache_sha256": file_sha256(directory / f"{s}.pt")
                    for s in ("training", "validation")
                },
            ),
            inputs=tuple(
                input(
                    name, path=relative(directory / f"{s}.{ext}"), data_role="training"
                )
                for s in ("training", "validation")
                for name, ext in ((s, "json"), (f"{s}_cache", "pt"))
            ),
            outputs=fit_outputs(),
            metrics=metrics,
            objective=maximize(metrics[-1]),
            reuse="never",
        ),
    )
    model_path = artifact_path(fitted, "fit", "model", "model.pt")
    write_json(
        directory / "selection.json",
        {
            "status": "checkpoints_frozen",
            "test_scores_used_for_selection": False,
            "model_sha256": file_sha256(model_path),
        },
    )
    write_json(directory / "holdout.json", list(range(4)))
    write_json(
        directory / "cohorts.json",
        {
            "colour_regex": "color",
            "splits": {"test": {"condition_families": {"car color": "appearance"}}},
        },
    )
    metric = refit_evaluation_metric()
    evaluated = execute(
        "evaluate",
        stage(
            evaluate_converged_readouts,
            stage_id="evaluate",
            eval_id="csts_convergence_smoke",
            config=ConvergedEvaluationConfig(
                device="cpu",
                progress_path=str(progress_path),
                model_sha256=file_sha256(model_path),
                selection_sha256=file_sha256(directory / "selection.json"),
                test_sha256=file_sha256(directory / "test.json"),
                cache_sha256=file_sha256(directory / "test.pt"),
                intervention_rows_sha256=file_sha256(directory / "interventions.json"),
                intervention_cache_sha256=file_sha256(directory / "interventions.pt"),
                cohorts_sha256=file_sha256(directory / "cohorts.json"),
                bootstrap_draws=20,
            ),
            inputs=(
                input("model", source=stored_source(fitted, "fit", "model", "model")),
                *(
                    input(name, path=relative(directory / filename), data_role=role)
                    for name, filename, role in (
                        ("selection", "selection.json", "training"),
                        ("test", "test.json", "eval"),
                        ("holdout", "holdout.json", "eval"),
                        ("cache", "test.pt", "eval"),
                        ("intervention_rows", "interventions.json", "eval"),
                        ("intervention_cache", "interventions.pt", "eval"),
                        ("cohorts", "cohorts.json", "eval"),
                    )
                ),
            ),
            outputs=EvalOutputs(
                report=output(path="report.json", loader=load_json, data_role="eval"),
                predictions=output(
                    path="predictions.json", loader=load_json, data_role="eval"
                ),
            ),
            split_inputs=("holdout",),
            metrics=(metric,),
            objective=maximize(metric),
            reuse="never",
        ),
    )
    report = load_json(artifact_path(evaluated, "evaluate", "report", "report.json"))
    assert set(report["results"]) == {"A_parent", "7", "8", "9"}
    assert all("parent_comparison" in report["results"][s] for s in ("7", "8", "9"))
    assert len(report["contrasts"]) == 9
    receipt["status"] = "passed"
    write_json(directory / "receipt.json", receipt)
    print("CONVERGENCE_NATIVE_PASSED", directory / "receipt.json", flush=True)


if __name__ == "__main__":
    main()
