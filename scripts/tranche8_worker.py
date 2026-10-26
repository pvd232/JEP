"""Run pinned Tranche 8 operators and publish only their structured status.

The Mac worker owns one fixed control file, one status file, and a private
directory. A small local supervisor preserves the operator's exit receipt
even if this polling process restarts. No shell commands come from control.
"""

from __future__ import annotations

import argparse
import base64
import fcntl
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import quote

REPOSITORY = "pvd232/JEP"
BRANCH = "experiment/csts-proposition-lora-20261026"
CONTROL_PATH = "training_outputs/csts_tranche8_control.json"
STATUS_PATH = "training_outputs/csts_tranche8_operator_status.json"
OPERATOR_PATH = "scripts/tranche8_operator.py"
WORK_ROOT = Path("/tmp/jep-tranche8-worker-20261026")
POLL_SECONDS = 20
HEARTBEAT_SECONDS = 180
MAX_SECONDS = 8 * 60 * 60
TERMINAL = {"completed", "failed", "interrupted"}
PUBLIC_FIELDS = {
    "phase", "status", "stage", "split", "arm", "event", "counts",
    "completed", "total", "done", "epoch", "step", "elapsed_seconds",
    "metrics", "scores", "score", "validation", "spearman", "mse",
    "mse_0_1", "false_positive_rate", "recall", "coverage", "selection",
    "selected_epoch", "eligible", "gate", "summary", "result", "artifacts",
    "blinded_fresh_sample", "review_sample", "samples", "sample", "sample_size",
    "audit", "verification", "next_phase", "decision", "manifest",
}
PRIVATE_FIELDS = {
    "auth", "authorization", "api_key", "access_token", "refresh_token",
    "token", "credentials", "password", "secret", "env", "environ",
    "environment", "stdout", "stderr", "logs", "log_tail", "log_tails",
    "command", "argv", "arguments",
}
SECRET_TEXT = re.compile(
    r"(?:\bsk-[A-Za-z0-9_-]{16,}|\bgh[pousr]_[A-Za-z0-9_]{16,}|"
    r"\bgithub_pat_[A-Za-z0-9_]{16,}|\bhf_[A-Za-z0-9_]{16,}|"
    r"\bya29\.[A-Za-z0-9._-]{16,}|\bAIza[A-Za-z0-9_-]{25,}|"
    r"\bBearer\s+[A-Za-z0-9._~+/-]{16,})", re.IGNORECASE,
)


def now() -> str:
    """Return a UTC timestamp for receipts and published observations."""
    return datetime.now(timezone.utc).isoformat()


def save_json(path: Path, value: Any) -> None:
    """Atomically replace one JSON record and flush its directory entry."""
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    fd, temporary = tempfile.mkstemp(prefix=path.name + ".", dir=path.parent)
    try:
        with os.fdopen(fd, "w") as stream:
            json.dump(value, stream, allow_nan=False, indent=2)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
        directory = os.open(path.parent, os.O_RDONLY)
        try:
            os.fsync(directory)
        finally:
            os.close(directory)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def read_json(path: Path, default: Any = None) -> Any:
    """Read an existing receipt without interpreting it as instructions."""
    return json.loads(path.read_text()) if path.exists() else default


def gh_binary() -> str:
    """Reuse the Mac's existing authenticated GitHub CLI installation."""
    fixed = Path("/opt/homebrew/bin/gh")
    found = str(fixed) if fixed.is_file() else shutil.which("gh")
    if not found:
        raise RuntimeError("GitHub CLI unavailable")
    return found


def github_file(path: str, ref: str) -> tuple[dict[str, Any] | None, bytes | None]:
    """Fetch a fixed repository file; a status-file 404 means first publication."""
    endpoint = f"repos/{REPOSITORY}/contents/{path}?ref={quote(ref, safe='')}"
    response = subprocess.run(
        [gh_binary(), "api", endpoint], stdin=subprocess.DEVNULL,
        capture_output=True, timeout=35, check=False,
    )
    if response.returncode:
        if path == STATUS_PATH and b"HTTP 404" in response.stderr:
            return None, None
        raise RuntimeError("GitHub file fetch failed")
    record = json.loads(response.stdout)
    if record.get("type") != "file" or record.get("path") != path:
        raise ValueError("Unexpected GitHub file identity")
    if record.get("encoding") != "base64":
        raise ValueError("Unsupported GitHub file encoding")
    encoded = "".join(record["content"].split())
    return record, base64.b64decode(encoded, validate=True)


def publish(status: dict[str, Any]) -> bool:
    """Update only the fixed status file, guarded by its latest blob SHA."""
    try:
        previous, _ = github_file(STATUS_PATH, BRANCH)
        body = {
            "branch": BRANCH,
            "message": "Update Tranche 8 operator status",
            "content": base64.b64encode(
                (json.dumps(status, allow_nan=False, indent=2) + "\n").encode()
            ).decode(),
        }
        if previous is not None:
            body["sha"] = previous["sha"]
        response = subprocess.run(
            [gh_binary(), "api", "--method", "PUT",
             f"repos/{REPOSITORY}/contents/{STATUS_PATH}", "--input", "-"],
            input=json.dumps(body).encode(), capture_output=True,
            timeout=35, check=False,
        )
        return response.returncode == 0
    except (OSError, ValueError, RuntimeError, subprocess.TimeoutExpired):
        return False


def validate_control(value: Any) -> dict[str, Any]:
    """Require a pinned operator and string argv before accepting a run action."""
    if not isinstance(value, dict) or not isinstance(value.get("action"), str) or value["action"] not in {"wait", "run", "stop"}:
        raise ValueError("Invalid control action")
    if not isinstance(value.get("action_id"), str) or not value["action_id"]:
        raise ValueError("Invalid action identity")
    if len(value["action_id"]) > 200:
        raise ValueError("Action identity is too long")
    if value["action"] == "run":
        if not isinstance(value.get("source_commit"), str) or not re.fullmatch(r"[0-9a-f]{40}", value["source_commit"]):
            raise ValueError("Operator source must be an immutable commit")
        if not isinstance(value.get("operator_sha256"), str) or not re.fullmatch(r"[0-9a-f]{64}", value["operator_sha256"]):
            raise ValueError("Operator content digest is required")
        arguments = value.get("arguments")
        if not isinstance(arguments, list) or any(
            not isinstance(argument, str) or "\x00" in argument for argument in arguments
        ):
            raise ValueError("Operator arguments must be strings")
    return value


def private_field(key: str) -> bool:
    """Recognize credential names without dropping harmless numeric token counts."""
    normalized = re.sub(r"[^a-z0-9]", "", key.lower())
    return key.lower().replace("-", "_") in PRIVATE_FIELDS or any(
        word in normalized for word in (
            "apikey", "authorization", "authentication", "credential",
            "password", "secret", "environment", "environ", "stdout", "stderr", "logtail",
        )
    ) or normalized.startswith("env") or normalized.endswith("token")


def clean(value: Any, depth: int = 0) -> Any:
    """Exclude credential/environment/log fields from structured public payloads."""
    if depth > 12:
        return "[depth limit]"
    if isinstance(value, dict):
        return {
            str(key): clean(item, depth + 1)
            for key, item in value.items()
            if not private_field(str(key))
        }
    if isinstance(value, list):
        return [clean(item, depth + 1) for item in value[:500]]
    if isinstance(value, str):
        return SECRET_TEXT.sub("[redacted]", value[:20000])
    if value is None or isinstance(value, (bool, int, float)):
        return value
    return "[unsupported value]"


def public_event(value: Any, result: bool) -> dict[str, Any] | None:
    """Keep documented progress/result fields, including explicit blinded samples."""
    if not isinstance(value, dict):
        return None
    # Results come from the source-pinned reviewed operator. Preserve new safe
    # result fields so a repaired operator does not require reinstalling worker.
    filtered = clean(value if result else {key: item for key, item in value.items() if key in PUBLIC_FIELDS})
    if len(json.dumps(filtered, allow_nan=False)) > (200000 if result else 20000):
        return {"status": "payload_omitted", "summary": "Structured payload exceeds status limit"}
    return filtered


def directory_for(action_id: str) -> Path:
    """Derive a filesystem-safe action key without trusting control as a path."""
    return WORK_ROOT / "actions" / hashlib.sha256(action_id.encode()).hexdigest()


def pid_matches(pid: Any, directory: Path) -> bool:
    """Avoid treating a reused PID as this action's supervisor or operator."""
    if not isinstance(pid, int) or pid <= 0:
        return False
    try:
        result = subprocess.run(
            ["ps", "-p", str(pid), "-o", "command="], capture_output=True,
            timeout=5, check=False,
        )
        command = result.stdout.decode(errors="replace")
        return str(directory / "operator.py") in command or (
            "--supervise" in command and directory.name in command
        )
    except (OSError, subprocess.TimeoutExpired):
        return False


def supervise(key: str) -> int:
    """Persist PID and completion around one operator, independently of polling."""
    if not re.fullmatch(r"[0-9a-f]{64}", key):
        return 2
    directory = WORK_ROOT / "actions" / key
    receipt_path = directory / "receipt.json"
    with (directory / "action.lock").open("a+") as lock:
        fcntl.flock(lock.fileno(), fcntl.LOCK_EX)
        receipt = read_json(receipt_path)
        # A restarting worker can cancel an unstarted supervisor under this lock.
        if not receipt or receipt.get("status") != "launching":
            return 2
        operator = directory / "operator.py"
        if hashlib.sha256(operator.read_bytes()).hexdigest() != receipt["operator_sha256"]:
            receipt.update(status="failed", error="Pinned operator digest mismatch", returncode=2)
            save_json(receipt_path, receipt)
            return 2
        receipt.update(status="running", supervisor_pid=os.getpid(), started_at=now())
        save_json(receipt_path, receipt)
        child = None
        try:
            with (directory / "stdout.log").open("ab") as stdout, (directory / "stderr.log").open("ab") as stderr:
                child = subprocess.Popen(
                    [sys.executable, str(operator), *receipt["arguments"]],
                    cwd=WORK_ROOT, stdin=subprocess.DEVNULL, stdout=stdout, stderr=stderr,
                )
                receipt["operator_pid"] = child.pid
                save_json(receipt_path, receipt)
                returncode = child.wait()
            receipt.update(
                status="completed" if returncode == 0 else "failed",
                returncode=returncode, finished_at=now(),
            )
            if returncode:
                receipt["error"] = "Operator exited with a nonzero return code"
            save_json(receipt_path, receipt)
            return returncode
        except Exception:
            if child is not None and child.poll() is None:
                # A failed receipt write must not release serialization while
                # an already-started operator continues its authorized work.
                child.wait()
            receipt.update(status="failed", returncode=None, error="Operator supervisor failed", finished_at=now())
            save_json(receipt_path, receipt)
            return 1


def observe(directory: Path) -> dict[str, Any]:
    """Read only complete event lines and persist their consumed byte offset."""
    path = directory / "observed.json"
    observation = read_json(path, {"stdout_offset": 0})
    stdout = directory / "stdout.log"
    if stdout.exists():
        with stdout.open("rb") as stream:
            stream.seek(observation["stdout_offset"])
            chunk = stream.read(1024 * 1024)
        end = chunk.rfind(b"\n") + 1
        if not end and len(chunk) == 1024 * 1024:
            end = len(chunk)  # Never grow status memory around an oversized log line.
        for line in chunk[:end].splitlines():
            for prefix, name in ((b"OPERATOR_PROGRESS ", "progress"), (b"OPERATOR_RESULT ", "result")):
                if line.startswith(prefix):
                    try:
                        value = public_event(json.loads(line[len(prefix):]), result=name == "result")
                        if value is not None:
                            observation[name] = value
                    except (ValueError, TypeError):
                        observation["event_error"] = "Invalid structured operator event"
        observation["stdout_offset"] += end
        save_json(path, observation)
    return observation


def still_active(directory: Path, launched: subprocess.Popen | None = None) -> bool:
    """Recover in-flight work; never relaunch an action after an interrupted run."""
    receipt_path = directory / "receipt.json"
    receipt = read_json(receipt_path)
    if receipt["status"] in TERMINAL:
        return False
    if launched is not None and launched.poll() is None:
        return True
    with (directory / "action.lock").open("a+") as lock:
        try:
            fcntl.flock(lock.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            return True
        receipt = read_json(receipt_path)
        if receipt["status"] in TERMINAL:
            return False
        if pid_matches(receipt.get("operator_pid"), directory):
            return True  # Supervisor loss must not permit a concurrent operator.
        receipt.update(status="interrupted", returncode=None, error="Prior action ended without a completion receipt", finished_at=now())
        save_json(receipt_path, receipt)
        return False


def launch(control: dict[str, Any]) -> tuple[Path, subprocess.Popen | None]:
    """Download one fixed operator at its pinned commit and durably bind argv."""
    directory = directory_for(control["action_id"])
    receipt_path = directory / "receipt.json"
    if receipt_path.exists():
        receipt = read_json(receipt_path)
        if any(receipt.get(key) != control.get(key) for key in ("action_id", "source_commit", "operator_sha256", "arguments")):
            raise ValueError("Action identity reused with a different operator binding")
        return directory, None
    directory.mkdir(parents=True, mode=0o700)
    receipt = {key: control[key] for key in ("action_id", "source_commit", "operator_sha256", "arguments")}
    receipt.update(status="preparing", created_at=now())
    save_json(receipt_path, receipt)
    try:
        _, operator = github_file(OPERATOR_PATH, control["source_commit"])
        if operator is None or hashlib.sha256(operator).hexdigest() != control["operator_sha256"]:
            raise ValueError("Pinned operator digest mismatch")
        (directory / "operator.py").write_bytes(operator)
        receipt["status"] = "launching"
        save_json(receipt_path, receipt)
        with (directory / "supervisor.log").open("ab") as log:
            process = subprocess.Popen(
                [sys.executable, str(Path(__file__).resolve()), "--supervise", directory.name],
                cwd=WORK_ROOT, stdin=subprocess.DEVNULL, stdout=log, stderr=subprocess.STDOUT,
                start_new_session=True,
            )
        return directory, process
    except (OSError, ValueError, RuntimeError, subprocess.TimeoutExpired):
        receipt.update(status="failed", returncode=None, error="Pinned operator preparation or launch failed", finished_at=now())
        save_json(receipt_path, receipt)
        return directory, None


def status_for(directory: Path | None, worker_state: str, error: str | None = None) -> dict[str, Any]:
    """Build a public observation without argv, environment, credentials or logs."""
    result: dict[str, Any] = {"updated_at": now(), "worker_status": worker_state}
    if error:
        result["error"] = error
    if directory is not None:
        receipt = read_json(directory / "receipt.json")
        result.update({key: receipt[key] for key in ("action_id", "source_commit", "operator_sha256", "status")})
        result["returncode"] = receipt.get("returncode")
        if receipt.get("error"):
            result["operator_error"] = receipt["error"]
        observed = observe(directory)
        result.update({key: observed[key] for key in ("progress", "event_error") if key in observed})
        if receipt["status"] not in {"failed", "interrupted"} and "result" in observed:
            result["result"] = observed["result"]
    return clean(result)


def publication_signature(status: dict[str, Any]) -> str:
    """Ignore batch counters; publish phase, score, action or terminal changes."""
    progress = status.get("progress", {})
    chosen = {key: value for key, value in status.items() if key not in {"updated_at", "progress"}}
    chosen["progress"] = {
        key: value for key, value in progress.items()
        if key in {"phase", "status", "stage", "split", "arm", "scores", "score", "validation", "spearman", "mse", "mse_0_1", "false_positive_rate", "recall", "selection", "selected_epoch", "eligible", "gate"}
    }
    metrics = progress.get("metrics", {})
    if isinstance(metrics, dict):
        chosen["progress"]["metrics"] = {
            key: value for key, value in metrics.items()
            if any(word in key.lower() for word in ("spearman", "mse", "recall", "accuracy", "false_positive", "score"))
        }
    return hashlib.sha256(json.dumps(chosen, sort_keys=True, allow_nan=False).encode()).hexdigest()


def run_worker() -> int:
    """Poll one control path, serializing actions and recovering existing children."""
    WORK_ROOT.mkdir(parents=True, exist_ok=True, mode=0o700)
    os.chmod(WORK_ROOT, 0o700)
    with (WORK_ROOT / "worker.lock").open("a+") as lock:
        try:
            fcntl.flock(lock.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            return 0
        state_path = WORK_ROOT / "worker_state.json"
        state = read_json(state_path, {})
        active, process, last = None, None, None
        for receipt_path in sorted((WORK_ROOT / "actions").glob("*/receipt.json")):
            if still_active(receipt_path.parent):
                if active is not None:
                    publish(status_for(active, "blocked", "Multiple in-flight action receipts require reconciliation"))
                    return 2
                active = receipt_path.parent
            last = receipt_path.parent
        stop_requested = bool(state.get("stop_requested", False))
        started = time.monotonic()
        last_published, last_signature = 0.0, ""
        while time.monotonic() - started < MAX_SECONDS:
            cycle_started = time.monotonic()
            error = None
            try:
                _, contents = github_file(CONTROL_PATH, BRANCH)
                control = validate_control(json.loads(contents or b"null"))
                if control["action"] == "stop":
                    stop_requested = True
                    state["stop_requested"] = True
                    save_json(state_path, state)
                if active is not None:
                    observe(active)
                    if not still_active(active, process):
                        last, active, process = active, None, None
                if not stop_requested and active is None and control["action"] == "run":
                    directory, child = launch(control)
                    last = directory
                    if still_active(directory, child):
                        active, process = directory, child
            except (OSError, ValueError, RuntimeError, subprocess.TimeoutExpired):
                error = "Control fetch, validation or action binding failed; no unverified action launched"
                if active is not None:
                    observe(active)
                    if not still_active(active, process):
                        last, active, process = active, None, None
            worker_state = "draining" if stop_requested and active else "stopped" if stop_requested else "running" if active else "waiting"
            status = status_for(active or last, worker_state, error)
            signature = publication_signature(status)
            if signature != last_signature or time.monotonic() - last_published >= HEARTBEAT_SECONDS:
                if publish(status):
                    last_signature, last_published = signature, time.monotonic()
            if stop_requested and active is None:
                state.update(stop_requested=False, stopped_at=now())
                save_json(state_path, state)
                return 0
            time.sleep(min(
                max(0.0, POLL_SECONDS - (time.monotonic() - cycle_started)),
                max(0.0, MAX_SECONDS - (time.monotonic() - started)),
            ))
        publish(status_for(active or last, "deadline_reached"))
        return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--supervise", help=argparse.SUPPRESS)
    arguments = parser.parse_args()
    raise SystemExit(supervise(arguments.supervise) if arguments.supervise else run_worker())
