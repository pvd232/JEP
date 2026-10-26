"""Bounded recovery of transient failures in the unchanged frozen capture."""

import argparse
import fcntl
import hashlib
import importlib.util
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

COMMIT = "8a0b50d5bdd2a77ab0c9444f4bf10d484f8ba6bb"
DIRECTORY = Path("/tmp/jep-tranche8-worker-20261026/full_capture") / COMMIT
ROOT = Path("/tmp/jep-proposition-input-20261026/full_v2_6895d17242704944")
CONTROLLER_SHA = "d359b57dfe0cefd592b96d9b560e5de47251e0c78899d9010b856e3519b3d216"
CAPTURE_SHA = "e8ee5293f2a77420a5fe2f69168988e7772da2b3478927f73531856827a8f462"
BATCH = re.compile(r"batch_([0-9]{4})(?:-attempt_([0-9]{2,}))?")
BLOCK = re.compile(r"unauthori[sz]ed|authentication|invalid.api.?key|token expired|\b401\b|\b403\b|permission denied|access denied|approval|policy|sign[ -]?in|log[ -]?in|reauth|usage[_ .-](?:limit|cap)|insufficient[_ .-]quota|insufficient.credits|billing|\bquota\b|limit for (?:your|this) (?:account|plan)", re.I)
TRANSIENT = re.compile(r"too many requests|\b429\b|request.?rate|rate.?limit|connection|network|socket|disconnect|\bdns\b|\btls\b|capacity|overload|server busy|deadline.exceeded|timed? out|timeout", re.I)
ALLOWED = {"thread.started", "turn.started", "item.started", "item.updated", "item.completed", "turn.completed", "turn.failed", "error"}


class RecoveryFailure(RuntimeError):
    """Content-free operational failure."""


def digest(data):
    return hashlib.sha256(data).hexdigest()


def save(path, value):
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, indent=2, allow_nan=False) + "\n")
    temporary.replace(path)


def load(path):
    spec = importlib.util.spec_from_file_location("frozen_recovery_dependency", path)
    if spec is None or spec.loader is None:
        raise RecoveryFailure("Cannot load the pinned dependency.")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def pinned():
    controller_path = DIRECTORY / "full_capture_controller.py"
    capture_path = DIRECTORY / "proposition_capture.py"
    if digest(controller_path.read_bytes()) != CONTROLLER_SHA or digest(capture_path.read_bytes()) != CAPTURE_SHA:
        raise RecoveryFailure("Original controller or capture source differs.")
    controller, capture = load(controller_path), load(capture_path)
    controller.verify_gate(json.loads((DIRECTORY / "audit_gate.json").read_text()), capture, capture_path.read_bytes())
    controller.verify_inventory(capture)
    return controller, capture


def retryable(directory, capture):
    receipt = json.loads((directory / "receipt.json").read_text())
    text = (directory / "stderr.log").read_text(errors="replace") if (directory / "stderr.log").is_file() else ""
    transient = False
    for line in (directory / "events.jsonl").read_text().splitlines():
        if not line.strip():
            continue
        event = json.loads(line)
        kind = event.get("type")
        if kind not in ALLOWED or (kind.startswith("item.") and event.get("item", {}).get("type") not in {"agent_message", "reasoning"}):
            return False
        if kind in {"error", "turn.failed"}:
            error = json.dumps(event)
            if BLOCK.search(error) or not TRANSIENT.search(error):
                return False
            transient = True
    if BLOCK.search(text):
        return False
    # TimeoutExpired embeds the static command (including approval_policy), so
    # only recognize its timeout phrase, never classify the command as policy.
    timed_out = bool(re.search(r"timed out after [0-9.]+ seconds", receipt.get("error", "")))
    if transient or TRANSIENT.search(text) or timed_out:
        return True
    if receipt.get("returncode") != 0:
        return False
    try:
        capture.checked_events(directory / "events.jsonl")
    except (ValueError, TypeError, KeyError):
        return False
    try:
        capture.checked_records(json.loads((directory / "inputs.json").read_text()), json.loads((directory / "response.json").read_text()))
    except (ValueError, TypeError, KeyError):
        return True
    return False


def preflight(root, capture):
    """Every unresolved batch has a durable total cap of three raw attempts."""
    outstanding = False
    for split in ("training", "validation"):
        groups = {}
        for directory in sorted((root / split).glob("batch_*")):
            match = BATCH.fullmatch(directory.name)
            if match is None or directory.is_symlink():
                raise RecoveryFailure("Unexpected batch path.")
            groups.setdefault(match[1], []).append((int(match[2] or 1), directory))
        for attempts in groups.values():
            complete = []
            for _, directory in attempts:
                receipt = json.loads((directory / "receipt.json").read_text())
                if receipt.get("status") == "complete":
                    capture.completed_batch(json.loads((directory / "inputs.json").read_text()), directory, capture.CLI)
                    complete.append(directory)
                elif receipt.get("status") != "failed":
                    raise RecoveryFailure("A batch is still running or interrupted.")
            if complete:
                continue
            outstanding = True
            if max(number for number, _ in attempts) >= 3 or len(attempts) >= 3:
                raise RecoveryFailure("A batch exhausted its three-attempt total allowance.")
            if not all(retryable(directory, capture) for _, directory in attempts):
                raise RecoveryFailure("A failure is outside the permitted transient/response recovery policy.")
    return outstanding


def archive_terminal(directory):
    history = directory / "recovery_history" / str(time.time_ns())
    history.mkdir(parents=True, exist_ok=False)
    hashes = {}
    for name in ("supervisor_receipt.json", "result.json"):
        path = directory / name
        if path.exists():
            data = path.read_bytes()
            (history / name).write_bytes(data)
            hashes[name] = digest(data)
    save(history / "manifest.json", {"sha256": hashes, "recovery_sha256": digest(Path(__file__).read_bytes())})
    result = directory / "result.json"
    if result.exists():
        result.unlink()
    return str(history)


def no_live_capture(receipt):
    pid = receipt.get("pid")
    if isinstance(pid, int) and pid > 1:
        try:
            os.kill(pid, 0)
        except ProcessLookupError:
            pass
        else:
            raise RecoveryFailure("The prior supervisor remains alive.")
    processes = subprocess.check_output(["ps", "-axo", "pid=,command="], text=True, timeout=10)
    if any(str(ROOT) in line and "codex" in line.lower() for line in processes.splitlines()):
        raise RecoveryFailure("A capture CLI remains alive.")


def run(lock_fd):
    # Descriptor inherited from the launcher keeps the exact original bank lock
    # continuously owned across detachment.
    fcntl.flock(lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
    receipt_path = DIRECTORY / "supervisor_receipt.json"
    receipt = {}
    controller = None
    try:
        receipt = json.loads(receipt_path.read_text())
        controller, capture = pinned()
        receipt.update(status="running", pid=os.getpid())
        save(receipt_path, receipt)

        def permitted(root, module):
            allowed = preflight(root, module)
            if allowed:
                time.sleep(30)
            return allowed

        controller.retryable_output_failures = permitted
        preflight(ROOT, capture)
        time.sleep(30)
        result = controller.full_capture(COMMIT, concurrency=2)
    except Exception:
        result = {"phase": "full_capture", "status": "failed", "counts": controller.counts(ROOT) if controller is not None else {}, "error": "Bounded recovery stopped; private logs, all attempts and receipt history remain preserved."}
    save(DIRECTORY / "result.json", result)
    receipt.update(status=result["status"], finished_unix=time.time())
    save(receipt_path, receipt)
    return result


def launch():
    lock = (ROOT / "supervisor.lock").open("a+")
    try:
        fcntl.flock(lock.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        return {"phase": "capture_recovery", "status": "running", "existing_lock_owner_preserved": True}
    controller, capture = pinned()
    receipt_path = DIRECTORY / "supervisor_receipt.json"
    receipt = json.loads(receipt_path.read_text())
    if receipt.get("status") not in {"failed", "interrupted"} or receipt.get("source_commit") != COMMIT or receipt.get("output_path") != str(ROOT):
        raise RecoveryFailure("The stopped original capture binding differs.")
    no_live_capture(receipt)
    preflight(ROOT, capture)
    history = archive_terminal(DIRECTORY)
    source = Path(__file__).read_bytes()
    target = DIRECTORY / ("capture_recovery_" + digest(source) + ".py")
    if target.exists() and target.read_bytes() != source:
        raise RecoveryFailure("The immutable recovery source differs.")
    target.write_bytes(source)
    receipt.update(status="launching", recovery_sha256=digest(source), recovery_history=history, concurrency=2, recovery_attempt_cap=3, recovery_started_unix=time.time())
    save(receipt_path, receipt)
    with (DIRECTORY / "recovery.stdout").open("ab") as stdout, (DIRECTORY / "recovery.stderr").open("ab") as stderr:
        child = subprocess.Popen([sys.executable, "-I", str(target), "--run", "--lock-fd", str(lock.fileno())], stdin=subprocess.DEVNULL, stdout=stdout, stderr=stderr, start_new_session=True, pass_fds=(lock.fileno(),))
    # The child exclusively owns subsequent receipt updates. A parent read/write
    # could race with and overwrite the child's already-running receipt.
    return {"phase": "capture_recovery", "status": "running", "pid": child.pid, "counts": controller.counts(ROOT), "recovery_sha256": digest(source), "concurrency": 2, "total_attempt_cap_per_batch": 3}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", action="store_true")
    parser.add_argument("--lock-fd", type=int)
    args = parser.parse_args()
    try:
        if args.run and args.lock_fd is None:
            raise RecoveryFailure("A detached run requires the inherited bank lock.")
        result = run(args.lock_fd) if args.run else launch()
    except Exception:
        result = {"phase": "capture_recovery", "status": "failed", "error": "Recovery preflight failed; original evidence remains preserved."}
    print("OPERATOR_RESULT " + json.dumps(result, allow_nan=False), flush=True)
    raise SystemExit(0 if result.get("status") in {"running", "complete"} else 1)
