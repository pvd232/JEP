#!/usr/bin/env python3
"""Monitor manifest-selected Spot workers and clean up only their owned resources.

VIPER publication runs asynchronously on each worker under its attached identity.
This controller uses the existing administrator connection for lifecycle actions.
Unverified checkpoints keep their recovery disk; a successful final export permits
deletion of the exact task-owned boot disk recorded in the allocation manifest.
"""
from __future__ import annotations

import argparse
import concurrent.futures
import datetime as dt
import json
import hashlib
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


def cleanup(assignment: dict, account: str, verified: bool, delete_disk: bool) -> dict:
    """Delete the exact task VM, retaining recovery bytes until verified export."""
    instance = describe(assignment, account)
    if instance is not None:
        require_ok(run(["gcloud", "compute", "instances", "delete", assignment["instance_name"],
                        "--keep-disks=all", *flags(assignment, account)], 180))
    disk_deleted = False
    disk = assignment.get("boot_disk")
    if verified and delete_disk and disk:
        result = run(["gcloud", "compute", "disks", "describe", disk["name"],
                      *flags(assignment, account), "--format=json"], 60)
        info = json.loads(require_ok(result))
        if (info["id"] != disk["id"] or info.get("users")
                or info.get("labels", {}).get("task") != TASK):
            raise PermissionError("Recovery disk identity, ownership or attachment changed.")
        require_ok(run(["gcloud", "compute", "disks", "delete", disk["name"],
                        *flags(assignment, account)], 180))
        disk_deleted = True
    return {"instance": assignment["instance_name"], "instance_deleted": True,
            "disk_deleted": disk_deleted, "recovery_disk_preserved": not disk_deleted}


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


def verify_cloud_archive(uri: str, manifest: dict, assignment: dict, account: str) -> dict:
    """Stream independent cloud bytes on the controller before deleting a recovery disk."""
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
                    proofs.append(verify_cloud_archive(uri, entry['manifest'], assignment, account))
                verified = True
                (args.local / f"{worker}-final-viper-receipt.json").write_text(json.dumps(proofs, indent=2) + "\n")
                return {"worker": worker, "status": "training_collected_test_still_locked",
                        "trials": len(last["trials"]), "controller_cloud_proofs": proofs}
            if last and last["status"] == "failed_preserved":
                failure_at = failure_at or time.monotonic()
                if not obj["ready"] or time.monotonic() - failure_at > 120:
                    raise RuntimeError(json.dumps(last.get("failure", {})))
            time.sleep(20)
        raise TimeoutError("Allocation collection deadline ended; recovery disk retained.")
    finally:
        receipt = cleanup(assignment, account, verified, args.delete_verified_disks)
        (args.local / f"{worker}-cleanup.json").write_text(json.dumps(receipt, indent=2) + "\n")
        print(json.dumps({"event": "resource_cleanup", "worker": worker, **receipt}), flush=True)


def main() -> None:
    """Run bounded lifecycle monitors for the worker set in one approved manifest."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True)
    parser.add_argument("--local", type=Path, required=True)
    parser.add_argument("--approval", type=Path, required=True)
    parser.add_argument("--max-hours", type=float, default=22)
    parser.add_argument("--delete-verified-disks", action="store_true")
    args = parser.parse_args()
    if not 0 < args.max_hours <= 23:
        raise ValueError("Controller duration must fit the allocation deadline.")
    args.approval = json.loads(args.approval.read_text())
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
    records = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=len(assignments)) as pool:
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
