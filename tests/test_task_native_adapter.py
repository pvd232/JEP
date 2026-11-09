"""Source-grounded development examples and adversarial projection checks."""

import copy
import json
from pathlib import Path
import unittest
from unittest.mock import patch

from csts_pilot.native_adapter.schema import backend_schemas, bounded_input, compile_condition, implementation_identity, native_prompt, plan_digest, render_schema, verify_bound_input
from csts_pilot.native_adapter.normalize import normalize_native
from csts_pilot.native_adapter.gates import check_case, model_inputs, semantic_view
from csts_pilot.native_adapter.inventory import build

ROOT = Path(__file__).resolve().parent / "fixtures/native_adapter_scope_v5"


class AdapterTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cases = json.loads((ROOT / "evidence/development_gate_cases_v3.json").read_text())["cases"]

    def test_native_api_envelope_whitespace_preserves_annotations(self):
        plan = compile_condition("type of animal")
        for model, payload in (("knowcoder", ' results = [Animal("elephant")]'),
                               ("gollie", ' [Animal(span="elephant")]')):
            expected = normalize_native(payload.strip(), plan, model, "An elephant stands.")
            for framed in (payload, "\n\t" + payload + "\n  "):
                self.assertEqual(normalize_native(framed, plan, model, "An elephant stands."), expected)

    def test_whitespace_is_not_an_empty_list_or_an_extra_statement_escape(self):
        plan = compile_condition("type of animal")
        for payload in (" \n\t", ' results = [Animal("elephant")]\nprint("elephant")'):
            with self.assertRaises(ValueError):
                normalize_native(payload, plan, "knowcoder", "An elephant stands.")

    def test_every_real_development_annotation_has_equivalent_meaning_in_both_native_formats(self):
        for case in self.cases:
            plan = compile_condition(case["condition"])
            with self.subTest(case=case["case_id"]):
                go = normalize_native(case["expected_native_annotations"]["gollie"], plan, "gollie", case["passage"])
                know = normalize_native(case["expected_native_annotations"]["knowcoder"], plan, "knowcoder", case["passage"])
                self.assertEqual(semantic_view(go), semantic_view(know))
                self.assertEqual(sorted({node['type'] for node in go['entities']}), sorted(case['independent_expected_entity_types']))
                self.assertTrue(check_case(case, case["expected_native_annotations"]["gollie"], "gollie")["passed"])

    def test_python_valid_wrong_animal_fails_semantic_gate(self):
        case = next(item for item in self.cases if item["case_id"] == "animal")
        wrong = "[Animal(span='red bench')]"
        self.assertEqual(normalize_native(wrong, compile_condition(case["condition"]), "gollie", case["passage"])["status"], "answered")
        self.assertFalse(check_case(case, wrong, "gollie")["passed"])

    def test_python_valid_wrong_color_binding_fails_semantic_gate(self):
        case = next(item for item in self.cases if item["case_id"] == "board_color")
        self.assertFalse(check_case(case, "[HasColor(object='male surfer', color='white')]", "gollie")["passed"])

    def test_python_valid_wrong_event_actor_fails_semantic_gate(self):
        case = next(item for item in self.cases if item["case_id"] == "dog_event")
        wrong = "[ActivityEvent(mention='fetches',actor=['a stick'],theme=['A dog'],place=['the dead leaves'])]"
        self.assertFalse(check_case(case, wrong, "gollie")["passed"])

    def test_additional_grounded_annotations_trigger_review_without_failing_minimal_anchor(self):
        case = next(item for item in self.cases if item['case_id']=='animal_color')
        payload="[HasColor(object='brown dog',color='brown'),HasColor(object='his eyes',color='glowing')]"
        result=check_case(case,payload,'gollie')
        self.assertTrue(result['minimal_anchor_recovered'])
        self.assertFalse(result['strict_graph_match'])
        self.assertTrue(result['semantic_review_required'])
        self.assertFalse(result['completeness_established'])

    def test_source_absence_and_adapter_unsupported_are_distinct(self):
        supported = normalize_native("[]", compile_condition("type of animal"), "gollie", "A person walks.")
        unsupported = normalize_native("[]", compile_condition("sequence of events"), "gollie", "A person runs.")
        self.assertEqual(supported["status"], "not_specified")
        self.assertEqual(unsupported["status"], "adapter_unsupported")
        with self.assertRaisesRegex(ValueError, "adapter_unsupported"):
            native_prompt(compile_condition("sequence of events"), "gollie", "A person runs.")

    def test_quantities_three_people_and_one_separate_man_are_four_only_with_coverage(self):
        passage = "Three people look up at a man on a ladder against a brick wall ."
        plan = compile_condition("number of people")
        payload = "[PersonGroup(span='Three people'),PersonGroup(span='a man'),DistinctFrom(arg1='Three people',arg2='a man')]"
        conservative = normalize_native(payload, plan, "gollie", passage)
        checked = normalize_native(payload, plan, "gollie", passage, coverage_complete=True)
        self.assertEqual(conservative["quantity"]["kind"], "lower_bound")
        self.assertEqual(conservative["quantity"]["lower"], 4)
        self.assertEqual((checked["quantity"]["kind"], checked["quantity"]["lower"]), ("exact", 4))

    def test_quantity_bindings_cannot_launder_uncertain_group_presence(self):
        plan=compile_condition('number of people')
        items=["UncertainPersonGroup(span='Possibly three people')", "HasQuantity(arg1='Possibly three people',arg2='three')"]
        for ordered in (items,list(reversed(items))):
            result=normalize_native('['+','.join(ordered)+']',plan,'gollie','Possibly three people are outside.',coverage_complete=True)
            self.assertEqual(result['quantity']['kind'],'unknown')
            self.assertEqual(len([n for n in result['entities'] if n['type']=='Person']),1)
            self.assertEqual(result['entities'][0]['polarity'],'uncertain')

    def test_quantity_link_without_scoped_group_is_not_a_presence_assertion(self):
        result=normalize_native("[HasQuantity(arg1='three people',arg2='three')]",compile_condition('number of people'),'gollie','Possibly three people are outside.',coverage_complete=True)
        self.assertEqual(result['quantity']['kind'],'unknown')
        self.assertIn('count_relation_without_scoped_group_annotation',result['issues'])

    def test_repeated_dog_within_two_dogs_does_not_add_a_third(self):
        passage = "Two black dogs run through the snow with a red toy in one dog 's mouth ."
        plan = compile_condition("number of animals")
        payload = "[AnimalGroup(span='Two black dogs'), AnimalGroup(span='one dog'), PartOf(arg1='one dog',arg2='Two black dogs')]"
        evidence = normalize_native(payload, plan, "gollie", passage, coverage_complete=True)
        self.assertEqual((evidence["quantity"]["kind"], evidence["quantity"]["lower"]), ("exact", 2))

    def test_jersey_number_does_not_create_five_animals(self):
        passage = "A brown and white greyhound wearing a red number five is caught in midair racing ."
        plan = compile_condition("number of animals")
        payload = "[AnimalGroup(span='A brown and white greyhound')]"
        evidence = normalize_native(payload, plan, "gollie", passage, coverage_complete=True)
        self.assertEqual((evidence["quantity"]["kind"], evidence["quantity"]["lower"]), ("exact", 1))
        bad = payload[:-1] + ", HasQuantity(arg1='A brown and white greyhound',arg2='five')]"
        self.assertEqual(normalize_native(bad, plan, "gollie", passage, coverage_complete=True)["quantity"]["kind"], "unknown")

    def test_unspecified_children_are_not_an_invented_exact_number(self):
        passage = "A number of children enjoy themselves on the coast of a city ."
        plan = compile_condition("number of people")
        evidence = normalize_native("[PersonGroup(span='A number of children')]", plan, "gollie", passage, coverage_complete=True)
        self.assertEqual(evidence["quantity"]["kind"], "lower_bound")
        self.assertEqual(evidence["quantity"]["lower"], 2)

    def test_explicit_negative_zero_differs_from_empty_output(self):
        plan = compile_condition("number of people")
        absent = normalize_native("[NegatedPersonGroup(span='No people')]", plan, "gollie", "No people are present.", coverage_complete=True)
        unknown = normalize_native("[]", plan, "gollie", "A field is visible.", coverage_complete=True)
        self.assertEqual(absent["status"], "answered")
        self.assertEqual((absent["quantity"]["kind"], absent["quantity"]["lower"]), ("exact", 0))
        self.assertEqual(unknown["status"], "not_specified")
        self.assertEqual(unknown["quantity"]["kind"], "unknown")

    def test_identical_repeated_spans_never_get_a_guessed_occurrence(self):
        plan = compile_condition("number of dogs")
        evidence = normalize_native("[DogGroup(span='a dog')]", plan, "gollie", "I see a dog; a dog runs.", coverage_complete=True)
        self.assertEqual(evidence["status"], "ambiguous")
        self.assertEqual(len(evidence["entities"][0]["span"]["candidates"]), 2)
        self.assertEqual(evidence["quantity"]["kind"], "unknown")

    def test_negation_and_event_uncertainty_survive(self):
        negative = normalize_native("[NegatedHasColor(object='The dog',color='brown')]", compile_condition("color of dog"), "gollie", "The dog is not brown.")
        self.assertEqual(negative["relations"][0]["polarity"], "negative")
        self.assertTrue(all(node['polarity'] == 'positive' for node in negative['entities']))
        uncertain = normalize_native("[UncertainActivityEvent(mention='may run',actor=['A boy'],theme=[],place=[])]", compile_condition("action of person"), "gollie", "A boy may run.")
        self.assertEqual(uncertain["events"][0]["polarity"], "uncertain")

    def test_no_execution_or_silent_unknown_constructor(self):
        for payload in ("__import__('os').system('echo no')", "[Entity('dog')]", "[Unknown(span='dog')]", "[Animal(span='dog',extra='x')]"):
            with self.subTest(payload=payload), self.assertRaises(ValueError):
                normalize_native(payload, compile_condition("type of animal"), "knowcoder", "A dog runs.")

    def test_schema_depends_on_condition_only_and_native_task_matches_family(self):
        for condition, task in (("type of food", "NER"), ("color of animal", "RE"), ("action of dog", "EE")):
            plan = compile_condition(condition)
            self.assertEqual(plan["native_task"], task)
            before = render_schema(plan, "gollie")
            first = native_prompt(plan, "gollie", "Source one.")
            second = native_prompt(plan, "gollie", "Different source.")
            self.assertEqual(before, render_schema(plan, "gollie"))
            self.assertTrue(first.startswith(before) and second.startswith(before))
            self.assertNotIn("ConditionRelation", before)

    def test_count_prompt_stages_are_separate_and_gated(self):
        plan = compile_condition("number of people")
        with self.assertRaisesRegex(ValueError, "separately gated"):
            native_prompt(plan, "knowcoder", "Three people walk.")
        mentions = render_schema(plan, "knowcoder", count_stage="mentions")
        quantities = render_schema(plan, "knowcoder", count_stage="quantity_bindings")
        self.assertIn("class PersonGroup", mentions)
        self.assertNotIn("class DistinctFrom", mentions)
        self.assertNotIn("class HasQuantity", mentions)
        self.assertIn("class HasQuantity", quantities)
        self.assertNotIn("class SameReferent", quantities)
        with self.assertRaisesRegex(ValueError, 'dispatch is disabled'):
            bounded_input(plan, 'knowcoder', 'Three people walk.', lambda _:100, count_stage='mentions')
        with self.assertRaisesRegex(ValueError, 'Undeclared'):
            normalize_native("[HasQuantity(arg1='Three people',arg2='Three')]", plan, 'gollie', 'Three people walk.', count_stage='mentions')

    def test_relation_arguments_match_each_backends_declared_types(self):
        plan = compile_condition('color of animal')
        for payload in ("[Color('dog','brown')]", "[Color(Entity('dog'),'brown')]"):
            with self.subTest(payload=payload), self.assertRaisesRegex(ValueError, 'Entity constructors'):
                normalize_native(payload, plan, 'knowcoder', 'A brown dog runs.')
        self.assertEqual(normalize_native("[Color(Entity('dog'),Entity('brown'))]", plan, 'knowcoder', 'A brown dog runs.')['status'], 'answered')
        with self.assertRaisesRegex(ValueError, 'Undeclared'):
            normalize_native("[Color(arg1='dog',arg2='brown')]", plan, 'gollie', 'A brown dog runs.')

    def test_spatial_target_types_are_independently_specified(self):
        for condition, subject, value in (
            ('location of person', 'Person', 'Location'),
            ('location of food', 'Food', 'Location'),
            ('location of zebras standing', 'Animal', 'Location'),
            ('positioning of skateboarders', 'Person', 'Location'),
            ('decoration location', 'Object', 'Location'),
            ('object food is in', 'Food', 'Container'),
            ('furniture food is on', 'Food', 'Furniture'),
        ):
            with self.subTest(condition=condition):
                schema = compile_condition(condition)['schemas'][0]
                self.assertEqual((schema['target_type'],schema['value_type']), (subject,value))

    def test_known_working_gollie_role_anchors_are_preserved(self):
        for condition, name, fields in (
            ('color of animal','HasColor',['object','color']),
            ('clothing of person','WearsClothing',['person','clothing']),
            ('type of sport','PlaysSport',['participant','sport']),
        ):
            with self.subTest(condition=condition):
                schema=next(s for s in backend_schemas(compile_condition(condition),'gollie') if s['name']==name)
                self.assertEqual((schema['name'],schema['fields']),(name,fields))
        self.assertEqual(backend_schemas(compile_condition('type of sport'),'knowcoder')[0]['name'],'Sport')

    def test_positive_anchor_preserves_canonical_know_task_instruction_and_scope(self):
        for condition, instruction, required, excluded in (
            ('type of food', 'Some Entity Classes are defined above. Please instantiate all the corresponding Entity Objects', 'class Food(Entity)', 'class Relation'),
            ('clothing of person', 'Some Relation Classes and related Entity Classes are defined above. Please instantiate all the corresponding Relation Objects', 'class Wears(Relation)', 'class Event'),
        ):
            with self.subTest(condition=condition):
                plan=compile_condition(condition)
                prompt=native_prompt(plan,'knowcoder','A man in a wetsuit eats food.',profile='positive_anchor')
                self.assertIn(instruction,prompt)
                self.assertIn(required,prompt)
                self.assertNotIn(excluded,prompt)
                self.assertNotIn('Negated',prompt)
                self.assertNotIn('Uncertain',prompt)
                self.assertIn('"""\nThis is an object-oriented programming task:',prompt)
                self.assertIn('\n\tDescription:',prompt)
        with self.assertRaisesRegex(ValueError,'Undeclared'):
            normalize_native("[NegatedFood('food')]",compile_condition('type of food'),'knowcoder','No food.',profile='positive_anchor')

    def test_native_event_roles_obey_declared_entity_arguments(self):
        with self.assertRaisesRegex(ValueError,'Entity constructors'):
            normalize_native("[ActivityEvent(trigger='runs',actor=['A boy'],theme=[],place=[])]",compile_condition('action of person'),'knowcoder','A boy runs.')

    def test_lexical_categories_do_not_require_invented_literal_source_words(self):
        plan=compile_condition('gender of person')
        evidence=normalize_native("[Male(span='man')]",plan,'gollie','A man walks.')
        self.assertEqual(evidence['properties'][0]['value'],'male')
        self.assertEqual(evidence['entities'][0]['span']['text'],'man')
        with self.assertRaisesRegex(ValueError,'lexical source cue'):
            normalize_native("[Male(span='Alex')]",plan,'gollie','Alex walks.')
        with self.assertRaisesRegex(ValueError,'broader gender'):
            normalize_native("[NegatedMale(span='not a man')]",plan,'gollie','They are not a man.')
        with self.assertRaisesRegex(ValueError,'complete source token'):
            normalize_native("[Male(span='man')]",plan,'gollie','A woman walks.')
        clothing=normalize_native("[Clothing(span='pants')]",compile_condition('type of clothing'),'gollie','A person in pants walks.')
        self.assertEqual(clothing['entities'][0]['type'],'Clothing')

    def test_presence_does_not_get_enabled_by_an_ordinary_ner_unit_test(self):
        self.assertEqual(compile_condition('presence of helmets')['gate_status'],'wearer_binding_and_negation_canaries_required')

    def test_actual_tokenizer_budget_is_required_and_never_truncates(self):
        plan = compile_condition("type of animal")
        ready = bounded_input(plan, "knowcoder", "A dog runs.", lambda prompt: 100, 512)
        self.assertEqual(ready["input_tokens"], 100)
        self.assertEqual(ready["context_limit"], 2048)
        with self.assertRaisesRegex(ValueError, "no truncation"):
            bounded_input(plan, "knowcoder", "A dog runs.", lambda prompt: 2040, 512)

    def test_new_helper_bytes_are_bound_and_stale_gate_plan_is_rejected(self):
        self.assertIn("normalize.py", implementation_identity())
        self.assertIn("counts.py", implementation_identity())
        self.assertIn("gates.py", implementation_identity())
        case = copy.deepcopy(self.cases[0])
        case["plan_sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "plan changed"):
            check_case(case, "[]", "gollie")

    def test_mutated_helper_invalidates_a_prepared_native_request(self):
        plan = compile_condition("type of animal")
        request = bounded_input(plan, "knowcoder", "A dog runs.", lambda prompt: 100)
        original = Path.read_bytes
        def changed(path):
            value = original(path)
            return value + b"\n" if path.name == "counts.py" else value
        with patch.object(Path, "read_bytes", changed):
            with self.assertRaisesRegex(ValueError, "identity changed"):
                verify_bound_input(request, plan, "A dog runs.", lambda prompt: 100)

    def test_compound_subject_scope_does_not_change_to_an_incidental_person(self):
        plan = compile_condition("color of clothing on runner's legs")
        self.assertEqual(plan["schemas"][0]["target_type"], "Clothing")
        vehicle = compile_condition("type of sport vehicle")
        self.assertEqual(vehicle["family"], "unary_typed_mentions")
        self.assertEqual(vehicle["schemas"][0]["target_type"], "Vehicle")
        incidental_board = compile_condition("activity involving boards")
        self.assertEqual(incidental_board["schemas"][0]["target_type"], "Entity")
        incidental_snow = compile_condition("activity in snow")
        self.assertEqual(incidental_snow["schemas"][0]["target_type"], "Entity")

    def test_model_inputs_exclude_gold_annotations(self):
        for item in model_inputs(self.cases):
            self.assertNotIn("expected_native_annotations", item)
            self.assertEqual(set(item), {"case_id", "source_id", "passage", "condition", "profile", "plan", "plan_sha256"})

    def test_fresh_reserve_excludes_all_exposed_groups_and_labels_are_unused(self):
        screen = [{"id": "s1", "passage": "Seen source.", "condition": "type of animal", "group_id": "seen"}]
        validation = [
            {"row_id": "v1", "sentence1": "Seen source.", "sentence2": "Other.", "condition": "type of animal", "group_id": "seen", "rating": "DO NOT READ"},
            {"row_id": "v2", "sentence1": "Fresh one.", "sentence2": "Fresh two.", "condition": "type of food", "group_id": "new", "rating": object()},
        ]
        result = build(screen, validation)
        self.assertFalse(result["labels_consumed"])
        self.assertEqual(result["fresh_reserve"]["rows"], 1)
        self.assertEqual(result["fresh_reserve"]["identities"][0]["row_id"], "v2")


if __name__ == "__main__":
    unittest.main()
