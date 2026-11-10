"""Bind the frozen JEP workload to the shared bounded GCP L4 provider."""

import argparse
import base64
import gzip
import hashlib
import json
import os
import subprocess
import sys
import tarfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
config = json.loads((HERE / "gcp_provider.json").read_text())
provider_scripts = Path(config["provider_scripts"])
if not (provider_scripts / "gcp_l4_provider.py").is_file():
    raise RuntimeError(
        "Deploy the pinned run-gcp-l4-job skill package before using this adapter"
    )
for filename, expected in config["provider_files"].items():
    if (
        hashlib.sha256((provider_scripts / filename).read_bytes()).hexdigest()
        != expected
    ):
        raise RuntimeError("Shared provider bytes differ from the pinned deployment")
sys.path.insert(0, str(provider_scripts))
import capacity_advisor
import gcp_l4_provider as provider

ROOT = Path(config["worktree"])
RUN = Path(config["run_dir"])
PROJECT = config["project"]
NAME = config["resource_name"]
LABEL = config["labels"]["task"]
BUCKET = config["workload_bucket"]


def startup(payload):
    encoded = base64.b64encode(gzip.compress(json.dumps(payload).encode())).decode()
    parts = [encoded[i : i + 150000] for i in range(0, len(encoded), 150000)]
    worker = base64.b64encode((HERE / "gpu_worker.py").read_bytes()).decode()
    advisor = base64.b64encode(
        (provider_scripts / "capacity_advisor.py").read_bytes()
    ).decode()
    script = (
        "#!/bin/bash\nset -euo pipefail\nmkdir -p /var/lib/jep-moral-pilot\nexec > >(tee -a /var/lib/jep-moral-pilot/startup.log /dev/ttyS0) 2>&1\necho MORAL_BOOT\n/usr/bin/python3 - <<'BOOT'\nimport base64,gzip,urllib.request,hashlib\nfrom pathlib import Path\nr=Path('/var/lib/jep-moral-pilot')\nbase='http://metadata.google.internal/computeMetadata/v1/instance/attributes/'\nparts=[]\nfor i in range("
        + str(len(parts))
        + "):\n q=urllib.request.Request(base+'moral-payload-'+str(i),headers={'Metadata-Flavor':'Google'})\n parts.append(urllib.request.urlopen(q,timeout=10).read())\nraw=gzip.decompress(base64.b64decode(b''.join(parts)))\nassert hashlib.sha256(raw).hexdigest()=='"
        + hashlib.sha256(json.dumps(payload).encode()).hexdigest()
        + "'\n(r/'payload.json').write_bytes(raw)\n(r/'worker.py').write_bytes(base64.b64decode('"
        + worker
        + "'))\n(r/'capacity_advisor.py').write_bytes(base64.b64decode('"
        + advisor
        + "'))\nBOOT\n/usr/bin/python3 -m pip install 'transformers==4.57.1' 'peft==0.17.1' 'jinja2>=3.1.0' accelerate requests > /var/lib/jep-moral-pilot/install.log 2>&1\n/usr/bin/python3 -m pip freeze > /var/lib/jep-moral-pilot/environment.txt\nnvidia-smi\n/usr/bin/python3 -u /var/lib/jep-moral-pilot/worker.py\necho MORAL_WORKER_EXIT\n"
    )
    items = [
        dict(key="startup-script", value=script),
        dict(key="install-nvidia-driver", value="True"),
    ] + [dict(key="moral-payload-" + str(i), value=p) for i, p in enumerate(parts)]
    assert max(len(x["value"].encode()) for x in items) < 262144
    assert sum(len(x["value"].encode()) + len(x["key"]) for x in items) < 512000
    return items


def collect(payload):
    if (RUN / "collection.json").exists():
        return True
    j = provider.ledger()
    if not j["allocations"]:
        return False
    zone = j["allocations"][-1]["zone"]
    common = [
        "--project=" + PROJECT,
        "--zone=" + zone,
        "--account=dev-vm@pvd-dev-232.iam.gserviceaccount.com",
        "--tunnel-through-iap",
        "--ssh-key-file=/home/pvd2112_columbia_edu/.ssh/google_compute_engine",
        "--quiet",
    ]
    cmd = [
        "gcloud",
        "compute",
        "ssh",
        "machina@" + NAME,
        *common,
        "--ssh-flag=-oBatchMode=yes",
        "--ssh-flag=-oConnectTimeout=10",
        "--command=test -f /var/lib/jep-moral-pilot/transfer_ready.json && cat /var/lib/jep-moral-pilot/transfer_ready.json",
    ]
    status = subprocess.run(cmd, capture_output=True, text=True, timeout=45)
    if status.returncode:
        if any(x in status.stderr for x in ["PERMISSION_DENIED", "HTTP 403"]):
            raise RuntimeError(status.stderr[-1000:])
        return False
    if not status.stdout.strip():
        return False
    ready = json.loads(status.stdout)
    dest = RUN / "gpu_return.tar.gz"
    result = subprocess.run(
        [
            "gcloud",
            "compute",
            "scp",
            "machina@" + NAME + ":/var/lib/jep-moral-pilot/return.tar.gz",
            str(dest),
            *common,
        ],
        capture_output=True,
        text=True,
        timeout=90,
    )
    if result.returncode:
        raise RuntimeError(result.stderr[-1000:])
    assert provider.sha(dest) == ready["sha256"]
    folder = RUN / "gpu_return"
    folder.mkdir(exist_ok=True)
    with tarfile.open(dest) as archive:
        for member in archive.getmembers():
            assert member.isfile() and (folder / member.name).resolve().is_relative_to(
                folder.resolve()
            )
        archive.extractall(folder, filter="data")
    manifest = json.loads((folder / "result_manifest.json").read_text())
    for name, proof in manifest.items():
        assert provider.sha(folder / name) == proof["sha256"]
    assert (
        json.loads((folder / "compute.json").read_text())["encoder"]
        == payload["encoder"]
    )
    provider.save(
        RUN / "collection.json",
        dict(
            vm_id=str(j["allocations"][-1]["id"]),
            files=manifest,
            bundle_sha256=provider.sha(dest),
            transport="existing authenticated IAP",
            verified_at=provider.now(),
        ),
    )
    return True


def closeout():
    script = HERE / "analyze.py"
    if script.exists():
        subprocess.run([sys.executable, str(script), "--resume"], cwd=ROOT, check=True)
    else:
        provider.update(
            phase="inference_retained_analysis_pending",
            next_action="Run analyze.py on retained embeddings; never repeat inference.",
        )


def upgrade_legacy_collection():
    """Bind an original verified receipt to its sole recorded worker under the lock."""
    path = RUN / "collection.json"
    if not path.exists():
        return
    original = path.read_bytes()
    receipt = json.loads(original)
    if "vm_id" in receipt:
        return
    resources = provider.ledger()
    state = json.loads((RUN / "state.json").read_text())
    worker_id = str(state.get("gpu", {}).get("id"))
    records = [r for r in resources["allocations"] if str(r.get("id")) == worker_id]
    if len(records) != 1:
        raise RuntimeError("Legacy collection needs one unambiguous owned worker")
    record = records[0]
    if str(state.get("gpu", {}).get("id")) != str(record["id"]):
        raise RuntimeError("Legacy state and ledger worker identities disagree")
    if provider.sha(RUN / "gpu_return.tar.gz") != receipt["bundle_sha256"]:
        raise RuntimeError("Legacy retained bundle changed")
    for name, proof in receipt.get("files", {}).items():
        artifact = (RUN / "gpu_return" / name).resolve()
        if (
            not artifact.is_relative_to((RUN / "gpu_return").resolve())
            or provider.sha(artifact) != proof["sha256"]
        ):
            raise RuntimeError("Legacy retained artifact changed")
    if any(
        not r.get("deleted") and str(r.get("id")) != worker_id
        for r in resources["allocations"]
    ):
        raise RuntimeError("Reconcile other surviving workers before legacy binding")
    if record.get("deleted"):
        if not record.get("cleanup_verified_at"):
            raise RuntimeError("Legacy cleanup verification is missing")
    else:
        live = provider.compute(
            "zones/" + record["zone"] + "/instances/" + NAME, absent=True
        )
        if live is not None:
            provider.owned(live, record)
        disk = provider.compute(
            "zones/" + record["zone"] + "/disks/" + NAME, absent=True
        )
        if disk is not None and str(disk["id"]) != str(record["disk_id"]):
            raise RuntimeError("Legacy disk identity changed")
    backup = RUN / "collection.pre-provider.json"
    if backup.exists() and backup.read_bytes() != original:
        raise RuntimeError("Preserve the existing legacy receipt backup")
    if not backup.exists():
        backup.write_bytes(original)
    receipt.update(
        vm_id=str(record["id"]),
        legacy_binding=dict(
            original_receipt_sha256=hashlib.sha256(original).hexdigest(),
            resource_ledger_sha256=provider.sha(provider.resourcefile()),
            verified_at=provider.now(),
        ),
    )
    provider.save(path, receipt)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--cleanup-only", action="store_true")
    parser.add_argument("--plan-only", action="store_true")
    parser.add_argument("--plan-output", type=Path)
    parser.add_argument(
        "--plan-machine-type",
        choices=[capacity_advisor.MACHINE_TYPE, capacity_advisor.HOST_MEMORY_FALLBACK],
        default=capacity_advisor.MACHINE_TYPE,
    )
    args = parser.parse_args()
    if args.plan_only:
        output = args.plan_output or RUN / "diagnostics" / (
            "capacity_plan_" + str(time.time_ns()) + ".json"
        )
        plan = provider.capacity_plan(output, args.plan_machine_type)
        print(
            json.dumps(
                dict(
                    path=str(output),
                    ranked=plan["ranked"],
                    unknown_regions=[
                        x["region"]
                        for x in plan["region_reports"]
                        if x["status"] == "unknown"
                    ],
                )
            )
        )
        return
    with provider.execution_lock():
        try:
            state = json.loads((RUN / "state.json").read_text())
            if not args.cleanup_only and (
                state.get("phase", "").startswith("closed")
                or state.get("phase") == "complete"
            ):
                print(
                    json.dumps(
                        dict(phase=state["phase"], action="retained_outputs_preserved")
                    )
                )
                return
            upgrade_legacy_collection()
            frozen = json.loads((RUN / "frozen_v2.json").read_text())
            for n, h in frozen["files"].items():
                assert provider.sha(RUN / n) == h, "Frozen data/config changed"
            if args.cleanup_only:
                if not (RUN / "collection.json").exists():
                    raise RuntimeError("Retain output bytes before cleanup")
                for r in provider.ledger()["allocations"]:
                    if not r.get("deleted"):
                        provider.cleanup(r)
                return
            q = json.loads((RUN / "qwen_selection.json").read_text())
            encoder = json.loads((RUN / "encoder_identity.json").read_text())
            payload = dict(
                tasks=json.loads((RUN / "tasks.json").read_text()),
                encoder=encoder,
                selection=q["selected"],
                archive=q["archive"],
                bucket=BUCKET,
                result_object="moral_geometry_transfer_20261110/"
                + provider.sha(RUN / "frozen_v2.json")[:16]
                + "/"
                + provider.sha(HERE / "gpu_worker.py")[:16]
                + "/return.tar.gz",
                worker_sha256=provider.sha(HERE / "gpu_worker.py"),
            )
            payload["met_reasoner"] = None
            payload["capacity_advisor_sha256"] = provider.sha(
                provider_scripts / "capacity_advisor.py"
            )
            payload["compute_deadline_utc"] = json.loads(
                (RUN / "design_v2.json").read_text()
            )["deadline_utc"]
            payload["extension_cases"] = json.loads(
                (RUN / "extension_cases.json").read_text()
            )
            provider.save(
                RUN / "payload_identity.json",
                dict(
                    met_reasoner=payload["met_reasoner"],
                    extension_sha256=provider.sha(RUN / "extension_cases.json"),
                    worker_sha256=payload["worker_sha256"],
                    capacity_advisor_sha256=payload["capacity_advisor_sha256"],
                    compute_deadline_utc=payload["compute_deadline_utc"],
                    encoder=payload["encoder"],
                ),
            )
            provider.save(
                RUN / "controller_execution.json",
                dict(
                    argv=sys.argv,
                    python=sys.executable,
                    source_revision=subprocess.check_output(
                        ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
                    ).strip(),
                    worker_sha256=payload["worker_sha256"],
                    frozen_sha256=provider.sha(RUN / "frozen_v2.json"),
                    started_at=provider.now(),
                    owner_pid=os.getpid(),
                    unknown_hosted_run_id=None,
                ),
            )
            provider.update(
                owner_pid=os.getpid(),
                owner_relinquished=False,
                active_design_sha256=provider.sha(RUN / "design_v2.json"),
                next_action="Inspect this durable controller and resource ledger; no duplicate allocation.",
            )
            provider.save(RUN / "controller_payload.json", payload)
            provider.supervise(payload, collect, closeout)
        except Exception as error:
            provider.event("controller_error", error=repr(error))
            provider.update(
                phase="controller_attention",
                error=repr(error),
                next_action="Reconcile the actual job, resource intents and surviving writers before recovery",
            )
            raise


provider.configure(config, startup)
if __name__ == "__main__":
    try:
        main()
    except provider.ExecutionBusy:
        print(json.dumps(dict(action="healthy_owner_preserved")))
