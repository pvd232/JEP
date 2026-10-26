"""Run the single permitted fresh, label-blind proposition audit on the Mac."""

import argparse
import base64
import hashlib
import importlib.util
import inspect
import json
import random
import re
import shlex
import shutil
import subprocess
import sys
import time
import traceback
import unicodedata
from pathlib import Path
from typing import Any

REPOSITORY = "pvd232/JEP"
BRANCH = "experiment/csts-proposition-lora-20261026"
WORK_ROOT = Path("/tmp/jep-tranche8-worker-20261026")
GENERATION_ROOT = Path("/tmp/jep-proposition-input-20261026")
GPU_ROOT = "/home/machina/jep-csts-answer-input-20261026"
GPU_PYTHON = "/home/machina/jep-format-env/bin/python"
VALIDATION_SHA256 = "f01ec22320c590e381ede0b378895cdd241cd8079e06b18715bc13d2921a4273"
GCLOUD = "/Users/machina/google-cloud-sdk/bin/gcloud"
GCLOUD_FLAGS = [
    "--account=pvd2112@columbia.edu",
    "--project=mantra-477901",
    "--zone=asia-northeast3-a",
    "--tunnel-through-iap",
]


class OperatorFailure(RuntimeError):
    """A safe operational message that never includes subprocess output."""


def digest(data: bytes) -> str:
    """Hash immutable source and capture inputs for the phase receipt."""
    return hashlib.sha256(data).hexdigest()


def write_json(path: Path, value: Any) -> None:
    """Persist a task-private JSON record with intentional Unicode text."""
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n")


def progress(event: str, **counts: Any) -> None:
    """Publish only the phase name, bounded counts and operational hashes."""
    print(
        "OPERATOR_PROGRESS "
        + json.dumps({"phase": "fresh_audit", "event": event, **counts}, allow_nan=False),
        flush=True,
    )


def select_fresh(
    rows: list[dict[str, Any]], initial_row_ids: list[str]
) -> dict[str, Any]:
    """Choose 30 new source groups and expose no labels or companion fields."""
    row_lookup = {row["row_id"]: row for row in rows}
    if len(row_lookup) != len(rows) or len(initial_row_ids) != 60 or len(set(initial_row_ids)) != 60:
        raise ValueError("Initial audit comparison identities differ.")
    if not set(initial_row_ids) <= set(row_lookup):
        raise ValueError("Initial audit rows are absent from validation.")
    excluded = {row_lookup[row_id]["group_id"] for row_id in initial_row_ids}
    if len(excluded) != 60:
        raise ValueError("The initial audit does not contain 60 distinct source groups.")
    grouped = {}
    for row in rows:
        grouped.setdefault(row["group_id"], []).append(row)
    eligible = sorted(set(grouped) - excluded)
    if len(eligible) < 30:
        raise ValueError("Insufficient fresh source groups.")
    groups = random.Random(61029).sample(eligible, 30)
    left, right, batch_groups, selected_rows = [], [], {}, []

    def identity(passage: str, condition: str) -> str:
        def canonical(text: str) -> str:
            return " ".join(unicodedata.normalize("NFKC", text).casefold().split())
        value = json.dumps([canonical(passage), canonical(condition)])
        return hashlib.sha256(value.encode()).hexdigest()

    for index, group in enumerate(groups):
        candidates = sorted(grouped[group], key=lambda row: row["row_id"])
        row = random.Random(61030 + index).choice(candidates)
        selected_rows.append(row["row_id"])
        for side, target in (("sentence1", left), ("sentence2", right)):
            key = identity(row[side], row["condition"])
            if key in batch_groups:
                raise ValueError("Fresh selection does not contain 60 unique passage-conditions.")
            target.append({"id": key, "passage": row[side], "condition": row["condition"]})
            batch_groups[key] = group
    if len(left) != 30 or len(right) != 30 or len(batch_groups) != 60 or set(groups) & excluded:
        raise ValueError("Fresh source-group separation or sample size differs.")
    return {
        "left": left,
        "right": right,
        "groups": batch_groups,
        "private_manifest": {
            "seed": 61029,
            "pair_seed_base": 61030,
            "groups": groups,
            "excluded_groups": sorted(excluded),
            "row_ids": selected_rows,
            "n_pairs": 30,
            "unique_passage_conditions": 60,
        },
    }


def checked_run(command: list[str], directory: Path, label: str, timeout: int) -> bytes:
    """Retain private subprocess logs while publishing only a safe failure code."""
    result = subprocess.run(command, capture_output=True, timeout=timeout, check=False)
    (directory / f"{label}.stdout").write_bytes(result.stdout)
    (directory / f"{label}.stderr").write_bytes(result.stderr)
    if result.returncode:
        raise OperatorFailure(f"{label} exited with status {result.returncode}; private logs retained.")
    return result.stdout


def fetch_capture(source_commit: str, directory: Path) -> tuple[Path, str]:
    """Fetch the capture module from the exact same reviewed GitHub commit."""
    gh = shutil.which("gh")
    if gh is None:
        gh = next((str(path) for path in (Path("/opt/homebrew/bin/gh"), Path("/usr/local/bin/gh")) if path.is_file()), None)
    if gh is None:
        raise OperatorFailure("The existing gh executable is unavailable.")
    path = "csts_pilot/proposition_capture.py"
    payload = json.loads(checked_run([gh, "api", f"repos/{REPOSITORY}/contents/{path}?ref={source_commit}"], directory, "fetch_capture", 45))
    if payload.get("type") != "file" or payload.get("encoding") != "base64":
        raise OperatorFailure("The pinned capture source response is not a file.")
    source = base64.b64decode("".join(payload["content"].split()), validate=True)
    git_blob = hashlib.sha1(b"blob " + str(len(source)).encode() + b"\0" + source).hexdigest()
    if git_blob != payload.get("sha"):
        raise OperatorFailure("The pinned capture source Git blob differs.")
    destination = directory / "proposition_capture.py"
    if destination.exists() and destination.read_bytes() != source:
        raise OperatorFailure("Preserve the pre-existing task-private capture source.")
    destination.write_bytes(source)
    return destination, digest(source)


def prepare_sample(directory: Path) -> dict[str, Any]:
    """Save the new group sample natively and transfer only blinded fields."""
    script = (
        "import json,hashlib,pathlib,random,unicodedata\nfrom typing import Any\n"
        + inspect.getsource(select_fresh)
        + f"\nroot=pathlib.Path({GPU_ROOT!r})\n"
        + f"expected={VALIDATION_SHA256!r}\n"
        + "source=root/'csts_data/dev.json'\n"
        + "if hashlib.sha256(source.read_bytes()).hexdigest()!=expected: raise RuntimeError('Validation source identity changed.')\n"
        + "initial_path=root/'answer_input_results/proposition_audit/sample_manifest.json'\n"
        + "initial=json.loads(initial_path.read_text())\n"
        + "if initial.get('seed')!=61027: raise RuntimeError('Initial sample seed differs.')\n"
        + "selected=select_fresh(json.loads(source.read_text()),initial['row_ids'])\n"
        + "manifest=selected['private_manifest']\n"
        + "manifest['source_validation_sha256']=expected\n"
        + "manifest['initial_manifest_sha256']=hashlib.sha256(initial_path.read_bytes()).hexdigest()\n"
        + "native=root/'answer_input_results/proposition_audit/fresh60'\n"
        + "native.mkdir(parents=True,exist_ok=True)\n"
        + "files={'blinded_inputs.json':selected['left']+selected['right'],'left_inputs.json':selected['left'],'right_inputs.json':selected['right'],'group_ids.json':selected['groups'],'sample_manifest.json':manifest}\n"
        + "for name,value in files.items():\n"
        + " path=native/name\n"
        + " data=(json.dumps(value,ensure_ascii=False,indent=2,allow_nan=False)+'\\n').encode()\n"
        + " if path.exists() and path.read_bytes()!=data: raise RuntimeError('Preserve the existing fresh sample; its identities differ.')\n"
        + " if not path.exists(): path.write_bytes(data)\n"
        + "print(json.dumps(selected,ensure_ascii=False,allow_nan=False))\n"
    )
    command = [
        GCLOUD, "compute", "ssh", "jep-csts-format-20261021", *GCLOUD_FLAGS,
        "--command=sudo -n -u machina " + GPU_PYTHON + " -c " + shlex.quote(script),
    ]
    selected = json.loads(checked_run(command, directory, "prepare_sample", 60))
    if set(selected) != {"left", "right", "groups", "private_manifest"}:
        raise OperatorFailure("Unexpected fields in the fresh blinded sample.")
    if len(selected["left"]) != 30 or len(selected["right"]) != 30:
        raise OperatorFailure("Fresh sample does not have two 30-item sides.")
    for side in ("left", "right"):
        if any(set(row) != {"id", "passage", "condition"} for row in selected[side]):
            raise OperatorFailure("Fresh sample contains forbidden source fields.")
        write_json(directory / f"{side}_inputs.json", selected[side])
    write_json(directory / "blinded_inputs.json", selected["left"] + selected["right"])
    write_json(directory / "group_ids.json", selected["groups"])
    write_json(directory / "private_sample_manifest.json", selected["private_manifest"])
    return selected


def fresh_audit(source_commit: str) -> dict[str, Any]:
    """Collect only the revised 60-item audit; never launch full-corpus work."""
    directory = WORK_ROOT / "fresh_audit" / source_commit
    directory.mkdir(parents=True, exist_ok=True)
    progress("fetching_reviewed_source", source_commit=source_commit)
    capture, source_hash = fetch_capture(source_commit, directory)
    selected = prepare_sample(directory)
    inputs = selected["left"] + selected["right"]
    progress("sample_prepared", source_groups=30, excluded_source_groups=60, items=60)
    output = GENERATION_ROOT / "fresh60"
    command = [
        sys.executable, str(capture),
        "--inputs", str(directory / "blinded_inputs.json"),
        "--groups", str(directory / "group_ids.json"),
        "--output", str(output), "--split", "validation",
        "--batch-size", "64", "--concurrency", "2", "--timeout", "1200",
    ]
    if output.exists():
        manifest_path = output / "manifest.json"
        if not manifest_path.is_file():
            raise OperatorFailure("An existing fresh capture has no manifest; preserve it for review.")
        if json.loads(manifest_path.read_text()).get("status") == "failed":
            raise OperatorFailure("The existing fresh capture failed; preserve its logs for review.")
        command.append("--resume")
    started = time.monotonic()
    with (directory / "capture.stdout").open("wb") as stdout, (directory / "capture.stderr").open("wb") as stderr:
        process = subprocess.Popen(command, stdout=stdout, stderr=stderr, cwd=directory)
        while process.poll() is None:
            if time.monotonic() - started > 1300:
                process.terminate()
                try:
                    process.wait(timeout=30)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait()
                raise OperatorFailure("The fresh capture exceeded its declared wall allowance.")
            time.sleep(15)
            complete = 0
            for receipt_path in output.glob("batch_*/receipt.json"):
                try:
                    receipt = json.loads(receipt_path.read_text())
                    if receipt.get("status") == "complete":
                        complete += receipt.get("items", 0)
                except (OSError, ValueError):
                    continue
            progress("generating", completed_items=complete, total_items=60, elapsed_seconds=round(time.monotonic() - started, 1))
    if process.returncode:
        raise OperatorFailure(f"The fresh capture exited with status {process.returncode}; private logs retained.")
    manifest = json.loads((output / "manifest.json").read_text())
    if manifest.get("status") != "complete" or manifest.get("items") != 60:
        raise OperatorFailure("The fresh capture is not complete for all 60 inputs.")
    spec = importlib.util.spec_from_file_location("reviewed_proposition_capture", capture)
    if spec is None or spec.loader is None:
        raise OperatorFailure("The pinned capture module could not be loaded.")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    records = module.checked_records(inputs, {"records": json.loads((output / "records.json").read_text())})
    if module.MODEL != "gpt-6.1-sol" or module.EFFORT != "high":
        raise OperatorFailure("The reviewed generation model settings changed.")
    public_manifest = {
        "seed": 61029, "pair_seed_base": 61030,
        "source_groups": 30, "excluded_source_groups": 60,
        "unique_passage_conditions": 60,
        "source_validation_sha256": VALIDATION_SHA256,
        "input_sha256": digest((directory / "blinded_inputs.json").read_bytes()),
        "capture_source_sha256": source_hash,
        "capture_generation_source_sha256": sorted({receipt["source_sha256"] for receipt in manifest["receipts"]}),
        "prompt_template_sha256": digest(module.PROMPT.encode()),
        "schema_content_sha256": digest(json.dumps(module.SCHEMA, ensure_ascii=False).encode()),
        "model_alias": module.MODEL, "reasoning_effort": module.EFFORT,
        "no_model_tools": True, "semantic_fidelity_independently_verified": False,
        "source_commit": source_commit,
        "branch": BRANCH,
    }
    result = {
        "phase": "fresh_audit", "status": "complete",
        "blinded_fresh_sample": {
            "left": selected["left"], "right": selected["right"],
            "records": records, "manifest": public_manifest,
        },
    }
    write_json(directory / "operator_result.json", result)
    progress("captured", items=60, source_groups=30)
    return result


def inspect_failure(source_commit: str) -> dict[str, Any]:
    """Return bounded safe exception summaries from this task's failed phase."""
    directory = WORK_ROOT / "fresh_audit" / source_commit
    result_path = directory / "operator_result.json"
    result = json.loads(result_path.read_text()) if result_path.exists() else None
    summaries = {}
    for name in ("operator_failure.log", "prepare_sample.stderr", "fetch_capture.stderr", "capture.stderr"):
        path = directory / name
        if not path.exists():
            continue
        lines = path.read_text(errors="replace").splitlines()
        selected = [line[:1000] for line in lines if re.match(
            r"^(?:[A-Za-z_.]*(?:Error|Failure|Exception):|ERROR:|  File )", line
        )]
        summaries[name.replace(".", "_")] = selected[-12:]
    return {"phase": "inspect_failure", "status": "complete", "diagnostic": {
        "inspected_source_commit": source_commit, "safe_result": result,
        "exception_summaries": summaries,
        "present_files": sorted(path.name for path in directory.iterdir()) if directory.exists() else [],
    }}


def main() -> None:
    """Execute one allowlisted phase from a pinned repository source commit."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--phase", choices=("fresh_audit", "inspect_failure"), required=True)
    parser.add_argument("--source-commit", required=True)
    parser.add_argument("--inspect-source-commit")
    args = parser.parse_args()
    if re.fullmatch(r"[0-9a-f]{40}", args.source_commit) is None:
        raise OperatorFailure("A full immutable source commit is required.")
    try:
        if args.phase == "inspect_failure":
            if not args.inspect_source_commit or re.fullmatch(r"[0-9a-f]{40}", args.inspect_source_commit) is None:
                raise OperatorFailure("A failed task source commit is required for inspection.")
            result = inspect_failure(args.inspect_source_commit)
        else:
            result = fresh_audit(args.source_commit)
    except BaseException as exc:
        directory = WORK_ROOT / "fresh_audit" / args.source_commit
        directory.mkdir(parents=True, exist_ok=True)
        (directory / "operator_failure.log").write_text(traceback.format_exc())
        message = str(exc) if isinstance(exc, OperatorFailure) else "Fresh audit failed; private logs retained."
        result = {"phase": args.phase, "status": "failed", "error": message, "error_type": type(exc).__name__}
        write_json(directory / "operator_result.json", result)
        print("OPERATOR_RESULT " + json.dumps(result, allow_nan=False), flush=True)
        raise SystemExit(1) from None
    print("OPERATOR_RESULT " + json.dumps(result, ensure_ascii=False, allow_nan=False), flush=True)


if __name__ == "__main__":
    main()
