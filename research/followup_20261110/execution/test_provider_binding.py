"""Observe JEP's binding to the shared provider without allocating cloud resources."""

import ast
import base64
import gzip
import hashlib
import importlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from typing import Any
from unittest import mock

HERE = Path(__file__).resolve().parent
SOURCE = HERE / "controller_extracted.py"
if not SOURCE.exists():
    SOURCE = HERE / "controller.py"
CONFIG = json.loads((HERE / "gcp_provider.json").read_text())
SCRIPTS = Path(
    os.environ.get("JEP_PROVIDER_SCRIPTS") or str(CONFIG["provider_scripts"])
)
sys.path.insert(0, str(SCRIPTS))
provider = importlib.import_module("gcp_l4_provider")


class ProviderBindingTests(unittest.TestCase):
    """Preserve original JEP outputs and startup payloads through the shared boundary."""

    def setUp(self):
        """Create an isolated owned run and acquire the provider writer lock."""
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.run_dir = Path(self.temp.name)
        self.config = dict(CONFIG)
        self.config.update(
            provider_scripts=str(SCRIPTS),
            worktree=str(self.run_dir),
            run_dir=str(self.run_dir),
            design_path=str(self.run_dir / "design.json"),
            project="atlas-science",
            resource_name="atlas-worker",
            labels={"task": "atlas-job"},
            cloud_project="fixture",
            service_account="worker@atlas-science.iam.gserviceaccount.com",
            source_image="projects/example/global/images/pinned-image",
            workload_bucket="fixture",
        )
        provider.configure(self.config)
        self.lock = provider.execution_lock()
        self.lock.__enter__()
        self.addCleanup(self.lock.__exit__, None, None, None)
        self.record = dict(
            id="17",
            disk_id="18",
            zone="asia-east1-a",
            deleted=True,
            cleanup_verified_at="verified",
            name="atlas-worker",
        )
        self.write("state.json", dict(phase="inference_retained", gpu={"id": "17"}))
        self.write(
            "resources.json",
            dict(
                project="atlas-science",
                allocations=[self.record],
                intents=[],
                gpu_seconds=0,
            ),
        )
        (self.run_dir / "gpu_return.tar.gz").write_bytes(b"retained worker bytes")
        self.write(
            "collection.json",
            dict(
                bundle_sha256=hashlib.sha256(b"retained worker bytes").hexdigest(),
                files={},
            ),
        )

    def write(self, name, value):
        """Write one fixture record into the isolated run directory."""
        (self.run_dir / name).write_text(json.dumps(value))

    def function(self, name) -> Any:
        """Compile an actual adapter function with isolated workload bindings."""
        tree = ast.parse(SOURCE.read_text())
        node = next(
            n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == name
        )
        module = ast.Module(body=[node], type_ignores=[])
        namespace: dict[str, Any] = dict(
            RUN=self.run_dir,
            NAME="atlas-worker",
            provider=provider,
            json=json,
            hashlib=hashlib,
            base64=base64,
            gzip=gzip,
            HERE=HERE,
            provider_scripts=SCRIPTS,
        )
        exec(compile(ast.fix_missing_locations(module), str(SOURCE), "exec"), namespace)
        return namespace[name]

    def test_cleaned_legacy_output_is_reusable_without_cloud_calls(self):
        """Upgrade a verified original receipt after worker cleanup and reporting failure."""
        original = (self.run_dir / "collection.json").read_bytes()
        with mock.patch.object(provider, "compute") as cloud:
            self.function("upgrade_legacy_collection")()
            cloud.assert_not_called()
        self.assertEqual(
            json.loads((self.run_dir / "collection.json").read_text())["vm_id"], "17"
        )
        self.assertEqual(
            (self.run_dir / "collection.pre-provider.json").read_bytes(), original
        )
        provider.verify_collection(self.record)

    def test_live_legacy_output_checks_recorded_resource_identities(self):
        """Bind an original receipt only after verifying its surviving VM and disk."""
        self.record["deleted"] = False
        self.write(
            "resources.json",
            dict(
                project="atlas-science",
                allocations=[self.record],
                intents=[],
                gpu_seconds=0,
            ),
        )

        def compute(path, **kwargs):
            """Return the exact recorded simulated worker and disk."""
            if "/disks/" in path:
                return {"id": "18"}
            return dict(id="17", name="atlas-worker", labels={"task": "atlas-job"})

        with mock.patch.object(provider, "compute", side_effect=compute):
            self.function("upgrade_legacy_collection")()
        provider.verify_collection(self.record)

    def test_ambiguous_legacy_worker_binding_preserves_receipt(self):
        """Preserve the original receipt when allocation identity is ambiguous."""
        self.write(
            "resources.json",
            dict(
                project="atlas-science",
                allocations=[self.record, self.record],
                intents=[],
                gpu_seconds=0,
            ),
        )
        original = (self.run_dir / "collection.json").read_bytes()
        with self.assertRaisesRegex(RuntimeError, "unambiguous"):
            self.function("upgrade_legacy_collection")()
        self.assertEqual(original, (self.run_dir / "collection.json").read_bytes())

    def test_contended_resume_preserves_the_existing_owner_state(self):
        """Run the real adapter in another process while its execution lock is held."""
        shutil.copy2(SOURCE, self.run_dir / "controller.py")
        self.write("gcp_provider.json", self.config)
        before = (self.run_dir / "state.json").read_bytes()
        result = subprocess.run(
            [sys.executable, str(self.run_dir / "controller.py"), "--resume"],
            capture_output=True,
            text=True,
            timeout=20,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("healthy_owner_preserved", result.stdout)
        self.assertEqual(before, (self.run_dir / "state.json").read_bytes())
        self.assertFalse((self.run_dir / "events.jsonl").exists())

    def test_startup_preserves_the_exact_workload_payload(self):
        """Round-trip the actual compressed startup metadata through its payload bytes."""
        payload = dict(
            tasks=[dict(text="fixed harm", condition="explicit criterion")],
            encoder={"revision": "pinned"},
        )
        metadata = self.function("startup")(payload)
        chunks = [x["value"] for x in metadata if x["key"].startswith("moral-payload-")]
        restored = json.loads(gzip.decompress(base64.b64decode("".join(chunks))))
        self.assertEqual(restored, payload)


if __name__ == "__main__":
    unittest.main()
