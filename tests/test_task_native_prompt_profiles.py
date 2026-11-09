"""The explicit one-shot profile binds fixed demos without changing target schemas."""
import hashlib
import json
from pathlib import Path
import unittest
from unittest.mock import patch

from csts_pilot.native_adapter.schema import compile_condition,native_prompt,render_schema,bounded_input,verify_bound_input,implementation_identity
from csts_pilot.native_adapter.normalize import normalize_native,normalize_stages
from csts_pilot.native_adapter.prompt_profiles import ZERO_SHOT,ONE_SHOT,DEMONSTRATIONS_SHA256

ROOT = Path(__file__).resolve().parent / "fixtures/native_adapter_final"


class PromptProfileTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.original=json.loads((ROOT/'tests/fixtures/original_ordinary_requests.json').read_text())['items']
        cls.examples=json.loads((ROOT/'native_adapter/demonstrations.json').read_text())

    def test_all18_original_target_prompts_and_schemas_are_unchanged(self):
        for row in self.original:
            plan=compile_condition(row['condition'])
            for model in ('knowcoder','gollie'):
                with self.subTest(case=row['case_id'],model=model):
                    zero=native_prompt(plan,model,row['passage'],profile='positive_anchor',prompt_profile=ZERO_SHOT)
                    self.assertEqual(zero,row['requests'][model]['prompt'])
                    one=native_prompt(plan,model,row['passage'],profile='positive_anchor',prompt_profile=ONE_SHOT)
                    if model=='gollie':self.assertTrue(one.endswith(zero))
                    else:self.assertEqual(one.split('\nInput:\n',2)[2],zero.split('\nInput:\n',1)[1])
                    self.assertIn(render_schema(plan,model,profile='positive_anchor'),one)

    def test_one_fixed_demo_per_family_is_independent_of_each_target(self):
        seen={}
        for row in self.original:
            plan=compile_condition(row['condition']);family=plan['native_task'];demo=self.examples[family]
            prompt=native_prompt(plan,'knowcoder',row['passage'],profile='positive_anchor',prompt_profile=ONE_SHOT)
            self.assertEqual(prompt.count(demo['sentence']),1)
            prefix=prompt.split('\nInput:\n',2)[:2]
            seen.setdefault(family,prefix);self.assertEqual(seen[family],prefix)
            self.assertNotIn(row['passage'],demo['know_query'])

    def test_binding_includes_demo_profile_data_and_actual_combined_token_count(self):
        plan=compile_condition('type of animal');seen=[]
        def count(prompt):seen.append(prompt);return 600
        bound=bounded_input(plan,'knowcoder','An elephant stands.',count,profile='positive_anchor',prompt_profile=ONE_SHOT)
        self.assertEqual(bound['input_tokens'],600)
        self.assertIn('mica and quartz',seen[0])
        self.assertEqual(bound['prompt_profile_identity']['demonstrations_sha256'],DEMONSTRATIONS_SHA256)
        self.assertEqual(bound['prompt_profile_identity']['demonstrations'],1)
        self.assertIn('demonstrations.json',bound['implementation_sha256'])
        self.assertTrue(verify_bound_input(bound,plan,'An elephant stands.',count))
        with self.assertRaisesRegex(ValueError,'no truncation'):
            bounded_input(plan,'knowcoder','An elephant stands.',lambda _:2040,profile='positive_anchor',prompt_profile=ONE_SHOT)

    def test_demo_mutation_and_profile_swap_invalidate_the_frozen_request(self):
        plan=compile_condition('type of animal');bound=bounded_input(plan,'knowcoder','An elephant stands.',lambda _:600,profile='positive_anchor',prompt_profile=ONE_SHOT)
        original=Path.read_bytes
        def changed(path):return original(path)+b'\n' if path.name=='demonstrations.json' else original(path)
        with patch.object(Path,'read_bytes',changed),self.assertRaisesRegex(ValueError,'demonstration bytes changed'):
            verify_bound_input(bound,plan,'An elephant stands.',lambda _:600)
        bound['prompt_profile']=ZERO_SHOT
        with self.assertRaisesRegex(ValueError,'identity changed'):
            verify_bound_input(bound,plan,'An elephant stands.',lambda _:600)

    def test_counts_polarity_and_unknown_prompt_variants_are_not_qualified(self):
        for condition,kwargs in (
            ('number of people',{'count_stage':'mentions','profile':'positive_anchor'}),
            ('color of dog',{'profile':'scoped_experimental'}),
        ):
            with self.subTest(condition=condition),self.assertRaisesRegex(ValueError,'ordinary positive'):
                native_prompt(compile_condition(condition),'knowcoder','Three people see a dog.',prompt_profile=ONE_SHOT,**kwargs)
        with self.assertRaisesRegex(ValueError,'Unknown frozen'):
            native_prompt(compile_condition('type of food'),'knowcoder','A sandwich.',profile='positive_anchor',prompt_profile='per_target_example')

    def test_demo_constructor_does_not_become_an_allowed_target_output(self):
        with self.assertRaisesRegex(ValueError,'Undeclared'):
            normalize_native('results = [Mineral("mica")]',compile_condition('type of animal'),'knowcoder','An elephant stands.',profile='positive_anchor')

    def test_actual_ordinary_leading_space_payload_parses_without_changing_raw_bytes(self):
        path=ROOT/'tests/fixtures/ordinary_animal_actual_raw.txt';raw=path.read_text()
        self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(),'25af4648fe342571000819bbd21f759a8d02af508da595c7b1c2d0755aded89b')
        row=next(item for item in self.original if item['case_id']=='animal')
        graph=normalize_native(raw,compile_condition(row['condition']),'knowcoder',row['passage'],profile='positive_anchor')
        self.assertEqual(graph['entities'][0]['span']['text'],'elephant')
        self.assertTrue(raw.startswith(' '))

    def test_stage_reparse_strips_only_outer_whitespace_and_keeps_original_raw_hashes(self):
        raw={'mentions':' \n results = [PersonGroup("Three people")]\n ',
             'quantity_bindings':'\t results = [HasQuantity(Entity("Three people"),Entity("Three"))] ',
             'identity':' results = []\n'}
        graph=normalize_stages(raw,compile_condition('number of people'),'knowcoder','Three people stand.',profile='positive_anchor')
        self.assertEqual(graph['quantity']['lower'],3)
        self.assertEqual(graph['stage_inputs_sha256'],{key:hashlib.sha256(value.encode()).hexdigest() for key,value in raw.items()})
        for payload in (' results = [Animal("dog")]\nprint("no")', ' __import__("os").system("false")'):
            with self.subTest(payload=payload),self.assertRaises(ValueError):
                normalize_native(payload,compile_condition('type of animal'),'knowcoder','A dog stands.')


if __name__=='__main__':unittest.main()
