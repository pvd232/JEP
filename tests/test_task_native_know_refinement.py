"""Know-only completeness/palette illustrations with original Go/NER/Color invariants."""
import hashlib
import json
from pathlib import Path
import re
import unittest
from unittest.mock import patch

from csts_pilot.native_adapter.schema import compile_condition,bounded_input,native_prompt,verify_bound_input
from csts_pilot.native_adapter.task_recipe import CONTRACT_RECIPE,SPATIAL_PALETTE
from csts_pilot.native_adapter.know_refinement import KNOW_REFINEMENT,DATA_SHA256
from csts_pilot.native_adapter.normalize import normalize_native

ROOT = Path(__file__).resolve().parent / "fixtures/native_adapter_final"


class KnowRefinementTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base=json.loads((ROOT/'tests/fixtures/base_task_contract_requests.json').read_text())['items']
        cls.data=json.loads((ROOT/'native_adapter/know_refinement_demonstrations.json').read_text())

    def test_all_go_prompts_stay_byte_identical_and_go_refinement_is_rejected(self):
        for row in self.base:
            with self.subTest(case=row['case_id']):
                p=compile_condition(row['condition'],contract_recipe=CONTRACT_RECIPE)
                self.assertEqual(native_prompt(p,'gollie',row['passage'],profile='positive_anchor'),row['requests']['gollie']['prompt'])
        row=self.base[0]
        with self.assertRaisesRegex(ValueError,'only for Know'):
            native_prompt(row['plan'],'gollie',row['passage'],profile='positive_anchor',prompt_profile=KNOW_REFINEMENT)

    def test_know_ner_and_color_prompts_and_original2048_cap_are_unchanged(self):
        for row in self.base:
            route=row['requests']['knowcoder']['prompt_profile_identity']['recipe_route']
            if route not in {'preserved_zero_shot_ner','preserved_fixed_re_family_one_shot'}:continue
            with self.subTest(case=row['case_id']):
                b=bounded_input(row['plan'],'knowcoder',row['passage'],lambda _:500,profile='positive_anchor',prompt_profile=KNOW_REFINEMENT)
                self.assertEqual(b['prompt'],row['requests']['knowcoder']['prompt'])
                self.assertIsNone(b['prompt_profile_identity']['active_refinement'])
                self.assertEqual(b['context_limit'],2048)

    def test_every_spatial_constructor_has_one_fixed_literal_illustration(self):
        example=self.data['spatial_palette']
        self.assertEqual(example['illustrated_constructors'],[row[0] for row in SPATIAL_PALETTE])
        p=compile_condition('location of entity',contract_recipe=CONTRACT_RECIPE)
        evidence=normalize_native(example['know_output'],p,'knowcoder',example['sentence'],profile='positive_anchor')
        self.assertEqual(len(evidence['relations']),len(SPATIAL_PALETTE))
        self.assertTrue(all(not edge['predicate_argument_association_validated'] for edge in evidence['relations']))
        prefixes=[]
        for condition in ('location of person','location of food','location of zebras standing'):
            target=compile_condition(condition,contract_recipe=CONTRACT_RECIPE)
            text=native_prompt(target,'knowcoder','An independent target source.',profile='positive_anchor',prompt_profile=KNOW_REFINEMENT)
            prefixes.append(text.split('\nInput:\n',2)[:2])
        self.assertTrue(all(value==prefixes[0] for value in prefixes))

    def test_spatial4096_is_explicit_and_does_not_expand_the_original_profile(self):
        row=next(item for item in self.base if item['case_id']=='spatial_qualifier')
        b=bounded_input(row['plan'],'knowcoder',row['passage'],lambda _:3500,profile='positive_anchor',prompt_profile=KNOW_REFINEMENT)
        self.assertEqual(b['context_limit'],4096)
        self.assertIn('max_position_embeddings4096',b['prompt_profile_identity']['context_bound_basis'])
        self.assertTrue(verify_bound_input(b,row['plan'],row['passage'],lambda _:3500))
        with self.assertRaisesRegex(ValueError,'no truncation'):
            bounded_input(row['plan'],'knowcoder',row['passage'],lambda _:3500,profile='positive_anchor')
        with self.assertRaisesRegex(ValueError,'no truncation'):
            bounded_input(row['plan'],'knowcoder',row['passage'],lambda _:4090,profile='positive_anchor',prompt_profile=KNOW_REFINEMENT)

    def test_action_refinement_has_two_fixed_examples_and_full_retrieval_origin_contrast(self):
        data=self.data['action_completeness']
        self.assertEqual(data['contrast']['incomplete_quote'],'retrieves')
        self.assertEqual(data['contrast']['complete_quote'],'retrieves a scroll from a cabinet in a quiet gallery')
        for condition in ('action of dog','motion of person'):
            p=compile_condition(condition,contract_recipe=CONTRACT_RECIPE)
            b=bounded_input(p,'knowcoder','A separate source.',lambda _:1000,profile='positive_anchor',prompt_profile=KNOW_REFINEMENT)
            self.assertEqual(b['prompt_profile_identity']['demonstrations'],2)
            self.assertEqual(b['context_limit'],2048)
            self.assertIn('A gardener plants lavender in a pot.',b['prompt'])
            self.assertIn(data['sentence'],b['prompt'])
            self.assertIn('bare verb',b['prompt'])
        encoded=json.dumps(self.data)
        self.assertIsNone(re.search(r'\b(?:dogs?|sticks?|leaves)\b',encoded,re.I))

    def test_refinement_asset_mutation_invalidates_binding_and_original_bytes_are_retained(self):
        row=next(item for item in self.base if item['case_id']=='spatial_qualifier')
        b=bounded_input(row['plan'],'knowcoder',row['passage'],lambda _:2500,profile='positive_anchor',prompt_profile=KNOW_REFINEMENT)
        self.assertEqual(b['prompt_profile_identity']['demonstrations_sha256'],DATA_SHA256)
        self.assertIn('know_refinement_demonstrations.json',b['implementation_sha256'])
        original=Path.read_bytes
        def changed(path):return original(path)+b' ' if path.name=='know_refinement_demonstrations.json' else original(path)
        with patch.object(Path,'read_bytes',changed),self.assertRaisesRegex(ValueError,'demonstrations changed'):
            verify_bound_input(b,row['plan'],row['passage'],lambda _:2500)


if __name__=='__main__':unittest.main()
