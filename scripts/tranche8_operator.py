"""Harvest the stopped answer subset and run one native validation-only trial."""

import argparse
import base64
import contextlib
import hashlib
import importlib.util
import io
import json
import re
import shutil
import subprocess
import sys
import tarfile
import time
from pathlib import Path

REPO = "pvd232/JEP"
BRANCH = "experiment/csts-proposition-lora-20261026"
WORK = Path("/tmp/jep-tranche8-worker-20261026/subset")
CAPTURE_COMMIT = "8a0b50d5bdd2a77ab0c9444f4bf10d484f8ba6bb"
ORIGINAL = WORK.parent / "full_capture" / CAPTURE_COMMIT
BANK = Path("/tmp/jep-proposition-input-20261026/full_v2_6895d17242704944")
CONTROLLER_SHA = "d359b57dfe0cefd592b96d9b560e5de47251e0c78899d9010b856e3519b3d216"
CAPTURE_SHA = "e8ee5293f2a77420a5fe2f69168988e7772da2b3478927f73531856827a8f462"
HELPER_COMMIT = "d5b7e513e7067538159aaffeb8d2ce463b845739"
HELPER_SHA = "4928c30aa81fbf253dbd7e9c4b538aef067cc9c5acf7f6782c5a26b57d618525"
SUPERVISOR_SHA = "a22523165d1af74897dc863009167192be8cfb8d5f46ac71969a69ba2ce0e368"
MODULE = "csts_pilot.proposition_subset"
NAME = "proposition_subset_v1"
EXTRA_SOURCE = ["csts_pilot/proposition_subset.py", "tests/test_csts_proposition_subset.py"]
INPUTS = ("proposition_subset_training_records.json", "proposition_subset_training_manifest.json")
RESULT_PATH = "training_outputs/csts_tranche8_subset_results.json"
STATUS_PATH = "training_outputs/csts_tranche8_subset_status.md"


class SubsetFailure(RuntimeError):
    """A content-free failure suitable for the task status."""


def sha(data):
    return hashlib.sha256(data).hexdigest()


def save(path, value):
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n")
    temporary.replace(path)


def gh():
    value = shutil.which("gh") or next((str(p) for p in (Path("/opt/homebrew/bin/gh"), Path("/usr/local/bin/gh")) if p.is_file()), None)
    if value is None:
        raise SubsetFailure("The existing GitHub executable is unavailable.")
    return value


def api(arguments, payload=None):
    command = [gh(), "api", *arguments]
    if payload is not None:
        command += ["--input", "-"]
    result = subprocess.run(command, input=json.dumps(payload).encode() if payload is not None else None, capture_output=True, timeout=60, check=False)
    if result.returncode:
        raise SubsetFailure("The task GitHub operation failed; no response text was published.")
    return json.loads(result.stdout)


def fetch(path, commit):
    value = api([f"repos/{REPO}/contents/{path}?ref={commit}"])
    if value.get("type") != "file" or value.get("encoding") != "base64":
        raise SubsetFailure("The pinned dependency is not a file.")
    data = base64.b64decode("".join(value["content"].split()), validate=True)
    if hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest() != value.get("sha"):
        raise SubsetFailure("The pinned dependency Git blob differs.")
    return data


def load(path):
    spec = importlib.util.spec_from_file_location(path.stem + "_subset_pinned", path)
    if spec is None or spec.loader is None:
        raise SubsetFailure("Cannot load the pinned task dependency.")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def native_helper(directory):
    source = fetch("scripts/tranche8_native.py", HELPER_COMMIT)
    if sha(source) != HELPER_SHA:
        raise SubsetFailure("The native transport helper differs.")
    path = directory / "native_helper.py"
    path.write_bytes(source)
    module = load(path)
    module.OWNED = [*module.OWNED, *EXTRA_SOURCE]
    return module


def harvest(directory):
    """Validate exact original batches, accounting for macOS /tmp realpaths."""
    controller_path, capture_path = ORIGINAL / "full_capture_controller.py", ORIGINAL / "proposition_capture.py"
    if sha(controller_path.read_bytes()) != CONTROLLER_SHA or sha(capture_path.read_bytes()) != CAPTURE_SHA:
        raise SubsetFailure("The original controller or capture source differs.")
    controller, capture = load(controller_path), load(capture_path)
    gate_bytes = (ORIGINAL / "audit_gate.json").read_bytes()
    bindings = controller.verify_gate(json.loads(gate_bytes), capture, capture_path.read_bytes())
    inventory = controller.verify_inventory(capture)
    root = BANK.resolve(strict=True)
    if any(json.loads(path.read_text()).get("status") == "running" for path in root.glob("*/batch_*/receipt.json")):
        raise SubsetFailure("A capture batch remains active; subset harvesting stopped.")
    groups_path = controller.GENERATION_ROOT / "full_inventory/training_groups.json"
    selected = capture.batches(inventory["training"], json.loads(groups_path.read_text()), 64)
    records, batches, seen = [], [], set()
    for batch in sorted((root / "training").glob("batch_*")):
        match = re.fullmatch(r"batch_([0-9]{4})(?:-attempt_[0-9]{2,})?", batch.name)
        if match is None or batch.is_symlink():
            raise SubsetFailure("An unexpected capture batch path was found.")
        receipt_path = batch / "receipt.json"
        receipt = json.loads(receipt_path.read_text())
        if receipt.get("status") != "complete":
            continue
        index = int(match[1])
        if index >= len(selected) or index in seen:
            raise SubsetFailure("The completed batch identity is duplicated or outside the inventory.")
        with contextlib.redirect_stdout(io.StringIO()):
            capture.completed_batch(selected[index], batch.resolve(strict=True), capture.CLI)
        values = json.loads((batch / "records.json").read_text())
        records.extend(values)
        seen.add(index)
        batches.append({"batch": batch.name, "receipt_sha256": sha(receipt_path.read_bytes()), "records_sha256": sha((batch / "records.json").read_bytes())})
    if len(records) != 2880 or len({row["id"] for row in records}) != 2880:
        raise SubsetFailure("The user-selected completed subset is not exactly 2,880 unique records.")
    expected = {row["id"]: row for row in inventory["training"]}
    checked = capture.checked_records([expected[row["id"]] for row in records], {"records": records})
    records_path = directory / INPUTS[0]
    save(records_path, sorted(checked, key=lambda row: row["id"]))
    manifest = {"items": len(checked), "records_sha256": sha(records_path.read_bytes()), "source_training_sha256": controller.EXPECTED["training"]["source"], "capture_source_sha256": CAPTURE_SHA, "capture_source_commit": CAPTURE_COMMIT, **bindings, "audit_gate_sha256": sha(gate_bytes), "completed_batches": batches, "operational_subset_only": True, "full_generation_resumed": False}
    save(directory / INPUTS[1], manifest)
    return {"phase": "subset_harvest", "status": "complete", "items": len(checked), "completed_batches": len(batches), "records_sha256": manifest["records_sha256"], "source_training_sha256": manifest["source_training_sha256"], "resolved_command_bindings_verified": True}


def transfer(native, commit, directory):
    manifest = json.loads((directory / INPUTS[1]).read_text())
    if manifest["items"] != 2880 or manifest["records_sha256"] != sha((directory / INPUTS[0]).read_bytes()):
        raise SubsetFailure("The harvested subset identity differs.")
    expected = {name: sha((directory / name).read_bytes()) for name in INPUTS}
    archive = directory / ("subset-bank-" + manifest["records_sha256"][:16] + ".tar.gz")
    with tarfile.open(archive, "w:gz") as stream:
        for name in INPUTS:
            stream.add(directory / name, arcname=name, recursive=False)
    staging, digest = native.copy_to_gpu(archive, directory, "subset_bank")
    script = native.preamble(commit) + (
        "import tarfile\nclean()\n"
        f"archive=pathlib.Path({staging!r});assert digest(archive)=={digest!r}\nexpected={expected!r}\n"
        "with tarfile.open(archive,'r:gz') as stream:\n"
        " assert len(stream.getmembers())==len(expected) and set(stream.getnames())==set(expected)\n"
        " for member in stream.getmembers():\n"
        "  assert member.isfile() and member.name in expected\n"
        "  source=stream.extractfile(member);assert source is not None;data=source.read()\n"
        "  assert hashlib.sha256(data).hexdigest()==expected[member.name]\n"
        "  target=root/'csts_data'/member.name;assert not target.is_symlink()\n"
        "  if target.exists(): assert target.read_bytes()==data,'Existing subset input differs.'\n"
        "  else: target.write_bytes(data)\n"
        "print(json.dumps({'phase':'subset_import','status':'complete','source_inputs':expected}))\n"
    )
    return native.remote(script, directory, "subset_import")


def subset_supervisor(source):
    if sha(source) != SUPERVISOR_SHA:
        raise SubsetFailure("The original native supervisor differs.")
    text = source.decode()
    old_set = '{"csts_pilot.proposition_run", "csts_pilot.proposition_sample"}'
    old_choices = '("csts_pilot.proposition_run", "csts_pilot.proposition_sample")'
    if text.count(old_set) != 1 or text.count(old_choices) != 1:
        raise SubsetFailure("The supervisor allowlist shape differs.")
    text = text.replace(old_set, '{"csts_pilot.proposition_run", "csts_pilot.proposition_sample", "csts_pilot.proposition_subset"}').replace(old_choices, '("csts_pilot.proposition_run", "csts_pilot.proposition_sample", "csts_pilot.proposition_subset")')
    compile(text, "subset_supervisor", "exec")
    return text.encode()


def launch(native, commit, directory):
    supervisor = subset_supervisor(fetch("scripts/tranche8_native_supervisor.py", HELPER_COMMIT))
    local = directory / "subset_supervisor.py"
    local.write_bytes(supervisor)
    staging, supervisor_sha = native.copy_to_gpu(local, directory, "subset_supervisor")
    script = native.preamble(commit) + (
        "clean()\nchecks=json.loads((root/'answer_input_results/owner_checks'/commit/'receipt.json').read_text())\n"
        "assert checks.get('passed') is True and checks.get('source_clean') is True\n"
        "assert all(digest(root/p)==value for p,value in checks['owned_source_sha256'].items())\n"
        f"assert set({EXTRA_SOURCE!r})<=set(checks['owned_source_sha256'])\nname={NAME!r};module={MODULE!r}\n"
        "directory=root/'answer_input_results/supervisors'/name;directory.mkdir(parents=True,exist_ok=True)\nreceipt=directory/'receipt.json'\n"
        "if receipt.exists():\n print(json.dumps({'phase':'subset_launch',**json.loads(receipt.read_text())}))\n"
        "else:\n"
        f" source=pathlib.Path({staging!r});assert digest(source)=={supervisor_sha!r}\n"
        " target=directory/'supervisor.py';shutil.copyfile(source,target)\n"
        " save(receipt,{'status':'launching','source_commit':commit,'name':name,'module':module,'started_unix':time.time(),'supervisor_sha256':digest(target)})\n"
        " environment=os.environ.copy();environment.update({'VIRTUAL_ENV':'/home/machina/jep-format-env','HF_HOME':'/home/machina/jep-model-cache','HF_HUB_OFFLINE':'1','TRANSFORMERS_OFFLINE':'1','PATH':'/home/machina/jep-format-env/bin:/usr/local/cuda/bin:/usr/local/bin:/usr/bin:/bin'})\n"
        " with (directory/'supervisor.log').open('ab') as log:\n"
        f"  child=subprocess.Popen([{native.GPU_PYTHON!r},str(target),'--root',str(root),'--parent-root',str(parent),'--name',name,'--source-commit',commit,'--module',module],cwd=root,env=environment,stdin=subprocess.DEVNULL,stdout=log,stderr=log,start_new_session=True)\n"
        " print(json.dumps({'phase':'subset_launch','status':'running','source_commit':commit,'name':name,'pid':child.pid,'full_generation_resumed':False,'held_out_test_released':False}))\n"
    )
    return native.remote(script, directory, "subset_launch")


def publish(path, content):
    if path not in {RESULT_PATH, STATUS_PATH}:
        raise SubsetFailure("The subset status destination is outside its fixed allowlist.")
    try:
        current = api([f"repos/{REPO}/contents/{path}?ref={BRANCH}"])
    except SubsetFailure:
        current = None
    payload = {"branch": BRANCH, "message": "Update the validation-only proposition subset trial", "content": base64.b64encode(content).decode()}
    if current is not None:
        payload["sha"] = current["sha"]
    api(["--method", "PUT", f"repos/{REPO}/contents/{path}"], payload)


def watch(native, commit, directory):
    started, last_signature, last_publish = time.monotonic(), None, 0.0
    while time.monotonic() - started < 21600:
        value = native.native_status(commit, directory, NAME)
        snapshot = {"phase": "subset_trial", "source_commit": commit, "observed_unix": time.time(), "full_generation_resumed": False, "held_out_test_released": False, **value}
        signature = sha(json.dumps(value, sort_keys=True, allow_nan=False).encode())
        if signature != last_signature or time.monotonic() - last_publish >= 300:
            save(directory / "latest.json", snapshot)
            publish(RESULT_PATH, (json.dumps(snapshot, indent=2, allow_nan=False) + "\n").encode())
            text = "# Proposition subset trial\n\n" + f"Status: **{value.get('status', 'unknown')}**. Uses the 2,880 completed training answers and the 30-pair revised-policy development sample. Full answer generation remains stopped; no held-out test is released.\n\n" + "This is a small development triage experiment. Native metrics and training progress are preserved in [the results JSON](csts_tranche8_subset_results.json).\n\n" + "```json\n" + json.dumps(value, indent=2, allow_nan=False) + "\n```\n"
            publish(STATUS_PATH, text.encode())
            print("OPERATOR_PROGRESS " + json.dumps(snapshot, allow_nan=False), flush=True)
            last_signature, last_publish = signature, time.monotonic()
        if value.get("status") in {"complete", "failed", "timed_out", "interrupted"}:
            return snapshot
        time.sleep(30)
    return {"phase": "subset_watch", "status": "timed_out", "native_process_preserved": True}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--phase", required=True, choices=("harvest", "deploy", "checks", "source", "import", "launch", "status", "watch", "diagnostics"))
    parser.add_argument("--source-commit", required=True)
    parser.add_argument("--allow-format", action="store_true")
    parser.add_argument("--path", choices=EXTRA_SOURCE)
    args = parser.parse_args()
    if re.fullmatch(r"[0-9a-f]{40}", args.source_commit) is None:
        parser.error("Use one complete immutable source commit.")
    directory = WORK / args.source_commit
    directory.mkdir(parents=True, exist_ok=True)
    try:
        if args.phase == "harvest":
            result = harvest(directory)
        else:
            native = native_helper(directory)
            if args.phase == "deploy":
                result = native.native_deploy(args.source_commit, directory)
            elif args.phase == "checks":
                result = native.native_checks(args.source_commit, directory, args.allow_format)
            elif args.phase == "source":
                result = native.native_source(args.source_commit, directory, args.path)
            elif args.phase == "import":
                harvest(directory)
                result = transfer(native, args.source_commit, directory)
            elif args.phase == "launch":
                result = launch(native, args.source_commit, directory)
            elif args.phase == "watch":
                result = watch(native, args.source_commit, directory)
            elif args.phase == "diagnostics":
                result = native.check_diagnostics(args.source_commit, directory)
            else:
                result = native.native_status(args.source_commit, directory, NAME)
    except Exception:
        # Exit zero so the existing worker retains this safe structured failure.
        result = {"phase": "subset_" + args.phase, "status": "failed", "error": "Subset operation stopped; task-private logs and all capture attempts remain preserved."}
    print("OPERATOR_RESULT " + json.dumps(result, allow_nan=False), flush=True)


if __name__ == "__main__":
    main()
