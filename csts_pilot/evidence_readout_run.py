"""Queue and run the prospective evidence-readout screen through native VIPER."""

import argparse
import fcntl
import subprocess
import time
import uuid
from contextlib import ExitStack
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Literal

from viper import execution
from viper.authoring import experiment, input, plan, replicate, stage, variant
from viper.config import BuildConfig
from viper.metrics import max as maximize
from viper.metrics import measure
from viper.outputs import EvalOutputs, StageOutputs, TrainOutputs, output
from viper.references import GitFileRef
from viper.repository import read_source
from viper.runtime import (
    CPUComputeSpec,
    CUDAComputeSpec,
    LocalEnvSpec,
    observe_python_env,
)
from viper.storage import ViperCloudDestination

from csts_pilot.answers import answer_id
from csts_pilot.background_storage import _save, queue_publication
from csts_pilot.condition_reference import native_layout
from csts_pilot.convergence import (
    CheckpointConfig,
    file_sha256,
    promote_checkpoint,
    training_objective,
    validation_mse,
    validation_spearman,
    write_json,
)
from csts_pilot.convergence_run import artifact_path, check_inputs
from csts_pilot.evidence_attention_run import stored_source
from csts_pilot.evidence_readout import object_sha256, validate_capture
from csts_pilot.evidence_readout_retention import (
    ReadoutRetentionConfig,
    audit_writing_retention,
)
from csts_pilot.evidence_readout_stages import (
    ReadoutEvaluationConfig,
    ReadoutExtractionConfig,
    ReadoutFitConfig,
    evaluate_readout,
    extract_readout,
    fit_readout,
    readout_evaluation_metric,
)
from jep_pilot.loaders import load_json, load_model, load_state
from jep_pilot.stages import publish_evaluation_inputs


def checked_source(root: Path, expected: str) -> None:
    """Ensure the queued source still matches the reviewed, clean commit."""
    if (
        subprocess.check_output(
            ["git", "-C", str(root), "rev-parse", "HEAD"], text=True
        ).strip()
        != expected
    ):
        raise ValueError("The queued source commit changed.")
    if subprocess.check_output(
        ["git", "-C", str(root), "status", "--porcelain", "--untracked-files=normal"],
        text=True,
    ):
        raise ValueError("Commit all source changes before queueing the experiment.")


def validate_settings(root: Path, settings: dict[str, Any]) -> None:
    """Reject substitutions, mismatched cohorts, and unbound teacher captures."""
    if settings["dataset_revision"] != "jep-csts-v1.1" or settings["seeds"] != [
        7,
        8,
        9,
    ]:
        raise ValueError("Keep the reviewed dataset and three predeclared seeds.")
    if settings["training"] != {
        "query_dim": 128,
        "evidence_weight": 0.1,
        "learning_rate": 0.001,
        "weight_decay": 0.01,
        "batch_size": 32,
        "max_epochs": 48,
        "patience": 5,
        "device": "cuda",
        "comparison_max_epochs": 48,
        "comparison_patience": 5,
    }:
        raise ValueError("The reviewed paired fitting procedure changed.")
    if (
        settings["encoder"]["embedding_dimension"] != 4096
        or settings["encoder"]["encode_batch_size"] != 4
    ):
        raise ValueError(
            "Retain the full-width parent values and original forward layout."
        )
    check_inputs(root, settings)
    for name in (
        "records",
        "provenance",
        "audit_gate",
        "checkpoint_manifest",
        "writing_targets",
        "head",
        "cohorts",
        "interventions",
    ):
        item = settings[name]
        if file_sha256(root / item["path"]) != item["sha256"]:
            raise ValueError(f"Changed pinned input: {name}.")
    provenance = load_json(root / settings["provenance"]["path"])
    gate = load_json(root / settings["audit_gate"]["path"])
    validate_capture(
        provenance,
        gate,
        settings["records"]["sha256"],
        settings["splits"]["training"]["sha256"],
        settings["audit_gate"]["sha256"],
        len(load_json(root / settings["records"]["path"])),
    )
    records = load_json(root / settings["records"]["path"])
    keys = native_layout(load_json(root / settings["splits"]["training"]["path"]))[0]
    canonical = {answer_id(passage, condition) for condition, passage in keys}
    from collections import Counter

    if (
        len(records) != settings["records"]["items"]
        or {r["id"] for r in records} != canonical
        or len({r["id"] for r in records}) != len(records)
        or dict(Counter(r["status"] for r in records))
        != settings["records"]["status_counts"]
    ):
        raise ValueError("The complete canonical training evidence bank changed.")
    manifest = load_json(root / settings["checkpoint_manifest"]["path"])
    for name, item in settings["models"].items():
        if (
            file_sha256(root / item["path"]) != item["sha256"]
            or manifest["models"][name + ".pt"]["sha256"] != item["sha256"]
        ):
            raise ValueError(f"The archived frozen checkpoint changed: {name}.")
    if settings["retention"] != {
        "expected_targets": 121,
        "generated_samples": 32,
        "max_answer_tokens": 64,
    }:
        raise ValueError("The fixed writing retention policy changed.")


def run_study(
    root: Path, settings: dict[str, Any], directory: Path, source_commit: str
) -> None:
    """Extract training/validation, freeze every checkpoint, then open test labels."""
    checked_source(root, source_commit)
    validate_settings(root, settings)
    source, environment = read_source(root), observe_python_env()
    trusted = frozenset({str(source.repository)})
    destination = ViperCloudDestination.model_validate(
        settings["publication_destination"]
    )
    path = directory / "summary.json"
    if path.exists():
        raise ValueError(
            "Preserve the existing attempt; recovery must reconcile sealed native runs explicitly."
        )
    summary: dict[str, Any] = {
        "status": "running",
        "source_commit": source.commit,
        "settings": settings,
        "runs": [],
        "in_flight": None,
        "attempt": uuid.uuid4().hex[:8],
    }
    _save(path, summary)

    def execute(
        label: str, configured: Any, gpu: bool, seed: int = 7
    ) -> dict[str, Any]:
        trial = experiment(
            experiment_id=f"csts_readout_{source.commit[:8]}_{summary['attempt']}_{label}",
            variants=(
                variant(
                    label,
                    stages=(configured,),
                    estimator=next(iter(configured.outputs.values())),
                ),
            ),
            replicates=(replicate(seed=seed),),
        )
        summary["in_flight"] = {"name": label, "experiment_id": trial.experiment_id}
        _save(path, summary)
        started = time.monotonic()
        result = execution.run(
            plan(
                experiment=trial,
                source=source,
                env=LocalEnvSpec(
                    compute=CUDAComputeSpec(model="NVIDIA L4", count=1)
                    if gpu
                    else CPUComputeSpec(),
                    lockfile=GitFileRef(
                        repository=source.repository,
                        commit=source.commit,
                        path="tranche2_requirements.txt",
                    ),
                    python_env=environment,
                ),
            ),
            timeout_seconds=settings["stage_timeout_seconds"],
            trusted_source_repositories=trusted,
        )
        record = {
            "name": label,
            "status": result.status,
            "path": str(result.path),
            "reference": result.reference.model_dump(mode="json"),
            "seconds": time.monotonic() - started,
        }
        summary["runs"].append(record)
        summary["in_flight"] = None
        _save(path, summary)
        if result.status != "succeeded":
            raise RuntimeError(f"Native readout stage failed: {label}.")
        record["publication_queue"] = str(
            queue_publication(root, result.reference, destination)
        )
        _save(path, summary)
        return record

    parents = {}

    def extract(
        split: Literal["training", "validation", "test", "interventions"],
        parent_name: str = "proposition_final",
    ) -> dict[str, Any]:
        item = (
            settings["interventions"]
            if split == "interventions"
            else settings["splits"][split]
        )
        heldout = split in {"test", "interventions"}
        role = "eval" if heldout else "training"
        bindings: list[Any] = [
            input(
                "model",
                source=stored_source(parents[parent_name], "publish", "model", "model"),
            ),
            input("rows", path=item["path"], data_role=role),
        ]
        if heldout:
            bindings.append(
                input(
                    "selection",
                    path=(directory / "selection.json").relative_to(root).as_posix(),
                    data_role="training",
                )
            )
        if split == "training":
            bindings.extend(
                input(name, path=settings[name]["path"], data_role="training")
                for name in ("records", "provenance", "audit_gate")
            )
        return execute(
            f"extract_{split}_{parent_name}",
            stage(
                extract_readout,
                stage_id="extract",
                config=ReadoutExtractionConfig(
                    **settings["encoder"],
                    split=split,
                    rows_sha256=item["sha256"],
                    model_sha256=settings["models"][parent_name]["sha256"],
                    records_sha256=settings["records"]["sha256"]
                    if split == "training"
                    else None,
                    provenance_sha256=settings["provenance"]["sha256"]
                    if split == "training"
                    else None,
                    audit_gate_sha256=settings["audit_gate"]["sha256"]
                    if split == "training"
                    else None,
                    selection_sha256=summary["selection_sha256"] if heldout else None,
                ),
                inputs=tuple(bindings),
                outputs=StageOutputs(
                    cache=output(path="cache.pt", loader=load_model, data_role=role),
                    diagnostics=output(
                        path="diagnostics.json", loader=load_json, data_role=role
                    ),
                ),
                reuse="never",
            ),
            gpu=True,
        )

    try:
        for name, item in settings["models"].items():
            parents[name] = execute(
                f"publish_{name}",
                stage(
                    promote_checkpoint,
                    stage_id="publish",
                    config=CheckpointConfig(model_sha256=item["sha256"]),
                    inputs=(
                        input("checkpoint", path=item["path"], data_role="training"),
                    ),
                    outputs=StageOutputs(
                        model=output(
                            path="model.pt", loader=load_model, data_role="training"
                        )
                    ),
                    reuse="never",
                ),
                gpu=False,
            )
        retention = execute(
            "writing_retention",
            stage(
                audit_writing_retention,
                stage_id="retention",
                config=ReadoutRetentionConfig(
                    **settings["encoder"],
                    **settings["retention"],
                    writing_model_sha256=settings["models"][
                        "proposition_writing_epoch5"
                    ]["sha256"],
                    final_model_sha256=settings["models"]["proposition_final"][
                        "sha256"
                    ],
                    targets_sha256=settings["writing_targets"]["sha256"],
                    head_sha256=settings["head"]["sha256"],
                    training_sha256=settings["splits"]["training"]["sha256"],
                    validation_sha256=settings["splits"]["validation"]["sha256"],
                ),
                inputs=(
                    input(
                        "writing_model",
                        source=stored_source(
                            parents["proposition_writing_epoch5"],
                            "publish",
                            "model",
                            "writing_model",
                        ),
                    ),
                    input(
                        "final_model",
                        source=stored_source(
                            parents["proposition_final"],
                            "publish",
                            "model",
                            "final_model",
                        ),
                    ),
                    input(
                        "targets",
                        path=settings["writing_targets"]["path"],
                        data_role="training",
                    ),
                    input("head", path=settings["head"]["path"], data_role="training"),
                    input(
                        "training",
                        path=settings["splits"]["training"]["path"],
                        data_role="training",
                    ),
                    input(
                        "validation",
                        path=settings["splits"]["validation"]["path"],
                        data_role="training",
                    ),
                ),
                outputs=StageOutputs(
                    report=output(
                        path="report.json", loader=load_json, data_role="training"
                    ),
                    predictions=output(
                        path="predictions.json", loader=load_json, data_role="training"
                    ),
                ),
                reuse="never",
            ),
            gpu=True,
        )
        summary["writing_retention_report"] = str(
            artifact_path(retention, "retention", "report", "report.json")
        )
        _save(path, summary)
        caches = {split: extract(split) for split in ("training", "validation")}
        fitted = {}
        metrics = tuple(
            measure(m)
            for m in (training_objective, validation_mse, validation_spearman)
        )
        for seed in settings["seeds"]:
            bindings: list[Any] = [
                input(
                    split, path=settings["splits"][split]["path"], data_role="training"
                )
                for split in ("training", "validation")
            ]
            bindings.extend(
                input(
                    f"{split}_cache",
                    source=stored_source(
                        caches[split], "extract", "cache", f"{split}_cache"
                    ),
                )
                for split in ("training", "validation")
            )
            fitted[str(seed)] = execute(
                f"fit_{seed}",
                stage(
                    fit_readout,
                    stage_id="fit",
                    config=ReadoutFitConfig.model_validate(
                        {
                            **settings["training"],
                            "seed": seed,
                            **{
                                f"{s}_sha256": settings["splits"][s]["sha256"]
                                for s in ("training", "validation")
                            },
                            **{
                                f"{s}_cache_sha256": file_sha256(
                                    artifact_path(
                                        caches[s], "extract", "cache", "cache.pt"
                                    )
                                )
                                for s in ("training", "validation")
                            },
                        }
                    ),
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
                            path="predictions.json",
                            loader=load_json,
                            data_role="training",
                        ),
                    ),
                    metrics=metrics,
                    objective=maximize(metrics[-1]),
                    reuse="never",
                ),
                gpu=True,
                seed=seed,
            )
        frozen = {
            "status": "checkpoints_frozen",
            "test_scores_used_for_selection": False,
            "source_commit": source.commit,
            "models": {
                s: {
                    "run": r,
                    "sha256": file_sha256(artifact_path(r, "fit", "model", "model.pt")),
                }
                for s, r in fitted.items()
            },
        }
        _save(directory / "selection.json", frozen)
        summary["selection_sha256"] = file_sha256(directory / "selection.json")
        _save(path, summary)
        # This is the first test deserialization in the controller or its stages.
        caches.update({split: extract(split) for split in ("test", "interventions")})
        caches["ratings_test"] = extract("test", "ratings_final")
        holdout = directory / "holdout.json"
        test_rows = load_json(root / settings["splits"]["test"]["path"])
        write_json(holdout, list(range(len(test_rows))))
        published = execute(
            "publish_test",
            stage(
                publish_evaluation_inputs,
                stage_id="publish",
                config=BuildConfig(),
                inputs=(
                    input(
                        "test",
                        path=settings["splits"]["test"]["path"],
                        data_role="eval",
                    ),
                    input(
                        "holdout",
                        path=holdout.relative_to(root).as_posix(),
                        data_role="eval",
                    ),
                ),
                outputs=StageOutputs(
                    test=output(path="test.json", loader=load_json, data_role="eval"),
                    holdout=output(
                        path="holdout.json", loader=load_json, data_role="eval"
                    ),
                ),
                reuse="never",
            ),
            gpu=False,
        )
        bindings = [
            input(
                "selection",
                path=(directory / "selection.json").relative_to(root).as_posix(),
                data_role="training",
            ),
            input(
                "test",
                source=stored_source(published, "publish", "test", "test", "eval"),
            ),
            input(
                "holdout",
                source=stored_source(
                    published, "publish", "holdout", "holdout", "eval"
                ),
            ),
            input(
                "cache",
                source=stored_source(
                    caches["test"], "extract", "cache", "cache", "eval"
                ),
            ),
            input(
                "intervention_rows",
                path=settings["interventions"]["path"],
                data_role="eval",
            ),
            input(
                "intervention_cache",
                source=stored_source(
                    caches["interventions"],
                    "extract",
                    "cache",
                    "intervention_cache",
                    "eval",
                ),
            ),
        ]
        bindings.extend(
            (
                input(
                    "ratings_cache",
                    source=stored_source(
                        caches["ratings_test"],
                        "extract",
                        "cache",
                        "ratings_cache",
                        "eval",
                    ),
                ),
                input("cohorts", path=settings["cohorts"]["path"], data_role="eval"),
            )
        )
        for index, (seed, record) in enumerate(fitted.items()):
            bindings.append(
                input(
                    "model" if index == 0 else f"model_{seed}",
                    source=stored_source(
                        record,
                        "fit",
                        "model",
                        "model" if index == 0 else f"model_{seed}",
                    ),
                )
            )
        evaluated_metric = readout_evaluation_metric()
        final = execute(
            "evaluate",
            stage(
                evaluate_readout,
                stage_id="evaluate",
                eval_id="csts_evidence_readout",
                config=ReadoutEvaluationConfig(
                    selection_sha256=summary["selection_sha256"],
                    rows_sha256=settings["splits"]["test"]["sha256"],
                    cache_sha256=file_sha256(
                        artifact_path(caches["test"], "extract", "cache", "cache.pt")
                    ),
                    intervention_rows_sha256=settings["interventions"]["sha256"],
                    intervention_cache_sha256=file_sha256(
                        artifact_path(
                            caches["interventions"], "extract", "cache", "cache.pt"
                        )
                    ),
                    model_sha256={s: frozen["models"][s]["sha256"] for s in fitted},
                    bootstrap_draws=settings["bootstrap_draws"],
                    ratings_cache_sha256=file_sha256(
                        artifact_path(
                            caches["ratings_test"], "extract", "cache", "cache.pt"
                        )
                    ),
                    cohorts_sha256=settings["cohorts"]["sha256"],
                ),
                inputs=tuple(bindings),
                outputs=EvalOutputs(
                    report=output(
                        path="report.json", loader=load_json, data_role="eval"
                    ),
                    predictions=output(
                        path="predictions.json", loader=load_json, data_role="eval"
                    ),
                ),
                split_inputs=("holdout",),
                metrics=(evaluated_metric,),
                objective=maximize(evaluated_metric),
                reuse="never",
            ),
            gpu=True,
        )
        summary.update(
            status="complete",
            report=str(artifact_path(final, "evaluate", "report", "report.json")),
        )
        _save(path, summary)
    except BaseException as error:
        summary.update(status="failed", error_type=type(error).__name__)
        _save(path, summary)
        raise


def queue_identity(
    root: Path, settings_path: Path, source_commit: str
) -> dict[str, str]:
    """Make an immutable, reviewable request; inspect no test labels."""
    checked_source(root, source_commit)
    settings = load_json(settings_path)
    validate_settings(root, settings)
    return {
        "root": str(root),
        "source_commit": source_commit,
        "settings_sha256": file_sha256(settings_path),
        "settings_path": str(settings_path),
    }


def gpu_idle() -> bool:
    """Require an L4 with no active compute process, in addition to shared leases."""
    names = (
        subprocess.check_output(
            ["nvidia-smi", "--query-gpu=name", "--format=csv,noheader"], text=True
        )
        .strip()
        .splitlines()
    )
    if names != ["NVIDIA L4"]:
        raise ValueError("This request is restricted to one NVIDIA L4.")
    processes = subprocess.check_output(
        ["nvidia-smi", "--query-compute-apps=pid", "--format=csv,noheader,nounits"],
        text=True,
    ).strip()
    return not processes


def queue_study(root: Path, settings_path: Path, name: str, source_commit: str) -> None:
    """Persist queue state and wait without preempting another GPU workload."""
    identity = queue_identity(root, settings_path, source_commit)
    directory = root / "qwen_evidence_results" / name
    directory.mkdir(parents=True, exist_ok=True)
    status_path = directory / "queue.json"
    with (directory / "worker.lock").open("a+") as worker:
        try:
            fcntl.flock(worker, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            raise RuntimeError("This request already has a queue worker.") from None
        if status_path.exists():
            old = load_json(status_path)
            if old["identity"] != identity or old["status"] in {
                "running",
                "complete",
                "failed",
            }:
                raise ValueError(
                    "Preserve the existing attempt and reconcile its recorded state."
                )
        settings = load_json(settings_path)
        while True:
            checked_source(root, source_commit)
            if file_sha256(settings_path) != identity["settings_sha256"]:
                raise ValueError("Queued settings changed.")
            state = {
                "identity": identity,
                "request_sha256": object_sha256(identity),
                "status": "queued",
                "heartbeat_utc": datetime.now(UTC).isoformat(),
            }
            _save(status_path, state)
            with ExitStack() as locks:
                acquired = True
                for lock_path in settings["gpu_locks"]:
                    path = Path(lock_path)
                    path.parent.mkdir(parents=True, exist_ok=True)
                    # Opening existing shared /tmp files without O_CREAT also works
                    # under Linux protected_regular when the owner differs.
                    lock = locks.enter_context(
                        path.open("r+" if path.exists() else "a+")
                    )
                    try:
                        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
                    except BlockingIOError:
                        acquired = False
                        break
                if acquired and gpu_idle():
                    validate_settings(root, settings)
                    state.update(
                        status="running", started_utc=datetime.now(UTC).isoformat()
                    )
                    _save(status_path, state)
                    try:
                        run_study(root, settings, directory, source_commit)
                    except BaseException as error:
                        state.update(
                            status="failed",
                            error_type=type(error).__name__,
                            finished_utc=datetime.now(UTC).isoformat(),
                        )
                        _save(status_path, state)
                        raise
                    state.update(
                        status="complete", finished_utc=datetime.now(UTC).isoformat()
                    )
                    _save(status_path, state)
                    return
            time.sleep(30)


def main() -> None:
    """A detached invocation remains queued until the shared L4 leases are free."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument(
        "--settings", type=Path, default=Path("configs/csts-evidence-readout.json")
    )
    parser.add_argument("--name", default="evidence_readout_20261027")
    parser.add_argument("--expected-source", required=True)
    args = parser.parse_args()
    if not args.name or Path(args.name).name != args.name or args.name in {".", ".."}:
        raise ValueError("The attempt name must be one directory component.")
    root = args.root.resolve(strict=True)
    queue_study(
        root,
        (root / args.settings).resolve(strict=True),
        args.name,
        args.expected_source,
    )


if __name__ == "__main__":
    main()
