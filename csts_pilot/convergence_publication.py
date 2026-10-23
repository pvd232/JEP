"""Publish the completed Tranche 1 report as a native CPU build."""

import hashlib
import json
import shutil
from pathlib import Path

import yaml
from google.cloud import storage
from viper import api, execution
from viper.authoring import experiment, input, plan, replicate, stage, variant
from viper.config import BuildConfig
from viper.gcs import GcsProvider
from viper.outputs import StageOutputs, output
from viper.references import GcsFileRef, GitFileRef
from viper.repository import read_source, resolve_root
from viper.runtime import CPUComputeSpec, LocalEnvSpec, observe_python_env
from viper.stages import StageContext, build

from jep_pilot.loaders import load_bytes


@build(config=BuildConfig)
def publish_report(context: StageContext[BuildConfig]) -> None:
    """Preserve the reviewed report bundle without changing training or scores."""
    shutil.copyfile(context.inputs["bundle"], context.outputs["bundle"])


def main() -> None:
    """Publish a fixed bundle and independently verify its native build graph."""
    root = resolve_root()
    source = read_source(root)
    trusted = frozenset({str(source.repository)})
    configured = stage(
        publish_report,
        stage_id="publish",
        inputs=(
            input(
                "bundle",
                path="csts_data/tranche1_report.zip",
                data_role="eval",
            ),
        ),
        outputs=StageOutputs(
            bundle=output(
                path="tranche1_report.zip",
                loader=load_bytes,
                data_role="eval",
            )
        ),
        reuse="never",
    )
    study = experiment(
        experiment_id=f"csts_tranche1_report_20261023_{source.commit[:12]}",
        variants=(
            variant(
                "report", stages=(configured,), estimator=configured.outputs["bundle"]
            ),
        ),
        replicates=(replicate(seed=7),),
    )
    environment = LocalEnvSpec(
        compute=CPUComputeSpec(),
        lockfile=GitFileRef(
            repository=source.repository,
            commit=source.commit,
            path="pilot_requirements.txt",
        ),
        python_env=observe_python_env(),
    )
    result = execution.run(
        plan(experiment=study, source=source, env=environment),
        timeout_seconds=1800,
        trusted_source_repositories=trusted,
    )
    if result.status != "succeeded":
        raise RuntimeError(f"Report publication failed: {result.path}")
    verified = api.verify_run(
        api.VerifyRunRequest(
            root=root, path=Path(result.path), trusted_source_repositories=trusted
        )
    )
    attempt = yaml.safe_load(
        (Path(result.path).parent / "attempts/1/resolved.yaml").read_text()
    )
    resolved = attempt["resolved_stages"][0]
    snapshot = resolved["snapshot"]
    provider = GcsProvider(
        root, snapshot["bucket"], client=storage.Client(project="mantra-477901")
    )
    spec_reference = GcsFileRef.model_validate(
        dict(snapshot, path=resolved["resolved_spec"]["path"])
    )
    spec_bytes = provider.fetch(spec_reference)
    if hashlib.sha256(spec_bytes).hexdigest() != resolved["resolved_spec"]["sha256"]:
        raise RuntimeError("Restored report spec identity differs.")
    spec = yaml.safe_load(spec_bytes)
    identity = spec["artifacts"]["bundle"]["file"]
    artifact_reference = dict(snapshot, path=identity["path"])
    restored = provider.fetch(GcsFileRef.model_validate(artifact_reference))
    if hashlib.sha256(restored).hexdigest() != identity["sha256"]:
        raise RuntimeError("Restored report bundle identity differs.")
    if restored != (root / "csts_data/tranche1_report.zip").read_bytes():
        raise RuntimeError("Restored report bundle differs from the reviewed input.")
    receipt = {
        "source_commit": source.commit,
        "artifact": {
            "stored_at": artifact_reference,
            "sha256": identity["sha256"],
            "bytes": identity["bytes"],
            "restored_and_checksum_verified": True,
        },
        "status": result.status,
        "reference": result.reference.model_dump(mode="json"),
        "verified_measurements": verified.measurement_count,
        "scope": "Completed report bundle; training and evaluations retain their original references.",
    }
    destination = root / "training_outputs/csts_tranche1_report_publication.json"
    destination.write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps(receipt), flush=True)


if __name__ == "__main__":
    main()
