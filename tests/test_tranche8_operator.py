"""Verify immutable operator dispatch without network access or a worker launch."""

import base64
import hashlib
import importlib.util
import json
import sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import pytest

SPEC = importlib.util.spec_from_file_location(
    "tranche8_operator",
    Path(__file__).resolve().parents[1] / "scripts/tranche8_operator.py",
)
assert SPEC is not None and SPEC.loader is not None
operator = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(operator)
COMMIT = "a" * 40


def test_module_path_is_allowlisted():
    assert operator.target_module("full_capture") == "scripts/tranche8_continue.py"
    assert operator.target_module("native_status") == "scripts/tranche8_native.py"
    assert (
        operator.target_module("formatted_sources")
        == "scripts/tranche8_formatted_sources.py"
    )
    with pytest.raises(ValueError):
        operator.target_module("../../other.py")


def test_fetch_preserves_exact_git_blob_and_rejects_tampering(tmp_path):
    content = b"print('fixture')\n"
    path = "scripts/tranche8_native.py"
    record = {
        "type": "file",
        "path": path,
        "encoding": "base64",
        "content": base64.b64encode(content).decode(),
        "sha": hashlib.sha1(
            b"blob " + str(len(content)).encode() + b"\0" + content
        ).hexdigest(),
    }
    with (
        patch.object(operator.shutil, "which", return_value="/fixture/gh"),
        patch.object(
            operator.subprocess,
            "run",
            return_value=SimpleNamespace(stdout=json.dumps(record)),
        ),
    ):
        destination = operator.fetch_module(path, COMMIT, tmp_path)
        assert destination.read_bytes() == content
        destination.write_bytes(b"unreviewed")
        with pytest.raises(ValueError, match="Existing operator"):
            operator.fetch_module(path, COMMIT, tmp_path)
    record["sha"] = "0" * 40
    with (
        patch.object(operator.shutil, "which", return_value="/fixture/gh"),
        patch.object(
            operator.subprocess,
            "run",
            return_value=SimpleNamespace(stdout=json.dumps(record)),
        ),
        pytest.raises(ValueError, match="Git blob"),
    ):
        operator.fetch_module(path, COMMIT, tmp_path / "other")


def test_native_dispatch_forwards_one_exact_source_and_phase(monkeypatch):
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "operator",
            "--phase",
            "native_status",
            "--source-commit",
            COMMIT,
            "--name",
            "fixture",
        ],
    )
    with (
        patch.object(
            operator, "fetch_module", return_value=Path("/fixture/native.py")
        ) as fetch,
        patch.object(
            operator.subprocess, "run", return_value=SimpleNamespace(returncode=0)
        ) as run,
        pytest.raises(SystemExit) as result,
    ):
        operator.main()
    assert result.value.code == 0
    assert fetch.call_args.args[:2] == ("scripts/tranche8_native.py", COMMIT)
    assert run.call_args.args[0] == [
        sys.executable,
        "-I",
        "/fixture/native.py",
        "--source-commit",
        COMMIT,
        "--phase",
        "native_status",
        "--name",
        "fixture",
    ]
