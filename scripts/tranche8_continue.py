"""Resume the frozen, audited proposition capture; retain raw native checkpoints.

This module is invoked only by the pinned tranche-8 operator.  It deliberately
does not launch training.  Source, gate and split identities are checked before
any paid generation, and failed CLI attempts remain available for inspection.
"""

import argparse
import base64
import fcntl
import hashlib
import importlib.util
import json
import os
import re
import shlex
import shutil
import subprocess
import sys
import tarfile
import time
from pathlib import Path
from typing import Any

REPOSITORY = "pvd232/JEP"
WORK_ROOT = Path("/tmp/jep-tranche8-worker-20261026")
GENERATION_ROOT = Path("/tmp/jep-proposition-input-20261026")
GPU_ROOT = "/home/machina/jep-csts-answer-input-20261026"
GPU_PYTHON = "/home/machina/jep-format-env/bin/python"
GCLOUD = "/Users/machina/google-cloud-sdk/bin/gcloud"
GCLOUD_FLAGS = [
    "--account=pvd2112@columbia.edu",
    "--project=mantra-477901",
    "--zone=asia-northeast3-a",
    "--tunnel-through-iap",
]
EXPECTED = {
    "training": {
        "items": 13744,
        "inputs": "0a99ac4ec215eda3131b094292cfee380544b32e885770a49f4929803eeca68f",
        "groups": "0b5c2b42199d482f78cb089162761c706c1f05a075ab310dcd81f12776108edb",
        "representatives": "354f775ddb7d82c2be8c4effc167a1503c7def11945fea031c0d76e54392568a",
        "source": "4058b7f63a5285ebdb5061f24f7f2907e76e2ddc7c99480bfd39fc69062a7d01",
    },
    "validation": {
        "items": 3590,
        "inputs": "1129660ff464d9af2154cce1af5677661dfee5c6797bad06abe5daf49e761dae",
        "groups": "0ee536b63e8e6c359355b81d20a65b1cea1f713668f18223c81e7832b970f708",
        "representatives": "4f5fdb99d20cc98f7f2b0efcf37e4d8ffcb1a29596ba29554d745f2f805df1ba",
        "source": "f01ec22320c590e381ede0b378895cdd241cd8079e06b18715bc13d2921a4273",
    },
}


class ContinuationFailure(RuntimeError):
    """A safe error message with no process output or credential content."""


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def save(path: Path, value: Any) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n"
    )
    temporary.replace(path)


def progress(event: str, **values: Any) -> None:
    print(
        "OPERATOR_PROGRESS "
        + json.dumps(
            {"phase": "full_capture", "event": event, **values}, allow_nan=False
        ),
        flush=True,
    )


def run(command: list[str], directory: Path, label: str, timeout: int) -> bytes:
    result = subprocess.run(command, capture_output=True, timeout=timeout, check=False)
    (directory / (label + ".stdout")).write_bytes(result.stdout)
    (directory / (label + ".stderr")).write_bytes(result.stderr)
    if result.returncode:
        raise ContinuationFailure(
            f"{label} exited with status {result.returncode}; private logs retained."
        )
    return result.stdout


def fetch(path: str, commit: str, directory: Path, destination: Path) -> bytes:
    gh = shutil.which("gh") or next(
        (
            str(p)
            for p in (Path("/opt/homebrew/bin/gh"), Path("/usr/local/bin/gh"))
            if p.is_file()
        ),
        None,
    )
    if gh is None:
        raise ContinuationFailure("The existing gh executable is unavailable.")
    label = "fetch_" + destination.name.replace(".", "_")
    payload = json.loads(
        run(
            [gh, "api", f"repos/{REPOSITORY}/contents/{path}?ref={commit}"],
            directory,
            label,
            60,
        )
    )
    if payload.get("type") != "file" or payload.get("encoding") != "base64":
        raise ContinuationFailure("Pinned GitHub source is not a regular file.")
    data = base64.b64decode("".join(payload["content"].split()), validate=True)
    if hashlib.sha1(
        b"blob " + str(len(data)).encode() + b"\0" + data
    ).hexdigest() != payload.get("sha"):
        raise ContinuationFailure("Pinned GitHub blob identity differs.")
    if destination.exists() and destination.read_bytes() != data:
        raise ContinuationFailure(
            "Preserve the existing pinned source; its bytes differ."
        )
    destination.write_bytes(data)
    return data


def load_capture(path: Path) -> Any:
    spec = importlib.util.spec_from_file_location("frozen_proposition_capture", path)
    if spec is None or spec.loader is None:
        raise ContinuationFailure("Cannot load the frozen capture module.")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def verify_gate(
    gate: dict[str, Any],
    capture: Any,
    source: bytes,
    audit_files: dict[str, str] | None = None,
    gate_text: str | None = None,
    verifier: Any = None,
) -> dict[str, str]:
    """Keep audited policy/source identity separate from operational lock repairs."""
    if verifier is None:
        from csts_pilot import proposition_provenance as verifier
    if audit_files is None or gate_text is None:
        raise ContinuationFailure(
            "Complete frozen audit evidence is required before capture."
        )
    verifier.verify_frozen_audit(gate_text, audit_files, capture)
    if source != Path(capture.__file__).read_bytes():
        raise ContinuationFailure(
            "Operational capture bytes differ from their pinned module."
        )
    if gate.get("capture_source_sha256") != verifier.AUDITED_CAPTURE_SHA256:
        raise ContinuationFailure(
            "The original audited capture source identity differs."
        )
    return {
        "generation_template_sha256": sha(capture.PROMPT.encode()),
        "schema_sha256": sha(json.dumps(capture.SCHEMA, ensure_ascii=False).encode()),
        "model_alias": capture.MODEL,
        "reasoning_effort": capture.EFFORT,
    }


def load_verified_policy(
    source_commit: str, directory: Path, source: bytes, gate_bytes: bytes, capture: Any
) -> tuple[dict[str, str], Any, dict[str, str]]:
    """Fetch the exact standalone verifier and its audit dependency closure."""
    helper = directory / "proposition_provenance.py"
    fetch("csts_pilot/proposition_provenance.py", source_commit, directory, helper)
    verifier = load_capture(helper)
    if sha(gate_bytes) != verifier.AUDIT_GATE_SHA256:
        raise ContinuationFailure(
            "The fidelity gate differs from the reviewed immutable receipt."
        )
    gate = json.loads(gate_bytes)
    audit = directory / "audit_evidence"
    audit.mkdir(exist_ok=True)
    evidence = {}
    for name in gate["audit_files"]:
        if Path(name).name != name:
            raise ContinuationFailure("Invalid frozen audit filename.")
        evidence[name] = fetch(
            "training_outputs/proposition_audit/" + name,
            source_commit,
            directory,
            audit / name,
        ).decode()
    bindings = verify_gate(
        gate, capture, source, evidence, gate_bytes.decode(), verifier
    )
    return bindings, verifier, evidence


def verify_inventory(capture: Any) -> dict[str, list[dict[str, Any]]]:
    root = GENERATION_ROOT / "full_inventory"
    inventory = json.loads((root / "inventory_manifest.json").read_text())
    result = {}
    seen_ids: set[str] = set()
    seen_groups: set[str] = set()
    for split, expected in EXPECTED.items():
        for suffix, key in (
            ("inputs", "inputs"),
            ("groups", "groups"),
            ("representatives_audit", "representatives"),
        ):
            if sha((root / f"{split}_{suffix}.json").read_bytes()) != expected[key]:
                raise ContinuationFailure(f"Frozen {split} {suffix} inventory differs.")
        if inventory[split].get("original_sha256") != expected["source"]:
            raise ContinuationFailure(f"Frozen {split} source identity differs.")
        items = json.loads((root / f"{split}_inputs.json").read_text())
        groups = json.loads((root / f"{split}_groups.json").read_text())
        capture.validate_inputs(items)
        ids = {row["id"] for row in items}
        if (
            len(items) != expected["items"]
            or set(groups) != ids
            or ids & seen_ids
            or set(groups.values()) & seen_groups
        ):
            raise ContinuationFailure(
                "Split sizes, identities or source-group separation differ."
            )
        seen_ids.update(ids)
        seen_groups.update(groups.values())
        result[split] = items
    return result


def closed_batches(root: Path) -> dict[str, Path]:
    result = {}
    for split in EXPECTED:
        for directory in sorted((root / split).glob("batch_*")):
            receipt = directory / "receipt.json"
            try:
                data = json.loads(receipt.read_text())
                if data.get("status") in {"complete", "failed"}:
                    result[f"{split}/{directory.name}"] = directory
            except (OSError, ValueError):
                continue
    return result


def counts(root: Path) -> dict[str, int]:
    complete: dict[str, int] = {}
    failed = 0
    for relative, directory in closed_batches(root).items():
        receipt = json.loads((directory / "receipt.json").read_text())
        if receipt["status"] == "complete":
            complete[relative.split("-attempt_")[0]] = receipt["items"]
        else:
            failed += 1
    return {
        "completed_items": sum(complete.values()),
        "total_items": 17334,
        "completed_batches": len(complete),
        "failed_attempts": failed,
    }


def retryable_output_failures(root: Path, capture: Any) -> bool:
    """Retry response defects only; tools, policy and CLI failures stop work."""
    failed = 0
    for directory in closed_batches(root).values():
        receipt = json.loads((directory / "receipt.json").read_text())
        if receipt["status"] != "failed":
            continue
        failed += 1
        if receipt.get("returncode") != 0:
            return False
        try:
            capture.checked_events(directory / "events.jsonl")
        except (OSError, ValueError, TypeError, KeyError):
            return False
        try:
            response = json.loads((directory / "response.json").read_text())
            capture.checked_records(
                json.loads((directory / "inputs.json").read_text()), response
            )
        except (ValueError, TypeError, KeyError):
            continue
        except OSError:
            return False
        # An otherwise valid response failed for an unexpected local reason.
        return False
    return failed > 0


def checkpoint(
    root: Path, directory: Path, state: dict[str, Any], final: bool = False
) -> dict[str, Any]:
    """Copy closed raw attempts to owner storage; do not delete either copy."""
    closed = closed_batches(root)
    added = sorted(set(closed) - set(state.get("archived_batches", [])))
    if not added and not final:
        return state
    index = len(state.get("checkpoints", [])) + 1
    name = f"capture-checkpoint-{index:04d}-{time.time_ns()}.tar.gz"
    archive = directory / name
    with tarfile.open(archive, "w:gz") as stream:
        for relative in added:
            stream.add(closed[relative], arcname=f"capture/{relative}", recursive=True)
        for path in (
            directory / "proposition_capture.py",
            directory / "audit_gate.json",
            root / "launch.json",
        ):
            stream.add(path, arcname=f"source/{path.name}")
        if final:
            for split in EXPECTED:
                for basename in ("manifest.json", "records.json"):
                    path = root / split / basename
                    if path.exists():
                        stream.add(path, arcname=f"capture/{split}/{basename}")
            for path in root.glob("propositions_tranche8*.json"):
                stream.add(path, arcname=f"capture/{path.name}")
            stream.add(
                GENERATION_ROOT / "full_inventory", arcname="inventory", recursive=True
            )
    archive_hash = sha(archive.read_bytes())
    name = f"capture-checkpoint-{index:04d}-{archive_hash[:16]}.tar.gz"
    archive = archive.rename(directory / name)
    staging = f"/tmp/jep-tranche8-{archive_hash}.tar.gz"
    run(
        [
            GCLOUD,
            "compute",
            "scp",
            str(archive),
            f"jep-csts-format-20261021:{staging}",
            *GCLOUD_FLAGS,
        ],
        directory,
        f"checkpoint_{index:04d}_scp",
        180,
    )
    target = f"{GPU_ROOT}/answer_input_results/proposition_capture_full/{root.name}"
    script = f"import hashlib,pathlib,shutil\ns=pathlib.Path({staging!r})\nb=s.read_bytes()\nassert hashlib.sha256(b).hexdigest()=={archive_hash!r}\nd=pathlib.Path({target!r});d.mkdir(parents=True,exist_ok=True)\np=d/{name!r}\nassert not p.exists() or hashlib.sha256(p.read_bytes()).hexdigest()=={archive_hash!r}\nif not p.exists(): shutil.copyfile(s,p)\nprint('checkpoint_verified')\n"
    # The SSH account owns staging; permit only owner read for the verified copy.
    command = (
        "chmod 644 "
        + shlex.quote(staging)
        + " && sudo -n -u machina "
        + GPU_PYTHON
        + " -c "
        + shlex.quote(script)
    )
    run(
        [
            GCLOUD,
            "compute",
            "ssh",
            "jep-csts-format-20261021",
            *GCLOUD_FLAGS,
            "--command=" + command,
        ],
        directory,
        f"checkpoint_{index:04d}_install",
        60,
    )
    receipt = {
        "name": name,
        "sha256": archive_hash,
        "bytes": archive.stat().st_size,
        "native_path": f"{target}/{name}",
        "closed_batch_attempts": len(added),
        "final": final,
        "cloud_publication": "pending_native_queue",
    }
    state = {
        "archived_batches": sorted(set(state.get("archived_batches", [])) | set(added)),
        "checkpoints": [*state.get("checkpoints", []), receipt],
    }
    save(root / "checkpoints.json", state)
    progress("native_checkpoint_saved", counts=counts(root), checkpoint=receipt)
    return state


def full_capture(source_commit: str, concurrency: int = 4) -> dict[str, Any]:
    directory = WORK_ROOT / "full_capture" / source_commit
    directory.mkdir(parents=True, exist_ok=True)
    source = fetch(
        "csts_pilot/proposition_capture.py",
        source_commit,
        directory,
        directory / "proposition_capture.py",
    )
    gate_bytes = fetch(
        "csts_data/propositions_tranche8_audit_gate.json",
        source_commit,
        directory,
        directory / "audit_gate.json",
    )
    capture = load_capture(directory / "proposition_capture.py")
    bindings, verifier, audit_files = load_verified_policy(
        source_commit, directory, source, gate_bytes, capture
    )
    inventory = verify_inventory(capture)
    # Same frozen generation settings share one output across controller commits.
    root = GENERATION_ROOT / ("full_v2_" + bindings["generation_template_sha256"][:16])
    root.mkdir(parents=True, exist_ok=True)
    launch = {
        "generation_source_sha256": verifier.AUDITED_CAPTURE_SHA256,
        "audit_gate_sha256": sha(gate_bytes),
        **bindings,
        "inventory": EXPECTED,
        "batch_size": 64,
        "maximum_one_item_per_source_group_per_request": True,
    }
    if (root / "launch.json").exists() and json.loads(
        (root / "launch.json").read_text()
    ) != launch:
        raise ContinuationFailure("Existing full capture launch bindings differ.")
    if not (root / "launch.json").exists():
        save(root / "launch.json", launch)
    operational = root / "operational_capture_sources.json"
    previous = json.loads(operational.read_text()) if operational.exists() else []
    implementation = {
        "source_commit": source_commit,
        "capture_sha256": sha(source),
        "verifier_sha256": sha((directory / "proposition_provenance.py").read_bytes()),
        "audited_capture_sha256": verifier.AUDITED_CAPTURE_SHA256,
    }
    if implementation not in previous:
        save(operational, [*previous, implementation])
    state = (
        json.loads((root / "checkpoints.json").read_text())
        if (root / "checkpoints.json").exists()
        else {}
    )
    started = time.monotonic()
    last_checkpoint = started
    last_checkpoint_items = counts(root)["completed_items"]
    progress(
        "frozen_gate_and_inventory_verified",
        counts=counts(root),
        manifest=launch,
        source_commit=source_commit,
    )
    for split, items in inventory.items():
        output = root / split
        for attempt in range(1, 4):
            command = [
                sys.executable,
                "-I",
                str(directory / "proposition_capture.py"),
                "--inputs",
                str(GENERATION_ROOT / "full_inventory" / f"{split}_inputs.json"),
                "--groups",
                str(GENERATION_ROOT / "full_inventory" / f"{split}_groups.json"),
                "--output",
                str(output),
                "--split",
                split,
                "--batch-size",
                "64",
                "--concurrency",
                str(concurrency),
                "--timeout",
                "1200",
            ]
            if output.exists():
                command.append("--resume")
            log_id = f"{split}-{time.time_ns()}-attempt{attempt}"
            with (
                (directory / (log_id + ".stdout")).open("wb") as stdout,
                (directory / (log_id + ".stderr")).open("wb") as stderr,
            ):
                child = subprocess.Popen(
                    command,
                    cwd=directory,
                    stdin=subprocess.DEVNULL,
                    stdout=stdout,
                    stderr=stderr,
                )
                while child.poll() is None:
                    time.sleep(15)
                    current = counts(root)
                    progress(
                        "generating",
                        split=split,
                        attempt=attempt,
                        counts=current,
                        elapsed_seconds=round(time.monotonic() - started),
                    )
                    if (
                        time.monotonic() - last_checkpoint >= 600
                        or current["completed_items"] - last_checkpoint_items >= 500
                    ):
                        try:
                            state = checkpoint(root, directory, state)
                            last_checkpoint = time.monotonic()
                            last_checkpoint_items = current["completed_items"]
                        except (
                            OSError,
                            ValueError,
                            subprocess.SubprocessError,
                            ContinuationFailure,
                        ):
                            progress(
                                "native_checkpoint_retry_pending",
                                split=split,
                                counts=current,
                            )
                            last_checkpoint = time.monotonic()
                returncode = child.returncode
            if returncode == 0:
                manifest = json.loads((output / "manifest.json").read_text())
                records = json.loads((output / "records.json").read_text())
                capture.checked_records(items, {"records": records})
                if manifest.get("status") != "complete" or manifest.get(
                    "records_sha256"
                ) != sha((output / "records.json").read_bytes()):
                    raise ContinuationFailure(
                        "Completed partition aggregation differs."
                    )
                break
            progress(
                "capture_invocation_failed_preserved",
                split=split,
                attempt=attempt,
                counts=counts(root),
                retry=attempt < 3,
            )
            state = checkpoint(root, directory, state)
            if not retryable_output_failures(root, capture):
                raise ContinuationFailure(
                    "Capture stopped on a CLI, event, tool or unexpected local failure; no policy or authentication retry attempted."
                )
        else:
            raise ContinuationFailure(
                f"{split} exhausted three bounded capture attempts; all raw artifacts preserved."
            )
    records = []
    partitions = {}
    for split in EXPECTED:
        partitions[split] = json.loads((root / split / "manifest.json").read_text())
        groups = json.loads(
            (GENERATION_ROOT / "full_inventory" / f"{split}_groups.json").read_text()
        )
        records.extend(
            verifier.check_partition(
                inventory[split], groups, root / split, partitions[split], capture
            )
        )
    capture.checked_records(
        inventory["training"] + inventory["validation"], {"records": records}
    )
    save(root / "propositions_tranche8.json", records)
    manifest = {
        **launch,
        "source_commit": source_commit,
        "records_sha256": sha((root / "propositions_tranche8.json").read_bytes()),
        "items": len(records),
        "partitions": partitions,
        "semantic_fidelity_independently_verified": False,
        "audit_gate_passed_for_frozen_generation": True,
    }
    save(root / "propositions_tranche8_manifest.json", manifest)
    provenance = verifier.make_provenance(
        root, GENERATION_ROOT / "full_inventory", audit_files
    )
    save(root / "propositions_tranche8_provenance.json", provenance)
    state = checkpoint(root, directory, state, final=True)
    return {
        "phase": "full_capture",
        "status": "complete",
        "counts": counts(root),
        "manifest": {
            **bindings,
            "items": len(records),
            "records_sha256": manifest["records_sha256"],
            "source_commit": source_commit,
            "capture_source_sha256": sha(source),
            "audit_gate_sha256": sha(gate_bytes),
        },
        "output_path": str(root),
        "checkpoints": state.get("checkpoints", []),
        "next_phase": "native_deploy_checks",
    }


def capture_status(source_commit: str) -> dict[str, Any]:
    directory = WORK_ROOT / "full_capture" / source_commit
    path = directory / "supervisor_receipt.json"
    if not path.exists():
        return {"phase": "full_capture", "status": "not_started"}
    receipt = json.loads(path.read_text())
    root = Path(receipt["output_path"])
    result = {
        "phase": "full_capture",
        "status": receipt["status"],
        "source_commit": source_commit,
        "counts": counts(root),
        "output_path": str(root),
        "controller_sha256": receipt["controller_sha256"],
    }
    if (directory / "result.json").exists():
        result.update(json.loads((directory / "result.json").read_text()))
    elif receipt["status"] in {"launching", "running"}:
        with (root / "supervisor.lock").open("a+") as lock:
            try:
                fcntl.flock(lock.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError:
                result["status"] = "running"
            else:
                # A launcher may be between Popen and acquiring its lock.
                if time.time() - receipt["started_unix"] > 30:
                    result["status"] = "interrupted"
    return result


def launch_capture(source_commit: str, concurrency: int) -> dict[str, Any]:
    """Bind and detach one durable supervisor so the worker remains available."""
    directory = WORK_ROOT / "full_capture" / source_commit
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / "supervisor_receipt.json"
    if path.exists():
        return capture_status(source_commit)
    source = fetch(
        "csts_pilot/proposition_capture.py",
        source_commit,
        directory,
        directory / "proposition_capture.py",
    )
    gate = fetch(
        "csts_data/propositions_tranche8_audit_gate.json",
        source_commit,
        directory,
        directory / "audit_gate.json",
    )
    capture = load_capture(directory / "proposition_capture.py")
    bindings, _, _ = load_verified_policy(
        source_commit, directory, source, gate, capture
    )
    verify_inventory(capture)
    root = GENERATION_ROOT / ("full_v2_" + bindings["generation_template_sha256"][:16])
    root.mkdir(parents=True, exist_ok=True)
    controller = directory / "full_capture_controller.py"
    controller_bytes = Path(__file__).read_bytes()
    if controller.exists() and controller.read_bytes() != controller_bytes:
        raise ContinuationFailure("The existing detached controller source differs.")
    controller.write_bytes(controller_bytes)
    receipt = {
        "status": "launching",
        "source_commit": source_commit,
        "output_path": str(root),
        "controller_sha256": sha(controller_bytes),
        "started_unix": time.time(),
        "concurrency": concurrency,
    }
    save(path, receipt)
    command = [
        sys.executable,
        "-I",
        str(controller),
        "--phase",
        "_full_capture_run",
        "--source-commit",
        source_commit,
        "--concurrency",
        str(concurrency),
    ]
    with (
        (directory / "supervisor.stdout").open("ab") as stdout,
        (directory / "supervisor.stderr").open("ab") as stderr,
    ):
        child = subprocess.Popen(
            command,
            cwd=directory,
            stdin=subprocess.DEVNULL,
            stdout=stdout,
            stderr=stderr,
            start_new_session=True,
        )
    receipt["pid"] = child.pid
    # The child owns receipt updates after launching; avoid overwriting running.
    if json.loads(path.read_text()).get("status") == "launching":
        save(path, receipt)
    return {
        **capture_status(source_commit),
        "status": "running",
        "pid": child.pid,
        "manifest": bindings,
        "next_phase": "full_capture_status",
    }


def supervise_capture(source_commit: str, concurrency: int) -> dict[str, Any]:
    directory = WORK_ROOT / "full_capture" / source_commit
    receipt_path = directory / "supervisor_receipt.json"
    receipt = json.loads(receipt_path.read_text())
    root = Path(receipt["output_path"])
    with (root / "supervisor.lock").open("a+") as lock:
        try:
            fcntl.flock(lock.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            raise ContinuationFailure(
                "Another full capture supervisor already owns this frozen bank."
            ) from None
        receipt.update(status="running", pid=os.getpid())
        save(receipt_path, receipt)
        try:
            result = full_capture(source_commit, concurrency)
        except Exception as error:  # noqa: BLE001 - operator boundary keeps private logs out of status
            result = {
                "phase": "full_capture",
                "status": "failed",
                "counts": counts(root),
                "error": str(error)
                if isinstance(error, ContinuationFailure)
                else "Capture supervisor failed; private logs and raw capture remain preserved.",
            }
        save(directory / "result.json", result)
        receipt.update(status=result["status"], finished_unix=time.time())
        save(receipt_path, receipt)
        return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--phase",
        choices=("full_capture", "full_capture_status", "_full_capture_run"),
        required=True,
    )
    parser.add_argument("--source-commit", required=True)
    parser.add_argument("--concurrency", type=int, choices=(1, 2, 3, 4), default=4)
    args = parser.parse_args()
    if re.fullmatch(r"[0-9a-f]{40}", args.source_commit) is None:
        parser.error("source-commit must be a complete Git commit")
    try:
        if args.phase == "full_capture":
            result = launch_capture(args.source_commit, args.concurrency)
        elif args.phase == "full_capture_status":
            result = capture_status(args.source_commit)
        else:
            result = supervise_capture(args.source_commit, args.concurrency)
    except Exception as error:  # noqa: BLE001 - operator boundary keeps private logs out of status
        result = {
            "phase": args.phase,
            "status": "failed",
            "error": str(error)
            if isinstance(error, ContinuationFailure)
            else "Continuation failed; private logs and raw capture remain preserved.",
        }
        print("OPERATOR_RESULT " + json.dumps(result), flush=True)
        raise SystemExit(1) from None
    print(
        "OPERATOR_RESULT " + json.dumps(result, ensure_ascii=False, allow_nan=False),
        flush=True,
    )


if __name__ == "__main__":
    main()
