"""Explicit scope contracts for the previously unsupported development facets."""

import json
from pathlib import Path
import unittest

from csts_pilot.native_adapter.schema import bounded_input, compile_condition, native_prompt, render_schema
from csts_pilot.native_adapter.normalize import normalize_native


CONDITIONS = (
    "background features", "contents of bathroom", "design of bathroom", "environment",
    "items used by people", "man with food", "means of transportation",
    "method of transportation", "mode of transportation", "nature of place",
    "object's purpose", "people's immediate attention", "person", "purpose of running",
    "quantity of food", "rider", "substance on ground", "sweetness of food",
    "train on track", "type of hobby", "type of play",
)


class ScopeExtensionTest(unittest.TestCase):
    def test_every_previously_unsupported_screen_facet_has_an_explicit_unapproved_contract(self):
        for condition in CONDITIONS:
            with self.subTest(condition=condition):
                plan=compile_condition(condition)
                self.assertTrue(plan['supported'])
                self.assertEqual(plan['gate_status'],'new_scope_contract_requires_development_gates')
                self.assertEqual(plan['interpretation_status'],'candidate_condition_scope_requires_development_review')
                self.assertFalse(plan['coverage_complete'])
                self.assertNotIn('ConditionRelation',{s['name'] for s in plan['schemas']})

    def test_extension_schema_cannot_depend_on_source_or_labels(self):
        for condition in CONDITIONS:
            plan=compile_condition(condition)
            stages=list(plan.get('stage_contract') or {None:None})
            for stage in stages:
                with self.subTest(condition=condition,stage=stage):
                    before=render_schema(plan,'knowcoder',profile='positive_anchor',task_stage=stage)
                    first=native_prompt(plan,'knowcoder','Unrelated input one.',profile='positive_anchor',task_stage=stage)
                    second=native_prompt(plan,'knowcoder','Different source two.',profile='positive_anchor',task_stage=stage)
                    self.assertIn(before,first)
                    self.assertIn(before,second)
                    self.assertNotIn('Unrelated input',before)

    def test_multitask_conditions_require_small_native_stages(self):
        plan=compile_condition('person')
        with self.assertRaisesRegex(ValueError,'declared native task stage'):
            native_prompt(plan,'knowcoder','A man runs.',profile='positive_anchor')
        subjects=render_schema(plan,'knowcoder',profile='positive_anchor',task_stage='subjects')
        self.assertIn('class Person(Entity)',subjects)
        self.assertNotIn('class Wears',subjects)
        with self.assertRaisesRegex(ValueError,'Undeclared'):
            normalize_native("[Wears(Entity('man'),Entity('shirt'))]",plan,'knowcoder','A man in a shirt runs.',profile='positive_anchor',task_stage='subjects')
        request=bounded_input(plan,'knowcoder','A man runs.',lambda _:100,profile='positive_anchor',task_stage='subjects')
        self.assertEqual(request['task_stage'],'subjects')

    def test_actual_development_item_category_does_not_invent_a_user(self):
        passage='Brush, books, bag, umbrella and couple of other items laid out on the bed'
        plan=compile_condition('items used by people')
        categories=normalize_native("[HumanUseItem('Brush'),HumanUseItem('books'),HumanUseItem('bag'),HumanUseItem('umbrella')]",plan,'knowcoder',passage,profile='positive_anchor',task_stage='item_categories')
        self.assertEqual(len(categories['entities']),4)
        self.assertEqual(categories['relations'],[])
        self.assertTrue(all(node['type']=='Object' for node in categories['entities']))
        participation=normalize_native('[]',plan,'knowcoder',passage,profile='positive_anchor',task_stage='explicit_use')
        self.assertEqual(participation['facet_statuses']['actual_use'],'not_specified')
        self.assertEqual(participation['facet_statuses']['item_categories'],'not_evaluated')
        self.assertEqual(participation['entities'],[])

    def test_actual_food_context_does_not_assert_ownership_or_eating(self):
        passage='a man drinking a drink with a few hot dogs out front of him'
        plan=compile_condition('man with food')
        graph=normalize_native("[FoodContext(Entity('a man'),Entity('a few hot dogs'))]",plan,'knowcoder',passage,profile='positive_anchor')
        self.assertEqual(graph['relations'][0]['predicate'],'food_context')
        self.assertEqual(set(plan['relation_does_not_imply']),{'owns','eats','holds'})
        self.assertFalse(any(edge['predicate'] in {'owns','eats','holds'} for edge in graph['relations']))

    def test_explicit_state_contracts_abstain_on_ordinary_exposed_sources(self):
        sources={
            'purpose of running':'Several runners round a corner on an autumn day .',
            'sweetness of food':'A close up shot of a plate with eggs and fruit on a table.',
            'type of hobby':'A surfboarder emerging from the ocean with his board , as the waves crash ashore behind him .',
            "object's purpose":'A street pole with a street sign on it that says B 86 Street, and a lamp post in the distance.',
        }
        for condition,passage in sources.items():
            with self.subTest(condition=condition):
                graph=normalize_native('[]',compile_condition(condition),'knowcoder',passage,profile='positive_anchor')
                self.assertEqual(graph['status'],'not_specified')
                self.assertEqual(graph['relations'],[])

    def test_food_amount_retains_units_without_a_fake_shared_total(self):
        passage='Two slices of pizza and 100 grams of rice are on the table.'
        plan=compile_condition('quantity of food')
        graph=normalize_native("[FoodAmount(Entity('pizza'),Entity('Two slices')),FoodAmount(Entity('rice'),Entity('100 grams'))]",plan,'knowcoder',passage,profile='positive_anchor')
        nodes={node['id']:node for node in graph['entities']}
        values=[nodes[edge['object']]['span']['text'] for edge in graph['relations']]
        self.assertEqual(values,['Two slices','100 grams'])
        self.assertNotIn('quantity',graph)
        self.assertEqual(plan['quantity_projection'],'verbatim_units_only_no_numeric_aggregation')

    def test_actual_transport_and_play_development_spans_are_preserved(self):
        travel='A man on a bicycle jumping off a dirt ramp with one foot on the ground'
        graph=normalize_native("[TransportMode('bicycle')]",compile_condition('method of transportation'),'knowcoder',travel,profile='positive_anchor')
        self.assertEqual(graph['entities'][0]['span']['text'],'bicycle')
        play='The girl and the lady hold their game controllers and play with their Wii console.'
        graph=normalize_native("[PlayEvent(trigger='play',actor=[Entity('The girl'),Entity('the lady')],theme=[Entity('their Wii console')],place=[])]",compile_condition('type of play'),'knowcoder',play,profile='positive_anchor')
        self.assertEqual(graph['events'][0]['predicate'],'play_activity')
        self.assertEqual(len(graph['events'][0]['roles']['actor']),2)

    def test_observed_activity_survives_without_becoming_a_persistent_hobby(self):
        passage='A male surfer in a black wetsuit standing on a white surfboard is riding in a small wave on the ocean .'
        plan=compile_condition('type of hobby')
        payload="[ActivityEvent(trigger='riding',actor=[Entity('A male surfer')],theme=[Entity('a white surfboard')],place=[Entity('in a small wave')])]"
        graph=normalize_native(payload,plan,'knowcoder',passage,profile='positive_anchor',task_stage='observed_activity')
        self.assertEqual(graph['requested_facet_status'],'not_specified')
        self.assertTrue(graph['context_annotations_present'])
        self.assertEqual(graph['events'][0]['answer_role'],'context')
        self.assertEqual(graph['events'][0]['predicate'],'activity')
        self.assertFalse(any(edge['predicate']=='explicit_hobby' for edge in graph['relations']))
        self.assertFalse(graph['coverage_validated'])

    def test_sport_category_does_not_require_an_invented_participant(self):
        plan=compile_condition('type of sport')
        for model,payload in (('knowcoder',"[Sport('Tennis')]"),('gollie',"[Sport(span='Tennis')]")):
            with self.subTest(model=model):
                graph=normalize_native(payload,plan,model,'Tennis balls lie on a court.',profile='positive_anchor',task_stage='sport_categories')
                self.assertEqual(graph['status'],'answered')
                self.assertEqual(graph['relations'],[])
                self.assertEqual(len(graph['entities']),1)
        participation=render_schema(plan,'gollie',profile='positive_anchor',task_stage='participants')
        self.assertIn('class PlaysSport(Relation)',participation)
        self.assertIn('participant: str',participation)
        self.assertIn('sport: str',participation)


if __name__=='__main__':
    unittest.main()
