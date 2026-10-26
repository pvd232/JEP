"""Retain an owner-run native validation receipt beyond the Mac action lifetime."""

import argparse
import fcntl
import hashlib
import json
import os
import re
import signal
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Any


def save(path: Path, value: Any) -> None:
    with tempfile.NamedTemporaryFile("w", dir=path.parent, delete=False) as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2, allow_nan=False)
        stream.write("\n")
        stream.flush()
        os.fsync(stream.fileno())
        temporary = Path(stream.name)
    temporary.replace(path)


def supervise(root: Path, parent: Path, name: str, commit: str, module: str) -> dict[str, Any]:
    root, parent = root.resolve(strict=True), parent.resolve(strict=True)
    directory = root / "answer_input_results" / "supervisors" / name
    receipt_path = directory / "receipt.json"
    with (directory / "supervisor.lock").open("a+") as lock:
        fcntl.flock(lock.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        receipt = json.loads(receipt_path.read_text())
        if receipt["source_commit"] != commit or receipt["name"] != name or receipt.get("module") != module:
            raise ValueError("Supervisor launch binding differs.")
        if receipt["status"] in {"complete", "failed", "timed_out"}:
            return receipt
        actual = subprocess.check_output(["git", "-C", str(root), "rev-parse", "HEAD"], text=True).strip()
        dirty = subprocess.check_output(["git", "-C", str(root), "status", "--porcelain", "--untracked-files=no"], text=True).strip()
        if actual != commit or dirty:
            raise ValueError("Native source is not the checked clean commit.")
        checks = json.loads((root / "answer_input_results/owner_checks" / commit / "receipt.json").read_text())
        if checks.get("passed") is not True or checks.get("source_clean") is not True:
            raise ValueError("Owner checks did not pass on clean source.")
        for path, expected in checks["owned_source_sha256"].items():
            if hashlib.sha256((root / path).read_bytes()).hexdigest() != expected:
                raise ValueError("Checked native source changed.")
        if module not in {"csts_pilot.proposition_run", "csts_pilot.proposition_sample"}:
            raise ValueError("Native module is outside the fixed allowlist.")
        command = [sys.executable, "-m", module, "--root", str(root), "--parent-root", str(parent), "--name", name]
        receipt.update(status="running", supervisor_pid=os.getpid(), started_unix=time.time())
        save(receipt_path, receipt)
        try:
            with (directory / "native.stdout").open("ab") as stdout, (directory / "native.stderr").open("ab") as stderr:
                child = subprocess.Popen(command, cwd=root, stdin=subprocess.DEVNULL, stdout=stdout, stderr=stderr, start_new_session=True)
                receipt["native_pid"] = child.pid
                save(receipt_path, receipt)
                try:
                    returncode = child.wait(timeout=21600)
                except subprocess.TimeoutExpired:
                    os.killpg(child.pid, signal.SIGTERM)
                    try:
                        child.wait(timeout=30)
                    except subprocess.TimeoutExpired:
                        os.killpg(child.pid, signal.SIGKILL)
                        child.wait()
                    receipt.update(status="timed_out", error="Native validation exceeded six-hour supervisor allowance.")
                else:
                    receipt.update(status="complete" if returncode == 0 else "failed", returncode=returncode)
        except Exception:
            receipt.update(status="failed", error="Native supervisor failed; task logs retained.")
            raise
        finally:
            receipt["finished_unix"] = time.time()
            save(receipt_path, receipt)
        return receipt


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", required=True, type=Path)
    parser.add_argument("--parent-root", required=True, type=Path)
    parser.add_argument("--name", required=True)
    parser.add_argument("--source-commit", required=True)
    parser.add_argument("--module", required=True, choices=("csts_pilot.proposition_run", "csts_pilot.proposition_sample"))
    args = parser.parse_args()
    if re.fullmatch(r"[0-9a-f]{40}", args.source_commit) is None or re.fullmatch(r"[A-Za-z0-9_-]{1,80}", args.name) is None:
        parser.error("Use a complete commit and safe attempt name.")
    result = supervise(args.root, args.parent_root, args.name, args.source_commit, args.module)
    print(json.dumps({"phase": "native_supervisor", **result}, allow_nan=False), flush=True)


if __name__ == "__main__":
    main()
