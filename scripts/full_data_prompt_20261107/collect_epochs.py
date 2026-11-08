#!/usr/bin/env python3
"""Inspect or explicitly monitor approved workers through Columbia's keyless runner.

Read-only inspection is the default. Monitor mode may stop only its matching
completed/failed assignment, never delete instances or disks. Unexpected access,
transport or verification errors retain the worker and its independent deadline.
This candidate does not migrate or modify any already-running collector.
"""
from __future__ import annotations

import argparse
import concurrent.futures
import datetime as dt
import json
import hashlib
import fcntl
import os
import sys
from contextlib import ExitStack, contextmanager
import re
import tempfile
import threading
from pathlib import Path
import shlex
import subprocess
import time

from csts_pilot.full_data_prompt_lease import validate_placement
from csts_pilot.full_data_prompt_worker import acknowledgment_matches

REMOTE_ROOT = "/home/machina/jep-full-data-task-20261107/repo"
TASK = "jep-full-data-20261107"


def run(args: list[str], timeout: int = 120) -> subprocess.CompletedProcess:
    """Run a bounded cloud command without shell interpolation."""
    return subprocess.run(args, capture_output=True, text=True, timeout=timeout)


def require_ok(result: subprocess.CompletedProcess) -> str:
    """Expose provider failures without presenting a partial action as successful."""
    if result.returncode:
        raise RuntimeError(result.stderr[-1800:] or result.stdout[-1800:])
    return result.stdout


def flags(assignment: dict, account: str) -> list[str]:
    """Bind every lifecycle call to its declared account, project and zone."""
    return [f"--project={assignment['project']}", f"--zone={assignment['zone']}",
            f"--account={account}", "--quiet"]


def describe(assignment: dict, account: str) -> dict | None:
    """Require immutable instance identity and task ownership before cleanup."""
    result = run(["gcloud", "compute", "instances", "describe", assignment["instance_name"],
                  *flags(assignment, account), "--format=json"], 60)
    if result.returncode and ("was not found" in result.stderr or "Not Found" in result.stderr):
        return None
    instance = json.loads(require_ok(result))
    if (instance["id"] != assignment["instance_id"]
            or instance.get("labels", {}).get("task") != TASK):
        raise PermissionError("Instance identity or task label differs from the allocation.")
    return instance


def cleanup(assignment: dict, account: str, verified: bool, delete_disk: bool = False) -> dict:
    """Stop the exact owned instance after a terminal outcome; preserve every disk."""
    if delete_disk:
        raise PermissionError("Keyless lifecycle control cannot delete recovery disks.")
    instance = describe(assignment, account)
    if instance is None:
        return {"instance": assignment["instance_name"], "status": "ABSENT",
                "recovery_disk_preserved": True, "instance_deleted": False, "disk_deleted": False}
    if instance["status"] != "TERMINATED":
        require_ok(run(["gcloud", "compute", "instances", "stop", assignment["instance_name"],
                        *flags(assignment, account)], 180))
    final = describe(assignment, account)
    if final is None or final["status"] != "TERMINATED":
        raise RuntimeError("Assigned worker shutdown was not verified.")
    return {"instance": assignment["instance_name"], "status": "TERMINATED",
            "recovery_disk_preserved": True, "instance_deleted": False, "disk_deleted": False,
            "artifacts_verified": verified}


def load_keyless_context(profile_path: Path, approval_path: Path) -> tuple[dict, dict]:
    """Verify the installed runner, real attached principal and exact approval bytes.

    This must run inside cloud-project's project environment. Its readiness probe
    performs read-only calls and does not imply IAP, guest SSH or storage access.
    """
    if profile_path.is_symlink() or not profile_path.is_file():
        raise ValueError("A regular project runtime profile is required.")
    profile = json.loads(profile_path.read_text())
    identity = profile.get("job_identity", {})
    account = identity.get("service_account_email", "")
    if (identity.get("mode") != "attached_service_account"
            or re.fullmatch(r'[a-z0-9-]+@[a-z0-9-]+\.iam\.gserviceaccount\.com', account) is None):
        raise PermissionError("The controller requires its attached workload identity.")
    settings = profile.get("resolved", {}).get("project_environment", {})
    for key, expected in (("CLOUDSDK_CORE_ACCOUNT", account),
                          ("CLOUDSDK_CONFIG", settings.get("CLOUDSDK_CONFIG")),
                          ("CLOUD_DEV_CONFIG", str(profile_path))):
        if not expected or os.environ.get(key) != expected:
            raise PermissionError("Launch the candidate through the matching cloud-project environment.")
    forbidden = {"GOOGLE_APPLICATION_CREDENTIALS", "GOOGLE_OAUTH_ACCESS_TOKEN",
                 "CLOUDSDK_ACTIVE_CONFIG_NAME", "GCE_METADATA_HOST", "GCE_METADATA_IP", "GCE_METADATA_ROOT"}
    if any(k in forbidden or k.startswith(("CLOUDSDK_AUTH_", "CLOUDSDK_API_ENDPOINT_OVERRIDES_")) for k in os.environ):
        raise PermissionError("The controller environment contains a credential or endpoint override.")
    script = Path(profile["paths"]["install_root"]) / "bin" / "probe_identity.py"
    check = run([sys.executable, str(script), "--profile", str(profile_path), "--workload"], 120)
    receipt = json.loads(require_ok(check))
    if (receipt.get("workload_access_verified") is not True
            or receipt.get("controller_account") != account
            or receipt.get("resource_project") != "mantra-477901"):
        raise PermissionError("The keyless host/destination identity check did not pass.")
    if approval_path.is_symlink() or not approval_path.is_file():
        raise ValueError("A regular approval manifest is required.")
    raw = approval_path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != receipt.get("manifest_sha256"):
        raise PermissionError("Controller approval differs from the profile-bound manifest.")
    approval = json.loads(raw)
    if (approval.get("controller_account") != account
            or approval.get("source_commit") != receipt.get("source_commit")):
        raise PermissionError("Controller account or source differs from the verified context.")
    if os.environ.get("CLOUDSDK_CORE_PROJECT") != receipt["resource_project"]:
        raise PermissionError("Runtime resource project differs from the verified workload target.")
    return profile, receipt


@contextmanager
def controller_locks(profile: dict, assignments: dict):
    """Exclude duplicate controllers on Columbia regardless of output-directory choice.

    This is a host-local exclusion, not cross-host fencing. A live old controller
    must finish its assignment before this candidate may take ownership.
    """
    directory = Path(profile["paths"]["state_root"]) / "collector-locks"
    directory.mkdir(mode=0o700, parents=True, exist_ok=True)
    with ExitStack() as stack:
        for assignment in sorted(assignments.values(), key=lambda a: (a["project"], a["instance_id"])):
            name = assignment["project"] + "-" + assignment["instance_id"] + ".lock"
            path = directory / name
            if path.is_symlink():
                raise PermissionError("Controller lock must not be a symlink.")
            stream = stack.enter_context(path.open("a+"))
            try:
                fcntl.flock(stream, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError as error:
                raise RuntimeError("Another Columbia controller owns this instance.") from error
        yield


def read_worker(assignment: dict, account: str, worker: str) -> dict:
    """Read only study state and generation receipts through the established IAP route."""
    base = f"{REMOTE_ROOT}/baseline_results/full_data_prompt_20261107/{worker}"
    program = f"""import json,pathlib,hashlib
p=pathlib.Path({base!r})
s=json.loads((p/'state.json').read_text()) if (p/'state.json').exists() else None
generations=[]
for path in sorted((p/'transfer').glob('*/ready.json')):
 if path.is_symlink() or not path.resolve().is_relative_to(p.resolve()):raise ValueError('Invalid generation path')
 manifest=json.loads(path.read_text());a=path.parent/'ack.json'
 if a.is_symlink():raise ValueError('Invalid acknowledgment path')
 generations.append({{'manifest':manifest,'manifest_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
                     'ack':json.loads(a.read_text()) if a.exists() else None,
                     'ack_sha256':hashlib.sha256(a.read_bytes()).hexdigest() if a.exists() else None}})
c=p/'completion.json'
if c.is_symlink():raise ValueError('Invalid completion path')
print(json.dumps({{'state':s,'generations':generations,'completion':json.loads(c.read_text()) if c.exists() else None}}))
"""
    obj = json.loads(require_ok(run(
        ["gcloud", "compute", "ssh", f"machina@{assignment['instance_name']}",
         *flags(assignment, account), "--tunnel-through-iap",
         "--command=python3 -c " + shlex.quote(program)], 90)))
    obj["ready"] = [entry["manifest"] for entry in obj["generations"]
                    if not entry["ack"] or not acknowledgment_matches(entry["manifest"], entry["ack"])]
    return obj


def validate_completion(worker: str, assignment: dict, obj: dict) -> None:
    """Require terminal publication and valid receipts for the complete sealed inventory."""
    state = obj['state']
    terminal = 'publication-complete-' + assignment['execution_id']
    if state.get('completion_generation') != terminal:
        raise ValueError('Worker has no terminal publication for this execution.')
    inventory = []
    found_terminal = False
    seen = set()
    for entry in obj['generations']:
        manifest, ack = entry['manifest'], entry['ack']
        generation = manifest['generation']
        if (generation in seen or manifest['worker'] != worker
                or re.fullmatch(r'[A-Za-z0-9_-]+', generation) is None
                or not ack or not acknowledgment_matches(manifest, ack)):
            raise ValueError('Completion contains a missing, duplicated or mismatched generation receipt.')
        seen.add(generation)
        if generation == terminal:
            found_terminal = (ack.get('transport') == 'viper_cloud'
                              and bool(ack.get('cloud_references'))
                              and manifest['instance_id'] == assignment['instance_id']
                              and manifest['execution_id'] == assignment['execution_id'])
        else:
            inventory.append({'generation': generation, 'manifest_sha256': entry['manifest_sha256'],
                              'ack_sha256': entry['ack_sha256']})
    completion = obj.get('completion') or {}
    if (not found_terminal or inventory != state.get('publication_inventory')
            or completion.get('generations') != inventory
            or completion.get('source_commit') != state['source_commit']
            or completion.get('lease') != state['lease'] or completion.get('worker') != worker):
        raise ValueError('Terminal receipt does not bind the complete generation inventory.')


def cloud_archive_uri(worker: str, manifest: dict, ack: dict, cloud: dict) -> str:
    """Resolve an exact current VIPER archive or the study's preserved legacy archive."""
    archive = f"{REMOTE_ROOT}/baseline_results/full_data_prompt_20261107/{worker}/transfer/{manifest['generation']}/native.tar"
    if manifest['archive'] != archive:
        raise ValueError('Archive reference leaves the worker generation namespace.')
    references = ack.get('cloud_references')
    if references:
        path = archive.removeprefix(REMOTE_ROOT + '/')
        reference = references.get(path, {})
        location = reference.get('stored_at', {})
        if (reference.get('sha256') != manifest['archive_sha256']
                or reference.get('bytes') != manifest['archive_size']
                or location.get('kind') != 'gcs' or location.get('path') != path
                or any(location.get(key) != cloud[key] for key in ('bucket','prefix','owner','workspace'))
                or re.fullmatch(r'[0-9a-f]{64}', location.get('revision', '')) is None):
            raise ValueError('VIPER reference differs from the declared immutable archive.')
        return ('gs://' + cloud['bucket'] + '/' + cloud['prefix'] + '/' + cloud['owner'] + '/'
                + cloud['workspace'] + '/' + location['revision'] + '/' + path)
    prefix = ('gs://' + cloud['bucket'] + '/viper/pvd232/jep_full_data_prompt_20261107/'
              + manifest['source_commit'] + '/' + worker + '/' + manifest['execution_id']
              + '/' + manifest['generation'])
    if ack.get('cloud_prefix') != prefix:
        raise ValueError('Legacy archive is outside its original verified study namespace.')
    return prefix + '/native.tar'


def verify_cloud_archive(uri: str, manifest: dict, assignment: dict, account: str,
                         artifact_prefix: str) -> dict:
    """Stream independent cloud bytes on the controller before deleting a recovery disk."""
    if not artifact_prefix.endswith("/") or not uri.startswith(artifact_prefix):
        raise PermissionError("Artifact URI leaves the configured storage boundary.")
    digest = hashlib.sha256()
    size = 0
    with tempfile.TemporaryFile() as errors:
        process = subprocess.Popen(['gcloud','storage','cat',uri,
                                    '--project=' + assignment['project'], '--account=' + account,
                                    '--quiet'], stdout=subprocess.PIPE, stderr=errors)
        timer = threading.Timer(900, process.kill)
        timer.start()
        try:
            for block in iter(lambda: process.stdout.read(4 * 1024 * 1024), b''):
                digest.update(block); size += len(block)
            result = process.wait(timeout=10)
        finally:
            timer.cancel()
            if process.poll() is None: process.kill(); process.wait()
        if result or size != manifest['archive_size'] or digest.hexdigest() != manifest['archive_sha256']:
            errors.seek(0)
            raise ValueError('Controller cloud verification failed: ' + errors.read(1200).decode(errors='replace'))
    return {'uri': uri, 'bytes': size, 'sha256': digest.hexdigest(), 'controller_verified': True}


def monitor(worker: str, args: argparse.Namespace) -> dict:
    """Observe one independent worker and finalize its resources after export or failure."""
    assignment = args.approval["assignments"][worker]
    account = args.approval["controller_account"]
    deadline = time.monotonic() + args.max_hours * 3600
    last = None
    started = time.monotonic()
    failure_at = None
    verified = False
    terminal_outcome = False
    try:
        while time.monotonic() < deadline:
            instance = describe(assignment, account)
            if instance is None or instance["status"] == "TERMINATED":
                raise RuntimeError("Spot worker stopped or disappeared; recovery disk retained.")
            if instance["status"] != "RUNNING":
                time.sleep(15)
                continue
            obj = read_worker(assignment, account, worker)
            if not obj["state"] and time.monotonic() - started > 300:
                raise RuntimeError("Training did not start within the five-minute allocation window.")
            if obj["state"]:
                last = obj["state"]
                (args.local / f"{worker}-latest-state.json").write_text(json.dumps(last, indent=2) + "\n")
                if (last["source_commit"] != args.source
                        or last.get("lease", {}).get("execution_id") != assignment["execution_id"]
                        or not last.get("lease", {}).get("deadline_verified")):
                    raise ValueError("Worker source or execution lease differs from this launch.")
            if last and last["status"] == "assigned_training_complete_test_not_opened":
                validate_completion(worker, assignment, obj)
                proofs = []
                for entry in obj['generations']:
                    uri = cloud_archive_uri(worker, entry['manifest'], entry['ack'], args.approval['cloud'])
                    proofs.append(verify_cloud_archive(uri, entry['manifest'], assignment, account, args.artifact_prefix))
                verified = True
                terminal_outcome = True
                (args.local / f"{worker}-final-viper-receipt.json").write_text(json.dumps(proofs, indent=2) + "\n")
                return {"worker": worker, "status": "training_collected_test_still_locked",
                        "trials": len(last["trials"]), "controller_cloud_proofs": proofs}
            if last and last["status"] == "failed_preserved":
                failure_at = failure_at or time.monotonic()
                if not obj["ready"] or time.monotonic() - failure_at > 120:
                    terminal_outcome = True
                    raise RuntimeError("Worker reported a terminal failure; recovery artifacts retained.")
            time.sleep(20)
        terminal_outcome = bool(last)
        raise TimeoutError("Allocation collection deadline ended; recovery disk retained.")
    finally:
        if terminal_outcome:
            receipt = cleanup(assignment, account, verified, False)
        else:
            receipt = {"instance": assignment["instance_name"], "status": "NO_LIFECYCLE_ACTION",
                       "reason": "Unverified access/transport/state failure or interruption; retain independent deadline.",
                       "recovery_disk_preserved": True, "instance_deleted": False, "disk_deleted": False}
        (args.local / f"{worker}-cleanup.json").write_text(json.dumps(receipt, indent=2) + "\n")
        print(json.dumps({"event": "resource_cleanup", "worker": worker, **receipt}), flush=True)


def main() -> None:
    """Default to read-only inspection; require explicit ownership for lifecycle monitoring."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True)
    parser.add_argument("--local", type=Path, required=True)
    parser.add_argument("--approval", type=Path, required=True)
    parser.add_argument("--max-hours", type=float, default=22)
    parser.add_argument("--profile", type=Path, default=os.environ.get("CLOUD_DEV_CONFIG"))
    parser.add_argument("--monitor", action="store_true", help="Explicitly assume an idle/new assignment's lifecycle")
    args = parser.parse_args()
    if not 0 < args.max_hours <= 23:
        raise ValueError("Controller duration must fit the allocation deadline.")
    if args.profile is None:
        parser.error("--profile or CLOUD_DEV_CONFIG is required; use the keyless cloud-project runner")
    profile, context = load_keyless_context(args.profile, args.approval)
    args.artifact_prefix = context["artifact_prefix"]
    raw = args.approval.read_bytes()
    if hashlib.sha256(raw).hexdigest() != context["manifest_sha256"]:
        raise PermissionError("Approval changed after the identity preflight.")
    args.approval = json.loads(raw)
    if args.approval.get("source_commit") != args.source or args.approval.get("user_execution_approved") is not True:
        raise PermissionError("Controller manifest is not the approved source.")
    assignments = args.approval["assignments"]
    if not assignments or len(assignments) > 2:
        raise ValueError("The approved study uses at most two independent workers.")
    identities = set()
    for worker, assignment in assignments.items():
        validate_placement(worker, assignment)
        key = assignment["project"], assignment["instance_id"]
        if key in identities:
            raise ValueError("Two worker labels cannot share one instance.")
        identities.add(key)
    args.local.mkdir(parents=True, exist_ok=True)
    if not args.monitor:
        observations = []
        for worker, assignment in assignments.items():
            instance = describe(assignment, context["controller_account"])
            observations.append({"worker": worker, "instance_id": assignment["instance_id"],
                                 "status": instance["status"] if instance else "ABSENT"})
        print(json.dumps({"mode": "READ_ONLY", "account": context["controller_account"],
                          "instances": observations, "lifecycle_action": False}), flush=True)
        return
    records = []
    with controller_locks(profile, assignments), concurrent.futures.ThreadPoolExecutor(max_workers=len(assignments)) as pool:
        pending = {pool.submit(monitor, worker, args): worker for worker in assignments}
        for future in concurrent.futures.as_completed(pending):
            worker = pending[future]
            try:
                record = future.result()
            except Exception as exc:
                record = {"worker": worker, "status": "failed_preserved", "reason": str(exc)}
            records.append(record)
            print(json.dumps(record), flush=True)
    (args.local / "collection-final.json").write_text(json.dumps(records, indent=2) + "\n")
    if any(r["status"] != "training_collected_test_still_locked" for r in records):
        raise SystemExit(2)


if __name__ == "__main__":
    main()
