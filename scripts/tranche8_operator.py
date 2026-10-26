"""Dispatch one allowlisted task module from an immutable target source commit.

The worker separately pins this dispatcher's bytes. Its structured target-source
pin must match --source-commit; a target module is fetched at that exact commit.
Formatting export remains a separate explicit phase, not the default operator.
"""

import argparse
import base64
import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path

REPOSITORY = "pvd232/JEP"
NATIVE_PHASES = (
    "native_deploy",
    "native_checks",
    "native_source",
    "native_import_capture",
    "native_launch",
    "native_sample",
    "native_status",
    "native_check_diagnostics",
    "native_operation_diagnostics",
    "native_archive",
    "capture_diagnostics",
)
CAPTURE_PHASES = ("full_capture", "full_capture_status")


def target_module(phase: str) -> str:
    """Choose a fixed repository path without accepting executable paths in argv."""
    if phase in NATIVE_PHASES:
        return "scripts/tranche8_native.py"
    if phase in CAPTURE_PHASES:
        return "scripts/tranche8_continue.py"
    if phase == "formatted_sources":
        return "scripts/tranche8_formatted_sources.py"
    raise ValueError("Phase is outside the fixed operator allowlist.")


def fetch_module(path: str, commit: str, directory: Path) -> Path:
    """Verify a Git blob and preserve an already-downloaded immutable module."""
    gh = shutil.which("gh")
    if gh is None:
        raise RuntimeError("The existing authenticated GitHub CLI is unavailable.")
    result = subprocess.run(
        [gh, "api", f"repos/{REPOSITORY}/contents/{path}?ref={commit}"],
        capture_output=True,
        check=True,
        timeout=60,
    )
    record = json.loads(result.stdout)
    if (
        record.get("type") != "file"
        or record.get("path") != path
        or record.get("encoding") != "base64"
    ):
        raise ValueError("Unexpected pinned operator module identity.")
    content = base64.b64decode("".join(record["content"].split()), validate=True)
    blob = hashlib.sha1(
        b"blob " + str(len(content)).encode() + b"\0" + content
    ).hexdigest()
    if blob != record.get("sha"):
        raise ValueError("Pinned operator module Git blob differs.")
    directory.mkdir(parents=True, exist_ok=True)
    destination = directory / Path(path).name
    if destination.exists():
        if destination.is_symlink() or destination.read_bytes() != content:
            raise ValueError(
                "Existing operator module differs; preserve the earlier attempt."
            )
    else:
        with destination.open("xb") as stream:
            stream.write(content)
    return destination


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    parser.add_argument(
        "--phase",
        required=True,
        choices=(*NATIVE_PHASES, *CAPTURE_PHASES, "formatted_sources"),
    )
    parser.add_argument("--source-commit", required=True)
    parser.add_argument("--name")
    parser.add_argument("--concurrency", type=int, choices=(1, 2, 3, 4))
    parser.add_argument("--allow-format", action="store_true")
    parser.add_argument("--path")
    parser.add_argument("--operation")
    args = parser.parse_args()
    if len(args.source_commit) != 40 or any(
        c not in "0123456789abcdef" for c in args.source_commit
    ):
        parser.error("Use a complete target source commit.")
    selected = target_module(args.phase)
    # Forward only parsed values, never unchecked shell or extra source options.
    forwarded = ["--source-commit", args.source_commit]
    if args.phase != "formatted_sources":
        forwarded += ["--phase", args.phase]
    if args.phase in CAPTURE_PHASES:
        if args.name or args.allow_format or args.path or args.operation:
            parser.error("Native options do not apply to capture phases.")
        if args.concurrency is not None:
            forwarded += ["--concurrency", str(args.concurrency)]
    elif args.phase in NATIVE_PHASES:
        if args.concurrency is not None:
            parser.error("Concurrency applies only to capture phases.")
        for option in ("name", "path", "operation"):
            value = getattr(args, option)
            if value is not None:
                forwarded += ["--" + option, value]
        if args.allow_format:
            forwarded.append("--allow-format")
    elif any(
        (args.name, args.concurrency, args.allow_format, args.path, args.operation)
    ):
        parser.error("Formatting export accepts only its target source commit.")
    directory = Path(__file__).resolve().parent / "dispatch" / args.source_commit
    module = fetch_module(selected, args.source_commit, directory)
    result = subprocess.run(
        [sys.executable, "-I", str(module), *forwarded], check=False, timeout=2100
    )
    raise SystemExit(result.returncode)


if __name__ == "__main__":
    main()
