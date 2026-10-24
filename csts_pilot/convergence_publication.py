"""Publish the completed Tranche 1 report as a native CPU build."""

import argparse
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
from viper.references import GcsFileRef, GitFileRef, LocalFileRef, ResolvedRunRef
from viper.repository import read_source, resolve_root
from viper.runtime import CPUComputeSpec, LocalEnvSpec, observe_python_env
from viper.stages import StageContext, build
from viper.storage import ViperCloudDestination

from csts_pilot.background_storage import drain_publications
from jep_pilot.loaders import load_bytes


@build(config=BuildConfig)
def publish_report(context: StageContext[BuildConfig]) -> None:
    """Preserve the reviewed report bundle without changing training or scores."""
    shutil.copyfile(context.inputs["bundle"], context.outputs["bundle"])


def cloud_report_reference(root: Path, reference: ResolvedRunRef) -> ResolvedRunRef:
    """Require finished study uploads before publishing the final CPU report."""
    drain_publications(root)
    directory = root / ".viper" / "publication_queue"
    for path in directory.glob("*.json"):
        if json.loads(path.read_text())["status"] != "published":
            raise RuntimeError(f"Study cloud publication is still pending: {path}")
    if isinstance(reference.stored_at, LocalFileRef):
        settings = json.loads((root / "configs/csts-tranche-1.json").read_text())
        return execution.promote_run_to_cloud(
            root,
            reference,
            ViperCloudDestination.model_validate(settings["publication_destination"]),
        )
    return reference


def main() -> None:
    """Publish a fixed bundle and independently verify its native build graph."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bundle", default="csts_data/tranche1_report.zip")
    parser.add_argument(
        "--receipt", default="training_outputs/csts_tranche1_report_publication.json"
    )
    parser.add_argument("--experiment-prefix", default="csts_tranche1_report_20261023")
    args = parser.parse_args()
    root = resolve_root()
    source = read_source(root)
    trusted = frozenset({str(source.repository)})
    configured = stage(
        publish_report,
        stage_id="publish",
        inputs=(
            input(
                "bundle",
                path=args.bundle,
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
        experiment_id=f"{args.experiment_prefix}_{source.commit[:12]}",
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
    reference = cloud_report_reference(root, result.reference)
    if not isinstance(reference.stored_at, GcsFileRef):
        raise RuntimeError("The final report requires a verified GCS run reference.")
    provider = GcsProvider(
        root,
        reference.stored_at.bucket,
        client=storage.Client(project="mantra-477901"),
    )
    run_bytes = provider.fetch(reference.stored_at)
    if hashlib.sha256(run_bytes).hexdigest() != reference.sha256:
        raise RuntimeError("Restored report run identity differs.")
    run = yaml.safe_load(run_bytes)
    attempt = None
    for candidate in run["attempts"]:
        attempt_bytes = provider.fetch(
            GcsFileRef.model_validate(candidate["stored_at"])
        )
        if hashlib.sha256(attempt_bytes).hexdigest() != candidate["sha256"]:
            raise RuntimeError("Restored report attempt identity differs.")
        saved = yaml.safe_load(attempt_bytes)
        if saved["attempt_id"] == run["successful_attempt_id"]:
            attempt = saved
            break
    if attempt is None:
        raise RuntimeError("The published report has no successful attempt.")
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
    if restored != (root / args.bundle).read_bytes():
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
        "reference": reference.model_dump(mode="json"),
        "local_reference": result.reference.model_dump(mode="json"),
        "verified_measurements": verified.measurement_count,
        "scope": "Completed report bundle; training and evaluations retain their original references.",
    }
    destination = root / args.receipt
    destination.write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps(receipt), flush=True)


if __name__ == "__main__":
    main()
