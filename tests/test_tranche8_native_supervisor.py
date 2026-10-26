"""Exercise source and workspace ownership without launching a native experiment."""

import importlib.util
import json
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import pytest


def module(name):
    spec = importlib.util.spec_from_file_location(
        name, Path(__file__).resolve().parents[1] / "scripts" / (name + ".py")
    )
    assert spec is not None and spec.loader is not None
    loaded = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(loaded)
    return loaded


native = module("tranche8_native")
supervisor = module("tranche8_native_supervisor")
COMMIT = "a" * 40


def workspace(tmp_path, monkeypatch):
    root, parent = tmp_path / "owner", tmp_path / "parent"
    root.mkdir()
    parent.mkdir()
    monkeypatch.setattr(native, "GPU_ROOT", str(root))
    monkeypatch.setattr(native, "PARENT_ROOT", str(parent))
    namespace = {}
    exec(native.preamble(COMMIT), namespace)  # noqa: S102 - execute only the authored program in a temporary workspace.
    return root, parent, namespace


def test_workspace_mutation_owner_prevents_supervised_launch(tmp_path, monkeypatch):
    root, parent, namespace = workspace(tmp_path, monkeypatch)
    (root / "answer_input_results/supervisors/attempt").mkdir(parents=True)
    with (
        namespace["workspace_lease"](),
        patch.object(supervisor.subprocess, "Popen") as launch,
    ):
        with pytest.raises(BlockingIOError):
            supervisor.supervise(
                root, parent, "attempt", COMMIT, "csts_pilot.proposition_run"
            )
        launch.assert_not_called()


def test_native_child_retains_workspace_lease_after_supervisor_returns(
    tmp_path, monkeypatch
):
    root, parent, namespace = workspace(tmp_path, monkeypatch)
    directory = root / "answer_input_results/supervisors/attempt"
    directory.mkdir(parents=True)
    (directory / "receipt.json").write_text(
        json.dumps(
            {
                "source_commit": COMMIT,
                "name": "attempt",
                "module": "csts_pilot.proposition_run",
                "status": "launching",
            }
        )
    )
    checks = root / "answer_input_results/owner_checks" / COMMIT
    checks.mkdir(parents=True)
    (checks / "receipt.json").write_text(
        json.dumps({"passed": True, "source_clean": True, "owned_source_sha256": {}})
    )
    original_popen = subprocess.Popen
    children = []

    def fake_native(_argv, **kwargs):
        child = original_popen(
            [sys.executable, "-c", "import time; time.sleep(30)"],
            pass_fds=kwargs["pass_fds"],
        )
        children.append(child)
        # Simulate supervisor interruption while the native process remains.
        return SimpleNamespace(pid=child.pid, wait=lambda **_kwargs: 0)

    try:
        with (
            patch.object(
                supervisor.subprocess, "check_output", side_effect=[COMMIT + "\n", ""]
            ),
            patch.object(supervisor.subprocess, "Popen", side_effect=fake_native),
        ):
            supervisor.supervise(
                root, parent, "attempt", COMMIT, "csts_pilot.proposition_run"
            )
        with pytest.raises(BlockingIOError):
            namespace["workspace_lease"]()
    finally:
        for child in children:
            child.terminate()
            child.wait(timeout=5)
    with namespace["workspace_lease"]():
        pass


def test_source_clean_rejects_untracked_import_shadow(tmp_path, monkeypatch):
    root, _, namespace = workspace(tmp_path, monkeypatch)

    def git(*args):
        return subprocess.run(
            ["git", *args], cwd=root, check=True, capture_output=True, text=True
        )

    git("init", "--quiet")
    (root / "reviewed.py").write_text("VALUE = 1\n")
    git("add", "reviewed.py")
    git(
        "-c",
        "user.name=Fixture",
        "-c",
        "user.email=fixture@example.invalid",
        "-c",
        "commit.gpgsign=false",
        "-c",
        "core.hooksPath=/dev/null",
        "commit",
        "--quiet",
        "-m",
        "Reviewed",
    )
    namespace["commit"] = git("rev-parse", "HEAD").stdout.strip()
    namespace["clean"]()
    (root / "torch.py").write_text("raise RuntimeError('unreviewed import shadow')\n")
    with pytest.raises(AssertionError, match="dirty or untracked"):
        namespace["clean"]()


def test_mutator_gpu_guard_respects_direct_cli_owner_and_shared_readers_coexist(
    tmp_path, monkeypatch
):
    import fcntl

    _, parent, namespace = workspace(tmp_path, monkeypatch)
    (parent / ".viper").mkdir()
    with (parent / ".viper/overnight_gpu.lock").open("a+") as direct_cli_owner:
        fcntl.flock(direct_cli_owner.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        with pytest.raises(BlockingIOError):
            namespace["gpu_lease"]()
    with (
        namespace["workspace_lease"](shared=True),
        namespace["workspace_lease"](shared=True),
        pytest.raises(BlockingIOError),
    ):
        namespace["workspace_lease"]()


def test_cpu_archive_child_retains_shared_source_lease_after_wrapper_exit(
    tmp_path, monkeypatch
):
    _, _, namespace = workspace(tmp_path, monkeypatch)
    original_popen = subprocess.Popen
    children = []

    def fake_archive(_argv, **kwargs):
        child = original_popen(
            [sys.executable, "-c", "import time; time.sleep(30)"],
            pass_fds=kwargs["pass_fds"],
        )
        children.append(child)
        return SimpleNamespace(returncode=0, stdout=b"", stderr=b"")

    def local_remote(script, *_args):
        wrapper = {}
        try:
            exec(script, wrapper)  # noqa: S102 - execute the authored remote program in an isolated fixture.
        finally:
            # Simulate the remote wrapper ending while its archive child lives.
            if "workspace_owner" in wrapper:
                wrapper["workspace_owner"].close()
        return {"status": "complete"}

    try:
        with (
            patch.object(native, "remote", side_effect=local_remote),
            patch.object(
                native.subprocess, "check_output", side_effect=[COMMIT + "\n", ""]
            ),
            patch.object(native.subprocess, "run", side_effect=fake_archive),
        ):
            native.native_archive(COMMIT, tmp_path)
        with pytest.raises(BlockingIOError):
            namespace["workspace_lease"]()
        with namespace["workspace_lease"](shared=True):
            pass
    finally:
        for child in children:
            child.terminate()
            child.wait(timeout=5)
    with namespace["workspace_lease"]():
        pass
