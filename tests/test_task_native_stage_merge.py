"""A stage union preserves only individually schema-valid annotations."""

import json
from pathlib import Path
import unittest

from csts_pilot.native_adapter.schema import compile_condition
from csts_pilot.native_adapter.normalize import normalize_stages

ROOT = Path(__file__).resolve().parent / "fixtures/native_adapter_scope_v5"


class StageMergeTest(unittest.TestCase):
    def test_exposed_count_stage_proposals_only_make_conditional_lower_bound_claims(self):
        cases=json.loads((ROOT/'evidence/count_development_gates_v1.json').read_text())['cases']
        for case in cases:
            for model,payloads in case['expected_native_stages'].items():
                with self.subTest(case=case['case_id'],model=model):
                    graph=normalize_stages(payloads,case['plan'],model,case['passage'],profile='positive_anchor')
                    self.assertEqual({key:graph['quantity'][key] for key in ('kind','lower','upper')},case['minimal_conditional_quantity'])
                    self.assertFalse(graph['coverage_validated'])
                    self.assertFalse(graph['semantic_support_validated'])
                    self.assertEqual(set(graph['stage_inputs_sha256']),{'mentions','quantity_bindings','identity'})

    def test_missing_stage_or_cross_stage_constructor_does_not_get_repaired(self):
        plan=compile_condition('number of people')
        with self.assertRaisesRegex(ValueError,'every declared'):
            normalize_stages({'mentions':'[]'},plan,'gollie','Three people stand.')
        bad={'mentions':"[HasQuantity(arg1='Three people',arg2='Three')]",'quantity_bindings':'[]','identity':'[]'}
        with self.assertRaisesRegex(ValueError,'Undeclared'):
            normalize_stages(bad,plan,'gollie','Three people stand.')

    def test_context_union_retains_activity_without_inventing_a_hobby(self):
        plan=compile_condition('type of hobby')
        captures={'observed_activity':"[ActivityEvent(trigger='plays',actor=[Entity('A woman')],theme=[Entity('tennis')],place=[])]",'explicit_hobby':'[]'}
        graph=normalize_stages(captures,plan,'knowcoder','A woman plays tennis.')
        self.assertEqual(graph['requested_facet_status'],'not_specified')
        self.assertEqual(len(graph['events']),1)
        self.assertEqual(graph['relations'],[])
        self.assertTrue(graph['context_annotations_present'])

    def test_category_answer_cannot_become_an_answer_about_actual_use(self):
        plan=compile_condition('items used by people')
        captures={'item_categories':"[HumanUseItem('Brush'),HumanUseItem('books')]",'explicit_use':'[]'}
        graph=normalize_stages(captures,plan,'knowcoder','Brush, books and other items lie on a bed.')
        self.assertEqual(graph['facet_statuses'],{'item_categories':'answered','actual_use':'not_specified'})
        self.assertEqual(graph['requested_facet_status'],'ambiguous')
        self.assertEqual(graph['relations'],[])


if __name__=='__main__':unittest.main()
