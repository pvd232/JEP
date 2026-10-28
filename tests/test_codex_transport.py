"""Exercise CA validation and subprocess trust configuration without network calls."""

import hashlib
import json
import os
from pathlib import Path
import ssl
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest import mock

from csts_pilot.codex_transport import codex_environment
from csts_pilot.extraction_comparison import capture_codex


class CodexTransportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        certs = ssl.create_default_context().get_ca_certs(binary_form=True)
        if not certs:
            try:
                import certifi
            except ModuleNotFoundError:
                pass
            else:
                certs = ssl.create_default_context(cafile=certifi.where()).get_ca_certs(binary_form=True)
        if not certs:
            raise unittest.SkipTest("The host has no trusted CA certificate fixture")
        cls.pem = ssl.DER_cert_to_PEM_cert(certs[0])

    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.addCleanup(self.folder.cleanup)
        self.root = Path(self.folder.name)
        self.ca = self.root / "trusted-ca.pem"
        self.ca.write_text(self.pem)

    def test_explicit_ca_populates_only_missing_setting_without_environment_mutation(self):
        original = {"CODEX_CA_CERTIFICATE": str(self.ca), "UNCHANGED": "yes"}
        before = dict(os.environ)
        environment, receipt = codex_environment(original)
        self.assertEqual(environment["SSL_CERT_FILE"], str(self.ca.resolve()))
        self.assertNotIn("SSL_CERT_FILE", original)
        self.assertEqual(dict(os.environ), before)
        self.assertEqual(receipt["trust_source"], "explicit")
        self.assertEqual(receipt["bundles"][0]["sha256"], hashlib.sha256(self.ca.read_bytes()).hexdigest())

    def test_ssl_setting_is_used_when_codex_setting_is_absent(self):
        environment, _ = codex_environment({"SSL_CERT_FILE": str(self.ca)})
        self.assertEqual(environment["CODEX_CA_CERTIFICATE"], str(self.ca.resolve()))

    def test_distinct_explicit_trust_files_are_preserved(self):
        other = self.root / "other-ca.pem"
        other.write_text(self.pem)
        environment, receipt = codex_environment({"CODEX_CA_CERTIFICATE": str(self.ca), "SSL_CERT_FILE": str(other)})
        self.assertEqual(environment["SSL_CERT_FILE"], str(other.resolve()))
        self.assertEqual(len(receipt["bundles"]), 2)

    def test_certifi_default_validates_and_records_the_bundle(self):
        with mock.patch.dict(sys.modules, {"certifi": SimpleNamespace(where=lambda: str(self.ca))}):
            environment, receipt = codex_environment({})
        self.assertEqual(environment["CODEX_CA_CERTIFICATE"], environment["SSL_CERT_FILE"])
        self.assertEqual(receipt["trust_source"], "certifi")
        self.assertEqual(receipt["tls_verification"], "enabled")

    def test_missing_certifi_uses_verified_os_defaults(self):
        with mock.patch.dict(sys.modules, {"certifi": None}):
            environment, receipt = codex_environment({"UNCHANGED": "yes"})
        self.assertEqual(environment, {"UNCHANGED": "yes"})
        self.assertEqual(receipt, {"tls_verification": "enabled", "trust_source": "os_default", "bundles": []})

    def test_bad_explicit_files_fail_even_if_the_other_file_is_valid(self):
        invalid = self.root / "invalid.pem"
        invalid.write_text("not a certificate")
        for value in ("", str(self.root / "missing.pem"), str(invalid)):
            with self.subTest(value=value), self.assertRaises(ValueError):
                codex_environment({"CODEX_CA_CERTIFICATE": str(self.ca), "SSL_CERT_FILE": value})

    def test_capture_forwards_the_same_verified_environment_to_both_children(self):
        capture = self.root / "capture"
        capture.mkdir()
        (capture / "response.json").write_text(json.dumps({"payload": "ok"}))
        process = mock.Mock(returncode=0)
        config = {"model": "gpt-6.1-sol", "reasoning_effort": "max", "timeout_seconds": 5}
        with mock.patch.dict(os.environ, {"CODEX_CA_CERTIFICATE": str(self.ca)}, clear=True), \
             mock.patch("csts_pilot.extraction_comparison.subprocess.run", return_value=SimpleNamespace(stdout="test-cli")) as version, \
             mock.patch("csts_pilot.extraction_comparison.subprocess.Popen", return_value=process) as launch, \
             mock.patch("csts_pilot.extraction_comparison.completed_codex", return_value="ok"):
            self.assertEqual(capture_codex(capture, "fixed prompt", config, "/fake/codex", self.root), "ok")
            self.assertNotIn("SSL_CERT_FILE", os.environ)
        self.assertEqual(version.call_args.kwargs["env"], launch.call_args.kwargs["env"])
        self.assertEqual(launch.call_args.kwargs["env"]["SSL_CERT_FILE"], str(self.ca.resolve()))
        command = launch.call_args.args[0]
        self.assertIn("--no-daemon", command)
        self.assertIn('model_reasoning_effort="max"', command)
        self.assertEqual(command[command.index("--model") + 1], "gpt-6.1-sol")
        runtime = json.loads((capture / "runtime.json").read_text())
        self.assertEqual(runtime["tls"]["tls_verification"], "enabled")
        process.communicate.assert_called_once_with("fixed prompt", timeout=5)

    def test_invalid_ca_prevents_any_cli_subprocess(self):
        with mock.patch.dict(os.environ, {"SSL_CERT_FILE": str(self.root / "missing")}, clear=True), \
             mock.patch("csts_pilot.extraction_comparison.subprocess.run") as version, \
             mock.patch("csts_pilot.extraction_comparison.subprocess.Popen") as launch:
            with self.assertRaises(ValueError):
                capture_codex(self.root, "fixed", {}, "/fake/codex", self.root)
        version.assert_not_called()
        launch.assert_not_called()


if __name__ == "__main__":
    unittest.main()
