"""Capture and score test propositions only after the native eligible release.

This standalone Mac transport uses existing authenticated gh/gcloud and the
exact pinned capture implementation. Importing it performs no remote actions.
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
import threading
import time
import traceback
from concurrent.futures import FIRST_COMPLETED, ThreadPoolExecutor, wait
from pathlib import Path
from typing import Any

REPOSITORY = "pvd232/JEP"
WORK_ROOT = Path("/tmp/jep-tranche8-worker-20261026/test_capture")
GENERATION_ROOT = Path("/tmp/jep-proposition-input-20261026")
GPU_ROOT = "/home/machina/jep-csts-proposition-lora-20261026"
PARENT_ROOT = "/home/machina/jep-csts-qwen-evidence-20261024"
GPU_PYTHON = "/home/machina/jep-format-env/bin/python"
GCLOUD = "/Users/machina/google-cloud-sdk/bin/gcloud"
FLAGS = ["--account=pvd2112@columbia.edu", "--project=mantra-477901", "--zone=asia-northeast3-a", "--tunnel-through-iap"]
VALIDATION_NAME = "proposition_lora_v2"
EVALUATION_NAME = "proposition_lora_v2_test"
POLICY_FIELDS = ("generation_template_sha256", "schema_sha256", "model_alias", "reasoning_effort")
ATTEMPT = re.compile(r"batch_([0-9]{4})(?:-attempt_([0-9]{2}))?")


class TestCaptureFailure(RuntimeError):
    """Only safe operational details are returned to the worker status."""


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def save(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    with temporary.open("w") as stream:
        stream.write(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n")
        stream.flush()
        os.fsync(stream.fileno())
    temporary.replace(path)


def preserve(path: Path, data: bytes) -> None:
    if path.exists() and path.read_bytes() != data:
        raise TestCaptureFailure("An existing pinned test capture artifact differs; preserve it for review.")
    if not path.exists():
        path.write_bytes(data)


def progress(event: str, **values: Any) -> None:
    print("OPERATOR_PROGRESS " + json.dumps({"phase": "eligible_test", "event": event, **values}, allow_nan=False), flush=True)


def run(command: list[str], directory: Path, label: str, timeout: int = 120) -> bytes:
    result = subprocess.run(command, capture_output=True, timeout=timeout, check=False)
    (directory / f"{label}.stdout").write_bytes(result.stdout)
    (directory / f"{label}.stderr").write_bytes(result.stderr)
    if result.returncode:
        raise TestCaptureFailure(f"{label} exited with status {result.returncode}; private logs retained.")
    return result.stdout


def remote(script: str, directory: Path, label: str, timeout: int = 120) -> dict[str, Any]:
    command = "sudo -n -u machina " + GPU_PYTHON + " -c " + shlex.quote(script)
    return json.loads(run([GCLOUD, "compute", "ssh", "jep-csts-format-20261021", *FLAGS, "--command=" + command], directory, label, timeout))


def preamble(commit: str) -> str:
    return (
        "import pathlib,json,hashlib,subprocess,os,shutil,time,base64\n"
        f"root=pathlib.Path({GPU_ROOT!r});parent=pathlib.Path({PARENT_ROOT!r});commit={commit!r}\n"
        "def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()\n"
        "def save(p,v):\n p.write_text(json.dumps(v,ensure_ascii=False,indent=2,allow_nan=False)+'\\n')\n"
        "def clean():\n"
        " assert subprocess.check_output(['git','-C',str(root),'rev-parse','HEAD'],text=True).strip()==commit,'Source commit differs.'\n"
        " assert not subprocess.check_output(['git','-C',str(root),'status','--porcelain','--untracked-files=no'],text=True).strip(),'Tracked source changed.'\n"
        "os.chdir(root)\n"
    )


def native_release(commit: str, directory: Path) -> dict[str, Any]:
    """The first remote operation checks eligibility before test data is opened."""
    script = preamble(commit) + (
        "clean()\n"
        "logs=root/'answer_input_results'/'test_capture_transport';logs.mkdir(parents=True,exist_ok=True)\n"
        f"command=[{GPU_PYTHON!r},'-m','csts_pilot.proposition_test','--phase','inventory','--root',str(root),'--parent-root',str(parent),'--validation-name',{VALIDATION_NAME!r}]\n"
        "with (logs/'inventory.stdout').open('ab') as out,(logs/'inventory.stderr').open('ab') as err:\n"
        " result=subprocess.run(command,cwd=root,stdout=out,stderr=err,timeout=300,check=False)\n"
        "assert result.returncode==0,'Native eligible inventory release did not pass.'\n"
        f"path=root/'answer_input_results'/{VALIDATION_NAME!r}/'test_inventory/pre_generation.json'\n"
        "release=json.loads(path.read_text())\n"
        "assert release.get('status')=='eligible_test_generation_released'\n"
        "assert release.get('labels_or_companions_in_generation_inputs') is False\n"
        "assert release.get('test_scores_used_for_selection') is False\n"
        "print(json.dumps({'release':release,'release_sha256':digest(path)},allow_nan=False))\n"
    )
    return remote(script, directory, "native_release", 360)


def fetch_inventory(commit: str, released: dict[str, Any], directory: Path) -> None:
    """Transfer only the already released source fields and opaque group IDs."""
    selection = released["release"]["selection_sha256"]
    script = preamble(commit) + (
        "clean()\nfrom csts_pilot.proposition_test import frozen_context\n"
        f"frozen=frozen_context(root,parent,{VALIDATION_NAME!r})\nassert frozen['selection_sha256']=={selection!r}\n"
        "inventory=frozen['validation_directory']/'test_inventory'\nrelease=inventory/'pre_generation.json'\n"
        f"assert digest(release)=={released['release_sha256']!r},'Test release changed.'\n"
        "result={}\n"
        "for name in ('generation_inputs.json','group_ids.json','pre_generation.json'):\n"
        " path=inventory/name;assert path.is_file() and not path.is_symlink()\n"
        " result[name]=base64.b64encode(path.read_bytes()).decode()\n"
        "print(json.dumps(result))\n"
    )
    payload = remote(script, directory, "source_only_inventory")
    if set(payload) != {"generation_inputs.json", "group_ids.json", "pre_generation.json"}:
        raise TestCaptureFailure("Unexpected fields in the released source-only inventory.")
    expected = {"generation_inputs.json": released["release"]["generation_inputs_sha256"], "group_ids.json": released["release"]["external_group_ids_sha256"], "pre_generation.json": released["release_sha256"]}
    for name, encoded in payload.items():
        data = base64.b64decode(encoded, validate=True)
        if sha(data) != expected[name]:
            raise TestCaptureFailure("Transferred test inventory bytes differ from the eligible release.")
        preserve(directory / name, data)


def fetch_capture(commit: str, directory: Path) -> tuple[Any, bytes]:
    gh = shutil.which("gh") or next((str(path) for path in (Path("/opt/homebrew/bin/gh"), Path("/usr/local/bin/gh")) if path.is_file()), None)
    if gh is None:
        raise TestCaptureFailure("The existing gh executable is unavailable.")
    payload = json.loads(run([gh, "api", f"repos/{REPOSITORY}/contents/csts_pilot/proposition_capture.py?ref={commit}"], directory, "fetch_capture"))
    if payload.get("type") != "file" or payload.get("encoding") != "base64":
        raise TestCaptureFailure("Pinned capture source is not a file.")
    source = base64.b64decode("".join(payload["content"].split()), validate=True)
    if hashlib.sha1(b"blob " + str(len(source)).encode() + b"\0" + source).hexdigest() != payload.get("sha"):
        raise TestCaptureFailure("Pinned capture source Git blob differs.")
    path = directory / "proposition_capture.py"
    preserve(path, source)
    spec = importlib.util.spec_from_file_location("frozen_test_proposition_capture", path)
    if spec is None or spec.loader is None:
        raise TestCaptureFailure("Cannot load the pinned capture source.")
    capture = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(capture)
    return capture, source


def frozen_policy(capture: Any, release: dict[str, Any]) -> dict[str, str]:
    bindings = {"generation_template_sha256": sha(capture.PROMPT.encode()), "schema_sha256": sha(json.dumps(capture.SCHEMA, ensure_ascii=False).encode()), "model_alias": capture.MODEL, "reasoning_effort": capture.EFFORT}
    if set(release.get("generation_policy", {})) != set(POLICY_FIELDS) or release["generation_policy"] != bindings:
        raise TestCaptureFailure("Test generation differs from the four frozen validation policy fields.")
    return bindings


def attempt_directories(output: Path, index: int | None = None) -> list[tuple[int, int, Path]]:
    found = []
    for directory in output.glob("batch_*"):
        match = ATTEMPT.fullmatch(directory.name)
        if match is None or directory.is_symlink() or not directory.is_dir():
            raise TestCaptureFailure("Unexpected existing batch path; preserve it for review.")
        batch, attempt = int(match[1]), int(match[2] or 1)
        if attempt < 1 or attempt > 3:
            raise TestCaptureFailure("A batch exceeded the durable maximum of three attempts.")
        if index is None or batch == index:
            found.append((batch, attempt, directory))
    if len({(batch, attempt) for batch, attempt, _ in found}) != len(found):
        raise TestCaptureFailure("Duplicate batch-attempt identities.")
    return sorted(found)


def response_failure_only(capture: Any, directory: Path, expected_items: list[dict[str, Any]]) -> bool:
    """Never retry CLI, tool, missing-file, authentication or local failures."""
    try:
        receipt = json.loads((directory / "receipt.json").read_text())
        if receipt.get("status") != "failed" or receipt.get("returncode") != 0:
            return False
        capture.checked_events(directory / "events.jsonl")
        inputs = json.loads((directory / "inputs.json").read_text())
        capture.validate_inputs(inputs)
        if inputs != expected_items:
            return False
        response_text = (directory / "response.json").read_text()
    except (OSError, ValueError, TypeError, KeyError):
        return False
    try:
        capture.checked_records(inputs, json.loads(response_text))
    except (ValueError, TypeError, KeyError):
        return True
    return False


def batch_counts(output: Path, total: int) -> dict[str, int]:
    complete, failed = {}, 0
    for batch, _, directory in attempt_directories(output):
        try:
            receipt = json.loads((directory / "receipt.json").read_text())
        except (OSError, ValueError):
            continue
        if receipt.get("status") == "complete":
            complete[batch] = receipt["items"]
        elif receipt.get("status") == "failed":
            failed += 1
    return {"completed_items": sum(complete.values()), "total_items": total, "completed_batches": len(complete), "failed_attempts": failed}


def checkpoint(root: Path, directory: Path, commit: str, selection: str, final: bool = False) -> dict[str, Any]:
    """Store closed raw attempts natively before retries and before evaluation."""
    state_path = root / "checkpoints.json"
    state = json.loads(state_path.read_text()) if state_path.exists() else {"archived_attempts": [], "checkpoints": []}
    closed = {}
    for _, _, attempt in attempt_directories(root / "test"):
        path = attempt / "receipt.json"
        try:
            terminal = json.loads(path.read_text()).get("status") in {"complete", "failed"}
        except (OSError, ValueError):
            terminal = False
        # Final is called only after the executor has joined every request.
        # It also preserves attempts that failed before writing their receipt.
        if final or terminal:
            closed[attempt.name] = attempt
    added = sorted(set(closed) - set(state["archived_attempts"]))
    if not added and not final:
        return state
    archive = directory / f"test-checkpoint-{time.time_ns()}.tar.gz"
    with tarfile.open(archive, "w:gz") as stream:
        for name in added:
            stream.add(closed[name], arcname=f"test/{name}", recursive=True)
        for name in ("launch.json", "generation_inputs.json", "group_ids.json", "pre_generation.json", "proposition_capture.py"):
            stream.add(root / name, arcname=f"source/{name}", recursive=False)
        if final:
            for path in (root / "test/manifest.json", root / "test/records.json", root / "propositions_tranche8_test.json", root / "propositions_tranche8_test_manifest.json"):
                if path.is_file():
                    stream.add(path, arcname=f"capture/{path.name}", recursive=False)
    archive_sha = sha(archive.read_bytes())
    name = f"test-checkpoint-{len(state['checkpoints']) + 1:04d}-{archive_sha[:16]}.tar.gz"
    archive = archive.rename(directory / name)
    staging = f"/tmp/jep-tranche8-test-{archive_sha}.tar.gz"
    run([GCLOUD, "compute", "scp", str(archive), f"jep-csts-format-20261021:{staging}", *FLAGS], directory, f"checkpoint_{len(state['checkpoints']) + 1}_scp", 240)
    run([GCLOUD, "compute", "ssh", "jep-csts-format-20261021", *FLAGS, "--command=chmod 644 " + shlex.quote(staging)], directory, "checkpoint_permissions")
    script = preamble(commit) + (
        "clean()\n"
        f"source=pathlib.Path({staging!r});assert digest(source)=={archive_sha!r}\n"
        f"target=root/'answer_input_results/proposition_capture_test'/{selection!r}/{name!r}\n"
        "target.parent.mkdir(parents=True,exist_ok=True);assert not target.is_symlink()\n"
        f"assert not target.exists() or digest(target)=={archive_sha!r}\n"
        "if not target.exists(): shutil.copyfile(source,target)\n"
        "os.environ.update({'VIRTUAL_ENV':'/home/machina/jep-format-env','PATH':'/home/machina/jep-format-env/bin:/usr/local/bin:/usr/bin:/bin'})\n"
        "from csts_pilot.proposition_archive import seal_one\n"
        "from viper.repository import read_source\nfrom viper.runtime import observe_python_env\n"
        "from viper.storage import ViperCloudDestination\n"
        "destination=ViperCloudDestination.model_validate(json.loads((root/'configs/csts-qwen-evidence.json').read_text())['publication_destination'])\n"
        "sealed=seal_one(root,target,digest(target),target.stat().st_size,read_source(root),observe_python_env(),destination)\n"
        "print(json.dumps({'status':'checkpoint_verified','native_path':str(target),'publication_queue':sealed['publication_queue']}))\n"
    )
    installed = remote(script, directory, "checkpoint_install", 1020)
    receipt = {"name": name, "sha256": archive_sha, "bytes": archive.stat().st_size, "native_path": installed["native_path"], "closed_attempts": len(added), "final": final, "publication_queue": installed["publication_queue"]}
    state["archived_attempts"] = sorted(set(state["archived_attempts"]) | set(added))
    state["checkpoints"].append(receipt)
    save(state_path, state)
    progress("raw_capture_checkpointed", checkpoint={key: receipt[key] for key in ("sha256", "bytes", "closed_attempts", "final")})
    return state


def capture_test(capture: Any, root: Path, directory: Path, commit: str, release: dict[str, Any], concurrency: int) -> dict[str, Any]:
    """Run at most four independent source-only requests with durable retries."""
    items = json.loads((root / "generation_inputs.json").read_text())
    groups = json.loads((root / "group_ids.json").read_text())
    capture.validate_inputs(items)
    if len(items) != release["unique_passage_conditions"]:
        raise TestCaptureFailure("The released canonical test inventory size differs.")
    selected = capture.batches(items, groups, 64)
    output = root / "test"
    output.mkdir(exist_ok=True)
    # All prior failures are checked, even when a later completed attempt exists.
    for batch, _, attempt in attempt_directories(output):
        if batch >= len(selected):
            raise TestCaptureFailure("An existing attempt is outside the frozen batch inventory.")
        receipt = json.loads((attempt / "receipt.json").read_text())
        if receipt.get("status") == "failed" and not response_failure_only(capture, attempt, selected[batch]):
            raise TestCaptureFailure("A preserved CLI/tool/local failure prevents automatic test capture retry.")
        if receipt.get("status") not in {"complete", "failed"}:
            raise TestCaptureFailure("An interrupted in-flight request requires owner review; no duplicate request launched.")
    manifest = {"split": "test", "input_file_sha256": sha((root / "generation_inputs.json").read_bytes()), "group_file_sha256": sha((root / "group_ids.json").read_bytes()), "items": len(items), "batches": len(selected), "batch_size": 64, "concurrency": concurrency, "maximum_one_item_per_source_group_per_request": True, "model_alias": capture.MODEL, "reasoning_effort": capture.EFFORT, "prompt_template_sha256": sha(capture.PROMPT.encode()), "schema_content_sha256": sha(json.dumps(capture.SCHEMA, ensure_ascii=False).encode()), "cli": capture.CLI, "status": "running"}
    save(output / "manifest.json", manifest)
    stopped, checkpoint_lock = threading.Event(), threading.Lock()

    def durable_checkpoint(final: bool = False) -> dict[str, Any]:
        with checkpoint_lock:
            return checkpoint(root, directory, commit, release["selection_sha256"], final)

    def one_batch(index: int) -> dict[str, Any]:
        try:
            attempts = attempt_directories(output, index)
            for _, _, attempt in attempts:
                if json.loads((attempt / "receipt.json").read_text()).get("status") == "complete":
                    return capture.completed_batch(selected[index], attempt, capture.CLI)
            while not stopped.is_set():
                number = max((number for _, number, _ in attempts), default=0) + 1
                if number > 3:
                    raise TestCaptureFailure("A test batch exhausted its durable three-attempt response budget.")
                target = output / (f"batch_{index:04d}" if number == 1 else f"batch_{index:04d}-attempt_{number:02d}")
                try:
                    return capture.capture_batch(selected[index], target, capture.CLI, 1200)
                except Exception as error:
                    retryable = response_failure_only(capture, target, selected[index])
                    if not retryable or number >= 3:
                        stopped.set()
                    # A raw native checkpoint must succeed before another request.
                    durable_checkpoint()
                    if not retryable:
                        raise TestCaptureFailure("Test capture stopped on a CLI, event, tool, authentication or unexpected local failure.") from error
                    attempts.append((index, number, target))
            raise TestCaptureFailure("Test capture stopped after another batch failed.")
        except BaseException:
            stopped.set()
            raise

    receipts: list[dict[str, Any] | None] = [None] * len(selected)
    try:
        with ThreadPoolExecutor(max_workers=concurrency) as pool:
            futures = {pool.submit(one_batch, index): index for index in range(len(selected))}
            try:
                pending = set(futures)
                last_checkpoint = time.monotonic()
                while pending:
                    done, pending = wait(pending, timeout=15, return_when=FIRST_COMPLETED)
                    for future in done:
                        receipts[futures[future]] = future.result()
                    progress("generating_test", counts=batch_counts(output, len(items)))
                    if time.monotonic() - last_checkpoint >= 600:
                        durable_checkpoint()
                        last_checkpoint = time.monotonic()
            except BaseException:
                stopped.set()
                for future in futures:
                    future.cancel()
                raise
        records = []
        for receipt in receipts:
            if receipt is None:
                raise TestCaptureFailure("A test batch has no completed receipt.")
            records.extend(json.loads((Path(receipt["directory"]) / "records.json").read_text()))
        checked = capture.checked_records(items, {"records": records})
        capture.write(output / "records.json", checked)
        manifest.update(status="complete", receipts=receipts, records_sha256=sha((output / "records.json").read_bytes()))
        save(output / "manifest.json", manifest)
        return manifest
    except BaseException as error:
        stopped.set()
        manifest.update(status="failed", error_type=type(error).__name__)
        save(output / "manifest.json", manifest)
        durable_checkpoint(final=True)
        raise


def import_bank(commit: str, directory: Path, root: Path, selection: str) -> dict[str, Any]:
    paths = {name: root / name for name in ("propositions_tranche8_test.json", "propositions_tranche8_test_manifest.json")}
    expected = {name: sha(path.read_bytes()) for name, path in paths.items()}
    archive = directory / f"test-bank-{time.time_ns()}.tar.gz"
    with tarfile.open(archive, "w:gz") as stream:
        for name, path in paths.items():
            stream.add(path, arcname=name, recursive=False)
    digest = sha(archive.read_bytes())
    staging = f"/tmp/jep-tranche8-test-bank-{digest}.tar.gz"
    run([GCLOUD, "compute", "scp", str(archive), f"jep-csts-format-20261021:{staging}", *FLAGS], directory, "test_bank_scp", 240)
    run([GCLOUD, "compute", "ssh", "jep-csts-format-20261021", *FLAGS, "--command=chmod 644 " + shlex.quote(staging)], directory, "test_bank_permissions")
    script = preamble(commit) + (
        "clean()\nimport tarfile\nfrom csts_pilot.proposition_test import frozen_context\n"
        f"assert frozen_context(root,parent,{VALIDATION_NAME!r})['selection_sha256']=={selection!r}\n"
        f"archive=pathlib.Path({staging!r});assert digest(archive)=={digest!r};expected={expected!r}\n"
        f"destination=root/'csts_data'/{('test_' + selection)!r};destination.mkdir(parents=True,exist_ok=True)\n"
        "with tarfile.open(archive,'r:gz') as stream:\n"
        " members=stream.getmembers();assert len(members)==len(expected) and {m.name for m in members}==set(expected)\n"
        " for member in members:\n"
        "  assert member.isfile() and member.name in expected\n"
        "  source=stream.extractfile(member);assert source is not None\n"
        "  data=source.read();assert hashlib.sha256(data).hexdigest()==expected[member.name]\n"
        "  target=destination/member.name;assert not target.is_symlink()\n"
        "  assert not target.exists() or target.read_bytes()==data\n"
        "  if not target.exists(): target.write_bytes(data)\n"
        "print(json.dumps({'status':'test_bank_imported','answers':str((destination/'propositions_tranche8_test.json').relative_to(root)),'manifest':str((destination/'propositions_tranche8_test_manifest.json').relative_to(root)),'source_inputs':expected}))\n"
    )
    return remote(script, directory, "test_bank_import")


def evaluate_native(commit: str, directory: Path, imported: dict[str, Any]) -> dict[str, Any]:
    """The native evaluate CLI, not this transport, owns the existing GPU lock."""
    script = preamble(commit) + (
        "clean()\n"
        "logs=root/'answer_input_results/test_capture_transport';logs.mkdir(parents=True,exist_ok=True)\n"
        f"command=[{GPU_PYTHON!r},'-m','csts_pilot.proposition_test','--phase','evaluate','--root',str(root),'--parent-root',str(parent),'--validation-name',{VALIDATION_NAME!r},'--name',{EVALUATION_NAME!r},'--answers',{imported['answers']!r},'--manifest',{imported['manifest']!r}]\n"
        "environment=os.environ.copy();environment.update({'HF_HOME':'/home/machina/jep-model-cache','HF_HUB_OFFLINE':'1','TRANSFORMERS_OFFLINE':'1','VIRTUAL_ENV':'/home/machina/jep-format-env','PATH':'/home/machina/jep-format-env/bin:/usr/local/cuda/bin:/usr/local/bin:/usr/bin:/bin'})\n"
        "with (logs/'evaluate.stdout').open('ab') as out,(logs/'evaluate.stderr').open('ab') as err:\n"
        " result=subprocess.run(command,cwd=root,env=environment,stdout=out,stderr=err,timeout=6000,check=False)\n"
        "assert result.returncode==0,'Native eligible frozen test evaluation failed; logs retained.'\n"
        f"summary=json.loads((root/'answer_input_results'/{EVALUATION_NAME!r}/'summary.json').read_text())\n"
        "assert summary.get('status')=='complete'\n"
        "print(json.dumps({'phase':'eligible_test','status':'complete','selection_sha256':summary['selection_sha256'],'selected_arm':summary['selected_arm'],'result':summary['result']},allow_nan=False))\n"
    )
    progress("native_frozen_test_evaluation")
    return remote(script, directory, "native_test_evaluate", 6120)


def capture_and_evaluate(commit: str, concurrency: int, native_source_commit: str | None = None) -> dict[str, Any]:
    native_commit = native_source_commit or commit
    directory = WORK_ROOT / (commit + "-" + native_commit)
    directory.mkdir(parents=True, exist_ok=True, mode=0o700)
    os.chmod(directory, 0o700)
    # No test source request, source fetch, or generation precedes this gate.
    released = native_release(native_commit, directory)
    release = released["release"]
    selection = release["selection_sha256"]
    if re.fullmatch(r"[0-9a-f]{64}", selection) is None:
        raise TestCaptureFailure("Native release has no immutable selection hash.")
    fetch_inventory(native_commit, released, directory)
    capture, source = fetch_capture(commit, directory)
    policy = frozen_policy(capture, release)
    root = GENERATION_ROOT / ("test_" + selection)
    root.mkdir(parents=True, exist_ok=True, mode=0o700)
    os.chmod(root, 0o700)
    with (root / "capture.lock").open("a+") as lock:
        try:
            fcntl.flock(lock.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as error:
            raise TestCaptureFailure("This frozen test capture already has an active controller.") from error
        launch = {"selection_sha256": selection, "pre_generation_release_sha256": released["release_sha256"], "capture_source_sha256": sha(source), **policy, "batch_size": 64, "maximum_one_item_per_source_group_per_request": True}
        preserve(root / "launch.json", (json.dumps(launch, ensure_ascii=False, indent=2, allow_nan=False) + "\n").encode())
        for name in ("generation_inputs.json", "group_ids.json", "pre_generation.json", "proposition_capture.py"):
            preserve(root / name, (directory / name).read_bytes())
        progress("eligible_release_and_policy_verified", source_commit=commit, selection_sha256=selection, total_items=release["unique_passage_conditions"])
        raw_manifest = capture_test(capture, root, directory, native_commit, release, concurrency)
        records = json.loads((root / "test/records.json").read_text())
        capture.write(root / "propositions_tranche8_test.json", records)
        manifest = {**launch, "source_commit": commit, "native_source_commit": native_commit, "items": len(records), "records_sha256": sha((root / "propositions_tranche8_test.json").read_bytes()), "partitions": {"test": raw_manifest}, "semantic_fidelity_independently_verified": False, "test_scores_used_for_selection": False}
        save(root / "propositions_tranche8_test_manifest.json", manifest)
        state = checkpoint(root, directory, native_commit, selection, final=True)
        imported = import_bank(native_commit, directory, root, selection)
        result = evaluate_native(native_commit, directory, imported)
        result.update(source_commit=commit, native_source_commit=native_commit)
        result.update(capture={"items": len(records), "records_sha256": manifest["records_sha256"], "policy": policy, "raw_checkpoints": state["checkpoints"], "failed_attempts": batch_counts(root / "test", len(records))["failed_attempts"]})
        save(directory / "result.json", result)
        return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-commit", required=True)
    parser.add_argument("--native-source-commit")
    parser.add_argument("--concurrency", type=int, choices=(1, 2, 3, 4), default=4)
    args = parser.parse_args()
    if re.fullmatch(r"[0-9a-f]{40}", args.source_commit) is None:
        parser.error("A complete pinned source commit is required.")
    if args.native_source_commit is not None and re.fullmatch(r"[0-9a-f]{40}", args.native_source_commit) is None:
        parser.error("The native source commit must be a complete Git commit.")
    try:
        result = capture_and_evaluate(args.source_commit, args.concurrency, args.native_source_commit)
    except BaseException as error:
        directory = WORK_ROOT / (args.source_commit + "-" + (args.native_source_commit or args.source_commit))
        directory.mkdir(parents=True, exist_ok=True, mode=0o700)
        (directory / "failure.log").write_text(traceback.format_exc())
        result = {"phase": "eligible_test", "status": "failed", "error_type": type(error).__name__, "error": str(error) if isinstance(error, TestCaptureFailure) else "Eligible test transport failed; private logs and raw captures are preserved."}
        save(directory / "result.json", result)
        print("OPERATOR_RESULT " + json.dumps(result, allow_nan=False), flush=True)
        raise SystemExit(1) from None
    print("OPERATOR_RESULT " + json.dumps(result, allow_nan=False), flush=True)


if __name__ == "__main__":
    main()
