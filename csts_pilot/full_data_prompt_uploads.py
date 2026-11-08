"""Publish sealed local generations through VIPER while training continues.

The uploader runs as a separate bounded service on the GPU VM and uses only
the attached workload identity. A generation becomes safe for cleanup after
VIPER has published its immutable manifest and streamed the cloud bytes back
through its SHA-256 verifier.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import time
import urllib.request
from pathlib import Path
from typing import Any

from csts_pilot.full_data_prompt_protocol import digest_file
from csts_pilot.full_data_prompt_worker import acknowledgment_matches, atomic_json


def require_workload_identity(expected: str) -> None:
    """Require the configured attached identity without reading credential files."""
    request = urllib.request.Request(
        "http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/email",
        headers={"Metadata-Flavor": "Google"},
    )
    with urllib.request.urlopen(request, timeout=5) as response:
        actual = response.read().decode().strip()
    if not expected or actual != expected:
        raise PermissionError("Attached workload account differs from the allocation manifest.")


def cloud_service(root: Path, project: str) -> Any:
    """Bind VIPER to metadata credentials and the workspace's declared repository."""
    from google.auth.compute_engine import Credentials
    from google.cloud import storage
    from viper.cloud import ViperCloud
    from viper.gcs import GcsProvider
    from viper.storage import load_storage_settings

    repository = load_storage_settings(root).repository
    if repository is None or repository.provider != "gcs":
        raise ValueError("This deployment requires the configured VIPER GCS repository.")
    client = storage.Client(project=project, credentials=Credentials())
    provider = GcsProvider(root, repository.bucket, prefix=repository.prefix, client=client)
    return ViperCloud(root, repository, provider=provider)


def publish_one(root: Path, manifest_path: Path, cloud: Any, owner: str,
                workspace: str) -> dict[str, Any]:
    """Publish one immutable local archive and acknowledge only verified cloud bytes."""
    from viper.storage import ViperCloudDestination

    manifest = json.loads(manifest_path.read_text())
    archive = manifest_path.parent / "native.tar"
    if archive.is_symlink() or manifest_path.is_symlink():
        raise ValueError("Publication inputs must be ordinary sealed files.")
    archive.resolve().relative_to(root.resolve())
    if manifest["archive"] != str(archive):
        raise ValueError("Manifest archive is outside its generation directory.")
    if archive.stat().st_size != manifest["archive_size"] or digest_file(archive) != manifest["archive_sha256"]:
        raise ValueError("Sealed native generation changed before VIPER publication.")
    destination = ViperCloudDestination(owner=owner, workspace=workspace)
    sources = {
        str(archive.relative_to(root)): archive,
        str(manifest_path.relative_to(root)): manifest_path,
    }
    references = cloud.resolved_files(destination, sources)
    for reference in references.values():
        cloud.verify_file(reference)
    archive_ref = references[str(archive.relative_to(root))]
    if archive_ref.sha256 != manifest["archive_sha256"] or archive_ref.bytes != manifest["archive_size"]:
        raise ValueError("VIPER's immutable reference differs from the sealed native archive.")
    ack = {
        "generation": manifest["generation"],
        "source_commit": manifest["source_commit"],
        "execution_id": manifest["execution_id"],
        "instance_id": manifest["instance_id"],
        "archive_sha256": manifest["archive_sha256"],
        "cloud_roundtrip_verified": True,
        "transport": "viper_cloud",
        "cloud_references": {path: ref.model_dump(mode="json") for path, ref in references.items()},
        "verified_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
    }
    atomic_json(manifest_path.parent / "ack.json", ack)
    return ack


def require_generation_authorization(path: Path, manifest: dict[str, Any],
                                     assignment: dict[str, Any], resume: dict[str, Any]) -> None:
    """Admit current generations or exact preserved manifests from an approved resume."""
    identity = (manifest["instance_id"], manifest["execution_id"])
    if identity == (assignment["instance_id"], assignment["execution_id"]):
        return
    preserved = resume.get("preserved_generations", {}).get(manifest["generation"], {})
    expected = (preserved.get("manifest_sha256"), preserved.get("archive_sha256"),
                preserved.get("instance_id"), preserved.get("execution_id"),
                preserved.get("source_commit"))
    actual = (digest_file(path), manifest["archive_sha256"], manifest["instance_id"],
              manifest["execution_id"], manifest["source_commit"])
    if expected != actual:
        raise PermissionError("Preserved generation is not bound to this explicit resume.")


def run(root: Path, worker: str, assignment: dict[str, Any], cloud_config: dict[str, str],
        max_hours: float, resume: dict[str, Any] | None = None) -> None:
    """Drain durable generation files with bounded retries and an exclusive uploader."""
    import fcntl

    require_workload_identity(assignment["service_account"])
    output = root / "baseline_results/full_data_prompt_20261107" / worker
    output.mkdir(parents=True, exist_ok=True)
    with (output / "upload.lock").open("a+") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        cloud = cloud_service(root, assignment["project"])
        deadline = time.monotonic() + max_hours * 3600
        while time.monotonic() < deadline:
            for path in sorted((output / "transfer").glob("*/ready.json")):
                manifest = json.loads(path.read_text())
                ack_path = path.parent / "ack.json"
                if ack_path.exists():
                    if not acknowledgment_matches(manifest, json.loads(ack_path.read_text())):
                        raise ValueError("Existing acknowledgment differs from its sealed generation.")
                    continue
                if manifest["worker"] != worker:
                    raise ValueError("Queued generation names another worker.")
                require_generation_authorization(path, manifest, assignment, resume or {})
                try:
                    ack = publish_one(root, path, cloud, cloud_config["owner"], cloud_config["workspace"])
                    print(json.dumps({"event": "viper_generation_verified", **ack}), flush=True)
                except Exception as exc:
                    atomic_json(output / "upload-error.json", {
                        "generation": manifest["generation"], "error": str(exc),
                        "utc": dt.datetime.now(dt.timezone.utc).isoformat(),
                    })
                    time.sleep(15)
                    break
            pending = [path for path in (output / "transfer").glob("*/ready.json")
                       if not (path.parent / "ack.json").exists()]
            if pending:
                time.sleep(2)
                continue
            final = output / "transfer" / ("publication-complete-" + assignment["execution_id"]) / "ack.json"
            if final.exists():
                final_ack = json.loads(final.read_text())
                if final_ack.get("execution_id") == assignment["execution_id"]:
                    atomic_json(output / "upload-complete.json", final_ack)
                    return
            failed = output / "transfer" / ("worker-failed-" + assignment["execution_id"]) / "ack.json"
            if failed.exists() and json.loads(failed.read_text()).get("execution_id") == assignment["execution_id"]:
                return
            time.sleep(2)
        raise TimeoutError("Bounded VIPER publication window ended; local recovery bytes remain.")


def main() -> None:
    """Run the independent publication service for one manifest-selected worker."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--worker", choices=["worker1", "worker2"], required=True)
    parser.add_argument("--approval", type=Path, required=True)
    parser.add_argument("--max-hours", type=float, default=22)
    args = parser.parse_args()
    if not 0 < args.max_hours <= 23:
        raise ValueError("Uploader duration must fit the allocation deadline.")
    from viper.repository import resolve_root
    approval = json.loads(args.approval.read_text())
    run(resolve_root(), args.worker, approval["assignments"][args.worker],
        approval["cloud"], args.max_hours, approval.get("resumes", {}).get(args.worker, {}))


if __name__ == "__main__":
    main()
