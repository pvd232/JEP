"""Read-only fixed-root diagnostics for the pinned capture recovery preflight."""

import contextlib
import hashlib
import importlib.util
import io
import json
import re
from pathlib import Path

WORK = Path("/tmp/jep-tranche8-worker-20261026")
DIRECTORY = WORK / "full_capture/8a0b50d5bdd2a77ab0c9444f4bf10d484f8ba6bb"
ROOT = Path("/tmp/jep-proposition-input-20261026/full_v2_6895d17242704944")
RECOVERY_SHA = "79f581303b7a619fcddd0ab1118c18a1ef7304a63858d2449913231094ac6f1a"
STATES = {"failed", "complete", "running", "launching", "interrupted"}
ERRORS = {"ValueError", "TypeError", "KeyError", "FileNotFoundError", "PermissionError", "RecoveryFailure", "ContinuationFailure", "OSError", "RuntimeError", "BlockingIOError", "AttributeError"}


def load(path):
    spec = importlib.util.spec_from_file_location("pinned_recovery_diagnostic_dependency", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def step(function):
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            value = function()
        return {"passed": True, **({"retryable": value} if isinstance(value, bool) else {})}
    except Exception as error:
        name = type(error).__name__
        return {"passed": False, "error_class": name if name in ERRORS else "other"}


def inspect():
    result = {"phase": "recovery_preflight_diagnostics", "status": "complete", "source_files": {}, "steps": {}}
    candidates = []
    for path in (WORK / "actions").glob("*/operator.py"):
        if path.is_file() and not path.is_symlink() and hashlib.sha256(path.read_bytes()).hexdigest() == RECOVERY_SHA:
            candidates.append(path)
    result["pinned_operator_copies"] = len(candidates)
    if not candidates:
        return result
    recovery = load(candidates[0])
    for name, expected in (("full_capture_controller.py", recovery.CONTROLLER_SHA), ("proposition_capture.py", recovery.CAPTURE_SHA)):
        path = DIRECTORY / name
        exists = path.is_file() and not path.is_symlink()
        actual = hashlib.sha256(path.read_bytes()).hexdigest() if exists else None
        result["source_files"][name] = {"exists": exists, "expected_hash_matches": actual == expected, "actual_sha256": actual}
    result["steps"]["pinned"] = step(recovery.pinned)
    controller_path, capture_path = DIRECTORY / "full_capture_controller.py", DIRECTORY / "proposition_capture.py"
    if not all(value["expected_hash_matches"] for value in result["source_files"].values()):
        return result
    controller, capture = load(controller_path), load(capture_path)
    result["steps"]["gate"] = step(lambda: controller.verify_gate(json.loads((DIRECTORY / "audit_gate.json").read_text()), capture, capture_path.read_bytes()))
    result["steps"]["inventory"] = step(lambda: controller.verify_inventory(capture))
    path = DIRECTORY / "supervisor_receipt.json"
    if path.is_file() and not path.is_symlink():
        receipt = json.loads(path.read_text())
        result["supervisor_status"] = receipt.get("status") if receipt.get("status") in STATES else "unknown"
        result["supervisor_binding_matches"] = receipt.get("source_commit") == recovery.COMMIT and receipt.get("output_path") == str(ROOT)
        result["steps"]["no_live_capture"] = step(lambda: recovery.no_live_capture(receipt))
    result["steps"]["preflight"] = step(lambda: recovery.preflight(ROOT, capture))
    batches = []
    for split in ("training", "validation"):
        for directory in sorted((ROOT / split).glob("batch_*")):
            if not recovery.BATCH.fullmatch(directory.name) or directory.is_symlink():
                continue
            receipt = json.loads((directory / "receipt.json").read_text())
            status = receipt.get("status")
            item = {"split": split, "batch": directory.name, "status": status if status in STATES else "unknown"}
            if status == "complete":
                item["validation"] = step(lambda: capture.completed_batch(json.loads((directory / "inputs.json").read_text()), directory, capture.CLI))
                if item["validation"]["passed"]:
                    continue
            elif status == "failed":
                item["validation"] = step(lambda: recovery.retryable(directory, capture))
                text = (directory / "stderr.log").read_text(errors="replace") if (directory / "stderr.log").is_file() else ""
                events = []
                for line in (directory / "events.jsonl").read_text().splitlines():
                    try:
                        event = json.loads(line)
                    except ValueError:
                        continue
                    if isinstance(event, dict) and event.get("type") in {"error", "turn.failed"}:
                        events.append(json.dumps(event))
                inspected = text + "\n" + "\n".join(events)
                item["classification"] = {"blocked": bool(recovery.BLOCK.search(inspected)), "transient": bool(recovery.TRANSIENT.search(inspected)), "auth": bool(re.search(r"auth|\b401\b|\b403\b", inspected, re.I)), "login": bool(re.search(r"sign[ -]?in|log[ -]?in|reauth", inspected, re.I)), "policy": bool(re.search(r"approval|policy|permission denied|access denied", inspected, re.I)), "quota": bool(re.search(r"quota|usage[_ .-](?:limit|cap)|insufficient.credits|billing", inspected, re.I))}
            else:
                continue
            batches.append(item)
    result["problem_batches"] = batches
    return result


if __name__ == "__main__":
    try:
        result = inspect()
    except Exception as error:
        name = type(error).__name__
        result = {"phase": "recovery_preflight_diagnostics", "status": "failed", "error_class": name if name in ERRORS else "other"}
    print("OPERATOR_RESULT " + json.dumps(result, allow_nan=False), flush=True)
