"""Run source-selection and cache-safety contracts without GPU/VIPER packages.

Only the named production functions are loaded from their ASTs. Their bodies
are unchanged; this keeps these CPU contracts runnable in the review workspace.
Native encoder behavior is shared with proposition_inputs and tested there.
"""

import ast
import copy
import fcntl
import hashlib
import json
import math
import os
import shutil
import tempfile
import time
import unittest
from pathlib import Path
from types import SimpleNamespace
from typing import Any

from jep_pilot.loaders import load_json

ROOT = Path(__file__).resolve().parents[1]


def load_functions():
    namespace = {
        "Any": Any,
        "Path": Path,
        "hashlib": hashlib,
        "json": json,
        "math": math,
        "os": os,
        "time": time,
        "shutil": shutil,
        "fcntl": fcntl,
        "load_json": load_json,
    }
    sources = {
        "data.py": {"canonical"},
        "answers.py": {"answer_id"},
        "baseline_models.py": {"validate_rows"},
        "proposition_capture.py": {"validate_inputs", "checked_records"},
        "proposition_inputs.py": {"validate_replacements"},
        "convergence.py": {"file_sha256", "write_json"},
        "proposition_sample.py": {
            "unique_records",
            "prepare_sample",
            "release_verified_model_cache",
        },
    }
    import unicodedata

    namespace["unicodedata"] = unicodedata
    for filename, names in sources.items():
        tree = ast.parse((ROOT / "csts_pilot" / filename).read_text())
        selected = [
            node
            for node in tree.body
            if isinstance(node, ast.FunctionDef) and node.name in names
        ]
        if {node.name for node in selected} != names:
            raise AssertionError(f"Missing production function in {filename}.")
        for node in selected:
            if node.decorator_list:
                raise AssertionError(
                    "Contracts must not silently strip a native decorator."
                )
        exec(  # noqa: S102 -- only statically selected repository contract functions
            compile(ast.Module(body=selected, type_ignores=[]), filename, "exec"),
            namespace,
        )
    namespace["frozen"] = SimpleNamespace(
        validate_replacements=namespace["validate_replacements"]
    )
    namespace["ARMS"] = ("old_spans", "checked_generated_v1")
    return namespace


class SelectionContracts(unittest.TestCase):
    def setUp(self):
        self.functions = load_functions()
        directory = ROOT / "training_outputs/proposition_audit"
        files = {
            "source_sample": "proposition_blind_sample.json",
            "pair_mapping": "proposition_audit_pair_mapping.json",
            "old_records": "proposition_old_audit120.json",
            "generated_records": "proposition_generated_audit120.json",
            "variant_mapping": "proposition_variant_mapping.json",
            "judgments_left": "proposition_judgments_left.json",
            "judgments_right": "proposition_judgments_right.json",
            "references_left": "proposition_reference_left.json",
            "references_right": "proposition_reference_right.json",
            "capture_manifest": "proposition_capture_audit_manifest.json",
        }
        self.audits = {
            key: json.loads((directory / filename).read_text())
            for key, filename in files.items()
        }
        items = {row["id"]: row for row in self.audits["source_sample"]}
        # Synthetic labels are deliberately unrelated to fidelity decisions.
        self.rows = []
        for index, (group, left, right) in enumerate(
            reversed(self.audits["pair_mapping"])
        ):
            a, b = items[left], items[right]
            self.assertEqual(a["condition"], b["condition"])
            self.rows.append(
                {
                    "row_id": f"sample-{index}",
                    "pair_id": group,
                    "group_id": group,
                    "sentence1": a["passage"],
                    "sentence2": b["passage"],
                    "condition": a["condition"],
                    "rating": 1.0 if index % 2 else 5.0,
                    "target": 0.0 if index % 2 else 1.0,
                }
            )

    def prepare(self, audits=None, rows=None):
        return self.functions["prepare_sample"](
            self.rows if rows is None else rows,
            self.audits if audits is None else audits,
        )

    def test_same_sixty_pairs_and_conditions_with_expected_policy_coverage(self):
        original, changed, audit = self.prepare()
        self.assertEqual(original, self.rows)
        self.assertEqual(len(audit["records"]), 120)
        for arm, expected, sides in (
            ("old_spans", {"both": 28, "one": 19, "neither": 13}, 75),
            ("checked_generated_v1", {"both": 42, "one": 14, "neither": 4}, 98),
        ):
            self.assertEqual(audit["coverage"][arm]["comparison_coverage"], expected)
            self.assertEqual(audit["coverage"][arm]["accepted_side_occurrences"], sides)
            self.functions["validate_replacements"](original, changed[arm])
        reversed_labels = [
            dict(row, rating=6 - row["rating"], target=1 - row["target"])
            for row in self.rows
        ]
        _, changed_labels, label_audit = self.prepare(rows=reversed_labels)
        self.assertEqual(audit["records"], label_audit["records"])
        for arm in changed:
            self.assertEqual(
                [(r["sentence1"], r["sentence2"]) for r in changed[arm]],
                [(r["sentence1"], r["sentence2"]) for r in changed_labels[arm]],
            )

    def test_blind_variant_lookup_rejection_fallback_and_no_reference_substitution(
        self,
    ):
        _, _, audit = self.prepare()
        old_audit_rejections = 0
        new_answer_rejections = 0
        for record in audit["records"]:
            old_variant = next(
                key for key, value in record["blind_variants"].items() if value == "old"
            )
            old = record["old_record"]
            if (
                old["status"] == "answered"
                and not record["blind_judgments"][old_variant]["fully_faithful"]
            ):
                old_audit_rejections += 1
                self.assertEqual(
                    record["selected_inputs"]["old_spans"]["passage"], old["answer"]
                )
            selected = record["selected_inputs"]["checked_generated_v1"]
            new = record["generated_v1_record"]
            if (
                record["generated_v1_passes_blind_fidelity"]
                and new["status"] == "answered"
            ):
                self.assertEqual(selected["passage"], new["answer"])
            else:
                self.assertFalse(selected["uses_answer"])
                self.assertEqual(selected["passage"], record["passage"])
                new_answer_rejections += new["status"] == "answered"
        self.assertGreater(old_audit_rejections, 0)
        self.assertEqual(new_answer_rejections, 2)

    def test_missing_duplicate_changed_source_and_nonboolean_judgments_rejected(self):
        for mutation in ("missing", "duplicate", "source", "judgment"):
            with self.subTest(mutation=mutation):
                audits = copy.deepcopy(self.audits)
                if mutation == "missing":
                    audits["generated_records"].pop()
                elif mutation == "duplicate":
                    audits["judgments_left"].append(audits["judgments_left"][0])
                elif mutation == "source":
                    audits["source_sample"][0]["condition"] += " changed"
                else:
                    audits["judgments_left"][0]["fully_faithful"] = "true"
                with self.assertRaises(ValueError):
                    self.prepare(audits=audits)


class CacheContracts(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.functions = load_functions()
        self.data = b"immutable parent model contract bytes"
        self.digest = hashlib.sha256(self.data).hexdigest()
        self.functions["MODEL_SHA256"] = self.digest
        self.original = self.root / "parent/.viper/store/sealed/model.pt"
        self.original.parent.mkdir(parents=True)
        self.original.write_bytes(self.data)
        self.cache = self.root / ".viper/cache/verified-objects" / self.digest
        self.cache.parent.mkdir(parents=True)
        self.cache.write_bytes(self.data)
        self.queue = self.root / ".viper/publication_queue"
        self.queue.mkdir(parents=True)
        (self.queue / "job.json").write_text(json.dumps({"status": "published"}))
        self.receipt = self.root / "results/release.json"

    def release(self):
        return self.functions["release_verified_model_cache"](
            self.root, self.original, self.receipt, wait_seconds=0
        )

    def test_deletes_only_exact_duplicate_and_preserves_immutable_original(self):
        result = self.release()
        self.assertEqual(result["status"], "deleted_duplicate")
        self.assertFalse(self.cache.exists())
        self.assertEqual(self.original.read_bytes(), self.data)
        self.assertEqual(json.loads(self.receipt.read_text())["bytes"], len(self.data))

    def test_wrong_hash_hardlink_symlink_ancestor_and_pending_publication_preserved(
        self,
    ):
        for mutation in ("hash", "hardlink", "symlink", "pending"):
            # Each subcase has an independent cache and publication state.
            with (
                self.subTest(mutation=mutation),
                tempfile.TemporaryDirectory() as directory,
            ):
                root = Path(directory)
                candidate = root / ".viper/cache/verified-objects" / self.digest
                candidate.parent.mkdir(parents=True)
                candidate.write_bytes(self.data)
                queue = root / ".viper/publication_queue"
                queue.mkdir(parents=True)
                (queue / "job.json").write_text(
                    json.dumps(
                        {
                            "status": "pending"
                            if mutation == "pending"
                            else "published"
                        }
                    )
                )
                if mutation == "hash":
                    candidate.write_bytes(b"changed model bytes")
                elif mutation == "hardlink":
                    candidate.unlink()
                    os.link(self.original, candidate)
                elif mutation == "symlink":
                    moved = root / "actual-cache"
                    candidate.parent.rename(moved)
                    candidate.parent.symlink_to(moved, target_is_directory=True)
                result = self.functions["release_verified_model_cache"](
                    root, self.original, root / "receipt.json", wait_seconds=0
                )
                self.assertNotEqual(result["status"], "deleted_duplicate")
                self.assertTrue(candidate.exists())
                self.assertEqual(self.original.read_bytes(), self.data)


if __name__ == "__main__":
    unittest.main()
