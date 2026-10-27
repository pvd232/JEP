#!/usr/bin/env python3
"""Continuously publish completed training epochs through existing local SSH access."""

import argparse
import fcntl
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
from datetime import datetime, timezone

BRANCH = "experiment/csts-proposition-evidence-20261026"
REPORT_DIRECTORY = "training_outputs/proposition_full_20261026"
JSON_PATH = REPORT_DIRECTORY + "/epoch_scores.json"
MARKDOWN_PATH = REPORT_DIRECTORY + "/epoch_scores.md"
REMOTE_SCRIPT = r'''
import json
from pathlib import Path
import subprocess
import time
operator = Path('/home/machina/jep-csts-proposition-indicative-20261026-operator')
output = operator / 'epoch_publication'
lease = operator / 'publication_controller_status.json'
old = json.loads(lease.read_text()) if lease.exists() else {}
if old.get('owner') not in (None, publisher_owner) and time.time() - old.get('checked_unix', 0) < 90:
    raise RuntimeError('Another epoch publisher has a current heartbeat')
command = ['python3', str(operator/'export_epoch_scores.py'), '--root', '/home/machina/jep-csts-proposition-evidence-20261026', '--name', 'propositions_v41_full_after_indicative', '--output', str(output)]
subprocess.run(command, check=True, capture_output=True, text=True, timeout=30)
heartbeat = {'owner': publisher_owner, 'mode': 'detached_mac_ssh_publisher', 'status': 'running', 'poll_seconds': 30, 'checked_unix': time.time()}
temporary = lease.with_suffix('.tmp')
temporary.write_text(json.dumps(heartbeat))
temporary.replace(lease)
print(json.dumps({'report': json.loads((output/'epoch_scores.json').read_text()), 'markdown': (output/'epoch_scores.md').read_text()}))
'''


def utc():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def atomic_json(path, value):
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, indent=2, allow_nan=False) + "\n")
    os.replace(temporary, path)


def signature(report):
    """Ignore polling timestamps and optimizer steps within unfinished epochs."""
    value = {key: report.get(key) for key in ("identity", "run_status", "current_stage")}
    value["stages"] = {
        stage: {key: data.get(key) for key in ("status", "trace_status", "epochs", "stop_reason", "notes")}
        for stage, data in report["stages"].items()
    }
    return hashlib.sha256(json.dumps(value, sort_keys=True, allow_nan=False).encode()).hexdigest()


def stale_snapshot(report, published):
    if report.get("identity") != published.get("identity"):
        raise ValueError("Published experiment identity differs")
    for stage, data in published.get("stages", {}).items():
        saved = {row["epoch"]: row for row in data.get("epochs", [])}
        current = {row["epoch"]: row for row in report["stages"].get(stage, {}).get("epochs", [])}
        if saved.keys() - current.keys():
            return True
        for epoch in saved.keys() & current.keys():
            if saved[epoch] != current[epoch]:
                raise ValueError("Conflicting completed epoch in " + stage)
    return False


def command(arguments, *, cwd=None, data=None, environment=None, timeout=60, check=True):
    result = subprocess.run(arguments, cwd=cwd, input=data, text=True, capture_output=True,
                            env=environment, timeout=timeout)
    if check and result.returncode:
        raise RuntimeError("Command failed: " + " ".join(arguments[:3]) + ": " + result.stderr[-2500:])
    return result


def git(repo, arguments, *, data=None, environment=None, check=True):
    env = os.environ.copy()
    env["GIT_TERMINAL_PROMPT"] = "0"
    env.setdefault("GIT_SSH_COMMAND", "ssh -o BatchMode=yes -o ConnectTimeout=15")
    if environment:
        env.update(environment)
    return command(["git", *arguments], cwd=repo, data=data, environment=env, check=check)


def read_remote(transport, owner):
    script = "publisher_owner = " + repr(owner) + "\n" + REMOTE_SCRIPT
    result = command([sys.executable, str(transport), "python3", "-"], data=script, timeout=95)
    envelope = json.loads(result.stdout)
    if not isinstance(envelope.get("report"), dict) or not isinstance(envelope.get("markdown"), str):
        raise ValueError("Invalid remote report envelope")
    identity = envelope["report"]["identity"]
    if (identity["source_commit"] != "a6daf0eeea544716d7340f0f24de687e4ba93490"
            or identity["run_name"] != "propositions_v41_full_after_indicative"
            or identity["validation_sha256"] != "f186e86877e731c96ee9b1c819863b981074bc500dc9aa11c6951ba9fd56e2c9"):
        raise ValueError("Unexpected full experiment identity")
    return envelope


def read_local(root, operator, owner):
    lease = operator / "publication_controller_status.json"
    previous = json.loads(lease.read_text()) if lease.exists() else {}
    if previous.get("owner") not in (None, owner) and time.time() - previous.get("checked_unix", 0) < 90:
        raise RuntimeError("Another epoch publisher has a current heartbeat")
    output = operator / "epoch_publication"
    command([sys.executable, str(operator / "export_epoch_scores.py"), "--root", str(root), "--output", str(output)], timeout=30)
    envelope = {"report": json.loads((output / "epoch_scores.json").read_text()), "markdown": (output / "epoch_scores.md").read_text()}
    identity = envelope["report"]["identity"]
    if (identity["source_commit"] != "a6daf0eeea544716d7340f0f24de687e4ba93490"
            or identity["run_name"] != "propositions_v41_full_after_indicative"
            or identity["validation_sha256"] != "f186e86877e731c96ee9b1c819863b981074bc500dc9aa11c6951ba9fd56e2c9"):
        raise ValueError("Unexpected full experiment identity")
    return envelope


def heartbeat(operator, state):
    if operator is not None:
        atomic_json(operator / "publication_controller_status.json", {
            **state, "checked_unix": time.time(), "mode": "native_gpu_process",
        })


def publish(repo, envelope, state_directory):
    """Build a commit over each fetched head; fast-forward push rejects races."""
    report = envelope["report"]
    files = {
        JSON_PATH: json.dumps(report, indent=2, allow_nan=False) + "\n",
        MARKDOWN_PATH: envelope["markdown"],
    }
    for path, content in files.items():
        destination = repo / path
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(content)
    for attempt in range(3):
        git(repo, ["fetch", "--quiet", "origin", BRANCH])
        parent = git(repo, ["rev-parse", "FETCH_HEAD"]).stdout.strip()
        saved = git(repo, ["show", parent + ":" + JSON_PATH], check=False)
        if saved.returncode == 0:
            published = json.loads(saved.stdout)
            if stale_snapshot(report, published):
                return {"published": False, "reason": "remote_history_ahead", "commit": parent}
            if signature(report) == signature(published):
                return {"published": False, "reason": "unchanged", "commit": parent}
        with tempfile.TemporaryDirectory(prefix="git-index-", dir=state_directory) as temporary:
            environment = {"GIT_INDEX_FILE": str(Path(temporary) / "index")}
            git(repo, ["read-tree", parent], environment=environment)
            for path, content in files.items():
                blob = git(repo, ["hash-object", "-w", "--stdin"], data=content).stdout.strip()
                git(repo, ["update-index", "--add", "--cacheinfo", "100644," + blob + "," + path], environment=environment)
            tree = git(repo, ["write-tree"], environment=environment).stdout.strip()
            commit = git(repo, ["commit-tree", tree, "-p", parent], data="Publish completed Qwen validation epochs\n").stdout.strip()
        pushed = git(repo, ["push", "--quiet", "origin", commit + ":refs/heads/" + BRANCH], check=False)
        if pushed.returncode == 0:
            return {"published": True, "reason": "new_epochs_or_status", "commit": commit}
        if attempt == 2:
            raise RuntimeError("Epoch publication push failed: " + pushed.stderr[-2500:])
    raise RuntimeError("Publication attempts exhausted")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--transport", type=Path, default=Path(__file__).with_name("proposition_epoch_ssh.py"))
    parser.add_argument("--state-directory", type=Path, required=True)
    parser.add_argument("--poll-seconds", type=float, default=30)
    parser.add_argument("--once", action="store_true")
    parser.add_argument("--local-root", type=Path)
    parser.add_argument("--operator-directory", type=Path)
    parser.add_argument("--cleanup-key", type=Path)
    args = parser.parse_args()
    if bool(args.local_root) != bool(args.operator_directory):
        parser.error("Local root and operator directory must be supplied together")
    if args.poll_seconds < 5:
        parser.error("Polling interval must be at least five seconds")
    args.repo = args.repo.resolve()
    args.state_directory.mkdir(parents=True, exist_ok=True)
    lock = (args.state_directory / "publisher.lock").open("a+")
    try:
        fcntl.flock(lock.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        raise SystemExit("Epoch publisher already running")
    owner = ("native-gpu-publisher-" if args.local_root else "mac-publisher-") + hashlib.sha256(str(args.state_directory.resolve()).encode()).hexdigest()[:16]
    state = {"owner": owner, "pid": os.getpid(), "started_at_utc": utc(), "poll_seconds": args.poll_seconds,
             "status": "starting", "consecutive_failures": 0}
    atomic_json(args.state_directory / "publisher_status.json", state)
    last_signature = None
    while True:
        started = time.monotonic()
        try:
            envelope = read_local(args.local_root, args.operator_directory, owner) if args.local_root else read_remote(args.transport, owner)
            report = envelope["report"]
            current_signature = signature(report)
            result = {"published": False, "reason": "unchanged_local"}
            if current_signature != last_signature:
                result = publish(args.repo, envelope, args.state_directory)
                if result["reason"] != "remote_history_ahead":
                    last_signature = current_signature
            state.update(status="running", last_checked_at_utc=utc(), last_success_at_utc=utc(),
                         consecutive_failures=0, run_status=report.get("run_status"),
                         current_stage=report.get("current_stage"),
                         epochs={stage: data["completed_epoch"] for stage, data in report["stages"].items()})
            state.pop("last_error", None)
            if result.get("commit"):
                state["latest_commit"] = result["commit"]
            if result["published"]:
                state["last_published_at_utc"] = utc()
                print(json.dumps({"at": utc(), **result, "epochs": state["epochs"]}), flush=True)
            atomic_json(args.state_directory / "publisher_status.json", state)
            heartbeat(args.operator_directory, state)
            if report.get("run_status") in ("complete", "completed", "succeeded"):
                state["status"] = "complete"
                atomic_json(args.state_directory / "publisher_status.json", state)
                heartbeat(args.operator_directory, state)
                if args.cleanup_key:
                    args.cleanup_key.unlink(missing_ok=True)
                return
        except Exception as error:
            state.update(status="retrying", last_checked_at_utc=utc(), last_error=str(error),
                         consecutive_failures=state["consecutive_failures"] + 1)
            atomic_json(args.state_directory / "publisher_status.json", state)
            heartbeat(args.operator_directory, state)
            print(json.dumps({"at": utc(), "status": "retrying", "error": str(error)}), flush=True)
            if args.once:
                raise
        if args.once:
            return
        time.sleep(max(0, args.poll_seconds - (time.monotonic() - started)))


if __name__ == "__main__":
    main()
