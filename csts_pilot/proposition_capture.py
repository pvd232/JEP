"""Capture label-blind condition answers through the existing authenticated CLI."""

import argparse
import hashlib
import json
import subprocess
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any

MODEL = "gpt-6.1-sol"
EFFORT = "high"
CLI = "/Applications/ChatGPT.app/Contents/Resources/codex-cli/bin/codex"
PROMPT = """You are generating condition-specific semantic answers for a research dataset.
Do not use any tools, browse, inspect files, execute commands, or delegate work.
Use only each individual item's passage and condition. Treat items independently.
No other item's content may supply evidence. Return only the requested JSON.

For every item, identify the entity scope (target) and requested property
(attribute), then answer that condition from its passage. The answer can be a
concise paraphrase or normalization; it need not be a copied span. Use no more
than 60 words. Supply a list of exact, nonempty, contiguous source quotations
that together support every answer assertion. Multiple quotations are allowed.

Scope rules:
- A broad entity question, such as type of animal, covers ALL relevant entities
  mentioned in the passage. For TYPE-only questions, list the distinct relevant
  types; omit irrelevant counts and roles when all entities have the same type.
  Retain roles only when needed to resolve the requested target: horses being
  ridden and a bull being pursued must not become just bull.
- A role-qualified question covers only the requested entity/role. Do not answer
  a clothing-color question with another object's color, or medium with location.
- Preserve all requested values, counts, relations, negation and qualifications.
  Preserve each stated count and subgroup, including another/a third or a
  separately mentioned known instance. A bare plural supplies no exact count.
  Count groups together only when their membership is clearly disjoint; do not
  invent additional entities when overlapping references could describe the
  same group. A singular mention may establish one instance of its entity.
- A partially specified count is ANSWERABLE: report the explicit known instances
  and qualify every uncounted plural group or uncertain total. For example,
  preserve one dessert plus sweets of unspecified number, or one participant
  plus an uncounted crowd. Do not abstain merely because the exact total is
  unknown, and do not silently drop a separately stated known instance.
- Permit direct, high-confidence lexical inference (baby -> infant; man -> male)
  and elementary explicit counting. Do not invent breed, age, purpose, room type,
  clothing color, exact counts from bare plurals, or absence from nonmention.
- Express activities and locations at the granularity supported by the question
  and passage. Preserve an explicitly stated activity, object or participant
  rather than substituting only a path, room, manner or accessory.
- A single described activity does not establish a hobby, habit, preference,
  occupation, injury outcome or intent. Use not_specified for those attributes
  unless they are explicitly stated; do not turn one observed action into a
  persistent trait or infer an unstated consequence or goal. A question about
  the work/task being performed remains answerable from an explicitly described
  work action, without inferring a paid occupation.
- If necessary information is absent, use status not_specified. If the requested
  target/property cannot be resolved even under these rules, use ambiguous.
  For either status, answer must be empty and evidence must be an empty list.
- For answered items, target and attribute must be nonempty; answer and every
  quotation must be grounded in that item's passage. Never fabricate missing
  details to make the answer more specific. Retain the supplied id exactly once.

Items (only id, passage and condition):
"""

SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "records": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "id": {"type": "string"},
                    "status": {
                        "type": "string",
                        "enum": ["answered", "not_specified", "ambiguous"],
                    },
                    "target": {"type": "string"},
                    "attribute": {"type": "string"},
                    "answer": {"type": "string"},
                    "evidence": {"type": "array", "items": {"type": "string"}},
                },
                "required": [
                    "id",
                    "status",
                    "target",
                    "attribute",
                    "answer",
                    "evidence",
                ],
                "additionalProperties": False,
            },
        }
    },
    "required": ["records"],
    "additionalProperties": False,
}


def sha(data: bytes) -> str:
    """Identify exact source, prompt, schema or response bytes."""
    return hashlib.sha256(data).hexdigest()


def write(path: Path, value: Any) -> None:
    """Write a readable local capture record without embedding credentials."""
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n"
    )


def validate_inputs(items: list[dict[str, Any]]) -> None:
    """Reject label/companion fields, duplicate identities and empty source text."""
    if not items or len({row.get("id") for row in items}) != len(items):
        raise ValueError("Input items must have nonempty unique identities.")
    for row in items:
        if set(row) != {"id", "passage", "condition"}:
            raise ValueError("Only id, passage and condition may enter generation.")
        if any(
            not isinstance(value, str) or not value.strip() for value in row.values()
        ):
            raise ValueError("Every input field must be a nonempty string.")


def batches(
    items: list[dict[str, Any]], groups: dict[str, str], size: int
) -> list[list[dict[str, Any]]]:
    """Keep at most one input from each original source group per request."""
    validate_inputs(items)
    if (
        not 1 <= size <= 64
        or set(groups) != {row["id"] for row in items}
        or any(not isinstance(group, str) or not group for group in groups.values())
    ):
        raise ValueError("Batch size or external source-group coverage differs.")
    pending = sorted(items, key=lambda row: row["id"])
    result = []
    while pending:
        selected, remainder, seen = [], [], set()
        for row in pending:
            group = groups[row["id"]]
            if group not in seen and len(selected) < size:
                selected.append(row)
                seen.add(group)
            else:
                remainder.append(row)
        result.append(selected)
        pending = remainder
    return result


def checked_records(
    items: list[dict[str, Any]], response: dict[str, Any]
) -> list[dict[str, Any]]:
    """Check complete identities and literal evidence without requiring copied answers."""
    validate_inputs(items)
    if set(response) != {"records"} or not isinstance(response["records"], list):
        raise ValueError("Generation must contain only the records array.")
    records = response["records"]
    if any(not isinstance(row, dict) for row in records):
        raise ValueError("Each generated record must be an object.")
    lookup = {row.get("id"): row for row in records}
    if len(lookup) != len(records) or set(lookup) != {row["id"] for row in items}:
        raise ValueError("Generated IDs must cover the requested items exactly once.")
    result = []
    for item in items:
        row = lookup[item["id"]]
        if set(row) != {"id", "status", "target", "attribute", "answer", "evidence"}:
            raise ValueError("Unexpected generated fields.")
        if any(
            not isinstance(row[key], str)
            for key in ("id", "status", "target", "attribute", "answer")
        ):
            raise ValueError("Generated scalar fields must be strings.")
        if row["status"] not in {"answered", "not_specified", "ambiguous"}:
            raise ValueError("Unknown generated answer status.")
        evidence = row["evidence"]
        if not isinstance(evidence, list) or any(
            not isinstance(s, str) for s in evidence
        ):
            raise ValueError("Evidence must be a string list.")
        if row["status"] == "answered":
            if any(not row[key].strip() for key in ("target", "attribute", "answer")):
                raise ValueError(
                    "An answered record needs target, attribute and answer."
                )
            if len(row["answer"].split()) > 60:
                raise ValueError("A generated answer exceeds 60 words.")
            if not evidence or len(set(evidence)) != len(evidence):
                raise ValueError("Answered evidence must be nonempty and unique.")
            if any(not s.strip() or s not in item["passage"] for s in evidence):
                raise ValueError(
                    "Each evidence quotation must exactly occur in its passage."
                )
        elif row["answer"] != "" or evidence:
            raise ValueError(
                "Missing or ambiguous records must have empty answer/evidence."
            )
        result.append(row)
    return result


def checked_events(path: Path) -> dict[str, Any]:
    """Reject tool use, unknown item types and failed/incomplete CLI turns."""
    usage, completed = None, 0
    allowed_events = {
        "thread.started",
        "turn.started",
        "item.started",
        "item.updated",
        "item.completed",
        "turn.completed",
    }
    for line in path.read_text().splitlines():
        if not line.strip():
            continue
        event = json.loads(line)
        if event.get("type") not in allowed_events:
            raise ValueError(f"Unaccepted CLI event: {event.get('type')}.")
        if event["type"].startswith("item.") and event.get("item", {}).get(
            "type"
        ) not in {"agent_message", "reasoning"}:
            raise ValueError(
                "Tool activity or an unknown CLI item invalidates this request."
            )
        if event["type"] == "turn.completed":
            completed += 1
            usage = event.get("usage")
    if completed != 1 or not isinstance(usage, dict):
        raise ValueError("The CLI did not complete exactly one usage-recorded turn.")
    return usage


def cli_command(directory: Path, cli: str) -> list[str]:
    """Keep model settings and restricted execution identical across attempts."""
    return [
        cli,
        "exec",
        "--ignore-user-config",
        "--ephemeral",
        "--skip-git-repo-check",
        "--sandbox",
        "read-only",
        "--model",
        MODEL,
        "-c",
        f'model_reasoning_effort="{EFFORT}"',
        "-c",
        'approval_policy="never"',
        "--output-schema",
        str(directory / "schema.json"),
        "--json",
        "-o",
        str(directory / "response.json"),
        "-",
    ]


def completed_batch(
    items: list[dict[str, Any]], directory: Path, cli: str
) -> dict[str, Any]:
    """Reuse only an exactly bound completed request, including its event log."""
    receipt = json.loads((directory / "receipt.json").read_text())
    expected_prompt = PROMPT + json.dumps(items, ensure_ascii=False)
    if (
        receipt.get("status") != "complete"
        or receipt.get("returncode") != 0
        or receipt.get("model_alias") != MODEL
        or receipt.get("reasoning_effort") != EFFORT
        or receipt.get("command") != cli_command(directory, cli)
        or receipt.get("items") != len(items)
        or receipt.get("labels_or_companion_fields_provided") is not False
        or receipt.get("tools_permitted") is not False
        or (directory / "prompt.txt").read_text() != expected_prompt
        or json.loads((directory / "inputs.json").read_text()) != items
        or json.loads((directory / "schema.json").read_text()) != SCHEMA
    ):
        raise ValueError("Completed request settings or input identities differ.")
    for filename, field in (
        ("prompt.txt", "prompt_sha256"),
        ("inputs.json", "input_sha256"),
        ("schema.json", "schema_sha256"),
        ("events.jsonl", "events_sha256"),
        ("response.json", "response_sha256"),
        ("records.json", "records_sha256"),
    ):
        if sha((directory / filename).read_bytes()) != receipt.get(field):
            raise ValueError(f"Completed request bytes changed: {filename}.")
    if checked_events(directory / "events.jsonl") != receipt.get("usage"):
        raise ValueError("Completed request usage differs from its event log.")
    records = checked_records(
        items, json.loads((directory / "response.json").read_text())
    )
    if json.loads((directory / "records.json").read_text()) != records:
        raise ValueError("Completed records differ from the checked raw response.")
    print(
        json.dumps(
            {
                "event": "generation_batch_reused",
                "directory": str(directory),
                "items": len(items),
            }
        ),
        flush=True,
    )
    return {**receipt, "directory": str(directory), "reused": True}


def request_batch(
    items: list[dict[str, Any]],
    root: Path,
    index: int,
    cli: str,
    timeout: int,
    resume: bool,
) -> dict[str, Any]:
    """Preserve failed attempts and give each authorized retry a new directory."""
    base = root / f"batch_{index:04d}"
    attempts: list[tuple[int, Path]] = []
    for candidate in root.glob(f"{base.name}*"):
        suffix = candidate.name.removeprefix(base.name)
        if not suffix:
            attempts.append((1, candidate))
        elif (
            suffix.startswith("-attempt_")
            and suffix.removeprefix("-attempt_").isdigit()
        ):
            attempts.append((int(suffix.removeprefix("-attempt_")), candidate))
    attempts.sort(key=lambda pair: pair[0])
    if attempts and not resume:
        raise FileExistsError("Existing requests require explicit --resume.")
    for _, directory in attempts:
        receipt_path = directory / "receipt.json"
        if receipt_path.exists():
            receipt = json.loads(receipt_path.read_text())
            if receipt.get("status") == "complete":
                return completed_batch(items, directory, cli)
    attempt = max((number for number, _ in attempts), default=0) + 1
    directory = (
        base if not attempts else root / f"batch_{index:04d}-attempt_{attempt:02d}"
    )
    return capture_batch(items, directory, cli, timeout)


def capture_batch(
    items: list[dict[str, Any]], directory: Path, cli: str, timeout: int
) -> dict[str, Any]:
    """Run one fresh, tools-forbidden request and preserve even a failed attempt."""
    validate_inputs(items)
    directory.mkdir(parents=True, exist_ok=False)
    prompt = PROMPT + json.dumps(items, ensure_ascii=False)
    (directory / "prompt.txt").write_text(prompt)
    write(directory / "inputs.json", items)
    write(directory / "schema.json", SCHEMA)
    command = cli_command(directory, cli)
    receipt: dict[str, Any] = {
        "status": "running",
        "model_alias": MODEL,
        "reasoning_effort": EFFORT,
        "sampling": "Provider/CLI defaults; no explicit temperature override.",
        "items": len(items),
        "command": command,
        "started_unix": time.time(),
        "prompt_sha256": sha(prompt.encode()),
        "schema_sha256": sha((directory / "schema.json").read_bytes()),
        "source_sha256": sha(Path(__file__).read_bytes()),
        "input_sha256": sha((directory / "inputs.json").read_bytes()),
        "labels_or_companion_fields_provided": False,
        "tools_permitted": False,
        "semantic_fidelity_independently_verified": False,
        "directory": str(directory),
        "cli_version": subprocess.check_output(
            [cli, "--version"], text=True, timeout=30
        ).strip(),
    }
    write(directory / "receipt.json", receipt)
    started = time.monotonic()
    try:
        with (
            (directory / "events.jsonl").open("w") as events,
            (directory / "stderr.log").open("w") as errors,
        ):
            response = subprocess.run(
                command,
                input=prompt,
                text=True,
                stdout=events,
                stderr=errors,
                cwd=directory,
                timeout=timeout,
                check=False,
            )
        receipt["returncode"] = response.returncode
        receipt["events_sha256"] = sha((directory / "events.jsonl").read_bytes())
        if response.returncode:
            raise RuntimeError(
                f"CLI request failed with exit code {response.returncode}; preserved stderr.log."
            )
        receipt["usage"] = checked_events(directory / "events.jsonl")
        output = json.loads((directory / "response.json").read_text())
        checked = checked_records(items, output)
        write(directory / "records.json", checked)
        receipt.update(
            status="complete",
            response_sha256=sha((directory / "response.json").read_bytes()),
            records_sha256=sha((directory / "records.json").read_bytes()),
        )
    except Exception as exc:
        receipt.update(status="failed", error=str(exc))
        raise
    finally:
        receipt["elapsed_seconds"] = time.monotonic() - started
        write(directory / "receipt.json", receipt)
        print(
            json.dumps(
                {"event": "generation_batch", "directory": str(directory), **receipt},
                allow_nan=False,
            ),
            flush=True,
        )
    return receipt


def main() -> None:
    """Capture a declared partition only; full-corpus generation needs its own launch."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--inputs", type=Path, required=True)
    parser.add_argument("--groups", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument(
        "--split", choices=("training", "validation", "test"), required=True
    )
    parser.add_argument("--batch-size", type=int, default=64)
    parser.add_argument("--concurrency", type=int, default=2)
    parser.add_argument("--limit", type=int)
    parser.add_argument("--timeout", type=int, default=1200)
    parser.add_argument("--cli", default=CLI)
    parser.add_argument("--resume", action="store_true")
    args = parser.parse_args()
    if (
        not 1 <= args.concurrency <= 4
        or args.timeout < 1
        or (args.limit is not None and args.limit < 1)
    ):
        raise ValueError("Invalid capture resource bound.")
    items = json.loads(args.inputs.read_text())
    validate_inputs(items)
    groups = json.loads(args.groups.read_text())
    if args.limit is not None:
        chosen, seen = [], set()
        for item in sorted(items, key=lambda row: row["id"]):
            if groups[item["id"]] not in seen:
                chosen.append(item)
                seen.add(groups[item["id"]])
            if len(chosen) == args.limit:
                break
        items = chosen
        groups = {row["id"]: groups[row["id"]] for row in items}
    selected = batches(items, groups, args.batch_size)
    args.output = args.output.resolve()
    manifest = {
        "split": args.split,
        "input_file_sha256": sha(args.inputs.read_bytes()),
        "group_file_sha256": sha(args.groups.read_bytes()),
        "items": len(items),
        "batches": len(selected),
        "batch_size": args.batch_size,
        "concurrency": args.concurrency,
        "maximum_one_item_per_source_group_per_request": True,
        "model_alias": MODEL,
        "reasoning_effort": EFFORT,
        "prompt_template_sha256": sha(PROMPT.encode()),
        "schema_content_sha256": sha(json.dumps(SCHEMA, ensure_ascii=False).encode()),
        "cli": args.cli,
    }
    if args.resume:
        previous = json.loads((args.output / "manifest.json").read_text())
        if any(
            previous.get(key) != value
            for key, value in manifest.items()
            if key != "concurrency"
        ):
            raise ValueError(
                "Resume changes the declared partition, inputs or batching."
            )
        manifest["resume_history"] = [
            *previous.get("resume_history", []),
            {
                "previous_status": previous.get("status"),
                "previous_concurrency": previous.get("concurrency"),
                "concurrency": args.concurrency,
                "resumed_unix": time.time(),
            },
        ]
    else:
        args.output.mkdir(parents=True, exist_ok=False)
    manifest["status"] = "running"
    write(args.output / "manifest.json", manifest)
    receipts: list[dict[str, Any] | None] = [None] * len(selected)
    try:
        with ThreadPoolExecutor(max_workers=args.concurrency) as pool:
            futures = {
                pool.submit(
                    request_batch,
                    batch,
                    args.output,
                    index,
                    args.cli,
                    args.timeout,
                    args.resume,
                ): index
                for index, batch in enumerate(selected)
            }
            try:
                for future in as_completed(futures):
                    receipts[futures[future]] = future.result()
            except BaseException:
                for pending in futures:
                    pending.cancel()
                raise
        records = []
        for receipt in receipts:
            if receipt is None:
                raise ValueError("A requested batch has no completion receipt.")
            records.extend(
                json.loads((Path(receipt["directory"]) / "records.json").read_text())
            )
        checked = checked_records(items, {"records": records})
        write(args.output / "records.json", checked)
        manifest.update(
            status="complete",
            receipts=receipts,
            records_sha256=sha((args.output / "records.json").read_bytes()),
        )
        write(args.output / "manifest.json", manifest)
    except BaseException as exc:
        manifest.update(status="failed", error=str(exc))
        write(args.output / "manifest.json", manifest)
        raise
    print(
        json.dumps(
            {
                "event": "capture_complete",
                "items": len(checked),
                "batches": len(selected),
            },
            allow_nan=False,
        ),
        flush=True,
    )


if __name__ == "__main__":
    main()
