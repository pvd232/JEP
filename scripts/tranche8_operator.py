"""Finish the approved Tranche 8 work using two immutable source bindings.

This Mac controller does not edit source, change generation policy, repeat a
baseline, or select on test.  Active capture/native/test children survive its
deadline.  Only the two explicitly authorized repository status files are
written externally; each update is guarded by the current Git blob identity.
"""

import argparse
import base64
import fcntl
import hashlib
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
import traceback
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import quote
from zoneinfo import ZoneInfo

REPO = "pvd232/JEP"
BRANCH = "experiment/csts-proposition-lora-20261026"
WORK_ROOT = Path("/tmp/jep-tranche8-worker-20261026/pipeline")
CAPTURE_COMMIT = "8a0b50d5bdd2a77ab0c9444f4bf10d484f8ba6bb"
NATIVE_HELPER_SHA256 = "4928c30aa81fbf253dbd7e9c4b538aef067cc9c5acf7f6782c5a26b57d618525"
NATIVE_HELPER = "scripts/tranche8_native.py"
TEST_HELPER = "scripts/tranche8_test_capture.py"
STATUS_PATH = "training_outputs/csts_tranche8_status.md"
RESULT_PATH = "training_outputs/csts_tranche8_results.json"
SAMPLE_NAME = "source_sample_v1"
VALIDATION_NAME = "proposition_lora_v2"
PRIVATE_KEYS = {"command", "commands", "argv", "arguments", "env", "environment", "environ", "stdout", "stderr", "prompt", "passage", "sentence1", "sentence2", "records", "credentials", "token", "access_token", "refresh_token", "password", "authorization", "api_key"}
TERMINAL_FAILURE = {"failed", "interrupted", "timed_out"}


class PipelineFailure(RuntimeError):
    """Safe orchestration failure; private process logs are never included."""


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def save(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    with tempfile.NamedTemporaryFile("w", dir=path.parent, delete=False) as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2, allow_nan=False)
        stream.write("\n")
        stream.flush()
        os.fsync(stream.fileno())
        temporary = Path(stream.name)
    temporary.replace(path)


def gh() -> str:
    path = shutil.which("gh") or next((str(p) for p in (Path("/opt/homebrew/bin/gh"), Path("/usr/local/bin/gh")) if p.is_file()), None)
    if path is None:
        raise PipelineFailure("The existing gh executable is unavailable.")
    return path


def github_file(path: str, ref: str, missing_ok: bool = False) -> tuple[dict[str, Any] | None, bytes | None]:
    if path not in {NATIVE_HELPER, TEST_HELPER, STATUS_PATH, RESULT_PATH}:
        raise PipelineFailure("GitHub path is outside the fixed pipeline allowlist.")
    endpoint = f"repos/{REPO}/contents/{path}?ref={quote(ref, safe='')}"
    response = subprocess.run([gh(), "api", endpoint], stdin=subprocess.DEVNULL, capture_output=True, timeout=45, check=False)
    if response.returncode:
        if missing_ok and path == RESULT_PATH and b"HTTP 404" in response.stderr:
            return None, None
        raise PipelineFailure("A pinned source/status fetch failed; no credentials or response text published.")
    record = json.loads(response.stdout)
    if record.get("type") != "file" or record.get("path") != path or record.get("encoding") != "base64":
        raise PipelineFailure("GitHub returned an unexpected file identity.")
    data = base64.b64decode("".join(record["content"].split()), validate=True)
    if hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest() != record.get("sha"):
        raise PipelineFailure("A GitHub blob failed its identity check.")
    return record, data


def guarded_write(path: str, data: bytes) -> None:
    if path not in {STATUS_PATH, RESULT_PATH}:
        raise PipelineFailure("Only the fixed Tranche 8 status/results files may be written.")
    for _ in range(3):
        previous, old = github_file(path, BRANCH, missing_ok=path == RESULT_PATH)
        if old == data:
            return
        request = {"branch": BRANCH, "message": "Update Tranche 8 experiment status", "content": base64.b64encode(data).decode()}
        if previous is not None:
            request["sha"] = previous["sha"]
        response = subprocess.run([gh(), "api", "--method", "PUT", f"repos/{REPO}/contents/{path}", "--input", "-"], input=json.dumps(request).encode(), capture_output=True, timeout=45, check=False)
        if response.returncode == 0:
            return
        # A concurrent guarded status update is the only automatic write retry.
        if not any(code in response.stderr for code in (b"HTTP 409", b"HTTP 422")):
            break
    raise PipelineFailure("Guarded repository status publication failed; active supervised work was preserved.")


def load_helper(path: str, commit: str, directory: Path, expected: str | None = None) -> Any:
    _, source = github_file(path, commit)
    assert source is not None
    if expected is not None and sha(source) != expected:
        raise PipelineFailure("Pinned native helper hash differs from the reviewed implementation.")
    destination = directory / Path(path).name
    if destination.exists() and destination.read_bytes() != source:
        raise PipelineFailure("Preserve the existing immutable helper; its source differs.")
    destination.write_bytes(source)
    spec = importlib.util.spec_from_file_location(destination.stem + "_pinned", destination)
    if spec is None or spec.loader is None:
        raise PipelineFailure("Cannot load an immutable helper.")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def public(value: Any, depth: int = 0) -> Any:
    if depth > 14:
        return "[nested detail retained privately]"
    if isinstance(value, dict):
        return {str(k): public(v, depth+1) for k, v in value.items() if str(k).casefold() not in PRIVATE_KEYS}
    if isinstance(value, list):
        return [public(v, depth+1) for v in value[:50]]
    if isinstance(value, str):
        value = re.sub(r"(?:\bsk-[A-Za-z0-9_-]{16,}|\bgh[pousr]_[A-Za-z0-9_]{16,}|\bgithub_pat_[A-Za-z0-9_]{16,}|\bhf_[A-Za-z0-9_]{16,}|\bya29\.[A-Za-z0-9._-]{16,}|\bBearer\s+[A-Za-z0-9._~+/-]{16,})", "[REDACTED]", value, flags=re.IGNORECASE)
        return value[:16000]
    if value is None or isinstance(value, (int, float, bool)):
        return value
    return str(type(value).__name__)


def audit_evidence(markdown: str) -> str:
    """Keep the exact frozen methodology and evidence paragraphs in every page."""
    paragraphs = markdown.split("\n\n")
    methodology = next((p for p in paragraphs if p.startswith("Each audit used source-sampled groups")), None)
    artifacts = next((p for p in paragraphs if p.startswith("Audit records, source-only references")), None)
    if methodology is None or artifacts is None:
        raise PipelineFailure("The pinned audit evidence paragraphs are absent; preserve the existing status page.")
    table = "| Development audit | Faithful decisions | Severe unsupported assertions | Gate |\n|---|---:|---:|---|\n| Original cached spans, initial sources | 73/120 | 2 | Descriptive comparator |\n| Generated propositions, initial policy | 115/120 | 1 | Failed |\n| Revised frozen policy, fresh disjoint sources | 58/60 | 0 | Passed |"
    return table + "\n\n" + methodology + "\n\n" + artifacts


def capture_state(native: Any) -> dict[str, Any]:
    result = native.capture_diagnostics()
    directory = native.MAC_ROOT.parent / "full_capture" / CAPTURE_COMMIT
    path = directory / "supervisor_receipt.json"
    if not path.is_file():
        raise PipelineFailure("The originally authorized full capture supervisor is absent.")
    receipt = json.loads(path.read_text())
    if receipt.get("source_commit") != CAPTURE_COMMIT or receipt.get("output_path") != str(native.GEN_ROOT):
        raise PipelineFailure("The running full capture identity differs.")
    status = receipt.get("status")
    result["status"] = status
    if (directory / "result.json").is_file():
        terminal = json.loads((directory / "result.json").read_text())
        result["status"] = terminal.get("status")
        result["manifest"] = terminal.get("manifest", {})
        result["native_checkpoints"] = len(terminal.get("checkpoints", []))
    if result["status"] in TERMINAL_FAILURE:
        raise PipelineFailure("The full capture stopped or failed; raw attempts and native checkpoints remain preserved.")
    if result["status"] == "complete":
        manifest_path = native.GEN_ROOT / "propositions_tranche8_manifest.json"
        manifest = json.loads(manifest_path.read_text())
        bank = native.GEN_ROOT / "propositions_tranche8.json"
        if manifest.get("items") != 17334 or manifest.get("records_sha256") != sha(bank.read_bytes()) or any(v.get("status") != "complete" for v in manifest.get("partitions", {}).values()) or set(manifest.get("partitions", {})) != {"training", "validation"}:
            raise PipelineFailure("The completed full bank failed its final manifest binding.")
    elif not any(item.get("process_alive") is True and item.get("source_commit") == CAPTURE_COMMIT for item in result.get("supervisors", [])):
        raise PipelineFailure("The original capture supervisor is no longer alive; no replacement was launched.")
    return result


def checked_owner(native: Any, commit: str, directory: Path) -> dict[str, Any]:
    script = native.preamble(commit) + (
        "clean()\nchecks=json.loads((root/'answer_input_results'/'owner_checks'/commit/'receipt.json').read_text())\n"
        "assert checks.get('source_commit')==commit and checks.get('passed') is True and checks.get('source_clean') is True\n"
        "assert all(digest(root/path)==expected for path,expected in checks['owned_source_sha256'].items())\n"
        "print(json.dumps({'status':'complete','source_commit':commit,'owner_checks_passed':True,'source_clean':True}))\n"
    )
    return native.remote(script, directory, "pipeline_owner_binding")


def known_reauthentication_block(directory: Path) -> bool:
    """Classify only the observed gcloud failure, without publishing log text."""
    path = directory / "native_checks.stderr"
    if not path.is_file() or path.is_symlink():
        return False
    with path.open("rb") as stream:
        size = path.stat().st_size
        stream.seek(max(0, size-32768))
        text = stream.read(32768).decode(errors="replace").casefold()
    text = " ".join(text.split())
    return "reauthentication failed" in text and "cannot prompt during non-interactive execution" in text


def wait_for_owner_checks(native: Any, commit: str, directory: Path, snapshot: dict[str, Any], evidence: str, started: float, hours: float) -> bool:
    """Wait for interactive sign-in, then bind read-only checks to native source.

    No credential operation occurs here.  A fresh read-only check attempt is
    allowed only for the specific observed gcloud reauthentication failure.
    Other operational failures and failed owner checks stop orchestration.
    """
    attempt = 0
    last_signature = None
    last_publish = 0.0
    while True:
        if time.monotonic() - started >= hours * 3600:
            snapshot.update(status="timed_out", updated_at=now(), stage="supervised_work_preserved", error="The orchestration allowance ended while waiting for native checks; local capture and supervised work were preserved.")
            publish_snapshot(snapshot, evidence, directory)
            return False
        iteration = directory / "owner_check_attempts" / str(time.time_ns())
        iteration.mkdir(parents=True)
        attempt += 1
        try:
            checks = native.native_checks(commit, iteration, False)
        except native.NativeFailure:
            if not known_reauthentication_block(iteration):
                raise PipelineFailure("Native owner checks failed for a reason other than the recognized interactive Google Cloud sign-in requirement.") from None
            snapshot.update(status="authentication_required", stage="waiting_for_google_cloud_sign_in", updated_at=now(), elapsed_seconds=round(time.monotonic()-started))
            snapshot["capture"] = capture_state(native)
            snapshot["sample"] = {"status": "awaiting_clean_owner_checks"}
            snapshot["adaptation"] = {"status": "awaiting_clean_owner_checks"}
            snapshot["test"] = {"status": "not_released", "test_inputs_opened": False}
            snapshot["authentication"] = {"service": "Google Cloud", "interactive_sign_in_required": True, "recognized_noninteractive_reauthentication_failure": True, "owner_check_attempts": attempt}
            signature = sha(json.dumps({"status": snapshot["status"], "counts": snapshot["capture"].get("counts", {})}, sort_keys=True, allow_nan=False).encode())
            if signature != last_signature or time.monotonic()-last_publish >= 600:
                publish_snapshot(snapshot, evidence, directory)
                last_signature, last_publish = signature, time.monotonic()
            print("OPERATOR_PROGRESS " + json.dumps({"phase": "pipeline", "status": "authentication_required", "stage": snapshot["stage"], "counts": snapshot["capture"].get("counts", {}), "authentication": {"interactive_sign_in_required": True}}, allow_nan=False), flush=True)
            time.sleep(30)
            continue
        verification = checks.get("verification", {})
        if checks.get("status") != "complete" or verification.get("passed") is not True or verification.get("source_clean") is not True:
            raise PipelineFailure("Owner Ruff/Pyrefly/tests did not pass on the clean native source; private diagnostics were preserved.")
        checked_owner(native, commit, iteration)
        snapshot.update(status="running", stage="capture_and_source_sample", updated_at=now())
        snapshot.pop("authentication", None)
        snapshot.pop("error", None)
        snapshot["owner_checks"] = {"status": "passed", "source_commit": commit, "source_clean": True}
        return True


def native_observation(native: Any, commit: str, directory: Path, name: str) -> dict[str, Any]:
    result = native.native_status(commit, directory, name)
    if result.get("status") in TERMINAL_FAILURE or result.get("summary", {}).get("status") == "failed":
        raise PipelineFailure(f"Native attempt {name} failed or was interrupted; no replacement was launched.")
    if result.get("status") != "not_started" and result.get("source_commit") != commit:
        raise PipelineFailure("A native attempt belongs to a different checked source commit.")
    return result


def validation_decision(adaptation: dict[str, Any]) -> str:
    if adaptation.get("status") != "complete":
        return "pending"
    result = adaptation.get("result", {})
    selection = result.get("selection")
    if not isinstance(selection, dict):
        raise PipelineFailure("Completed validation has no frozen selection record.")
    if selection.get("test_scores_used_for_selection") is not False:
        raise PipelineFailure("Validation selection did not preserve the held-out test gate.")
    arm = selection.get("selected_arm")
    if arm is None:
        if any(item.get("eligible") is True for item in selection.get("eligibility", {}).values()):
            raise PipelineFailure("Eligible validation candidate was omitted from selection.")
        return "no_eligible_candidate"
    if arm not in {"epoch_zero", "adapted"} or selection.get("eligibility", {}).get(arm, {}).get("eligible") is not True:
        raise PipelineFailure("Frozen validation candidate is not eligible for test.")
    return "eligible_test"


def test_observation(directory: Path, helper: Any, operator: str, native_commit: str, eligible: bool) -> dict[str, Any]:
    if not eligible:
        return {"status": "not_released", "test_inputs_opened": False}
    result_path = helper.WORK_ROOT / (operator + "-" + native_commit) / "result.json"
    receipt_path = directory / "test_helper_receipt.json"
    if result_path.is_file():
        result = json.loads(result_path.read_text())
        if result.get("status") != "complete":
            raise PipelineFailure("Eligible test transport failed; raw requests and native receipts remain preserved.")
        if result.get("source_commit") != operator or result.get("native_source_commit") != native_commit:
            raise PipelineFailure("Held-out test result source bindings differ.")
        return result
    if receipt_path.is_file():
        receipt = json.loads(receipt_path.read_text())
        if receipt.get("operator_source_commit") != operator or receipt.get("native_source_commit") != native_commit:
            raise PipelineFailure("Existing test helper launch bindings differ.")
        pid = receipt.get("pid")
        if isinstance(pid, int) and pid > 1:
            command = subprocess.run(["ps", "-p", str(pid), "-o", "command="], capture_output=True, timeout=5, check=False)
            if command.returncode == 0 and str(Path(helper.__file__).resolve()).encode() in command.stdout:
                return {"status": "running", "test_inputs_released_by_native_gate": True, "progress": test_progress(directory)}
        raise PipelineFailure("The test helper was interrupted without a final result; no duplicate was launched.")
    helper_path = Path(helper.__file__).resolve()
    receipt = {"operator_source_commit": operator, "native_source_commit": native_commit, "helper_sha256": sha(helper_path.read_bytes()), "started_unix": time.time(), "status": "launching"}
    save(receipt_path, receipt)
    with (directory / "test_helper.stdout").open("ab") as stdout, (directory / "test_helper.stderr").open("ab") as stderr:
        process = subprocess.Popen([sys.executable, "-I", str(helper_path), "--source-commit", operator, "--native-source-commit", native_commit, "--concurrency", "4"], cwd=directory, stdin=subprocess.DEVNULL, stdout=stdout, stderr=stderr, start_new_session=True)
    receipt.update(pid=process.pid, status="running")
    save(receipt_path, receipt)
    return {"status": "running", "test_inputs_released_by_native_gate": True}


def test_progress(directory: Path) -> dict[str, Any]:
    """Read only structured helper counters, ignoring every raw CLI log line."""
    path = directory / "test_helper.stdout"
    if not path.is_file():
        return {}
    size = path.stat().st_size
    with path.open("rb") as stream:
        stream.seek(max(0, size-262144))
        data = stream.read(262144)
    latest = {}
    for line in data.splitlines():
        if not line.startswith(b"OPERATOR_PROGRESS "):
            continue
        try:
            event = json.loads(line.removeprefix(b"OPERATOR_PROGRESS "))
        except ValueError:
            continue
        latest = {key: event[key] for key in ("phase", "event", "counts", "selection_sha256", "total_items") if key in event}
    return public(latest)


def scalar(value: Any) -> str:
    return "—" if value is None else (f"{value:.6f}" if isinstance(value, float) else str(value))


def score_table(title: str, result: dict[str, Any]) -> str:
    metrics = result.get("result", {}).get("metrics", {})
    if not isinstance(metrics, dict) or not metrics:
        return ""
    lines = [f"## {title}", "", "| Arm | Spearman | MSE (0–1) | False-positive rate | Condition ordering |", "|---|---:|---:|---:|---:|"]
    for arm, values in metrics.items():
        if isinstance(values, dict):
            lines.append("| " + " | ".join((arm, scalar(values.get("spearman")), scalar(values.get("mse_0_1")), scalar(values.get("operating_point", {}).get("false_positive_rate")), scalar(values.get("condition_changes", {}).get("accuracy_ties_half")))) + " |")
    return "\n".join(lines) + "\n\n"


def render(snapshot: dict[str, Any], evidence: str) -> str:
    capture = snapshot.get("capture", {})
    counts = capture.get("counts", {})
    training = snapshot.get("adaptation", {}).get("training", {})
    text = "# Checked propositions and LoRA — live results\n\n"
    display_time = datetime.fromisoformat(snapshot["updated_at"]).astimezone(ZoneInfo("America/New_York")).strftime("%b %d, %Y, %I:%M %p %Z")
    text += f"**{snapshot['status']} — {snapshot.get('stage', 'initializing')}**. Updated {display_time}.\n\n"
    if snapshot["status"] == "authentication_required":
        text += "Google Cloud requires interactive sign-in renewal. Existing local proposition generation continues; native sample, adaptation and test stages await clean owner checks.\n\n"
    text += f"Full training/development generation: **{counts.get('completed_items', 0):,}/17,334** accepted structural records; {counts.get('failed_attempts', 0)} preserved failed attempts. Capture: {capture.get('status', 'pending')}. Provider latency has varied; no fixed ETA is asserted.\n\n"
    text += f"Source sample: {snapshot.get('sample', {}).get('status', 'pending')}. Adaptation: {snapshot.get('adaptation', {}).get('status', 'pending')}. Held-out test: {snapshot.get('test', {}).get('status', 'not_released')}.\n\n"
    if training:
        epoch = training.get("latest_epoch", {})
        text += f"Live fitting: epoch {training.get('current_epoch', 'pending')}, {training.get('actual_updates', 0)} updates, {training.get('completed_epoch', 0)} completed epochs. Latest completed epoch training MSE: {scalar(epoch.get('training_mse_0_1'))}; validation Spearman: {scalar(epoch.get('validation', {}).get('spearman'))}; validation MSE: {scalar(epoch.get('validation', {}).get('mse_0_1'))}.\n\n"
    if snapshot.get("error"):
        text += f"Runtime issue: {snapshot['error']} Active supervised work and raw failures are preserved. This is not a statistical result.\n\n"
    text += score_table("Frozen source-sample diagnostic", snapshot.get("sample", {}))
    text += score_table("Full validation", snapshot.get("adaptation", {}))
    text += score_table("Frozen eligible test", snapshot.get("test", {}))
    text += "## Audit evidence and limits\n\n" + evidence + "\n\n"
    text += "The source sample compares old spans with blind-screened generated v1 answers, changing both generation and screening. It is a development diagnostic. The revised full bank uses the separate frozen v2 policy. Native validation alone chooses eligibility and the held-out test is evaluated once only for an eligible frozen candidate.\n\n"
    text += f"Operator source: `{snapshot['operator_source_commit']}`. Native source: `{snapshot['native_source_commit']}`. Original capture source: `{CAPTURE_COMMIT}`. Detailed live state: [csts_tranche8_results.json](csts_tranche8_results.json). Native artifacts seal locally and queue asynchronous cloud promotion.\n"
    return text


def publish_snapshot(snapshot: dict[str, Any], evidence: str, directory: Path) -> dict[str, Any]:
    value = public(snapshot)
    encoded = (json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n").encode()
    if len(encoded) >= 180000:
        raise PipelineFailure("Pipeline state exceeded the bounded status budget; detailed artifacts remain private.")
    save(directory / "latest.json", value)
    markdown = render(value, evidence)
    (directory / "latest.md").write_text(markdown)
    guarded_write(RESULT_PATH, encoded)
    guarded_write(STATUS_PATH, markdown.encode())
    return value


def run_pipeline(operator: str, native_commit: str, hours: float = 16, poll: int = 30) -> dict[str, Any]:
    directory = WORK_ROOT / (operator + "-" + native_commit)
    directory.mkdir(parents=True, exist_ok=True, mode=0o700)
    with (WORK_ROOT / "pipeline.lock").open("a+") as lock:
        try:
            fcntl.flock(lock.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            raise PipelineFailure("Another autonomous Tranche 8 pipeline owns this task.") from None
        native = load_helper(NATIVE_HELPER, operator, directory, NATIVE_HELPER_SHA256)
        test_helper = load_helper(TEST_HELPER, operator, directory)
        _, audit_source = github_file(STATUS_PATH, operator)
        assert audit_source is not None
        evidence = audit_evidence(audit_source.decode())
        started = time.monotonic()
        snapshot = {"phase": "pipeline", "status": "running", "stage": "capture_and_source_sample", "operator_source_commit": operator, "native_source_commit": native_commit, "capture_source_commit": CAPTURE_COMMIT, "audit_source_sha256": sha(audit_source), "helper_sha256": {"native": sha(Path(native.__file__).read_bytes()), "test": sha(Path(test_helper.__file__).read_bytes())}}
        last_signature = None
        last_publish = 0.0
        last_archive = 0.0
        archive_future = None
        final_archive = False
        executor = ThreadPoolExecutor(max_workers=1)
        try:
            if not wait_for_owner_checks(native, native_commit, directory, snapshot, evidence, started, hours):
                save(directory / "result.json", public(snapshot))
                return public(snapshot)
            while True:
                if time.monotonic() - started >= hours * 3600:
                    snapshot.update(status="timed_out", updated_at=now(), stage="supervised_work_preserved", error="The autonomous orchestration allowance ended; existing capture/native/test children were preserved without replacement.")
                    publish_snapshot(snapshot, evidence, directory)
                    save(directory / "result.json", public(snapshot))
                    return public(snapshot)
                iteration = directory / "calls" / str(time.time_ns())
                iteration.mkdir(parents=True)
                snapshot["updated_at"] = now()
                snapshot["elapsed_seconds"] = round(time.monotonic() - started)
                snapshot["capture"] = capture_state(native)
                sample = native_observation(native, native_commit, iteration, SAMPLE_NAME)
                if sample.get("status") == "not_started":
                    if time.monotonic() - started >= hours * 3600:
                        continue
                    native.native_launch(native_commit, iteration, SAMPLE_NAME, "csts_pilot.proposition_sample")
                    sample = native_observation(native, native_commit, iteration, SAMPLE_NAME)
                snapshot["sample"] = sample
                full_complete = snapshot["capture"]["status"] == "complete"
                if archive_future is not None and archive_future.done():
                    archive_result, was_final = archive_future.result()
                    if archive_result.get("status") != "complete":
                        raise PipelineFailure("Native raw capture sealing failed; source archives remain preserved.")
                    snapshot["archive"] = archive_result
                    final_archive = final_archive or was_final
                    archive_future = None
                if archive_future is None and not final_archive and (time.monotonic() - last_archive >= 600 or full_complete):
                    def archive_call(call_directory: Path = iteration, final: bool = full_complete) -> tuple[dict[str, Any], bool]:
                        return native.native_archive(native_commit, call_directory), final
                    archive_future = executor.submit(archive_call)
                    last_archive = time.monotonic()
                adaptation = native_observation(native, native_commit, iteration, VALIDATION_NAME)
                if full_complete and final_archive and sample.get("status") == "complete" and adaptation.get("status") == "not_started":
                    if time.monotonic() - started >= hours * 3600:
                        continue
                    native.native_launch(native_commit, iteration, VALIDATION_NAME)
                    adaptation = native_observation(native, native_commit, iteration, VALIDATION_NAME)
                snapshot["adaptation"] = adaptation
                decision = validation_decision(adaptation)
                snapshot["decision"] = decision
                if decision == "eligible_test" and time.monotonic() - started >= hours * 3600:
                    continue
                snapshot["test"] = test_observation(directory, test_helper, operator, native_commit, decision == "eligible_test")
                if snapshot["test"].get("status") == "complete":
                    arm = adaptation.get("result", {}).get("selection", {}).get("selected_arm")
                    if snapshot["test"].get("selected_arm") != arm or re.fullmatch(r"[0-9a-f]{64}", str(snapshot["test"].get("selection_sha256"))) is None:
                        raise PipelineFailure("The completed test result does not identify the validation-selected frozen candidate.")
                if decision == "no_eligible_candidate":
                    snapshot.update(status="complete", stage="no_validation_candidate_eligible")
                elif snapshot["test"].get("status") == "complete":
                    snapshot.update(status="complete", stage="eligible_frozen_test_complete")
                elif decision == "eligible_test":
                    snapshot["stage"] = "eligible_frozen_test"
                elif adaptation.get("status") != "not_started":
                    snapshot["stage"] = "native_validation_adaptation"
                if time.monotonic() - started >= hours * 3600 and snapshot["status"] != "complete":
                    snapshot.update(status="timed_out", stage="supervised_work_preserved", error="The autonomous orchestration allowance ended; existing capture/native/test children were preserved without replacement.")
                signature_value = {key: value for key, value in snapshot.items() if key not in {"updated_at", "elapsed_seconds"}}
                # Running timers change each poll; publication follows actual counts/scores/stages.
                signature_value["capture"] = {key: snapshot["capture"].get(key) for key in ("status", "counts", "manifest")}
                signature = sha(json.dumps(public(signature_value), sort_keys=True, allow_nan=False).encode())
                if signature != last_signature or time.monotonic() - last_publish >= 600 or snapshot["status"] != "running":
                    publish_snapshot(snapshot, evidence, directory)
                    print("OPERATOR_PROGRESS " + json.dumps({"phase": "pipeline", "status": snapshot["status"], "stage": snapshot["stage"], "counts": snapshot["capture"]["counts"], "sample": public(snapshot["sample"]), "validation": public(snapshot["adaptation"]), "decision": decision, "test": public(snapshot["test"])}, allow_nan=False), flush=True)
                    last_signature, last_publish = signature, time.monotonic()
                if snapshot["status"] != "running":
                    save(directory / "result.json", public(snapshot))
                    return public(snapshot)
                time.sleep(poll)
        except Exception as error:
            (directory / "failure.log").write_text(traceback.format_exc())
            snapshot.update(status="failed", updated_at=now(), error=str(error) if isinstance(error, PipelineFailure) else "Pipeline operation failed; private logs, raw captures and active supervised work were preserved.", error_type=type(error).__name__)
            save(directory / "result.json", public(snapshot))
            try:
                publish_snapshot(snapshot, evidence, directory)
            except Exception:
                pass
            raise PipelineFailure(snapshot["error"]) from None
        finally:
            # Archive CPU work is finite and independently queues publication;
            # the expensive model children are detached and are never killed.
            executor.shutdown(wait=False, cancel_futures=True)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-commit", required=True)
    parser.add_argument("--native-source-commit", required=True)
    parser.add_argument("--max-hours", type=float, default=16)
    parser.add_argument("--poll-seconds", type=int, default=30, choices=(15, 20, 30))
    args = parser.parse_args()
    if any(re.fullmatch(r"[0-9a-f]{40}", value) is None for value in (args.source_commit, args.native_source_commit)) or not 0 < args.max_hours <= 16:
        parser.error("Use complete immutable source commits and at most 16 hours.")
    try:
        result = run_pipeline(args.source_commit, args.native_source_commit, args.max_hours, args.poll_seconds)
    except Exception as error:
        result = {"phase": "pipeline", "status": "failed", "error": str(error) if isinstance(error, PipelineFailure) else "Pipeline failed before launch; no new source/model policy was applied."}
        print("OPERATOR_RESULT " + json.dumps(result, allow_nan=False), flush=True)
        raise SystemExit(1) from None
    print("OPERATOR_RESULT " + json.dumps(result, ensure_ascii=False, allow_nan=False), flush=True)


if __name__ == "__main__":
    main()
