"""Read-only, content-free inspection of the stopped frozen answer capture."""

import json
import os
import re
import time
from pathlib import Path

ROOT = Path("/tmp/jep-proposition-input-20261026/full_v2_6895d17242704944")
CONTROLLER = Path("/tmp/jep-tranche8-worker-20261026/full_capture/8a0b50d5bdd2a77ab0c9444f4bf10d484f8ba6bb")
PATTERNS = {
    "timeout": r"timed? out|timeout|deadline.exceeded",
    "capacity": r"capacity|overload|high demand|server busy",
    "rate_limit": r"\b429\b|rate.?limit|too many requests",
    "auth": r"unauthori[sz]ed|authentication|invalid.api.?key|token expired|\b401\b|\b403\b",
    "policy": r"approval|policy|permission denied|not allowed|access denied",
    "connection": r"connection|network|socket|\bdns\b|\btls\b|disconnect",
    "usage_limit": r"usage limit|quota|insufficient.credits|exceeded.*limit|limit.*reached",
}
EVENTS = {"thread.started", "turn.started", "item.started", "item.updated", "item.completed", "turn.completed", "turn.failed", "error"}


def alive(pid):
    if not isinstance(pid, int) or pid < 2:
        return None
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    return True


def flags(text):
    return {name: bool(re.search(pattern, text, re.IGNORECASE)) for name, pattern in PATTERNS.items()}


def inspect(root=ROOT, controller=CONTROLLER):
    failed, complete, running = [], 0, 0
    for split in ("training", "validation"):
        for batch in sorted((root / split).glob("batch_*")):
            receipt = json.loads((batch / "receipt.json").read_text())
            status = receipt.get("status")
            if status == "complete":
                complete += receipt["items"]
                continue
            if status == "running":
                running += 1
            if status not in {"failed", "running"}:
                continue
            item = {"split": split, "batch": batch.name, "status": status, "items": receipt.get("items"), "returncode": receipt.get("returncode"), "elapsed_seconds": receipt.get("elapsed_seconds"), "receipt_flags": flags(receipt.get("error", "")), "response_exists": (batch / "response.json").is_file()}
            event_types, item_types, event_flags = {}, {}, {key: False for key in PATTERNS}
            malformed = 0
            events = batch / "events.jsonl"
            if events.is_file():
                for line in events.read_text().splitlines():
                    try:
                        event = json.loads(line)
                    except ValueError:
                        malformed += 1
                        continue
                    kind = event.get("type")
                    kind = kind if kind in EVENTS else "unrecognized"
                    event_types[kind] = event_types.get(kind, 0) + 1
                    if kind.startswith("item."):
                        subtype = event.get("item", {}).get("type")
                        subtype = subtype if subtype in {"agent_message", "reasoning"} else "tool_or_unknown"
                        item_types[subtype] = item_types.get(subtype, 0) + 1
                    if kind in {"error", "turn.failed"}:
                        for key, value in flags(line).items():
                            event_flags[key] |= value
            log = batch / "stderr.log"
            diagnostic_flags = flags(log.read_text(errors="replace")[-262144:] if log.is_file() else "")
            item.update(event_types=event_types, item_types=item_types, event_flags=event_flags, diagnostic_flags=diagnostic_flags, malformed_event_lines=malformed)
            failed.append(item)
    supervisor = {}
    receipt_file = controller / "supervisor_receipt.json"
    if receipt_file.is_file():
        receipt = json.loads(receipt_file.read_text())
        supervisor = {"status": receipt.get("status"), "process_alive": alive(receipt.get("pid"))}
    return {"phase": "capture_failure_diagnostics", "status": "complete", "completed_items": complete, "running_batches": running, "failed_or_running": failed, "supervisor": supervisor, "observed_unix": time.time()}


if __name__ == "__main__":
    print("OPERATOR_RESULT " + json.dumps(inspect(), allow_nan=False), flush=True)
