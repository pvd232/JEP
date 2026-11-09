"""Source-scenario fixtures for conservative quantity and entity-set arithmetic."""

import unittest

from csts_pilot.native_adapter.counts import aggregate_count, quantity_from_text


def group(identity, text, polarity="positive"):
    return {"id": identity, "quantity": quantity_from_text(text), "polarity": polarity}


def relation(kind, left, right):
    return {"predicate": kind, "subject": left, "object": right}


class QuantityTest(unittest.TestCase):
    def test_unparsed_quantifier_suffixes_never_create_finite_false_counts(self):
        for text in ('one or more people','a dozen or more people','less than two people',
                     'no less than three people','one to two dozen people',
                     'at most two dozen people','two or three dozen people',
                     'one and a half people', 'two dozen or three people',
                     'two or three or four people', 'two people or four',
                     'a person and seven others', 'people under two',
                     'two people or a man', 'two people and another',
                     'two people and her', 'three doctors and another'):
            with self.subTest(text=text):
                self.assertEqual(quantity_from_text(text)['kind'],'unknown')
    def test_compound_numerals_and_coordinated_groups_never_keep_only_first_number(self):
        for text in ("twenty one people", "one hundred people", "three men and two women",
                     "a man and two women", "three men and women", "neither man", "none of the people",
                     "a group of one hundred people"):
            with self.subTest(text=text):
                self.assertEqual(quantity_from_text(text)["kind"], "unknown")

    def test_explicit_groups(self):
        for text, value in (("Three people", 3), ("a man", 1), ("an elephant", 1),
                            ("Five Boys Walking", 5), ("the two dogs", 2), ("12 cups", 12)):
            with self.subTest(text=text):
                self.assertEqual(quantity_from_text(text)["kind"], "exact")
                self.assertEqual(quantity_from_text(text)["lower"], value)

    def test_plural_and_collective_remain_inexact(self):
        for text in ("people", "dogs", "some dogs", "several workers", "a group of cyclists", "a number of children"):
            with self.subTest(text=text):
                self.assertEqual(quantity_from_text(text)["kind"], "lower_bound")
                self.assertEqual(quantity_from_text(text)["lower"], 2)
                self.assertIsNone(quantity_from_text(text)["upper"])

    def test_unrelated_numbers_are_not_target_quantities(self):
        self.assertEqual(quantity_from_text("a greyhound wearing the number five")["lower"], 1)
        self.assertEqual(quantity_from_text("a white race dog wearing number eight")["lower"], 1)
        for text in ("greyhound wearing number five", "number eight", "grass", "glass", "about three people", "1.5 people", "1/2 person", "two-tailed dog", "3-year-old boy"):
            with self.subTest(text=text):
                self.assertEqual(quantity_from_text(text)["kind"], "unknown")

    def test_declared_bounds(self):
        for text, kind, low, high in (("at least three people", "lower_bound", 3, None),
                                     ("more than three people", "lower_bound", 4, None),
                                     ("up to three people", "range", 0, 3),
                                     ("no more than three people", "range", 0, 3),
                                     ("no fewer than three people", "lower_bound", 3, None),
                                     ("between two and four people", "range", 2, 4),
                                     ("two or three people", "range", 2, 3)):
            with self.subTest(text=text):
                quantity = quantity_from_text(text)
                self.assertEqual((quantity["kind"], quantity["lower"], quantity["upper"]), (kind, low, high))

    def test_collective_units_are_not_confused_with_member_counts(self):
        self.assertEqual(quantity_from_text("a pair of dogs")["lower"], 2)
        self.assertEqual(quantity_from_text("a team of five players")["lower"], 5)
        self.assertEqual(quantity_from_text("two dozen dogs")["lower"], 24)
        self.assertEqual(quantity_from_text("three groups of people")["kind"], "unknown")
        self.assertEqual(quantity_from_text("a pair of scissors")["kind"], "unknown")


class CountGraphTest(unittest.TestCase):
    def test_transitive_containment_cannot_be_disjoint(self):
        groups=[group('a','one person'),group('b','two people'),group('c','three people')]
        edges=[relation('part_of','a','b'),relation('part_of','b','c'),relation('distinct_from','a','c')]
        result=aggregate_count(groups,edges,True)
        self.assertEqual(result['kind'],'unknown')
        self.assertIn('transitive_subset_declared_disjoint',result['issues'])

    def test_disjoint_groups_cannot_share_a_positive_descendant(self):
        groups=[group('x','one person'),group('a','two people'),group('b','three people')]
        edges=[relation('part_of','x','a'),relation('part_of','x','b'),relation('distinct_from','a','b')]
        result=aggregate_count(groups,edges,True)
        self.assertEqual(result['kind'],'unknown')
        self.assertIn('disjoint_groups_share_positive_subset',result['issues'])
    def test_denied_cardinality_is_not_zero_presence(self):
        value = aggregate_count([group("people", "not three people", "negative")], [], True)
        self.assertEqual(value["kind"], "unknown")
        self.assertIn("denied_cardinality_is_not_absence", value["issues"])

    def test_three_people_and_another_man_are_four(self):
        result = aggregate_count([group("lookers", "Three people"), group("climber", "a man")],
                                 [relation("distinct_from", "lookers", "climber")], True)
        self.assertEqual((result["kind"], result["lower"], result["upper"]), ("exact", 4, 4))

    def test_declared_coverage_is_required_for_exact_total(self):
        result = aggregate_count([group("lookers", "Three people"), group("climber", "a man")],
                                 [relation("distinct_from", "lookers", "climber")])
        self.assertEqual((result["kind"], result["lower"], result["upper"]), ("lower_bound", 4, None))
        self.assertIn("coverage_unverified", result["issues"])

    def test_repeated_man_and_he_do_not_add_people(self):
        result = aggregate_count([group("man", "a man"), group("he", "he")],
                                 [relation("same_referent", "man", "he")], True)
        self.assertEqual((result["kind"], result["lower"]), ("exact", 1))

    def test_three_people_including_one_man_stay_three(self):
        result = aggregate_count([group("all", "Three people"), group("man", "one man")],
                                 [relation("part_of", "man", "all")], True)
        self.assertEqual((result["kind"], result["lower"]), ("exact", 3))

    def test_unknown_coreference_blocks_adding_mentions(self):
        result = aggregate_count([group("man", "a man"), group("he", "he")], [], True)
        self.assertEqual((result["kind"], result["lower"]), ("lower_bound", 1))
        self.assertIn("group_overlap_unresolved", result["issues"])

    def test_unknown_plural_is_not_exact(self):
        result = aggregate_count([group("people", "people")], [], True)
        self.assertEqual((result["kind"], result["lower"], result["upper"]), ("lower_bound", 2, None))

    def test_explicit_absence_is_zero_only_with_complete_target_scope(self):
        result = aggregate_count([group("people", "No people", "negative")], [], True)
        self.assertEqual((result["kind"], result["lower"]), ("exact", 0))
        self.assertEqual(aggregate_count([group("people", "No people", "negative")], [])["kind"], "unknown")
        self.assertEqual(aggregate_count([], [], True)["kind"], "unknown")

    def test_negative_group_does_not_cancel_positive_people_elsewhere(self):
        result = aggregate_count([group("boat", "No people", "negative"), group("shore", "a man")], [], True)
        self.assertEqual((result["kind"], result["lower"]), ("exact", 1))

    def test_uncertain_group_prevents_exact_scene_total(self):
        result = aggregate_count([group("known", "two people"), group("possible", "three people", "uncertain")],
                                 [relation("distinct_from", "known", "possible")], True)
        self.assertEqual((result["kind"], result["lower"], result["upper"]), ("lower_bound", 2, None))
        self.assertIn("uncertain_group_presence", result["issues"])

    def test_contradictory_coreference_is_unknown(self):
        result = aggregate_count([group("a", "three people"), group("b", "one man")],
                                 [relation("same_referent", "a", "b")], True)
        self.assertEqual(result["kind"], "unknown")
        self.assertIn("contradictory_coreferent_quantities", result["issues"])

    def test_same_and_distinct_is_contradictory(self):
        result = aggregate_count([group("a", "one man"), group("b", "he")],
                                 [relation("same_referent", "a", "b"), relation("distinct_from", "a", "b")], True)
        self.assertEqual(result["kind"], "unknown")

    def test_subset_cannot_exceed_parent(self):
        result = aggregate_count([group("all", "one person"), group("subset", "three people")],
                                 [relation("part_of", "subset", "all")], True)
        self.assertEqual(result["kind"], "unknown")
        self.assertIn("subset_quantity_exceeds_parent", result["issues"])

    def test_group_range_is_preserved(self):
        result = aggregate_count([group("all", "between two and four people")], [], True)
        self.assertEqual((result["kind"], result["lower"], result["upper"]), ("range", 2, 4))

    def test_nested_subset_bounds_do_not_depend_on_annotation_order(self):
        values = [group("outer", "people"), group("middle", "people"),
                  group("a", "three men"), group("b", "two women")]
        edges = [relation("part_of", "a", "middle"), relation("part_of", "b", "middle"),
                 relation("part_of", "middle", "outer"), relation("distinct_from", "a", "b")]
        result = aggregate_count(values, edges, True)
        self.assertEqual((result["kind"], result["lower"]), ("lower_bound", 5))
        self.assertEqual(result, aggregate_count(list(reversed(values)), list(reversed(edges)), True))

    def test_invalid_identity_and_boolean_quantities_reject(self):
        with self.assertRaises(ValueError):
            aggregate_count([group("same", "one person"), group("same", "one person")], [], True)
        invalid = group("a", "one person")
        invalid["quantity"]["lower"] = True
        with self.assertRaises(ValueError):
            aggregate_count([invalid], [], True)
        with self.assertRaises(ValueError):
            aggregate_count([group("a", "one person")], [relation("part_of", "a", "missing")], True)


if __name__ == "__main__":
    unittest.main()
