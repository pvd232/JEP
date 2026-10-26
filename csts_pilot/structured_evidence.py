"""Validate caption-supported structured evidence and serialize its meaning."""

import json
from typing import Any


RECORD_KEYS = {"condition", "status", "reason", "entities", "facts"}
ENTITY_KEYS = {"id", "type", "source_quote"}
FACT_KEYS = {"entity_id", "predicate", "value", "source_quote", "support_status", "reason"}
STATUSES = {"answered", "unknown", "ambiguous"}
SUPPORT_STATUSES = {"explicit", "inferred"}


def _keys(value: Any, expected: set[str], label: str) -> None:
    if not isinstance(value, dict) or set(value) != expected:
        raise ValueError(f"{label} requires exactly these keys: {sorted(expected)}")


def _text(value: Any, label: str, allow_empty: bool = False) -> str:
    if not isinstance(value, str) or (not allow_empty and not value.strip()):
        raise ValueError(f"{label} requires a {'possibly empty ' if allow_empty else ''}string")
    return value


def validate_record(record: Any, passage: str, condition: str) -> dict[str, Any]:
    """Check structure, references and quotation support for one caption."""
    _keys(record, RECORD_KEYS, "record")
    _text(record["condition"], "condition")
    if record["condition"] != condition:
        raise ValueError("Condition differs from the supplied condition")
    if _text(record["status"], "record status") not in STATUSES:
        raise ValueError("Unsupported record status")
    _text(record["reason"], "record reason", record["status"] == "answered")
    if not isinstance(record["entities"], list) or not isinstance(record["facts"], list):
        raise ValueError("Entities and facts require lists")
    ids = set()
    for entity in record["entities"]:
        _keys(entity, ENTITY_KEYS, "entity")
        identity = _text(entity["id"], "entity id")
        if identity in ids:
            raise ValueError("Entity IDs require uniqueness")
        ids.add(identity)
        _text(entity["type"], "entity type")
        quote = _text(entity["source_quote"], "entity source quote")
        if quote not in passage:
            raise ValueError("Entity source quote must occur exactly in the caption")
    if record["status"] == "unknown" and record["facts"]:
        raise ValueError("Unknown records require an empty facts list")
    if record["status"] == "answered" and not record["facts"]:
        raise ValueError("Answered records require at least one fact")
    for fact in record["facts"]:
        _keys(fact, FACT_KEYS, "fact")
        if _text(fact["entity_id"], "fact entity id") not in ids:
            raise ValueError("Fact references an unavailable entity")
        for key in ("predicate", "value", "source_quote"):
            _text(fact[key], f"fact {key}")
        if fact["source_quote"] not in passage:
            raise ValueError("Fact source quote must occur exactly in the caption")
        if _text(fact["support_status"], "fact support status") not in SUPPORT_STATUSES:
            raise ValueError("Unsupported fact support status")
        _text(fact["reason"], "fact reason", fact["support_status"] == "explicit")
    return json.loads(json.dumps(record, ensure_ascii=False))


def canonical_text(record: Any, passage: str, condition: str) -> str:
    """Serialize condition-specific facts with stable local entity identities."""
    checked = validate_record(record, passage, condition)

    def text(value: str) -> str:
        return " ".join(value.split())

    def fact_key(fact: dict[str, str]) -> tuple[str, str, str]:
        return tuple(text(fact[k]) for k in ("predicate", "value", "support_status"))

    def entity_key(entity: dict[str, str]) -> tuple:
        facts = sorted(fact_key(f) for f in checked["facts"] if f["entity_id"] == entity["id"])
        return passage.index(entity["source_quote"]), text(entity["type"]), tuple(facts)

    entities = sorted(checked["entities"], key=entity_key)
    identities = {entity["id"]: f"e{i + 1}" for i, entity in enumerate(entities)}
    facts = [
        {
            "entity_id": identities[fact["entity_id"]],
            "predicate": text(fact["predicate"]),
            "value": text(fact["value"]),
            "support_status": fact["support_status"],
        }
        for fact in checked["facts"]
    ]
    facts.sort(key=lambda fact: (fact["entity_id"], *fact_key(fact)))
    return json.dumps(
        {
            "condition": condition,
            "status": checked["status"],
            "entities": [{"id": identities[e["id"]], "type": text(e["type"])} for e in entities],
            "facts": facts,
        },
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
