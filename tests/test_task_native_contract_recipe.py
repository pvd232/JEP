"""Source-independent palette, coarser clauses and fixed Food routing checks."""
import hashlib
import json
from pathlib import Path
import unittest

from csts_pilot.native_adapter.schema import compile_condition,native_prompt,bounded_input,verify_bound_input,selected_schemas
from csts_pilot.native_adapter.schema import plan_digest
from csts_pilot.native_adapter.task_recipe import CONTRACT_RECIPE,SPATIAL_PALETTE
from csts_pilot.native_adapter.normalize import normalize_native,normalize_stages
from csts_pilot.native_adapter.gates import check_case
from csts_pilot.native_adapter.export import canonical_text
from csts_pilot.native_adapter.cli import normalize_record,export_record
from csts_pilot.native_adapter.prompt_profiles import ZERO_SHOT,ONE_SHOT

ROOT = Path(__file__).resolve().parent / "fixtures/native_adapter_final"


def plan(condition):return compile_condition(condition,contract_recipe=CONTRACT_RECIPE)


class TaskContractRecipeTest(unittest.TestCase):
    def test_all_spatial_questions_offer_the_same_complete_palette(self):
        expected=[row[0] for row in SPATIAL_PALETTE]
        for condition in ('location of person','location of food','location of zebras standing','object food is in','positioning of skateboarders','decoration location'):
            with self.subTest(condition=condition):
                p=plan(condition)
                self.assertEqual([s['name'] for s in p['schemas']],expected)
                self.assertEqual(p['spatial_palette'],expected)
                first=native_prompt(p,'knowcoder','First source only.',profile='positive_anchor')
                second=native_prompt(p,'knowcoder','Unrelated second source.',profile='positive_anchor')
                self.assertIn('class Near(Relation)',first);self.assertIn('class Beside(Relation)',second)
                self.assertNotIn('First source only',json.dumps(p))

    def test_qualifier_is_model_emitted_edge_not_recovered_from_source(self):
        p=plan('location of person');source='A boy in a black swimsuit plays near the water.'
        graph=normalize_native('[Near(Entity("A boy"),Entity("the water"))]',p,'knowcoder',source,profile='positive_anchor')
        self.assertEqual(graph['relations'][0]['predicate'],'near')
        self.assertEqual(graph['entities'][1]['span']['text'],'the water')
        self.assertEqual(graph['relations'][0]['predicate_cue_spans'][0]['text'],'near')
        self.assertFalse(graph['semantic_support_validated'])
        with self.assertRaisesRegex(ValueError,'no declared source cue'):
            normalize_native('[At(Entity("A boy"),Entity("the water"))]',p,'knowcoder',source,profile='positive_anchor')
        with self.assertRaisesRegex(ValueError,'preposition phrases'):
            normalize_native('[Near(Entity("A boy"),Entity("near the water"))]',p,'knowcoder',source,profile='positive_anchor')

    def test_cue_is_only_consistency_not_entailment_attire_stays_semantic_error(self):
        p=plan('location of person');source='A boy in a black swimsuit plays near the water.'
        wrong='[Inside(Entity("A boy"),Entity("a black swimsuit"))]'
        graph=normalize_native(wrong,p,'knowcoder',source,profile='positive_anchor')
        self.assertEqual(graph['relations'][0]['predicate'],'inside')
        self.assertFalse(graph['semantic_support_validated'])
        # Compare the actual meanings/bindings to a fixed source-grounded anchor;
        # valid constructors and the word in cannot prove physical location.
        from csts_pilot.native_adapter.gates import semantic_view
        expected=normalize_native('[Near(Entity("A boy"),Entity("the water"))]',p,'knowcoder',source,profile='positive_anchor')
        self.assertNotEqual(semantic_view(graph),semantic_view(expected))
        case={'case_id':'independent-spatial-scope','condition':p['condition'],'passage':source,
              'contract_recipe':CONTRACT_RECIPE,'profile':'positive_anchor','plan_sha256':plan_digest(p),
              'independent_expected_entity_types':['Person','SpatialReference'],
              'expected_native_annotations':{'knowcoder':'[Near(Entity("A boy"),Entity("the water"))]'}}
        self.assertFalse(check_case(case,wrong,'knowcoder')['minimal_anchor_recovered'])

    def test_fronted_spatial_cue_is_supported_without_inventing_association(self):
        p=plan('location of person');payload='[Near(Entity("a boy"),Entity("the water"))]'
        from csts_pilot.native_adapter.gates import semantic_view
        graphs=[normalize_native(payload,p,'knowcoder',source,profile='positive_anchor')
                for source in ('a boy plays near the water.','Near the water, a boy plays.')]
        self.assertEqual(semantic_view(graphs[0]),semantic_view(graphs[1]))
        self.assertEqual(graphs[1]['relations'][0]['predicate_cue_spans'][0]['start'],0)
        self.assertFalse(graphs[1]['relations'][0]['predicate_argument_association_validated'])

    def test_unrelated_matching_cue_is_not_a_semantic_binding_certificate(self):
        p=plan('location of person');source='A boy is beside a tree; a man is near the water.'
        wrong=normalize_native('[Near(Entity("A boy"),Entity("the water"))]',p,'knowcoder',source,profile='positive_anchor')
        self.assertEqual(wrong['relations'][0]['predicate'],'near')
        self.assertFalse(wrong['relations'][0]['predicate_argument_association_validated'])
        self.assertFalse(wrong['semantic_support_validated'])
        case={'case_id':'independent-cue-association','condition':p['condition'],'passage':source,
              'contract_recipe':CONTRACT_RECIPE,'profile':'positive_anchor','plan_sha256':plan_digest(p),
              'expected_native_annotations':{'knowcoder':'[Beside(Entity("A boy"),Entity("a tree"))]'}}
        self.assertFalse(check_case(case,'[Near(Entity("A boy"),Entity("the water"))]','knowcoder')['minimal_anchor_recovered'])

    def test_to_toward_over_above_remain_distinct_in_export(self):
        p=plan('location of person');texts=[]
        for name,predicate,source in (
            ('To','to','The man walked to school.'),('Toward','toward','The man walked toward school.'),
            ('Over','over','The man jumped over the fence.'),('Above','above','The man stood above the fence.'),
        ):
            reference='school' if name in {'To','Toward'} else 'the fence'
            graph=normalize_native('['+name+'(Entity("The man"),Entity('+repr(reference)+'))]',p,'knowcoder',source,profile='positive_anchor')
            self.assertEqual(graph['relations'][0]['predicate'],predicate);texts.append(canonical_text(graph))
        self.assertEqual(len(set(texts)),4)

    def test_all_frozen_cue_prefixes_remain_outside_entity_arguments(self):
        from csts_pilot.native_adapter.task_recipe import spatial_argument_is_preposition_phrase
        for _,_,_,cues in SPATIAL_PALETTE:
            for cue in cues:
                with self.subTest(cue=cue):
                    self.assertTrue(spatial_argument_is_preposition_phrase(cue+' the reference'))
        p=plan('location of person')
        for constructor,source,reference in (
            ('To','The man walked to school.','to school'),
            ('Over','The man jumped over the fence.','over the fence'),
        ):
            with self.subTest(constructor=constructor),self.assertRaisesRegex(ValueError,'preposition phrases'):
                normalize_native('['+constructor+'(Entity("The man"),Entity('+repr(reference)+'))]',p,'knowcoder',source,profile='positive_anchor')

    def test_action_clause_preserves_object_prepositions_negation_and_not_roles(self):
        p=plan('action of dog');source='A dog does not fetch a stick from the leaves.'
        graph=normalize_native('[ActionDescription(Entity("A dog"),Entity("does not fetch a stick from the leaves"))]',p,'knowcoder',source,profile='positive_anchor')
        self.assertEqual(graph['entities'][1]['span']['text'],'does not fetch a stick from the leaves')
        self.assertEqual(graph['relations'][0]['predicate'],'has_action_description')
        self.assertFalse(graph['relations'][0]['event_roles_resolved'])
        self.assertFalse(graph['relations'][0]['clause_semantics_decomposed'])
        self.assertEqual(graph['events'],[])
        self.assertTrue(p['legacy_event_schemas'])

    def test_wrong_actor_clause_is_python_valid_but_not_the_semantic_anchor(self):
        p=plan('action of dog');source='A dog sits while a man throws a ball.'
        good=normalize_native('[ActionDescription(actor="A dog",verbal_clause="sits")]',p,'gollie',source,profile='positive_anchor')
        wrong=normalize_native('[ActionDescription(actor="A dog",verbal_clause="throws a ball")]',p,'gollie',source,profile='positive_anchor')
        from csts_pilot.native_adapter.gates import semantic_view
        self.assertNotEqual(semantic_view(good),semantic_view(wrong))
        self.assertFalse(wrong['semantic_support_validated'])
        case={'case_id':'independent-actor-binding','condition':p['condition'],'passage':source,
              'contract_recipe':CONTRACT_RECIPE,'profile':'positive_anchor','plan_sha256':plan_digest(p),
              'independent_expected_entity_types':['Animal','VerbalClause'],
              'expected_native_annotations':{'gollie':'[ActionDescription(actor="A dog",verbal_clause="sits")]'}}
        self.assertFalse(check_case(case,'[ActionDescription(actor="A dog",verbal_clause="throws a ball")]','gollie')['minimal_anchor_recovered'])

    def test_context_ee_stages_change_to_clause_re_without_inventing_hobby_or_goal(self):
        for condition,direct in (('type of hobby','explicit_hobby'),('purpose of running','explicit_purpose'),("people's immediate attention",'explicit_attention')):
            with self.subTest(condition=condition):
                p=plan(condition)
                self.assertEqual(p['stage_contract']['observed_activity'],['ActionDescription'])
                outputs={'observed_activity':'[ActionDescription(Entity("A woman"),Entity("plays tennis"))]',direct:'[]'}
                graph=normalize_stages(outputs,p,'knowcoder','A woman plays tennis.',profile='positive_anchor')
                self.assertEqual(graph['requested_facet_status'],'not_specified')
                self.assertTrue(graph['context_annotations_present'])
                self.assertEqual(graph['relations'][0]['answer_role'],'context')
                self.assertEqual(graph['events'],[])

    def test_know_ner_and_unrelated_go_ner_are_byte_identical_zero_shot(self):
        originals=json.loads((ROOT/'tests/fixtures/original_ordinary_requests.json').read_text())['items']
        for row in originals:
            p=plan(row['condition'])
            legacy=compile_condition(row['condition'])
            if legacy['native_task']!='NER':continue
            for model in ('knowcoder','gollie'):
                if model=='gollie' and selected_schemas(p,model,profile='positive_anchor')[0]['name']=='Food':continue
                with self.subTest(case=row['case_id'],model=model):
                    actual=native_prompt(p,model,row['passage'],profile='positive_anchor')
                    self.assertEqual(actual,row['requests'][model]['prompt'])

    def test_food_demo_only_targets_go_food_leaf_not_fruit_or_vegetable(self):
        food=plan('type of food')
        for model,expected_route in (('knowcoder','preserved_zero_shot_ner'),('gollie','gollie_food_same_class')):
            bound=bounded_input(food,model,'A meal is served.',lambda _:500,profile='positive_anchor')
            self.assertEqual(bound['prompt_profile_identity']['recipe_route'],expected_route)
        for condition,label in (('type of fruit','Fruit'),('type of vegetable','Vegetable')):
            p=plan(condition);old=compile_condition(condition)
            self.assertEqual(selected_schemas(p,'gollie',profile='positive_anchor')[0]['name'],label)
            self.assertEqual(native_prompt(p,'gollie','A meal is served.',profile='positive_anchor'),native_prompt(old,'gollie','A meal is served.',profile='positive_anchor'))
        data=json.loads((ROOT/'native_adapter/recipe_demonstrations.json').read_text())
        description=data['Food']['description']+data['Food']['go_query']+data['Food']['go_output']
        self.assertNotIn('sandwich',description.casefold());self.assertNotIn('pickle',description.casefold())

    def test_color_keeps_previous_fixed_one_shot_and_new_binding_is_full(self):
        source='A brown dog runs.';p=plan('color of dog');old=compile_condition('color of dog')
        self.assertEqual(native_prompt(p,'knowcoder',source,profile='positive_anchor'),native_prompt(old,'knowcoder',source,profile='positive_anchor',prompt_profile=ONE_SHOT))
        bound=bounded_input(p,'knowcoder',source,lambda _:500,profile='positive_anchor')
        self.assertEqual(bound['contract_recipe'],CONTRACT_RECIPE)
        self.assertEqual(bound['prompt_profile'],CONTRACT_RECIPE)
        self.assertIn('recipe_demonstrations.json',bound['implementation_sha256'])
        self.assertTrue(verify_bound_input(bound,p,source,lambda _:500))

    def test_cli_can_reproduce_the_explicit_recipe_and_retains_unvalidated_flags(self):
        raw={'source_id':'independent-spatial','condition':'location of person','passage':'A child is near a tree.','model':'knowcoder','contract_recipe':CONTRACT_RECIPE,'raw_output':'[Near(Entity("A child"),Entity("a tree"))]'}
        exported=export_record(normalize_record(raw))
        self.assertIn(' near ',exported['canonical_evidence'])
        self.assertFalse(exported['semantic_support_validated'])
        self.assertFalse(exported['route_production_approved'])


if __name__=='__main__':unittest.main()
