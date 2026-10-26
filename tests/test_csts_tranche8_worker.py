"""Verify the operator's fetched and executed source pins cannot diverge."""

import importlib.util
from pathlib import Path

import pytest

_SPEC = importlib.util.spec_from_file_location(
    "tranche8_worker",
    Path(__file__).resolve().parents[1] / "scripts/tranche8_worker.py",
)
assert _SPEC is not None and _SPEC.loader is not None
worker = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(worker)


def control(arguments):
    return {
        "action": "run",
        "action_id": "test-only",
        "source_commit": "a" * 40,
        "operator_sha256": "b" * 64,
        "arguments": arguments,
    }


@pytest.mark.parametrize(
    "pin", [["--source-commit", "a" * 40], ["--source-commit=" + "a" * 40]]
)
def test_source_pin_matches_verified_operator(pin):
    value = control(["--phase", "fresh_audit", *pin])
    assert worker.validate_control(value) == value


@pytest.mark.parametrize(
    "arguments",
    [
        [],
        ["--source-commit"],
        ["--source-commit", "c" * 40],
        ["--source-commit=" + "c" * 40],
        ["--source-commit", "a" * 40, "--source-commit", "c" * 40],
        ["--source-commit", "a" * 40, "--s", "c" * 40],
        ["--source-commit", "a" * 40, "--source-c=" + "c" * 40],
    ],
)
def test_missing_mismatched_duplicate_and_abbreviated_pins_fail_before_launch(
    arguments,
):
    with pytest.raises(ValueError, match="source"):
        worker.validate_control(control(arguments))


def test_explicit_target_source_is_separate_from_operator_code_pin():
    target = "c" * 40
    value = control(["--source-commit", target])
    with pytest.raises(ValueError, match="target source"):
        worker.validate_control(value)
    value["target_source_commit"] = target
    assert worker.validate_control(value) == value
    value["target_source_commit"] = "d" * 40
    with pytest.raises(ValueError, match="target source"):
        worker.validate_control(value)


def test_legacy_receipt_accepts_explicit_target_metadata_without_relaunch(
    tmp_path, monkeypatch
):
    import json
    from unittest.mock import patch

    value = control(["--source-commit", "c" * 40])
    value["target_source_commit"] = "c" * 40
    worker.validate_control(value)
    monkeypatch.setattr(worker, "WORK_ROOT", tmp_path)
    directory = worker.directory_for(value["action_id"])
    directory.mkdir(parents=True)
    receipt = {
        key: value[key]
        for key in ("action_id", "source_commit", "operator_sha256", "arguments")
    }
    receipt["status"] = "completed"
    path = directory / "receipt.json"
    path.write_text(json.dumps(receipt))
    original = path.read_bytes()
    with patch.object(worker, "github_file") as fetch:
        assert worker.launch(value) == (directory, None)
        fetch.assert_not_called()
    assert path.read_bytes() == original
    with pytest.raises(ValueError, match="different operator binding"):
        worker.launch(
            dict(
                value,
                arguments=["--source-commit", "d" * 40],
                target_source_commit="d" * 40,
            )
        )
