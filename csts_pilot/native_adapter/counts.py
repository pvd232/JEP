"""Conservative cardinality over source-supported entity/group annotations.

These functions do not establish that a model's annotations follow the source.
The caller must validate span support, target scope, coreference and coverage.
An exact total additionally requires declared complete coverage, exact group
quantities, and explicit disjointness among every surviving group. Mention
frequency is never a counting rule.
"""

from __future__ import annotations

import re
from typing import Any

WORDS = {
    "zero": 0, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
    "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10,
    "eleven": 11, "twelve": 12, "thirteen": 13, "fourteen": 14,
    "fifteen": 15, "sixteen": 16, "seventeen": 17, "eighteen": 18,
    "nineteen": 19, "twenty": 20,
}
NUMBER = r"(?:\d+|" + "|".join(WORDS) + r")"
PLURAL_WORDS = {
    "people", "persons", "men", "women", "children", "boys", "girls",
    "adults", "babies", "kids", "animals", "dogs", "cats", "bears",
    "elephants", "zebras", "cows", "horses", "birds", "cyclists",
    "riders", "workers", "players", "surfers", "skateboarders", "runners",
    "cars", "vehicles", "trucks", "planes", "wheels", "cups", "plates",
    "boxes", "items", "objects", "computers", "sinks", "mirrors",
    "donuts", "doughnuts", "pizzas", "sandwiches", "bottles", "glasses",
}


def _number(text: str) -> int:
    """Read a nonnegative integer already matched by the number grammar."""
    return int(text) if text.isdecimal() else WORDS[text]


def _plural(text: str) -> bool:
    """Recognize declared countable plural nouns without guessing from final s."""
    return bool(set(re.findall(r"[a-z]+", text)) & PLURAL_WORDS)


def quantity_from_text(text: str) -> dict[str, Any]:
    """Read leading cardinality; preserve uncertainty and unrelated number labels.

    Only the beginning of the extracted group/quantity span is interpreted.
    A caption mentioning a jersey number therefore cannot create extra people.
    Unrecognized morphology and approximate counts remain unknown.
    """
    if not isinstance(text, str):
        raise ValueError("Quantity source text must be a string")
    normalized = " ".join(text.casefold().split())
    result = {"kind": "unknown", "lower": None, "upper": None, "source_text": text}

    def interval(lower: int, upper: int | None, consumed: int) -> dict[str, Any]:
        # A successful prefix is insufficient: another cardinal operator,
        # number or unit in its tail can change the target count. Only an
        # explicitly recognizable non-target number label is exempted.
        tail = normalized[consumed:]
        tail = re.sub(rf"\b(?:jersey (?:number )?|number )({NUMBER})\b", "", tail)
        words = re.findall(r"[a-z]+|\d+", tail)
        adjective_modifiers = {"black", "white", "brown", "red", "orange", "blue", "green", "pink", "yellow", "grey", "gray", "large", "small", "big", "little", "young", "old", "tall", "short", "long", "dark", "light", "male", "female"}
        for index, word in enumerate(words):
            if word in {"or", "plus", "another", "others"}:
                return result
            if word == "and" and not (0 < index < len(words)-1 and words[index-1] in adjective_modifiers and words[index+1] in adjective_modifiers):
                return result  # Only declared adjective coordination is safe.
        if re.search(rf"\b{NUMBER}\b|\b(?:hundred|thousand|million|billion|dozen|pair|couple|groups?|sets?|collections?|crowds?|herds?|flocks?|teams?|families|more|less|fewer|least|most|half|quarter|exactly)\b", tail):
            return result
        result.update(kind="exact" if lower == upper else "range" if upper is not None else "lower_bound",
                      lower=lower, upper=upper)
        return result

    if re.match(r"^(?:about|around|roughly|approximately|maybe|possibly|not)\b|^\d+[./]\d", normalized):
        return result
    if re.match(r"^(?:neither|none)\b", normalized):
        # Neither man is running does not mean that there are zero men.
        return result
    if re.search(r"\b(?:or more|or less|or fewer|less than|no less than|half|quarters?)\b", normalized):
        return result  # Unsupported quantifier compositions must not be clipped.
    if "dozen" in normalized and not re.match(rf"^(?:(?:a|one) |{NUMBER} )?dozen(?: of)?(?=\s|$)", normalized):
        return result  # E.g. two-to-three dozen is not a range of two-to-three.
    magnitudes = {"hundred", "thousand", "million", "billion"}
    tokens = re.findall(r"[a-z]+|\d+", normalized)
    for left, right in zip(tokens, tokens[1:]):
        if (left in WORDS or left.isdecimal()) and (right in WORDS or right in magnitudes):
            return result  # Unsupported compound numerals must not lose a suffix.
    singulars = {"person", "man", "woman", "boy", "girl", "child", "dog", "cat", "animal", "bear", "elephant", "zebra", "cow", "horse", "bird", "rider", "worker", "player", "car", "vehicle", "wheel", "cup", "plate", "box", "item", "object", "computer", "donut", "doughnut", "pizza", "sandwich", "pickle", "bottle", "glass"}
    for coordinated in re.split(r"\b(?:and|plus)\b", normalized)[1:]:
        left = normalized.split(coordinated, 1)[0]
        left_nouns = set(re.findall(r"[a-z]+", left)) & (PLURAL_WORDS | singulars)
        right_nouns = set(re.findall(r"[a-z]+", coordinated)) & (PLURAL_WORDS | singulars)
        if left_nouns and (right_nouns or re.match(rf"\s*(?:a|an|{NUMBER})\b", coordinated)):
            return result  # Several groups need separate mentions and union logic.
    # Group phrases must precede the indefinite-article rule: a group is not
    # necessarily one target individual, and a number is not an exact count.
    group = re.match(r"^(?:a |the )?(?:group|number|lot|set|collection|crowd|herd|flock|team|family) of\b\s*(.*)$", normalized)
    if group:
        members = quantity_from_text(group.group(1))
        if members["kind"] == "unknown":
            return result
        return interval(members["lower"], members["upper"], len(normalized))
    pair = re.match(r"^(?:a |the )?(?:pair|couple) of\b\s*(.*)$", normalized)
    if pair:
        return interval(2, 2, pair.start(1)) if _plural(pair.group(1)) else result
    dozen = re.match(rf"^({NUMBER}) dozen(?=\s|$)", normalized)
    if dozen:
        count = 12 * _number(dozen.group(1))
        return interval(count, count, dozen.end())
    plain_dozen = re.match(r"^(?:a |one )?dozen(?=\s|$)", normalized)
    if plain_dozen:
        return interval(12, 12, plain_dozen.end())
    # The number of groups is not the number of target individuals. Their
    # membership, group quantities and overlap need a separate graph.
    if re.match(rf"^({NUMBER}) (?:groups|sets|collections|crowds|herds|flocks|teams|families|pairs) of\b", normalized):
        return result
    plural_quantifier = re.match(r"^(?:some|several|many|a few)\b", normalized)
    if plural_quantifier:
        return interval(2, None, plural_quantifier.end()) if _plural(normalized) else result
    between = re.match(rf"^between ({NUMBER}) and ({NUMBER})(?=\s|$)", normalized)
    if between:
        lower, upper = map(_number, between.groups())
        return interval(lower, upper, between.end()) if lower <= upper else result
    alternatives = re.match(rf"^({NUMBER}) (?:or|to) ({NUMBER})(?=\s|$)", normalized)
    if alternatives:
        lower, upper = map(_number, alternatives.groups())
        return interval(lower, upper, alternatives.end()) if lower <= upper else result
    bounded = re.match(rf"^(at least|more than|at most|fewer than|up to|no more than|no fewer than) ({NUMBER})(?=\s|$)", normalized)
    if bounded:
        operator, raw = bounded.groups()
        count = _number(raw)
        if operator in {"at least", "more than", "no fewer than"}:
            return interval(count + (operator == "more than"), None, bounded.end())
        upper = count - (operator == "fewer than")
        return interval(0, upper, bounded.end()) if upper >= 0 else result
    exact = re.match(rf"^(?:the )?({NUMBER})(?=\s|$)", normalized)
    if exact:
        count = _number(exact.group(1))
        return interval(count, count, exact.end())
    negative = re.match(r"^no\b", normalized)
    if negative:
        return interval(0, 0, negative.end())
    article = re.match(r"^(?:a|an)\b", normalized)
    if article:
        return interval(1, 1, article.end())
    # A bare recognized plural gives a lower bound, never an exact total.
    return interval(2, None, 0) if _plural(normalized) else result


def _quantity(value: Any) -> tuple[int, int | None]:
    """Validate one quantity interval and expose conservative numeric bounds."""
    if not isinstance(value, dict) or value.get("kind") not in {"exact", "range", "lower_bound", "unknown"}:
        raise ValueError("Unknown quantity contract")
    lower, upper = value.get("lower"), value.get("upper")
    if any(x is not None and (type(x) is not int or x < 0) for x in (lower, upper)):
        raise ValueError("Quantity bounds require nonnegative integers")
    kind = value["kind"]
    valid = ((kind == "unknown" and lower is None and upper is None)
             or (kind == "exact" and lower is not None and lower == upper)
             or (kind == "range" and lower is not None and upper is not None and lower < upper)
             or (kind == "lower_bound" and lower is not None and upper is None))
    if not valid:
        raise ValueError("Quantity bounds disagree with their declared kind")
    return (0 if lower is None else lower), upper


def aggregate_count(groups: list[dict[str, Any]], relations: list[dict[str, str]],
                    coverage_complete: bool = False) -> dict[str, Any]:
    """Aggregate declared groups, accounting for identity, containment and overlap.

    Exact totals are conditional on caller-validated source coverage. Unknown
    disjointness yields at most a safe lower bound. Explicit subsets are removed
    from the outer union rather than added again. Contradictions produce an
    unknown result with actionable issues rather than selecting a convenient
    number.
    """
    if type(coverage_complete) is not bool or not isinstance(groups, list) or not isinstance(relations, list):
        raise ValueError("Count graph requires lists and a boolean coverage assertion")
    issues = [] if coverage_complete else ["coverage_unverified"]
    assumptions = ["source_support_and_target_scope_require_caller_validation",
                   "coreference_and_disjointness_use_declared_graph_only"]

    def output(kind="unknown", lower=None, upper=None):
        return {"kind": kind, "lower": lower, "upper": upper,
                "issues": sorted(set(issues)), "assumptions": assumptions,
                "coverage_complete": coverage_complete}

    by_id = {}
    for group in groups:
        if not isinstance(group, dict) or not isinstance(group.get("id"), str) or not group["id"].strip():
            raise ValueError("Each group requires a nonempty id")
        if group["id"] in by_id:
            raise ValueError("Duplicate group id")
        if group.get("polarity") not in {"positive", "negative", "uncertain"}:
            raise ValueError("Unknown group polarity")
        _quantity(group.get("quantity"))
        by_id[group["id"]] = group
    if not by_id:
        issues.append("no_count_evidence")
        return output()
    parent = {identity: identity for identity in by_id}

    def find(identity):
        while parent[identity] != identity:
            parent[identity] = parent[parent[identity]]
            identity = parent[identity]
        return identity

    for relation in relations:
        if not isinstance(relation, dict) or set(relation) != {"predicate", "subject", "object"}:
            raise ValueError("Count relation requires exactly predicate/subject/object")
        if relation["subject"] not in by_id or relation["object"] not in by_id:
            raise ValueError("Count relation references an unknown group")
        if relation["predicate"] not in {"same_referent", "distinct_from", "part_of"}:
            raise ValueError("Unknown count relation")
        if relation["predicate"] == "same_referent":
            parent[find(relation["object"])] = find(relation["subject"])
    components = {}
    for identity, group in by_id.items():
        components.setdefault(find(identity), []).append(group)
    bounds, uncertain, negative = {}, set(), set()
    for identity, mentions in components.items():
        polarities = {group["polarity"] for group in mentions}
        if "negative" in polarities and "positive" in polarities:
            issues.append("contradictory_coreferent_polarity")
            return output()
        if polarities == {"negative"}:
            if any(_quantity(group["quantity"]) != (0, 0) for group in mentions):
                issues.append("denied_cardinality_is_not_absence")
                return output()
            negative.add(identity)
            bounds[identity] = (0, 0)
            continue
        if "uncertain" in polarities:
            uncertain.add(identity)
            issues.append("uncertain_group_presence")
        intervals = [_quantity(group["quantity"]) for group in mentions if group["polarity"] != "negative"]
        lower = max(x[0] for x in intervals)
        finite = [x[1] for x in intervals if x[1] is not None]
        upper = min(finite) if finite else None
        if upper is not None and lower > upper:
            issues.append("contradictory_coreferent_quantities")
            return output()
        bounds[identity] = (0 if identity in uncertain else lower, upper)
    distinct, subsets = set(), set()
    for relation in relations:
        left, right = find(relation["subject"]), find(relation["object"])
        if relation["predicate"] == "distinct_from":
            if left == right:
                issues.append("same_referent_declared_distinct")
                return output()
            distinct.add(frozenset((left, right)))
        elif relation["predicate"] == "part_of" and left != right:
            subsets.add((left, right))
    for left, right in subsets:
        if frozenset((left, right)) in distinct:
            issues.append("subset_declared_disjoint")
            return output()
    # Transitive closure identifies roots and detects containment cycles.
    closure = set(subsets)
    changed = True
    while changed:
        additions = {(a, d) for a, b in closure for c, d in closure if b == c} - closure
        changed = bool(additions)
        closure.update(additions)
    if any(left == right for left, right in closure):
        issues.append("cyclic_part_of")
        return output()
    if any(frozenset((left, right)) in distinct for left, right in closure):
        issues.append("transitive_subset_declared_disjoint")
        return output()
    for pair in distinct:
        left, right = tuple(pair)
        left_members = {left} | {child for child, owner in closure if owner == left}
        right_members = {right} | {child for child, owner in closure if owner == right}
        if any(bounds[child][0] > 0 for child in left_members & right_members):
            issues.append("disjoint_groups_share_positive_subset")
            return output()
    # Propagate bounds until stable so insertion order cannot affect nested
    # containment. Only explicitly disjoint immediate subsets may be summed.
    changed = True
    while changed:
        previous = dict(bounds)
        for child, owner in closure:
            child_lower, _ = bounds[child]
            owner_lower, owner_upper = bounds[owner]
            if owner_upper is not None and child_lower > owner_upper:
                issues.append("subset_quantity_exceeds_parent")
                return output()
            bounds[owner] = (max(owner_lower, child_lower), owner_upper)
        for owner in bounds:
            children = [child for child, ancestor in subsets if ancestor == owner and child not in negative]
            if children and all(frozenset((a, b)) in distinct for i, a in enumerate(children) for b in children[i+1:]):
                minimum = sum(bounds[child][0] for child in children)
                lower, upper = bounds[owner]
                if upper is not None and minimum > upper:
                    issues.append("disjoint_subsets_exceed_parent")
                    return output()
                bounds[owner] = (max(lower, minimum), upper)
        changed = bounds != previous
    roots = [identity for identity in bounds if not any(child == identity for child, _ in closure) and identity not in negative]
    if not roots:
        if coverage_complete and all(identity in negative for identity in bounds):
            return output("exact", 0, 0)
        issues.append("no_positive_count_evidence")
        return output()
    all_disjoint = all(frozenset((left, right)) in distinct
                       for i, left in enumerate(roots) for right in roots[i+1:])
    if not all_disjoint:
        issues.append("group_overlap_unresolved")
    lower = sum(bounds[root][0] for root in roots) if all_disjoint else max(bounds[root][0] for root in roots)
    if uncertain:
        return output("lower_bound", lower, None) if lower else output()
    if coverage_complete and all_disjoint and all(bounds[root][1] is not None for root in roots):
        upper = sum(bounds[root][1] for root in roots)
        return output("exact" if lower == upper else "range", lower, upper)
    return output("lower_bound", lower, None) if lower else output()
