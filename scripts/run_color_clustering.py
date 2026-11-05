"""Execute embedding, clustering and review artifacts as three native VIPER stages."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import tarfile
import time
from contextlib import contextmanager
from pathlib import Path

from csts_pilot.convergence_run import artifact_path, artifact_source
from pydantic import Field
from scripts import color_clustering
from viper import api, execution
from viper.authoring import experiment, input, plan, replicate, stage, variant
from viper.config import BuildConfig, EvalConfig
from viper.outputs import EvalOutputs, StageOutputs, output
from viper.references import GitFileRef
from viper.repository import read_source
from viper.runtime import (
    CPUComputeSpec,
    CUDAComputeSpec,
    LocalEnvSpec,
    observe_python_env,
)
from viper.stages import StageContext, build, eval


class BuildPins(BuildConfig):
    """Bind a data-building stage to the exact bytes of every declared input."""

    input_sha256: dict[str, str] = Field(
        description="SHA-256 of each named input supplied to this native stage."
    )
    work_root: Path = Field(
        description="Durable task-owned directory for resumable intermediate artifacts."
    )


class AnalysisPins(EvalConfig):
    """Bind clustering diagnostics to the frozen cohort, settings and embeddings."""

    input_sha256: dict[str, str] = Field(
        description="SHA-256 of each named input supplied to the clustering stage."
    )
    work_root: Path = Field(
        description="Durable task-owned directory for resumable intermediate artifacts."
    )


COMMON = {
    "points": "points.json",
    "labels": "color-labels.json",
    "pairs": "pairs.json",
    "cohort": "cohort-manifest.json",
    "probe_points": "probe-points.json",
    "switch_probe": "switch-probe.json",
    "settings": "experiment.toml",
    "model_manifest": "model-manifest.json",
}


def load_json(path: Path):
    """Load a tracked JSON output through VIPER's artifact loader interface."""
    return color_clustering.read(path)


def load_path(path: Path) -> Path:
    """Expose an immutable binary artifact without eagerly loading its bytes."""
    return path


def verify_inputs(context) -> None:
    """Compare every materialized native input with its frozen stage configuration."""
    if set(context.inputs) != set(context.config.input_sha256):
        raise ValueError("native COLOR stage input names differ")
    for name, path in context.inputs.items():
        if color_clustering.sha(path) != context.config.input_sha256[name]:
            raise ValueError("native COLOR stage input bytes differ: " + name)


@contextmanager
def working_directory(context, stage_name: str):
    """Retain resumable work under an input-and-implementation-specific directory."""
    identity = dict(
        inputs=context.config.input_sha256,
        implementation=color_clustering.sha(Path(color_clustering.__file__)),
        driver=color_clustering.sha(Path(__file__)),
    )
    digest = hashlib.sha256(json.dumps(identity, sort_keys=True).encode()).hexdigest()
    root = context.config.work_root / stage_name / digest[:20]
    root.mkdir(parents=True, exist_ok=True)
    yield root


def assemble(context, root: Path) -> None:
    """Place immutable inputs under the analysis command's stable filenames."""
    for name, filename in COMMON.items():
        shutil.copyfile(context.inputs[name], root / filename)


@build(config=BuildPins)
def embed(context: StageContext[BuildPins]) -> None:
    """Build all three conditional/control vector caches without parameter updates."""
    verify_inputs(context)
    with working_directory(context, "embed") as root:
        assemble(context, root)
        manifest = color_clustering.read(root / "model-manifest.json")
        manifest["checkpoint"] = str(context.inputs["checkpoint"])
        manifest["source_repository"] = str(Path(__file__).resolve().parents[1])
        color_clustering.write(root / "model-manifest.json", manifest)
        color_clustering.encode_inputs(root, root / "model-manifest.json")
        summaries = {}
        for arm in color_clustering.ARMS:
            for suffix, name in (("", arm), ("-probes", arm + "_probes")):
                shutil.copyfile(
                    root / "embeddings" / (arm + suffix + ".npz"), context.outputs[name]
                )
            summaries[arm] = color_clustering.read(
                root / "embeddings" / (arm + ".json")
            )
        color_clustering.write(
            context.outputs["metadata"],
            {
                "arms": summaries,
                "inputs": context.config.input_sha256,
                "model": manifest,
            },
        )


@eval(config=AnalysisPins)
def cluster(context: StageContext[AnalysisPins]) -> None:
    """Measure the complete fixed sweep and source-family paired comparisons."""
    verify_inputs(context)
    with working_directory(context, "cluster") as root:
        assemble(context, root)
        (root / "embeddings").mkdir()
        for arm in color_clustering.ARMS:
            shutil.copyfile(context.inputs[arm], root / "embeddings" / (arm + ".npz"))
            shutil.copyfile(
                context.inputs[arm + "_probes"],
                root / "embeddings" / (arm + "-probes.npz"),
            )
        color_clustering.fit_sweep(root)
        shutil.copyfile(root / "metrics.json", context.outputs["predictions"])
        with tarfile.open(context.outputs["clusters"], "w") as archive:
            archive.add(root / "clusters", arcname="clusters")


@build(config=BuildPins)
def report(context: StageContext[BuildPins]) -> None:
    """Produce the full visual review pack from tracked vectors and clustering artifacts."""
    from scripts.color_diagnostics import build_review_pack

    verify_inputs(context)
    with working_directory(context, "report") as root:
        assemble(context, root)
        shutil.copyfile(context.inputs["metrics"], root / "metrics.json")
        (root / "embeddings").mkdir()
        for arm in color_clustering.ARMS:
            shutil.copyfile(context.inputs[arm], root / "embeddings" / (arm + ".npz"))
        color_clustering.write_report(root)
        build_review_pack(root, context.inputs["clusters"])
        shutil.copyfile(root / "report.md", context.outputs["report"])
        shutil.copyfile(root / "dashboard.html", context.outputs["dashboard"])
        shutil.copyfile(root / "diagnostics.pdf", context.outputs["pdf"])
        shutil.copyfile(root / "review.zip", context.outputs["bundle"])
        shutil.copyfile(root / "run-receipt.json", context.outputs["receipt"])


def run(root: Path) -> None:
    """Freeze and execute the dependency-ordered native experiment stages."""
    root = root.resolve(strict=True)
    source = read_source(root)
    environment = observe_python_env()
    trusted = frozenset({str(source.repository)})
    directory = root / "color_results" / "run-20261104"
    directory.mkdir(parents=True, exist_ok=True)
    previous = (
        color_clustering.read(directory / "status.json")
        if (directory / "status.json").exists()
        else {}
    )
    status = {"source_commit": source.commit, "runs": [], "status": "running"}
    source_inputs = {
        name: root / "color_inputs" / filename for name, filename in COMMON.items()
    }
    source_inputs["checkpoint"] = root / "color_inputs" / "checkpoint.pt"
    checkpoint = color_clustering.read(source_inputs["model_manifest"])
    if (
        color_clustering.sha(source_inputs["checkpoint"])
        != checkpoint["checkpoint_sha256"]
    ):
        raise ValueError("encoder identity: checkpoint mismatch")
    common_hashes = {
        name: color_clustering.sha(path)
        for name, path in source_inputs.items()
        if name != "checkpoint"
    }
    common_specs = tuple(
        input(name, path=str(path.relative_to(root)), data_role="evaluation")
        for name, path in source_inputs.items()
        if name != "checkpoint"
    )

    def execute(name: str, configured, gpu: bool) -> dict:
        """Run and verify one plan, retaining its immutable VIPER reference."""
        expected_hashes = configured.config.input_sha256
        for old in previous.get("runs", []):
            if (
                old["name"] == name
                and old["status"] == "succeeded"
                and old.get("input_sha256") == expected_hashes
            ):
                api.verify_run(
                    api.VerifyRunRequest(
                        root=root,
                        path=Path(old["path"]),
                        trusted_source_repositories=trusted,
                    )
                )
                status["runs"].append(dict(old, reused=True))
                color_clustering.write(directory / "status.json", status)
                return old
        status["current_stage"] = name
        color_clustering.write(directory / "status.json", status)
        trial = experiment(
            experiment_id="csts_color_" + source.commit[:8] + "_" + name,
            variants=(
                variant(
                    name,
                    stages=(configured,),
                    estimator=next(iter(configured.outputs.values())),
                ),
            ),
            replicates=(replicate(seed=7),),
        )
        env = LocalEnvSpec(
            compute=CUDAComputeSpec(model="NVIDIA L4", count=1)
            if gpu
            else CPUComputeSpec(),
            lockfile=GitFileRef(
                repository=source.repository,
                commit=source.commit,
                path="color_clustering_requirements.txt",
            ),
            python_env=environment,
        )
        started = time.monotonic()
        result = execution.run(
            plan(experiment=trial, source=source, env=env),
            timeout_seconds={"embed": 1800, "cluster": 7200, "report": 3600}[name],
            trusted_source_repositories=trusted,
        )
        record = {
            "name": name,
            "status": result.status,
            "path": str(result.path),
            "reference": result.reference.model_dump(mode="json"),
            "seconds": time.monotonic() - started,
            "source_commit": source.commit,
            "input_sha256": expected_hashes,
        }
        status["runs"].append(record)
        color_clustering.write(directory / "status.json", status)
        if result.status != "succeeded":
            raise RuntimeError("Native COLOR stage failed: " + name)
        api.verify_run(
            api.VerifyRunRequest(
                root=root, path=Path(result.path), trusted_source_repositories=trusted
            )
        )
        return record

    try:
        embedding_outputs = {}
        for arm in color_clustering.ARMS:
            embedding_outputs[arm] = output(
                path=arm + ".npz", loader=load_path, data_role="evaluation"
            )
            embedding_outputs[arm + "_probes"] = output(
                path=arm + "-probes.npz", loader=load_path, data_role="evaluation"
            )
        embedding_outputs["metadata"] = output(
            path="metadata.json", loader=load_json, data_role="evaluation"
        )
        embedded = execute(
            "embed",
            stage(
                embed,
                stage_id="embed",
                config=BuildPins(
                    work_root=directory / "working",
                    input_sha256={
                        **common_hashes,
                        "checkpoint": color_clustering.sha(source_inputs["checkpoint"]),
                    },
                ),
                inputs=common_specs
                + (input("checkpoint", path="color_inputs/checkpoint.pt"),),
                outputs=StageOutputs(**embedding_outputs),
                reuse="never",
            ),
            True,
        )
        embeddings = {
            name: artifact_path(
                embedded, "embed", name, name.replace("_probes", "-probes") + ".npz"
            )
            for name in embedding_outputs
            if name != "metadata"
        }
        embedding_inputs = tuple(
            input(name, source=artifact_source(embedded, "embed", name))
            for name in embeddings
        )
        clustered = execute(
            "cluster",
            stage(
                cluster,
                stage_id="cluster",
                config=AnalysisPins(
                    work_root=directory / "working",
                    input_sha256={
                        **common_hashes,
                        **{
                            name: color_clustering.sha(path)
                            for name, path in embeddings.items()
                        },
                    },
                ),
                inputs=common_specs + embedding_inputs,
                outputs=EvalOutputs(
                    predictions=output(path="metrics.json", loader=load_json),
                    clusters=output(path="clusters.tar", loader=load_path),
                ),
                reuse="never",
            ),
            False,
        )
        metrics = artifact_path(clustered, "cluster", "predictions", "metrics.json")
        clusters = artifact_path(clustered, "cluster", "clusters", "clusters.tar")
        reported = execute(
            "report",
            stage(
                report,
                stage_id="report",
                config=BuildPins(
                    work_root=directory / "working",
                    input_sha256={
                        **common_hashes,
                        **{
                            name: color_clustering.sha(path)
                            for name, path in embeddings.items()
                            if not name.endswith("_probes")
                        },
                        "metrics": color_clustering.sha(metrics),
                        "clusters": color_clustering.sha(clusters),
                    },
                ),
                inputs=common_specs
                + tuple(
                    spec
                    for spec, name in zip(embedding_inputs, embeddings)
                    if not name.endswith("_probes")
                )
                + (
                    input(
                        "metrics",
                        source=artifact_source(clustered, "cluster", "predictions"),
                    ),
                    input(
                        "clusters",
                        source=artifact_source(clustered, "cluster", "clusters"),
                    ),
                ),
                outputs=StageOutputs(
                    report=output(path="report.md", loader=load_path),
                    dashboard=output(path="dashboard.html", loader=load_path),
                    pdf=output(path="diagnostics.pdf", loader=load_path),
                    bundle=output(path="review.zip", loader=load_path),
                    receipt=output(path="run-receipt.json", loader=load_json),
                ),
                reuse="never",
            ),
            False,
        )
        for name, filename in (
            ("report", "report.md"),
            ("dashboard", "dashboard.html"),
            ("pdf", "diagnostics.pdf"),
            ("bundle", "review.zip"),
            ("receipt", "run-receipt.json"),
        ):
            shutil.copyfile(
                artifact_path(reported, "report", name, filename), directory / filename
            )
        status["status"] = "complete"
    except Exception:
        status["status"] = "failed"
        raise
    finally:
        color_clustering.write(directory / "status.json", status)
        color_clustering.write(directory / "viper-provenance.json", status)


if __name__ == "__main__":
    from scripts import run_color_clustering

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    # VIPER seals callables under their importable module identity.
    run_color_clustering.run(parser.parse_args().root)
