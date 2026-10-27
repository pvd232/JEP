"""Check archival scope and completion on small metadata fixtures."""

import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from scripts.archive_proposition_indicative import checked_payload


class IndicativeArchiveTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name).resolve()
        self.directory = self.root / "indicative_results" / "short_8_25_v41"
        self.directory.mkdir(parents=True)
        self.source = "4" * 40
        settings = {
            "publication_destination": {
                "owner": "pvd232",
                "workspace": "jep_csts_joint_20261021",
            },
            "splits": {},
        }
        for name in (
            "training",
            "validation",
            "answers",
            "provenance",
            "audit_gate",
            "report_cohorts",
            "baseline_predictions",
        ):
            path = self.root / f"{name}.json"
            path.write_text("[]")
            spec = {
                "path": path.name,
                "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            }
            if name in ("training", "validation"):
                settings["splits"][name] = spec
            else:
                settings[name] = spec
        self.settings = self.root / "settings.json"
        self.settings.write_text(json.dumps(settings))
        self.settings_sha = hashlib.sha256(self.settings.read_bytes()).hexdigest()
        (self.directory / "summary.json").write_text(
            json.dumps(
                {"status": "complete", "provenance": {"source_commit": self.source}}
            )
        )
        (self.directory / "results.json").write_text(
            json.dumps(
                {
                    "protocol": {
                        "source_commit": self.source,
                        "settings_sha256": self.settings_sha,
                    }
                }
            )
        )
        for name in ("indicative_report.json", "indicative_report.md"):
            (self.directory / name).write_text("completed report")
        for arm in ("ratings", "evidence"):
            folder = self.directory / arm
            folder.mkdir()
            (folder / "validation_predictions.json").write_text("[]")
            for phase in ("pretrain", "ratings"):
                for kind in ("model.pt", "optimizer.pt", "trace.json"):
                    (folder / f"{phase}_{kind}").write_bytes(b"small fixture")

    def payload(self):
        return checked_payload(
            self.root, self.directory, self.settings, self.source, self.settings_sha
        )

    def test_completed_files_and_frozen_inputs_are_scoped_without_cloud_access(self):
        root, files, destination = self.payload()
        self.assertEqual(root, self.root)
        self.assertEqual(len(files), 26)
        self.assertEqual(destination.workspace, "jep_csts_joint_20261021")
        self.assertTrue(all(path.is_relative_to(self.root) for path in files.values()))
        self.assertTrue(
            any(name.endswith("evidence/ratings_optimizer.pt") for name in files)
        )

    def test_unfinished_or_missing_report_is_rejected(self):
        (self.directory / "indicative_report.md").unlink()
        with self.assertRaisesRegex(ValueError, "reports are required"):
            self.payload()
        (self.directory / "indicative_report.md").write_text("report")
        (self.directory / "summary.json").write_text(json.dumps({"status": "running"}))
        with self.assertRaisesRegex(ValueError, "must be complete"):
            self.payload()

    def test_changed_source_or_frozen_input_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "exact execution source"):
            checked_payload(
                self.root, self.directory, self.settings, "5" * 40, self.settings_sha
            )
        (self.root / "training.json").write_text("changed")
        with self.assertRaisesRegex(ValueError, "frozen source input changed"):
            self.payload()


if __name__ == "__main__":
    unittest.main()
