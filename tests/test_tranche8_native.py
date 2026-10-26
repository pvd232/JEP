"""Verify native transport boundaries without a device, network or model run."""

import importlib.util
import json
import subprocess
import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import patch

SPEC = importlib.util.spec_from_file_location(
    "tranche8_native", Path(__file__).parents[1] / "scripts/tranche8_native.py"
)
assert SPEC is not None and SPEC.loader is not None
native = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(native)
COMMIT = "a" * 40


class NativeTests(unittest.TestCase):
    def compile_remote(self, script, directory, label, timeout=120):
        compile(script, label, "exec")
        return {"status": "complete"}

    def test_all_remote_python_programs_compile(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            def fake_run(command, *args, **kwargs):
                return (COMMIT + "\n").encode() if "rev-parse" in command else b""
            with patch.object(native, "remote", side_effect=self.compile_remote), patch.object(native, "run", side_effect=fake_run), patch.object(native, "gh_path", return_value="/existing/gh"), patch.object(native, "copy_to_gpu", return_value=("/tmp/fixed", "b" * 64)):
                native.native_deploy(COMMIT, directory)
                native.native_checks(COMMIT, directory, False)
                native.native_checks(COMMIT, directory, True)
                native.native_source(COMMIT, directory, "csts_pilot/proposition_run.py")
                native.native_status(COMMIT, directory, "attempt")
                native.check_diagnostics(COMMIT, directory)
                native.native_archive(COMMIT, directory)
                with patch.object(native, "import_capture", return_value={}), patch.object(native, "fetch_file", return_value=b"fixed source"):
                    native.native_launch(COMMIT, directory, "attempt")
                    native.native_launch(COMMIT, directory, "sample_attempt", "csts_pilot.proposition_sample")

    def test_source_fetch_rejects_outside_allowlist(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            with self.assertRaises(native.NativeFailure):
                native.native_source(COMMIT, Path(temporary), "../outside")

    def test_incomplete_generation_cannot_be_transferred(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            bank = directory / "bank"
            bank.mkdir()
            (bank / "propositions_tranche8.json").write_text("[]\n")
            (bank / "propositions_tranche8_manifest.json").write_text(json.dumps({"items": 0}))
            with patch.object(native, "GEN_ROOT", bank), patch.object(native, "copy_to_gpu") as transfer:
                with self.assertRaises(native.NativeFailure):
                    native.import_capture(COMMIT, directory)
                transfer.assert_not_called()

    def test_complete_transport_program_compiles_and_never_extracts_arbitrary_members(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            bank = directory / "bank"
            bank.mkdir()
            records = b"[]\n"
            gate = b'{"passed":true}\n'
            (bank / "propositions_tranche8.json").write_bytes(records)
            manifest = {"items": 17334, "records_sha256": native.sha(records), "audit_gate_sha256": native.sha(gate), "partitions": {name: {"status": "complete"} for name in ("training", "validation")}}
            (bank / "propositions_tranche8_manifest.json").write_text(json.dumps(manifest))
            captured = []
            def checked_remote(script, *args, **kwargs):
                compile(script, "bank_install", "exec")
                captured.append(script)
                return {"status": "complete"}
            with patch.object(native, "GEN_ROOT", bank), patch.object(native, "fetch_file", return_value=gate), patch.object(native, "copy_to_gpu", return_value=("/tmp/fixed", "b" * 64)), patch.object(native, "remote", side_effect=checked_remote):
                native.import_capture(COMMIT, directory)
            self.assertIn("member.isfile()", captured[0])
            self.assertNotIn("extractall", captured[0])

    def test_verified_published_format_is_staged_before_git_checkout(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "repo"
            subprocess.run(["git", "init", "--quiet", str(root)], check=True)
            def git(*arguments, check=True):
                return subprocess.run(["git", "-C", str(root), *arguments], capture_output=True, text=True, check=check)
            source = root / "owned.py"
            source.write_text("x=1\n")
            git("add", "owned.py")
            git("-c", "user.name=Contract Test", "-c", "user.email=test@example.invalid", "commit", "--quiet", "-m", "old")
            old = git("rev-parse", "HEAD").stdout.strip()
            source.write_text("x = 1\n")
            git("add", "owned.py")
            git("-c", "user.name=Contract Test", "-c", "user.email=test@example.invalid", "commit", "--quiet", "-m", "published format")
            new = git("rev-parse", "HEAD").stdout.strip()
            git("checkout", "--detach", old)
            source.write_text("x = 1\n")
            self.assertNotEqual(git("checkout", "--detach", new, check=False).returncode, 0)
            published = git("show", new + ":owned.py").stdout.encode()
            self.assertEqual(source.read_bytes(), published)
            git("add", "--", "owned.py")
            git("checkout", "--detach", new)
            self.assertEqual(git("status", "--porcelain", "--untracked-files=no").stdout, "")

    def test_capture_observability_does_not_return_event_or_prompt_text(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "capture"
            batch = root / "training/batch_0000"
            batch.mkdir(parents=True)
            (batch / "receipt.json").write_text(json.dumps({"status": "running", "started_unix": time.time()-100, "items": 64, "command": ["PRIVATE_COMMAND"]}))
            (batch / "events.jsonl").write_text(json.dumps({"type": "item.completed", "item": {"type": "agent_message", "text": "PRIVATE_GENERATED_TEXT"}})+"\n")
            (batch / "prompt.txt").write_text("PRIVATE_PASSAGE")
            (batch / "stderr.log").write_text("capacity 429 retry connection PRIVATE_SECRET https://private.invalid/path")
            with patch.object(native, "GEN_ROOT", root), patch.object(native, "MAC_ROOT", Path(temporary) / "native"):
                result = native.capture_diagnostics()
            self.assertEqual(result["running"][0]["last_cli_event_type"], "item.completed")
            self.assertEqual(result["running"][0]["event_count"], 1)
            self.assertEqual(result["counts"]["running_batches"], 1)
            self.assertTrue(result["running"][0]["stderr_flags"]["capacity"])
            self.assertTrue(result["running"][0]["stderr_flags"]["rate_limit"])
            self.assertEqual(result["running"][0]["stderr_counts"]["retrying"], 1)
            self.assertNotIn("PRIVATE", json.dumps(result))
            self.assertNotIn("https://", json.dumps(result))

    def test_operation_diagnostics_redacts_credentials(self) -> None:
        self.assertNotIn("github_pat_", native.redact("github_pat_" + "a"*32))
        self.assertNotIn("privatevalue", native.redact("API_KEY=privatevalue"))


if __name__ == "__main__":
    unittest.main()
