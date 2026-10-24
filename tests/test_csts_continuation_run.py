"""Check the native continuation bindings and the default review-only command."""

import json
from pathlib import Path

import pytest

from csts_pilot import continuation_run


def test_continuation_uses_terminal_weights_and_matching_saved_state():
    """A continuation binds to sealed parent outputs instead of initialization."""
    root = Path(__file__).parents[1]
    settings = json.loads((root / "configs/csts-continuation.json").read_text())
    for arm in ("mse", "pearson"):
        configured = continuation_run.training_stage(arm, settings, 1800)
        inputs = configured.spec.inputs
        assert inputs["initial_model"].artifact.artifact_name == "last_model"
        assert inputs["parent_resume"].artifact.artifact_name == "resume_state"
        assert inputs["incumbent_model"].artifact.artifact_name == "model"
        assert configured.spec.config.start_epoch == 24
        assert configured.spec.config.schedule == "constant"
        assert configured.spec.config.max_epochs == 48


def test_default_continuation_command_only_displays_settings(monkeypatch, capsys):
    """Viewing settings has no training side effect."""
    monkeypatch.setattr("sys.argv", ["continuation_run"])
    monkeypatch.setattr(
        continuation_run, "resolve_root", lambda: Path(__file__).parents[1]
    )
    monkeypatch.setattr(
        continuation_run,
        "run_study",
        lambda *_args, **_kwargs: pytest.fail("Review executed training."),
    )
    continuation_run.main()
    assert json.loads(capsys.readouterr().out)["status"] == "review"
