"""Publish bounded, read-only training observations to a dedicated GitHub branch."""
from __future__ import annotations

import argparse
import concurrent.futures
import datetime as dt
import fcntl
import inspect
import json
import math
from pathlib import Path
import shlex
import statistics
import subprocess
import time
from zoneinfo import ZoneInfo

BRANCH = "monitor/full-data-prompt-20261107"
STATUS = "plans/full_data_prompt_20261107/live-status"
EASTERN = ZoneInfo("America/New_York")


def command(args, cwd=None, timeout=120):
    """Capture a bounded command while retaining existing authentication."""
    return subprocess.run(args, cwd=cwd, text=True, capture_output=True, timeout=timeout, check=True)


def project_state(state):
    """Keep progress counters and scientific identity while excluding artifact payloads."""
    trials = {}
    for name, trial in state.get("trials", {}).items():
        selection = trial.get("selection")
        trials[name] = {"epochs": len(trial.get("records", [])),
                        "seconds": [r.get("seconds") for r in trial.get("records", [])],
                        "selected_epoch": selection.get("selected_epoch") if selection else None,
                        "finished": bool(selection)}
    return {"status": state.get("status"), "worker": state.get("worker"),
            "source_commit": state.get("source_commit"), "seeds": state.get("seeds", []),
            "execution_id": state.get("lease", {}).get("execution_id"),
            "test_opened": state.get("test_opened"), "trials": trials}


REMOTE = """
import datetime, json, pathlib, subprocess, urllib.request
worker = __WORKER__
root = pathlib.Path("/home/machina/jep-full-data-task-20261107/repo")
folder = root / "baseline_results/full_data_prompt_20261107" / worker
request = urllib.request.Request("http://metadata.google.internal/computeMetadata/v1/instance/id", headers={"Metadata-Flavor":"Google"})
with urllib.request.urlopen(request, timeout=5) as response:
    instance_id = response.read().decode().strip()
state = project_state(json.loads((folder / "state.json").read_text()))
events = []
log = subprocess.run(["sudo", "-n", "journalctl", "-u", "jep-east-asia-train-" + worker + "-20261108.service", "-n", "30", "-o", "cat", "--no-pager"], capture_output=True, text=True, timeout=10)
for line in log.stdout.splitlines():
    try:
        event = json.loads(line)
        if event.get("event") == "native_epoch_start":
            events.append({key:event.get(key) for key in ["utc", "trial", "epoch"]})
    except json.JSONDecodeError:
        pass
verified = 0
native = 0
pending = 0
last_verified = None
for path in (folder / "transfer").glob("*/ready.json"):
    try:
        manifest = json.loads(path.read_text())
        ack_path = path.parent / "ack.json"
        ack = json.loads(ack_path.read_text()) if ack_path.exists() else {}
        valid = ack.get("cloud_roundtrip_verified") is True and all(ack.get(k) == manifest.get(k) for k in ["generation", "source_commit", "archive_sha256", "execution_id", "instance_id"])
        if not valid:
            pending += 1
        elif "_epoch" in manifest["generation"]:
            verified += 1
            native += ack.get("transport") == "viper_cloud"
            if ack.get("verified_utc"):
                last_verified = max(last_verified or "", ack["verified_utc"])
    except (OSError, ValueError, KeyError):
        pending += 1
gpu = subprocess.check_output(["nvidia-smi", "--query-gpu=uuid,utilization.gpu", "--format=csv,noheader"], text=True, timeout=10).strip()
services = {}
for role in ["train", "upload"]:
    services[role] = subprocess.run(["systemctl", "is-active", "jep-east-asia-" + role + "-" + worker + "-20261108.service"], capture_output=True, text=True, timeout=5).stdout.strip()
print(json.dumps({"observed_utc":datetime.datetime.now(datetime.timezone.utc).isoformat(), "instance_id":instance_id, "state":state, "epoch_start":events[-1] if events else None, "gpu":gpu, "services":services, "verified_epoch_checkpoints":verified, "native_viper_checkpoints":native, "pending_generations":pending, "last_verified_utc":last_verified}))
"""


def observe(worker, data):
    """Report controller failure separately from independent GPU activity."""
    approval = json.loads((data / ("approval-" + worker + ".json")).read_text())
    assignment = approval["assignments"][worker]
    state_file = data / ("collection-" + worker) / (worker + "-latest-state.json")
    try:
        state = project_state(json.loads(state_file.read_text()))
    except (OSError, ValueError):
        state = {"trials": {}, "seeds": []}
    result = {"worker": worker, "zone": assignment["zone"], "state": state,
              "fresh": False, "source": "collector_snapshot",
              "observed_utc": dt.datetime.fromtimestamp(state_file.stat().st_mtime, dt.timezone.utc).isoformat() if state_file.exists() else None}
    final = data / ("collection-" + worker) / "collection-final.json"
    if final.exists():
        try:
            receipt = json.loads(final.read_text())[0]
            cleanup_file = data / ("collection-" + worker) / (worker + "-cleanup.json")
            cleanup = json.loads(cleanup_file.read_text()) if cleanup_file.exists() else {}
            if (receipt["status"] == "training_collected_test_still_locked"
                    and cleanup.get("instance_deleted") is True):
                result.update(final=receipt, source="verified_controller_completion", fresh=True)
                result["cleanup"] = cleanup
                result["verified_epoch_checkpoints"] = sum(t["epochs"] for t in state["trials"].values())
                result["pending_generations"] = 0
                return result
            result["controller_final"] = receipt
            result["source"] = "collector_snapshot_after_controller_failure"
        except (OSError, ValueError, IndexError, KeyError):
            pass
    script = inspect.getsource(project_state) + REMOTE.replace("__WORKER__", repr(worker))
    try:
        response = command(["gcloud", "compute", "ssh", "machina@" + assignment["instance_name"],
                            "--zone=" + assignment["zone"], "--project=" + assignment["project"],
                            "--account=" + approval["controller_account"], "--quiet", "--tunnel-through-iap",
                            "--command=python3 -c " + shlex.quote(script)], timeout=90)
        live = json.loads(response.stdout)
        assert live["instance_id"] == assignment["instance_id"]
        assert live["state"]["source_commit"] == approval["source_commit"]
        assert live["state"]["execution_id"] == assignment["execution_id"]
        assert live["gpu"].split(",", 1)[0].strip() == assignment["gpu_uuid"]
        result.update(live, fresh=True, source="guest_observation")
    except (subprocess.SubprocessError, ValueError, AssertionError, OSError) as error:
        result["probe_error"] = type(error).__name__
        detail = str(getattr(error, "stderr", "") or error).lower()
        result["access_status"] = "authentication_required" if "reauthentication" in detail or "no valid credentials" in detail else "observation_unavailable"
    return result

def forecast(workers, cases, now):
    """Estimate the longest worker queue from observed epoch times and stopping lengths."""
    seconds = [s for w in workers for t in w["state"]["trials"].values()
               for s in t["seconds"] if isinstance(s, (int, float)) and math.isfinite(s) and 0 < s < 86400]
    lengths = [t["epochs"] for w in workers for t in w["state"]["trials"].values() if t["finished"]]
    failed = any(w.get("final", {}).get("status", "training_collected_test_still_locked") != "training_collected_test_still_locked"
                 or w["state"].get("status") == "failed_preserved" for w in workers)
    if failed or len(lengths) < 2 or not seconds or any(not w["fresh"] for w in workers):
        return None
    per_epoch = statistics.median(seconds)
    low, middle, high = min(lengths), statistics.median(lengths), max(max(lengths), min(lengths) + 2)
    forecasts = []
    for assumed in [low, middle, high]:
        remaining = []
        for worker in workers:
            epochs = 0
            for case in cases:
                if case["seed"] not in worker["state"]["seeds"]:
                    continue
                trial = worker["state"]["trials"].get(case["trial_id"])
                if trial and trial["finished"]:
                    continue
                epochs += max(1, assumed - trial["epochs"]) if trial else assumed
            remaining.append(epochs * per_epoch)
        forecasts.append(now + max(remaining, default=0))
    return {"epoch_minutes": per_epoch / 60, "finished_fit_samples": len(lengths),
            "assumed_epochs_per_fit": [low, middle, high],
            "earliest_epoch": forecasts[0], "central_epoch": forecasts[1], "latest_epoch": forecasts[2],
            "basis": "Conditional on remaining fits following observed stopping lengths; unfinished epochs counted conservatively. Spot interruptions and continued validation improvement can extend the estimate."}


def eastern(timestamp):
    """Format user-facing times in New York."""
    return dt.datetime.fromtimestamp(timestamp, EASTERN).strftime("%a %-I:%M %p %Z")


def render(report, cases):
    """Keep last confirmed work distinct from current GPU and cleanup observations."""
    workers = report["workers"]
    count = sum(t["finished"] for w in workers for t in w["state"]["trials"].values())
    all_fresh = all(w["fresh"] for w in workers)
    count_label = "Training fits finished" if all_fresh else "Fits confirmed finished at the last successful observations"
    test_line = ("The held-out test remains sealed for evaluation." if all_fresh else
                 "The held-out test was sealed at the last successful observations.") if all(w["state"].get("test_opened") is False for w in workers) else "The held-out test flag needs confirmation."
    lines = ["# Live training status", "",
             "Page checked: " + eastern(report["generated_epoch"]) + ". Worker observation times appear below.",
             "The background reporter checks every five minutes. A page update does not establish a fresh GPU observation.",
             "", "**" + count_label + ": " + str(count) + " / " + str(len(cases)) + ".**",
             test_line, ""]
    if report.get("monitor_status") == "final":
        lines += ["**Both workers have verified publication and successful compute cleanup receipts.**", ""]
    elif report.get("monitor_status") == "controller_unavailable":
        auth = any(w.get("access_status") == "authentication_required" for w in workers)
        lines += ["**" + ("Google reauthentication is required for monitoring." if auth else "The monitoring controllers failed.") +
                  " Current GPU activity, training completion and cleanup are unconfirmed.**", ""]
    elif report.get("monitor_status") == "runtime_limit":
        lines += ["**The reporter reached its runtime limit; this page has stopped refreshing.**", ""]
    eta = report["forecast"]
    if eta and count < len(cases):
        lines += ["**Estimated training finish: " + eastern(eta["central_epoch"]) + "**",
                  "Planning range: " + eastern(eta["earliest_epoch"]) + " to " + eastern(eta["latest_epoch"]) + ".",
                  "Basis: %.1f minutes per completed epoch; %s–%s total epochs per remaining fit, based on %s stopped fits." %
                  (eta["epoch_minutes"], eta["assumed_epochs_per_fit"][0], eta["assumed_epochs_per_fit"][2], eta["finished_fit_samples"]),
                  "Validation stopping or Spot interruptions can extend this estimate.", ""]
    elif count < len(cases):
        lines += ["There is no current ETA while worker observations are unavailable.", ""]
    lines += ["| Placement | Current work | Fits confirmed finished | GPU use | Cloud-verified epochs | Uploads pending |",
              "| --- | --- | ---: | ---: | ---: | ---: |"]
    for worker in workers:
        trials = worker["state"]["trials"]
        assigned = [c for c in cases if c["seed"] in worker["state"]["seeds"]]
        done = sum(t["finished"] for t in trials.values())
        event = worker.get("epoch_start")
        phase = (event["trial"] + ", epoch " + str(event["epoch"])) if event else worker["state"].get("status", "unconfirmed")
        if event and trials.get(event["trial"], {}).get("finished"):
            phase = "Preparing next fit"
        if worker["state"].get("status") == "assigned_training_complete_test_not_opened":
            phase = "Training finished; verifying cloud publication"
        elif worker["state"].get("status") == "failed_preserved":
            phase = "Worker reported failure; recovery state retained"
        if worker.get("final"):
            phase = "Publication verified; compute cleanup confirmed"
        if not worker["fresh"]:
            phase = "Current state unknown; last confirmed progress shown"
        location = "Seoul" if worker["zone"].startswith("asia-northeast3") else "Taiwan"
        gpu = (worker.get("gpu", "").split(",", 1)[-1].strip() or "—") if worker["fresh"] else "—"
        lines.append("| %s (%s) | %s | %s / %s | %s | %s | %s |" %
                     (location, worker["zone"], phase, done, len(assigned), gpu,
                      worker.get("verified_epoch_checkpoints", "—"), worker.get("pending_generations", "—")))
    lines += ["", "New checkpoint publications use native VIPER Cloud.",
              "Cleanup is unconfirmed while the controllers cannot access Google Cloud." if report.get("monitor_status") == "controller_unavailable" else
              "Controllers delete exact owned resources after verified publication and retain unverified recovery disks.", ""]
    for worker in workers:
        lines += [worker["worker"] + " last successful worker observation: " + str(worker.get("observed_utc")) + "."]
    lines += ["", "| Fit | Epochs completed at last observation | Status | Selected epoch |", "| --- | ---: | --- | ---: |"]
    running_ids = {w["epoch_start"]["trial"] for w in workers if w["fresh"] and w.get("epoch_start") and w["state"].get("status") == "running"}
    for case in cases:
        trial = next((w["state"]["trials"][case["trial_id"]] for w in workers if case["trial_id"] in w["state"]["trials"]), None)
        phase = "Finished" if trial and trial["finished"] else ("Running" if case["trial_id"] in running_ids else ("Checkpointed" if trial else "No completed epoch observed"))
        lines.append("| %s | %s | %s | %s |" % (case["trial_id"], trial["epochs"] if trial else 0,
                     phase, trial["selected_epoch"] if trial and trial["finished"] else "—"))
    lines += ["", "[Structured status](live-status.json) · [Deployment records](https://github.com/pvd232/JEP/blob/experiment/qwen-full-data-prompt-20261107/plans/full_data_prompt_20261107/lifecycle-launch-20261108/README.md)", "",
              "Monitoring reads progress metadata and publication receipts.", ""]
    return "\n".join(lines)

def publish(root):
    """Push only generated status files to the dedicated monitoring branch."""
    paths = [STATUS + ".md", STATUS + ".json"]
    command(["git", "add", "--", *paths], root)
    if subprocess.run(["git", "diff", "--cached", "--quiet"], cwd=root).returncode == 0:
        return
    name, email = command(["git", "log", "-1", "--format=%an%n%ae"], root).stdout.splitlines()
    command(["git", "-c", "user.name=" + name, "-c", "user.email=" + email,
             "commit", "-m", "Update live training observations [skip ci]"], root)
    command(["git", "push", "origin", "HEAD:refs/heads/" + BRANCH], root)


def main():
    """Run a bounded metadata publisher without owning or changing GPU jobs."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, required=True)
    parser.add_argument("--interval", type=int, default=300)
    parser.add_argument("--max-hours", type=float, default=24)
    parser.add_argument("--once", action="store_true")
    parser.add_argument("--publish", action="store_true")
    args = parser.parse_args()
    if not 60 <= args.interval <= 900 or not 0 < args.max_hours <= 26:
        raise ValueError("Use bounded monitoring cadence and duration.")
    root = Path(__file__).resolve().parents[2]
    if command(["git", "branch", "--show-current"], root).stdout.strip() != BRANCH:
        raise PermissionError("The reporter requires its dedicated monitoring branch.")
    from csts_pilot.full_data_prompt_protocol import trial_matrix
    cases = trial_matrix(json.loads((root / "configs/csts-full-data-prompt-20261107.json").read_text()))
    deadline = time.monotonic() + args.max_hours * 3600
    with (args.data / "github-status-publisher.lock").open("a+") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        while True:
            with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
                workers = list(pool.map(lambda w: observe(w, args.data), ["worker1", "worker2"]))
            now = time.time()
            report = {"generated_epoch": now, "generated_utc": dt.datetime.fromtimestamp(now, dt.timezone.utc).isoformat(),
                      "cadence_seconds": args.interval, "training_mode": "independent_seed_workers",
                      "target_fits": len(cases), "workers": workers, "forecast": forecast(workers, cases, now)}
            terminal = all("final" in w for w in workers)
            blocked = any(w.get("controller_final") and not w["fresh"] for w in workers)
            report["monitor_status"] = "final" if terminal else ("runtime_limit" if time.monotonic() >= deadline else ("controller_unavailable" if blocked else "active"))
            (root / (STATUS + ".json")).write_text(json.dumps(report, indent=2) + "\n")
            (root / (STATUS + ".md")).write_text(render(report, cases))
            if args.publish:
                try:
                    publish(root)
                except subprocess.SubprocessError as error:
                    print(json.dumps({"publication_retry_pending": type(error).__name__}), flush=True)
            print(json.dumps({"updated_utc": report["generated_utc"], "monitor_status": report["monitor_status"],
                              "finished_fits": sum(t["finished"] for w in workers for t in w["state"]["trials"].values()),
                              "forecast": report["forecast"]}), flush=True)
            if args.once or terminal or time.monotonic() >= deadline:
                break
            wake = time.monotonic() + args.interval
            while time.monotonic() < wake:
                time.sleep(min(30, wake - time.monotonic()))


if __name__ == "__main__":
    main()
