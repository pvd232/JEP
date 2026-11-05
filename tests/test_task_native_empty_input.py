"""Empty source strings are valid data; this never fabricates annotations."""
import hashlib
import json
from pathlib import Path
import unittest

from csts_pilot.native_adapter.schema import compile_condition, native_prompt, bounded_input, verify_bound_input
from csts_pilot.native_adapter.normalize import normalize_native, normalize_stages
from csts_pilot.native_adapter.task_recipe import CONTRACT_RECIPE
from csts_pilot.native_adapter.know_refinement import KNOW_REFINEMENT

PROJECT_ROOT=Path(__file__).resolve().parents[1]
ROOT=Path(__file__).resolve().parent / "fixtures/native_adapter_empty_input"


def prompt_options(model):
    return {"profile":"positive_anchor", **({"prompt_profile":KNOW_REFINEMENT} if model=="knowcoder" else {})}


class EmptyInputTest(unittest.TestCase):
    def test_empty_and_whitespace_source_are_literal_data_in_existing_renderers(self):
        for condition in ("type of animal","type of food","location of person","action of dog"):
            plan=compile_condition(condition,contract_recipe=CONTRACT_RECIPE)
            for model in ("knowcoder","gollie"):
                for passage in ("", " ", " \t\n"):
                    with self.subTest(condition=condition,model=model,passage=repr(passage)):
                        marker="__INDEPENDENT_SOURCE_SENTINEL__"
                        comparison=native_prompt(plan,model,marker,**prompt_options(model))
                        self.assertEqual(comparison.count(json.dumps(marker)),1)
                        expected=comparison.replace(json.dumps(marker),json.dumps(passage))
                        actual=native_prompt(plan,model,passage,**prompt_options(model))
                        self.assertEqual(actual,expected)

    def test_empty_bounded_input_verifies_and_source_drift_still_rejects(self):
        plan=compile_condition("type of animal",contract_recipe=CONTRACT_RECIPE)
        for model in ("knowcoder","gollie"):
            # This is a deterministic unit tokenizer stub; dispatch retains the
            # existing actual-tokenizer requirement and unchanged budget checks.
            counter=lambda prompt:123
            bound=bounded_input(plan,model,"",counter,**prompt_options(model))
            self.assertTrue(verify_bound_input(bound,plan,"",counter))
            with self.assertRaisesRegex(ValueError,"identity changed"):
                verify_bound_input(bound,plan," ",counter)

    def test_empty_output_normalizes_without_certifying_support_or_coverage(self):
        plan=compile_condition("type of animal",contract_recipe=CONTRACT_RECIPE)
        for model in ("knowcoder","gollie"):
            for passage in ("", " \t\n"):
                with self.subTest(model=model,passage=repr(passage)):
                    bound=bounded_input(plan,model,passage,lambda _:123,**prompt_options(model))
                    self.assertIn(json.dumps(passage),bound["prompt"])
                    payload=" results = []" if model=="knowcoder" else "[]"
                    graph=normalize_native(payload,plan,model,passage,profile="positive_anchor")
                    self.assertEqual(graph["status"],"not_specified")
                    self.assertEqual(graph["entities"],[])
                    self.assertEqual(graph["relations"],[])
                    self.assertFalse(graph["coverage_validated"])
                    self.assertFalse(graph["semantic_support_validated"])
                    self.assertEqual(graph["requested_facet_status_kind"],"candidate_prediction")

    def test_composite_empty_stages_are_complete_and_remain_unvalidated(self):
        for condition in ("type of hobby","object's purpose","person"):
            plan=compile_condition(condition,contract_recipe=CONTRACT_RECIPE)
            self.assertTrue(plan.get("stage_contract"))
            for model in ("knowcoder","gollie"):
                payloads={stage:"[]" for stage in plan["stage_contract"]}
                graph=normalize_stages(payloads,plan,model,"",profile="positive_anchor")
                self.assertEqual(graph["status"],"not_specified")
                self.assertFalse(graph["semantic_support_validated"])
                self.assertEqual(set(graph["stage_inputs_sha256"]),set(payloads))
                with self.assertRaisesRegex(ValueError,"every declared"):
                    normalize_stages({},plan,model,"",profile="positive_anchor")

    def test_nonempty_mentions_cannot_ground_empty_or_whitespace_source(self):
        plan=compile_condition("type of animal",contract_recipe=CONTRACT_RECIPE)
        for model in ("knowcoder","gollie"):
            for passage in ("", " \t\n"):
                with self.subTest(model=model,passage=repr(passage)),self.assertRaisesRegex(ValueError,"not an exact source span"):
                    normalize_native('[Animal("dog")]',plan,model,passage,profile="positive_anchor")

    def test_nonstring_sources_still_reject_before_rendering_or_normalization(self):
        plan=compile_condition("type of animal",contract_recipe=CONTRACT_RECIPE)
        for model in ("knowcoder","gollie"):
            for passage in (None,0,False,[],{},b""):
                with self.subTest(model=model,value=repr(passage)):
                    with self.assertRaisesRegex(ValueError,"string passage"):
                        native_prompt(plan,model,passage,**prompt_options(model))
                    with self.assertRaisesRegex(ValueError,"string source passage"):
                        normalize_native("[]",plan,model,passage,profile="positive_anchor")

    def test_all_eighteen_public_nonempty_generation_strings_are_unchanged(self):
        rows=json.loads((ROOT/"know-refinement-requests.json").read_text())["items"]
        self.assertEqual(len(rows),9)
        for row in rows:
            plan=compile_condition(row["condition"],contract_recipe=CONTRACT_RECIPE)
            self.assertEqual(plan,row["plan"])
            for model in ("knowcoder","gollie"):
                expected=row["requests"][model]
                prompt=native_prompt(plan,model,row["passage"],profile=expected["profile"],prompt_profile=expected["prompt_profile"])
                self.assertEqual(prompt,expected["prompt"])
                self.assertEqual(hashlib.sha256(prompt.encode()).hexdigest(),expected["prompt_sha256"])

    def test_runtime_source_delta_contains_only_two_passage_validation_guards(self):
        for name,old,new in (
            ("schema.py",'if not isinstance(passage, str) or not passage.strip():\n        raise ValueError("A nonempty passage is required")','if not isinstance(passage, str):\n        raise ValueError("A string passage is required")'),
            ("normalize.py",'if not isinstance(passage, str) or not passage.strip():\n        raise ValueError("A nonempty source passage is required")','if not isinstance(passage, str):\n        raise ValueError("A string source passage is required")'),
        ):
            before=(ROOT/"tests/fixtures"/("pre_empty_input_"+name)).read_text()
            self.assertEqual(before.count(old),1)
            self.assertEqual((PROJECT_ROOT/"csts_pilot/native_adapter"/name).read_text(),before.replace(old,new))


if __name__=="__main__":unittest.main()
