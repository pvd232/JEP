"""Exercise the paid-work gates and fixed publication boundaries offline."""

import base64
import importlib.util
import json
import tempfile
import unittest
from concurrent.futures import Future
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch

SPEC = importlib.util.spec_from_file_location("tranche8_pipeline", Path(__file__).parents[1] / "scripts/tranche8_pipeline.py")
assert SPEC is not None and SPEC.loader is not None
pipeline = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(pipeline)
OPERATOR = "a" * 40
NATIVE = "b" * 40
AUDIT = "# Status\n\nEach audit used source-sampled groups and independent reviewers. Exact quotations are checked separately.\n\nAudit records, source-only references and failures are preserved.\n"


class ImmediateExecutor:
    def __init__(self, **kwargs):
        pass

    def submit(self, function):
        future = Future()
        try:
            future.set_result(function())
        except Exception as error:
            future.set_exception(error)
        return future

    def shutdown(self, **kwargs):
        pass


def finished(selection=None):
    return {"status": "complete", "source_commit": NATIVE, "result": {"selection": selection or {"selected_arm": None, "eligibility": {"adapted": {"eligible": False}}, "test_scores_used_for_selection": False}}}


class PipelineTests(unittest.TestCase):
    def test_test_result_is_not_opened_without_validation_release(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            helper = SimpleNamespace(WORK_ROOT=Path(temporary))
            result = Path(temporary) / (OPERATOR + "-" + NATIVE) / "result.json"
            result.parent.mkdir()
            result.write_text("This existing file must not be read.")
            observation = pipeline.test_observation(Path(temporary), helper, OPERATOR, NATIVE, False)
            self.assertEqual(observation, {"status": "not_released", "test_inputs_opened": False})

    def test_validation_gate_requires_eligible_frozen_selection(self) -> None:
        self.assertEqual(pipeline.validation_decision(finished()), "no_eligible_candidate")
        selection = {"selected_arm": "adapted", "eligibility": {"adapted": {"eligible": True}}, "test_scores_used_for_selection": False}
        self.assertEqual(pipeline.validation_decision(finished(selection)), "eligible_test")
        for altered in ({**selection, "test_scores_used_for_selection": True}, {**selection, "eligibility": {"adapted": {"eligible": False}}}):
            with self.assertRaises(pipeline.PipelineFailure):
                pipeline.validation_decision(finished(altered))

    def test_public_state_removes_source_content_and_credentials(self) -> None:
        value = pipeline.public({"passage": "private passage", "command": ["private command"], "result": {"records": ["private"], "spearman": 0.8}, "note": "github_pat_" + "x" * 32})
        text = json.dumps(value)
        self.assertNotIn("private", text)
        self.assertNotIn("github_pat_", text)
        self.assertEqual(value["result"]["spearman"], 0.8)

    def test_guarded_write_only_updates_fixed_path_with_latest_sha(self) -> None:
        response = SimpleNamespace(returncode=0, stderr=b"", stdout=b"{}")
        with patch.object(pipeline, "github_file", return_value=({"sha": "c" * 40}, b"old")), patch.object(pipeline, "gh", return_value="gh"), patch.object(pipeline.subprocess, "run", return_value=response) as run:
            pipeline.guarded_write(pipeline.RESULT_PATH, b"new")
            command = run.call_args.args[0]
            body = json.loads(run.call_args.kwargs["input"])
            self.assertIn(pipeline.RESULT_PATH, command[-3])
            self.assertEqual(body["sha"], "c" * 40)
            self.assertEqual(base64.b64decode(body["content"]), b"new")
            self.assertEqual(body["branch"], pipeline.BRANCH)
            with self.assertRaises(pipeline.PipelineFailure):
                pipeline.guarded_write("unrelated.md", b"new")

    def test_revised_native_helper_cannot_be_silently_loaded(self) -> None:
        with tempfile.TemporaryDirectory() as temporary, patch.object(pipeline, "github_file", return_value=({}, b"raise RuntimeError('must not run')")):
            with self.assertRaises(pipeline.PipelineFailure):
                pipeline.load_helper(pipeline.NATIVE_HELPER, OPERATOR, Path(temporary), pipeline.NATIVE_HELPER_SHA256)

    def test_audit_methodology_is_retained_verbatim(self) -> None:
        evidence = pipeline.audit_evidence(AUDIT)
        self.assertIn(AUDIT.split("\n\n")[1], evidence)
        self.assertIn(AUDIT.split("\n\n")[2].strip(), evidence)

    def test_failed_original_capture_is_not_replaced(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "full_capture" / pipeline.CAPTURE_COMMIT
            source.mkdir(parents=True)
            (source / "supervisor_receipt.json").write_text(json.dumps({"source_commit": pipeline.CAPTURE_COMMIT, "output_path": str(root / "bank"), "status": "failed"}))
            native = SimpleNamespace(MAC_ROOT=root / "native", GEN_ROOT=root / "bank", capture_diagnostics=Mock(return_value={"counts": {"completed_items": 100}}))
            with self.assertRaises(pipeline.PipelineFailure):
                pipeline.capture_state(native)

    def test_running_test_helper_is_observed_without_duplicate_launch_or_raw_log_read(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            helper = SimpleNamespace(WORK_ROOT=directory / "test", __file__=__file__)
            pipeline.save(directory / "test_helper_receipt.json", {"operator_source_commit": OPERATOR, "native_source_commit": NATIVE, "pid": 1234})
            (directory / "test_helper.stdout").write_text('PRIVATE_RAW_LOG\nOPERATOR_PROGRESS {"event":"generating_test","counts":{"completed_items":64},"prompt":"PRIVATE_PROMPT"}\n')
            process = SimpleNamespace(returncode=0, stdout=str(Path(__file__).resolve()).encode())
            with patch.object(pipeline.subprocess, "run", return_value=process), patch.object(pipeline.subprocess, "Popen") as launch:
                result = pipeline.test_observation(directory, helper, OPERATOR, NATIVE, True)
            launch.assert_not_called()
            self.assertEqual(result["progress"]["counts"]["completed_items"], 64)
            self.assertNotIn("PRIVATE", json.dumps(result))

    def test_expired_allowance_does_not_launch_any_native_or_test_job(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            native = SimpleNamespace(__file__=__file__, native_launch=Mock())
            helper = SimpleNamespace(__file__=__file__)
            with patch.object(pipeline, "WORK_ROOT", root), patch.object(pipeline, "load_helper", side_effect=[native, helper]), patch.object(pipeline, "github_file", return_value=({}, AUDIT.encode())), patch.object(pipeline, "checked_owner"), patch.object(pipeline, "publish_snapshot"), patch.object(pipeline, "test_observation") as test:
                result = pipeline.run_pipeline(OPERATOR, NATIVE, hours=0)
            self.assertEqual(result["status"], "timed_out")
            native.native_launch.assert_not_called()
            test.assert_not_called()

    def exercise_pipeline(self, root, eligible):
        source = Path(__file__)
        native = SimpleNamespace(__file__=str(source), launched=False)
        native.native_checks = Mock(return_value={"status": "complete", "verification": {"passed": True, "source_clean": True}})
        native.native_archive = Mock(return_value={"status": "complete", "archives": 1})
        def launch(*args):
            native.launched = True
            return {"status": "running"}
        native.native_launch = Mock(side_effect=launch)
        helper = SimpleNamespace(__file__=str(source), WORK_ROOT=root / "test")
        selection = {"selected_arm": "adapted" if eligible else None, "eligibility": {"adapted": {"eligible": eligible}}, "test_scores_used_for_selection": False}
        def observe(native, commit, directory, name):
            if name == pipeline.SAMPLE_NAME:
                return {"status": "complete", "source_commit": NATIVE}
            return finished(selection) if native.launched else {"status": "not_started"}
        def observe_test(directory, helper, operator, native_commit, released):
            return {"status": "complete", "selected_arm": "adapted", "selection_sha256": "c" * 64} if released else {"status": "not_released"}
        patches = [
            patch.object(pipeline, "WORK_ROOT", root / "pipeline"),
            patch.object(pipeline, "load_helper", side_effect=[native, helper]),
            patch.object(pipeline, "github_file", return_value=({}, AUDIT.encode())),
            patch.object(pipeline, "checked_owner", return_value={"status": "complete"}),
            patch.object(pipeline, "capture_state", return_value={"status": "complete", "counts": {"completed_items": 17334, "failed_attempts": 0}}),
            patch.object(pipeline, "native_observation", side_effect=observe),
            patch.object(pipeline, "test_observation", side_effect=observe_test),
            patch.object(pipeline, "publish_snapshot", side_effect=lambda value, *args: value),
            patch.object(pipeline, "ThreadPoolExecutor", ImmediateExecutor),
            patch.object(pipeline.time, "sleep"),
        ]
        from contextlib import ExitStack
        with ExitStack() as stack:
            mocks = [stack.enter_context(item) for item in patches]
            result = pipeline.run_pipeline(OPERATOR, NATIVE)
        return result, native, mocks[6]

    def test_no_eligible_validation_finishes_without_test_release(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            result, native, test = self.exercise_pipeline(Path(temporary), False)
            self.assertEqual(result["stage"], "no_validation_candidate_eligible")
            self.assertTrue(all(call.args[-1] is False for call in test.call_args_list))
            native.native_launch.assert_called_once()
            self.assertEqual(native.native_launch.call_args.args[0], NATIVE)

    def test_eligible_validation_uses_separate_operator_and_native_pins(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            result, native, test = self.exercise_pipeline(Path(temporary), True)
            self.assertEqual(result["stage"], "eligible_frozen_test_complete")
            self.assertEqual(test.call_args.args[2:4], (OPERATOR, NATIVE))
            self.assertTrue(test.call_args.args[-1])
            self.assertEqual(result["operator_source_commit"], OPERATOR)
            self.assertEqual(result["native_source_commit"], NATIVE)

    def test_known_auth_block_waits_without_models_then_rechecks_clean_source(self) -> None:
        class NativeFailure(RuntimeError):
            pass
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            calls = []
            def checks(commit, directory, allow_format):
                calls.append((commit, allow_format))
                if len(calls) == 1:
                    (directory / "native_checks.stderr").write_text("Reauthentication failed. cannot prompt during non-interactive execution. PRIVATE_TOKEN")
                    raise NativeFailure("private process output must not be returned")
                return {"status": "complete", "verification": {"passed": True, "source_clean": True}}
            native = SimpleNamespace(NativeFailure=NativeFailure, native_checks=Mock(side_effect=checks), native_launch=Mock())
            snapshot = {"operator_source_commit": OPERATOR, "native_source_commit": NATIVE}
            published = []
            def publish(value, *args):
                published.append(json.loads(json.dumps(value)))
            with patch.object(pipeline, "capture_state", return_value={"status": "running", "counts": {"completed_items": 640}}), patch.object(pipeline, "publish_snapshot", side_effect=publish), patch.object(pipeline, "checked_owner") as owner, patch.object(pipeline.time, "sleep") as sleep:
                ready = pipeline.wait_for_owner_checks(native, NATIVE, root, snapshot, "audit evidence", pipeline.time.monotonic(), 16)
            self.assertTrue(ready)
            self.assertEqual(calls, [(NATIVE, False), (NATIVE, False)])
            sleep.assert_called_once_with(30)
            owner.assert_called_once()
            native.native_launch.assert_not_called()
            self.assertEqual(published[0]["status"], "authentication_required")
            self.assertEqual(published[0]["capture"]["counts"]["completed_items"], 640)
            self.assertNotIn("PRIVATE", json.dumps(published))
            self.assertEqual(snapshot["status"], "running")
            self.assertNotIn("authentication", snapshot)

    def test_other_check_failures_do_not_enter_auth_wait_or_launch_models(self) -> None:
        class NativeFailure(RuntimeError):
            pass
        with tempfile.TemporaryDirectory() as temporary:
            def checks(commit, directory, allow_format):
                (directory / "native_checks.stderr").write_text("Connection refused. A login command is not evidence of the observed auth failure.")
                raise NativeFailure("failure")
            native = SimpleNamespace(NativeFailure=NativeFailure, native_checks=checks, native_launch=Mock())
            with patch.object(pipeline.time, "sleep") as sleep:
                with self.assertRaises(pipeline.PipelineFailure):
                    pipeline.wait_for_owner_checks(native, NATIVE, Path(temporary), {}, "audit", pipeline.time.monotonic(), 16)
            sleep.assert_not_called()
            native.native_launch.assert_not_called()

    def test_auth_wait_is_included_in_deadline_and_preserves_local_capture(self) -> None:
        class NativeFailure(RuntimeError):
            pass
        with tempfile.TemporaryDirectory() as temporary:
            clock = [1.0]
            def checks(commit, directory, allow_format):
                (directory / "native_checks.stderr").write_text("Reauthentication failed. cannot prompt during non-interactive execution.")
                raise NativeFailure("failure")
            native = SimpleNamespace(NativeFailure=NativeFailure, native_checks=Mock(side_effect=checks), native_launch=Mock())
            snapshot = {}
            def advance(seconds):
                clock[0] += seconds
            with patch.object(pipeline.time, "monotonic", side_effect=lambda: clock[0]), patch.object(pipeline.time, "sleep", side_effect=advance), patch.object(pipeline, "capture_state", return_value={"status": "running", "counts": {"completed_items": 640}}), patch.object(pipeline, "publish_snapshot"):
                ready = pipeline.wait_for_owner_checks(native, NATIVE, Path(temporary), snapshot, "audit", 0, 0.001)
            self.assertFalse(ready)
            self.assertEqual(snapshot["status"], "timed_out")
            native.native_checks.assert_called_once()
            native.native_launch.assert_not_called()


if __name__ == "__main__":
    unittest.main()
