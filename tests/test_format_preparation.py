"""Check the declared unresolved-reference fallback before format scoring."""

import unittest

from scripts.prepare_format_similarity import unresolved_references


def record(entities, value):
    return {
        "entities": [{"id": identity, "type": kind} for identity, kind in entities],
        "facts": [{"value": value}],
    }


class LocalReferenceTests(unittest.TestCase):
    def test_reference_inside_a_relation_phrase_is_flagged(self):
        value = record([("dog1", "dog"), ("dog2", "dog")], "standing beside dog2")
        self.assertEqual(unresolved_references(value, "Two dogs stand together."), ["dog2"])

    def test_identifier_prefix_and_suffix_do_not_match(self):
        value = record([("dog2", "dog")], "dog20 and other_dog2 and dog2_other")
        self.assertEqual(unresolved_references(value, "Two dogs stand together."), [])
        value["facts"][0]["value"] = "(dog2), beside it"
        self.assertEqual(unresolved_references(value, "Two dogs stand together."), ["dog2"])

    def test_underscored_reference_is_flagged_and_results_are_deduplicated(self):
        value = record([("dog_1", "dog"), ("dog_2", "dog")], "dog_2 beside dog_1 and dog_2")
        self.assertEqual(unresolved_references(value, "Two dogs."), ["dog_1", "dog_2"])

    def test_numeric_count_and_plain_type_names_are_not_code_references(self):
        value = record([("2", "dog"), ("dog", "dog")], "2 dog")
        self.assertEqual(unresolved_references(value, "Two dogs."), [])

    def test_literal_source_id_and_entity_type_are_exempt(self):
        value = record([("jersey_7", "jersey"), ("type_1", "type_1")], "jersey_7 beside type_1")
        self.assertEqual(unresolved_references(value, "The jersey_7 label is printed."), [])

    def test_unmentioned_code_id_does_not_create_a_failure(self):
        value = record([("dog1", "dog"), ("dog2", "dog")], "another dog")
        self.assertEqual(unresolved_references(value, "Two dogs."), [])


if __name__ == "__main__":
    unittest.main()
