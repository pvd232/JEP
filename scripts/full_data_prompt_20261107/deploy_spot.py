#!/usr/bin/env python3
"""Allocate task-owned L4 Spot capacity across an explicit East Asia region set.

A prepared snapshot supplies the existing runtime. Every request remains Spot;
stockouts advance to another discovered zone instead of changing quota or IAM.
The journal records attempted placements and immutable IDs for later cleanup.
"""
from __future__ import annotations

import argparse
import concurrent.futures
import datetime as dt
import fcntl
import json
import os
from pathlib import Path
import subprocess
from typing import Any

EAST_ASIA = ("asia-east1", "asia-east2", "asia-northeast1", "asia-northeast2", "asia-northeast3")
TASK = "jep-full-data-20261107"


def command(args: list[str], timeout: int = 180) -> subprocess.CompletedProcess:
    """Capture one bounded provider call without a shell or hidden credential state."""
    return subprocess.run(args, capture_output=True, text=True, timeout=timeout)


def checked(args: list[str], timeout: int = 180) -> str:
    """Require provider success before using its output as allocation evidence."""
    result = command(args, timeout)
    if result.returncode:
        raise RuntimeError(result.stderr[-2000:] or result.stdout[-2000:])
    return result.stdout


def save(path: Path, value: Any) -> None:
    """Commit the current allocation journal through one atomic JSON replacement."""
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(".partial")
    with temp.open("w") as stream:
        json.dump(value, stream, indent=2)
        stream.write("\n")
        stream.flush()
        os.fsync(stream.fileno())
    temp.replace(path)
    directory = os.open(path.parent, os.O_RDONLY)
    try:
        os.fsync(directory)
    finally:
        os.close(directory)


def admission_paths(project: str) -> tuple[Path, Path]:
    """Share one admission lock and unresolved-intent record on the sole controller."""
    root = Path.home() / ".local/state/jep-spot-allocations"
    root.mkdir(parents=True, exist_ok=True)
    return root / (project + ".lock"), root / (project + ".json")


def candidates(regions: list[str], zones: list[str], advice: list[dict]) -> list[tuple[str, str]]:
    """Prefer provider recommendations, then visit each discovered region and zone."""
    if not regions or len(set(regions)) != len(regions) or set(regions) - set(EAST_ASIA):
        raise ValueError("Select distinct authorized East Asia regions.")
    allowed = {zone for zone in zones if zone.rsplit("-", 1)[0] in regions}
    recommended = []
    for item in advice:
        for recommendation in item.get("recommendations", []):
            for shard in recommendation.get("shards", []):
                zone = shard.get("zone", "").rsplit("/", 1)[-1]
                machine = shard.get("machineType")
                if zone in allowed and machine in {"g2-standard-4", "g2-standard-8"}:
                    recommended.append((zone, machine))
    rank = {region: i for i, region in enumerate(regions)}
    recommended.sort(key=lambda item: rank[item[0].rsplit("-", 1)[0]])
    fallback = [(zone, "g2-standard-4") for zone in
                sorted(allowed, key=lambda zone: (rank[zone.rsplit("-", 1)[0]], zone))]
    result = []
    for item in recommended + fallback:
        if item not in result:
            result.append(item)
    return result


def cleanup_failed_create(name: str, zone: str, snapshot_id: str, common: list[str]) -> None:
    """Reconcile only resources absent before this exact snapshot-backed create intent."""
    result = command(["gcloud", "compute", "instances", "describe", name,
                      f"--zone={zone}", *common, "--format=json"], 60)
    if result.returncode == 0:
        instance = json.loads(result.stdout)
        if instance.get("labels", {}).get("task") != TASK:
            raise PermissionError("Partial instance is not owned by this task.")
        checked(["gcloud", "compute", "instances", "delete", name, "--keep-disks=all",
                 f"--zone={zone}", *common])
    elif "was not found" not in result.stderr and "Not Found" not in result.stderr:
        raise RuntimeError(result.stderr[-1500:])
    result = command(["gcloud", "compute", "disks", "describe", name,
                      f"--zone={zone}", *common, "--format=json"], 60)
    if result.returncode == 0:
        disk = json.loads(result.stdout)
        if disk.get("users") or disk.get("sourceSnapshotId") != snapshot_id:
            raise PermissionError("Partial boot disk is attached or has another source identity.")
        checked(["gcloud", "compute", "disks", "delete", name, f"--zone={zone}", *common])
    elif "was not found" not in result.stderr and "Not Found" not in result.stderr:
        raise RuntimeError(result.stderr[-1500:])


def main() -> None:
    """Provision at most one additional GPU using a bounded, journaled search."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", required=True)
    parser.add_argument("--account", required=True)
    parser.add_argument("--service-account", required=True)
    parser.add_argument("--snapshot", required=True)
    parser.add_argument("--name", required=True)
    parser.add_argument("--journal", type=Path, required=True)
    parser.add_argument("--regions", nargs="+", default=list(EAST_ASIA))
    parser.add_argument("--max-attempts", type=int, default=9)
    parser.add_argument("--max-hours", type=int, default=23)
    parser.add_argument("--max-gpus", type=int, default=2)
    parser.add_argument("--plan-only", action="store_true")
    args = parser.parse_args()
    if args.project != "mantra-477901" or not args.name.startswith("jep-"):
        raise PermissionError("This adapter is scoped to the authorized Mantra JEP fleet.")
    if not 1 <= args.max_attempts <= 15 or not 1 <= args.max_hours <= 23 or not 1 <= args.max_gpus <= 2:
        raise ValueError("Allocation attempts, duration and GPU count must fit the approved bounds.")
    common = [f"--project={args.project}", f"--account={args.account}", "--quiet"]
    args.journal.parent.mkdir(parents=True, exist_ok=True)
    lock_path, admission_path = admission_paths(args.project)
    with lock_path.open("a+") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        admission = json.loads(admission_path.read_text()) if admission_path.exists() else {}
        if admission.get("pending_intent"):
            raise RuntimeError("Reconcile the controller's unresolved allocation intent before admission.")
        if args.journal.exists():
            prior = json.loads(args.journal.read_text())
            if prior.get("allocation"):
                raise ValueError("An existing allocation requires explicit reconciliation.")
        inventory = json.loads(checked(["gcloud", "compute", "instances", "list", *common, "--format=json"]))
        if any(instance["name"] == args.name for instance in inventory):
            raise ValueError("Requested instance name already exists; reuse its recorded allocation.")
        used = sum(sum(int(gpu.get("acceleratorCount", 0)) for gpu in instance.get("guestAccelerators", []))
                   for instance in inventory if instance["status"] != "TERMINATED")
        quota = json.loads(checked(["gcloud", "compute", "project-info", "describe", *common, "--format=json"]))
        global_quota = next((q for q in quota.get("quotas", []) if q["metric"] == "GPUS_ALL_REGIONS"), None)
        if used >= args.max_gpus or global_quota is None or global_quota["usage"] >= global_quota["limit"]:
            raise RuntimeError("The approved GPU concurrency or project quota is already occupied.")
        types = json.loads(checked(["gcloud", "compute", "accelerator-types", "list",
                                   "--filter=name=nvidia-l4", *common, "--format=json"]))
        zones = [item["zone"].rsplit("/", 1)[-1] for item in types]
        def advise(region: str) -> dict:
            """Keep a missing capacity recommendation distinct from an allocation error."""
            result = command(["gcloud", "beta", "compute", "advice", "capacity",
                              "--provisioning-model=SPOT",
                              "--instance-selection-machine-types=g2-standard-4,g2-standard-8",
                              "--target-distribution-shape=ANY_SINGLE_ZONE", "--size=1",
                              f"--region={region}", *common, "--format=json"], 45)
            return json.loads(result.stdout) if result.returncode == 0 else {"advice_error": result.stderr[-600:]}
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
            advice = list(pool.map(advise, args.regions))
        plan = candidates(args.regions, zones, advice)[:args.max_attempts]
        journal = {"project": args.project, "name": args.name, "snapshot": args.snapshot,
                   "regions": args.regions, "candidates": plan, "capacity_advice": advice, "attempts": [],
                   "bootstrap_minutes": 10, "approved_run_hours": args.max_hours,
                   "started_utc": dt.datetime.now(dt.timezone.utc).isoformat()}
        save(args.journal, journal)
        if args.plan_only:
            print(json.dumps(journal))
            return
        snapshot = json.loads(checked(["gcloud", "compute", "snapshots", "describe", args.snapshot,
                                      *common, "--format=json"]))
        if snapshot.get("status") != "READY" or snapshot.get("labels", {}).get("task") != TASK:
            raise PermissionError("Prepared snapshot is not ready or belongs to another task.")
        for index, (zone, machine) in enumerate(plan, 1):
            existing_disk = command(["gcloud", "compute", "disks", "describe", args.name,
                                     f"--zone={zone}", *common, "--format=json"], 60)
            if existing_disk.returncode == 0:
                raise PermissionError("A pre-existing disk occupies the planned allocation name.")
            if "was not found" not in existing_disk.stderr and "Not Found" not in existing_disk.stderr:
                raise RuntimeError(existing_disk.stderr[-1500:])
            attempt = {"zone": zone, "machine": machine, "status": "requesting",
                       "boot_disk_absent_before_create": True}
            journal["attempts"].append(attempt)
            save(args.journal, journal)
            save(admission_path, {"pending_intent": {"name": args.name, "zone": zone,
                  "journal": str(args.journal), "utc": dt.datetime.now(dt.timezone.utc).isoformat()}})
            try:
                result = command([
                    "gcloud", "compute", "instances", "create", args.name, f"--zone={zone}",
                    f"--machine-type={machine}", "--provisioning-model=SPOT",
                    "--no-restart-on-failure", "--maintenance-policy=TERMINATE",
                    "--instance-termination-action=DELETE", f"--max-run-duration={args.max_hours}h",
                    "--metadata=startup-script=#!/bin/sh\n/sbin/shutdown -P +10\n",
                    "--preemption-notice-duration=120s", f"--source-snapshot={args.snapshot}",
                    "--boot-disk-size=350", "--boot-disk-type=pd-balanced", "--no-boot-disk-auto-delete",
                    "--network=default", "--subnet=default", "--no-address",
                    f"--service-account={args.service_account}", "--scopes=cloud-platform",
                    f"--labels=task={TASK},purpose=spot-training", *common, "--async", "--format=json",
                ], 120)
                if result.returncode == 0:
                    operation = json.loads(result.stdout)
                    if isinstance(operation, list): operation = operation[0]
                    attempt['operation'] = operation['name']
                    save(args.journal, journal)
                    save(admission_path, {'pending_intent': {'name': args.name, 'zone': zone,
                         'journal': str(args.journal), 'operation': operation['name']}})
                    waited = command(['gcloud','compute','operations','wait',operation['name'],
                                      f'--zone={zone}',*common,'--format=json'],900)
                    if waited.returncode:
                        attempt.update(status='operation_observation_failed', error=waited.stderr[-2000:])
                        save(args.journal, journal)
                        raise RuntimeError('Provider operation completion is unknown; admission intent retained: ' + operation['name'])
                    else:
                        completed = json.loads(waited.stdout)
                        if completed.get('status') != 'DONE':
                            attempt.update(status='provider_operation_still_pending')
                            save(args.journal, journal)
                            raise RuntimeError('Provider operation is not terminal; admission intent retained: ' + operation['name'])
                        if completed.get('error'):
                            result = subprocess.CompletedProcess([],1,'',json.dumps(completed['error']))
                        else:
                            result = command(['gcloud','compute','instances','describe',args.name,
                                              f'--zone={zone}',*common,'--format=json'],60)
            except subprocess.TimeoutExpired:
                attempt.update(status="provider_timeout_requires_reconciliation")
                save(args.journal, journal)
                cleanup_failed_create(args.name, zone, snapshot["id"], common)
                raise RuntimeError("Allocation timed out; reconcile its journal before another request.")
            attempt.update(returncode=result.returncode, error=result.stderr[-2000:])
            if result.returncode == 0:
                created = json.loads(result.stdout)
                instance = created[0] if isinstance(created, list) else created
                boot_source = next(d["source"] for d in instance["disks"] if d.get("boot"))
                boot_name = boot_source.rsplit("/", 1)[-1]
                disk = json.loads(checked(["gcloud", "compute", "disks", "describe", boot_name,
                                          f"--zone={zone}", *common, "--format=json"]))
                checked(["gcloud", "compute", "disks", "add-labels", boot_name, f"--zone={zone}",
                         f"--labels=task={TASK}", *common])
                allocation = {"instance_name": instance["name"], "instance_id": instance["id"],
                              "project": args.project, "zone": zone,
                              "service_account": args.service_account,
                              "boot_disk": {"name": boot_name, "id": disk["id"]}}
                attempt["status"] = "allocated"
                journal["allocation"] = allocation
                save(args.journal, journal)
                save(admission_path, {"last_allocation": allocation, "pending_intent": None})
                print(json.dumps(allocation))
                return
            attempt["status"] = "failed"
            save(args.journal, journal)
            cleanup_failed_create(args.name, zone, snapshot["id"], common)
            attempt["partial_resources_reconciled"] = True
            save(args.journal, journal)
            save(admission_path, {"pending_intent": None})
            # Capacity and quota failures can use another approved placement.
            if any(code in result.stderr for code in ("QUOTA_EXCEEDED", "quota exceeded", "Quota exceeded")):
                continue
            if not any(code in result.stderr for code in ("RESOURCE_POOL_EXHAUSTED", "stockout", "currently unavailable")):
                raise RuntimeError(result.stderr[-2000:])
        raise RuntimeError("No Spot L4 allocation succeeded within the bounded East Asia search.")


if __name__ == "__main__":
    main()
