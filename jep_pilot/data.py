"""Construct a synthetic Spanish diagnostic with known semantic factors."""

import hashlib
import itertools
import json
import random
from pathlib import Path

SCHEMAS = {
    "reparaciones": {
        "events": ["una disculpa pública", "una indemnización", "un reconocimiento"],
        "results": [
            "restablecer el buen nombre",
            "recuperar el sustento",
            "preservar la memoria",
        ],
        "template": "{actor} solicita {event} para {result} en beneficio de {affected}.",
    },
    "daños": {
        "events": [
            "el desplazamiento",
            "la pérdida de ingresos",
            "el señalamiento social",
        ],
        "results": [
            "aislamiento social",
            "dificultades económicas",
            "sufrimiento emocional",
        ],
        "template": "{actor} relata que {event} provocó {result} para {affected}.",
    },
    "sanciones": {
        "events": [
            "trabajo comunitario",
            "una restricción de libertad",
            "una contribución a la verdad",
        ],
        "results": [
            "reconocer la responsabilidad",
            "prevenir la repetición",
            "reconstruir la confianza",
        ],
        "template": "{actor} propone {event} para {result} en favor de {affected}.",
    },
    "restauración": {
        "events": [
            "un encuentro de diálogo",
            "un proyecto comunitario",
            "un acto de memoria",
        ],
        "results": [
            "reconstruir los vínculos",
            "recuperar el territorio",
            "dignificar a las víctimas",
        ],
        "template": "{actor} pide {event} para {result} en beneficio de {affected}.",
    },
}
ACTORS = ["la representante de las víctimas", "el portavoz de la comunidad"]
AFFECTED = ["las familias", "las personas desplazadas", "la comunidad"]
QUESTIONS = {
    "actor": ("Compara quién habla en los pasajes.", ("actor",)),
    "event": ("Compara el hecho relatado o la acción solicitada.", ("event",)),
    "result": (
        "Compara la consecuencia relatada o la finalidad solicitada.",
        ("result",),
    ),
    "affected": ("Compara quién resulta afectado o beneficiado.", ("affected",)),
    "result_affected": (
        "Compara conjuntamente el resultado y las personas afectadas, con igual peso.",
        ("result", "affected"),
    ),
    "actor_event": (
        "Compara conjuntamente quién habla y la acción o el hecho, con igual peso.",
        ("actor", "event"),
    ),
}


def annotation(row: dict) -> str:
    """Serialize factors with their bindings within one passage."""
    return "; ".join(
        f"{key}: {row[key]}" for key in ("actor", "event", "result", "affected")
    )


def make_data() -> dict[str, list[dict]]:
    """Keep complete cases together and reserve factor combinations."""
    cases: dict[str, list[dict]] = {"train": [], "dev": [], "test": []}
    for category, schema in SCHEMAS.items():
        for a, e, r, b in itertools.product(range(2), range(3), range(3), range(3)):
            row = {
                "category": category,
                "actor": ACTORS[a],
                "event": schema["events"][e],
                "result": schema["results"][r],
                "affected": AFFECTED[b],
            }
            row["case_id"] = hashlib.sha256(
                f"{category}/{a}/{e}/{r}/{b}".encode()
            ).hexdigest()[:16]
            split = (
                "test"
                if (r, b) in {(0, 0), (0, 1), (1, 1)}
                else "dev"
                if (e, a) == (2, 1)
                else "train"
            )
            text = schema["template"].format(**row)
            if split == "dev":
                text = f"Durante su intervención, {text}"
            elif split == "test":
                text = f"Ante la audiencia, {text}"
            row["text"] = text
            row["annotation"] = annotation(row)
            cases[split].append(row)
    result = {}
    for split, rows in cases.items():
        rng = random.Random(101 + len(split))
        keys = list(QUESTIONS) if split == "test" else list(QUESTIONS)[:4]
        pairs = []
        for category in SCHEMAS:
            available = [r for r in rows if r["category"] == category]
            for name in keys:
                question, fields = QUESTIONS[name]
                # Equal sampling by category, condition and available target level.
                buckets: dict[float, list[tuple[dict, dict]]] = {}
                for left, right in itertools.combinations(available, 2):
                    agreement = sum(left[f] == right[f] for f in fields) / len(fields)
                    score = 0.5 + 0.5 * agreement
                    buckets.setdefault(score, []).append((left, right))
                for score, candidates in sorted(buckets.items()):
                    rng.shuffle(candidates)
                    for left, right in candidates[:12]:
                        pairs.append(
                            {
                                "left": left,
                                "right": right,
                                "question": question,
                                "condition": name,
                                "target": score,
                                "transfer": "composed" if len(fields) > 1 else "atomic",
                            }
                        )
        result[split] = pairs
    return result


def write_data(root: Path) -> None:
    """Save fixed inputs and their checksums before any model training."""
    root.mkdir(parents=True, exist_ok=True)
    splits = make_data()
    manifest = {
        "kind": "synthetic_mechanics_diagnostic",
        "expert_labels": False,
        "target": "0.5 + 0.5 * mean agreement on the specified factors",
        "files": {},
    }
    for split, rows in splits.items():
        raw = (json.dumps(rows, ensure_ascii=False, indent=2) + "\n").encode()
        (root / f"{split}.json").write_bytes(raw)
        manifest["files"][split] = {
            "rows": len(rows),
            "sha256": hashlib.sha256(raw).hexdigest(),
        }
    (root / "test_indices.json").write_text(
        json.dumps(list(range(len(splits["test"])))) + "\n"
    )
    (root / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")


if __name__ == "__main__":
    write_data(Path("pilot_data"))
