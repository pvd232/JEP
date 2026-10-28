"""Check matched scheduling and the label-free batch response contract."""

import json
import unittest

from csts_pilot.extraction_formats import POLICY, STRUCTURED_CONTRACT, JSON_FORMAT, PYTHON_FORMAT, PROPOSITION_FORMAT
from csts_pilot.format_batches import ARMS, batch_schema, build_batch_prompt, canonical, schedule_batches, source_groups


def fixture():
    sources, pairs = [], []
    for group in range(12):
        condition = (" Color of DOGS " if group % 3 == 0 else "color of dogs" if group % 3 == 1 else "number of animals")
        a, b = f"source-{group}-a", f"source-{group}-b"
        sources.extend([{"id": a, "passage": f"Passage A {group}.", "condition": condition},
                        {"id": b, "passage": f"Passage B {group}.", "condition": condition}])
        pairs.append({"id": f"pair-{group}", "source_a": a, "source_b": b, "group_id": f"group-{group}"})
    return sources, pairs


class BatchTests(unittest.TestCase):
    def test_schedule_is_order_independent_complete_and_group_condition_isolated(self):
        sources, pairs = fixture()
        batches = schedule_batches(sources, pairs)
        self.assertEqual(batches, schedule_batches(list(reversed(sources)), list(reversed(pairs))))
        self.assertEqual(sorted(identity for b in batches for identity in b["source_ids"]), sorted(s["id"] for s in sources))
        groups = source_groups(sources, pairs)
        by_id = {s["id"]: s for s in sources}
        for batch in batches:
            ids = batch["source_ids"]
            self.assertLessEqual(len(ids), 16)
            self.assertEqual(len({groups[i] for i in ids}), len(ids))
            self.assertEqual(len({canonical(by_id[i]["condition"]) for i in ids}), len(ids))

    def test_inconsistent_or_missing_groups_and_labels_are_rejected(self):
        sources, pairs = fixture()
        changed = [*pairs, dict(pairs[0], id="other", group_id="wrong")]
        with self.assertRaisesRegex(ValueError, "inconsistent"):
            schedule_batches(sources, changed)
        with self.assertRaisesRegex(ValueError, "Every source"):
            schedule_batches(sources, pairs[:-1])
        with self.assertRaisesRegex(ValueError, "label-free"):
            schedule_batches(sources, [dict(pairs[0], rating=4), *pairs[1:]])

    def test_schema_requires_every_exact_id_and_payload_only(self):
        schema = batch_schema(["a", "b"])
        self.assertEqual(schema["required"], ["records"])
        self.assertFalse(schema["additionalProperties"])
        records = schema["properties"]["records"]
        self.assertEqual(records["required"], ["a", "b"])
        self.assertFalse(records["additionalProperties"])
        self.assertEqual(records["properties"]["a"], {"type": "object", "properties": {"payload": {"type": "string"}}, "required": ["payload"], "additionalProperties": False})
        with self.assertRaises(ValueError):
            batch_schema(["a", "a"])

    def test_prompts_reuse_exact_format_policy_and_exclude_group_labels(self):
        sources, _ = fixture()
        for arm, instruction in zip(ARMS, (PROPOSITION_FORMAT, JSON_FORMAT, PYTHON_FORMAT)):
            prompt = build_batch_prompt(sources[:1], arm)
            self.assertIn(POLICY, prompt)
            self.assertIn(instruction, prompt)
            if arm != "gpt_propositions":
                self.assertIn(STRUCTURED_CONTRACT, prompt)
            data = json.loads(prompt.split("CASES:\n", 1)[1])
            self.assertEqual(data, sources[:1])
            self.assertNotIn("group-0", prompt)
            self.assertIn("ONLY that case's own passage and condition", prompt)
        with self.assertRaisesRegex(ValueError, "only nonempty"):
            build_batch_prompt([dict(sources[0], group_id="group-0")], ARMS[0])

    def test_common_source_order_is_not_changed_by_format(self):
        sources, _ = fixture()
        selected = sources[3:5]
        cases = [json.loads(build_batch_prompt(selected, arm).split("CASES:\n", 1)[1]) for arm in ARMS]
        self.assertEqual(cases, [selected, selected, selected])


if __name__ == "__main__":
    unittest.main()
