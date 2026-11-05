"""Prepare, encode and cluster the frozen JEP C-STS COLOR experiment."""

from __future__ import annotations

import argparse
import gc
import hashlib
import importlib.metadata
import json
import os
import re
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path

SOURCE_HASHES = {
    "train": "9a9eac21ee73b9b029ca6f62584891dd13c74aa78e80efd764532a87665ae6a4",
    "validation": "e42d9544b2aa6814708337d0ce38eba1d64124645b62489ed448c6784dbc71ff",
    "test": "d6b40b7b891ed147befb30801c2f85a8787775adebdd98d134157cbb2a6e9f76",
}
ARMS = ("finetuned_conditioned", "pretrained_conditioned", "finetuned_unconditioned")
CONDITIONED = "Instruct: Represent the passage for semantic similarity with respect to this condition: {condition}\nQuery: {passage}"
UNCONDITIONED = (
    "Instruct: Represent the passage for semantic similarity.\nQuery: {passage}"
)
COLOR_WORDS = "black white brown red orange yellow green blue purple pink gray grey tan beige gold golden silver blond blonde cream ivory navy teal turquoise violet maroon burgundy auburn chestnut bronze olive fawn roan palomino".split()
MODIFIERS = "light dark bright pale deep royal fluorescent neon navy jet off reddish yellowish bluish greenish".split()
ALIASES = {"grey": "gray", "blonde": "blond", "golden": "gold"}
ANIMALS = "animal dog cat horse bear cow bull cattle zebra elephant giraffe sheep goat bird duck puppy puppies kitten kittens pony ponies stallion retriever collie dalmatian canine feline cub deer rabbit bison lion tiger pig hog fox monkey ape gorilla penguin".split()
CLOTHING = "clothing clothes outfit apparel attire uniform jersey shirt shirts tshirt t-shirt shorts pants trousers jacket suit coat dress top sweater vest skirt bikini swimsuit swimwear wetsuit trunks hoodie costumes costume cap hat helmet shoes boots socks".split()
VEHICLES = "vehicle bus car truck van train plane airplane aircraft motorcycle bike bicycle boat watercraft kayak canoe vessel scooter sailboat yacht jet".split()
FOOD = "food fruit apple banana orange cake frosting icing sauce wine pizza bread cheese meat rice salad sandwich pasta vegetable carrot".split()
OBJECTS = "object objects item items color colors variety homogeneity".split()
COLOR_RE = re.compile(r"\b(?:" + "|".join(COLOR_WORDS) + r")\b", re.I)


def read(path: Path):
    """Read one UTF-8 JSON record."""
    return json.loads(path.read_text(encoding="utf-8"))


def write(path: Path, value) -> None:
    """Atomically replace one JSON record with canonical readable bytes."""
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    temporary.replace(path)


def sha(path: Path) -> str:
    """Hash a file without retaining its complete bytes in memory."""
    with path.open("rb") as handle:
        return hashlib.file_digest(handle, "sha256").hexdigest()


def point_id(condition: str, sentence: str) -> str:
    """Identify exact prompt components independently of row multiplicity."""
    text = json.dumps([condition, sentence], ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def target_words(condition: str) -> list[str]:
    """Resolve a conservative target vocabulary from the original condition."""
    tokens = set(re.findall(r"[a-z]+", condition.lower()))
    for family, words in (
        ({"animal", "animals", "fur"}, ANIMALS + ["fur"]),
        (
            {
                "clothing",
                "clothes",
                "outfit",
                "outfits",
                "apparel",
                "attire",
                "uniform",
                "uniforms",
            },
            CLOTHING,
        ),
        ({"vehicle", "vehicles", "vessel", "watercraft"}, VEHICLES),
        ({"food", "fruit"}, FOOD),
    ):
        if tokens & family:
            return list(set(words + [w + "s" for w in words]))
    targets = tokens - {
        "color",
        "colors",
        "colour",
        "colours",
        "of",
        "the",
        "a",
        "an",
        "s",
        "person",
        "people",
        "while",
        "on",
        "worn",
        "by",
        "with",
    }
    if not targets or targets <= set(OBJECTS):
        return []
    words = []
    for word in sorted(targets):
        words.append(word)
        if word.endswith("s"):
            words.append(word[:-1])
        else:
            words.append(word + "s")
    return words


def annotate(point: dict) -> dict:
    """Propose source-bound colors only when a target or global scope is explicit."""
    sentence, condition = point["sentence"], point["condition"]
    words = target_words(condition)
    record = {
        "point_id": point["point_id"],
        "target": condition,
        "color_terms": [],
        "color_labels": [],
        "shade": None,
        "status": "unresolved",
        "evidence_kind": "unspecified",
        "evidence": [],
        "rationale": "Target color requires semantic review.",
        "reviewer": "pending",
        "reviewed": False,
    }
    # Ordinal, relational and activity conditions require an explicit later review.
    if re.search(
        r"first|second|caught|pursued|touching|ridden|riding|activity|surfer|jockey|competitor|boxers|runner|children",
        condition,
        re.I,
    ):
        return record
    allowed = (
        COLOR_WORDS
        + MODIFIERS
        + "and or a an large small big little long short haired sleeved sleeve sleeveless teddy tennis baseball basketball football soccer rugby hockey racing golf furry fluffy spotted striped spots stripes polka dot colored coloured patched markings patterned".split()
    )
    bridge = r"(?:[\s,/-]+(?:" + "|".join(allowed) + r"))*[\s-]+"
    if words:
        noun = (
            r"(?:"
            + "|".join(re.escape(w) for w in sorted(set(words), key=len, reverse=True))
            + r")\b"
        )
        pattern = re.compile(
            r"(?:\b(?:light|dark|bright|pale|deep|royal|neon|fluorescent)\s+)?\b(?:"
            + "|".join(COLOR_WORDS)
            + r")\b"
            + bridge
            + noun,
            re.I,
        )
        evidence = [match.group() for match in pattern.finditer(sentence)]
        post = re.compile(
            r"\b"
            + noun
            + r"\s+(?:is|are|was|were)\s+(?:a\s+)?(?:"
            + "|".join(COLOR_WORDS)
            + r")\b(?:[\s,/]+(?:and|"
            + "|".join(COLOR_WORDS + MODIFIERS)
            + r"))*",
            re.I,
        )
        evidence += [match.group() for match in post.finditer(sentence)]
        if set(words) == set(CLOTHING):
            wearing = re.compile(
                r"\b(?:wearing|dressed in|clad in)\s+(?:"
                + "|".join(COLOR_WORDS)
                + r")\b(?:[\s,/-]+(?:and|"
                + "|".join(COLOR_WORDS + MODIFIERS)
                + r"))*",
                re.I,
            )
            evidence += [match.group() for match in wearing.finditer(sentence)]
    else:
        evidence = [sentence] if COLOR_RE.search(sentence) else []
    # Coat markings belong to the animal; collars and nearby objects do not.
    if set(words) & set(ANIMALS):
        anatomy = re.compile(
            r"\b(?:"
            + "|".join(COLOR_WORDS)
            + r")(?:[\s,-]+(?:and|"
            + "|".join(COLOR_WORDS)
            + r"))*\s+(?:fur|coat|spot|spots|patch|patches|marking|markings|paws|tail|ears|face)\b",
            re.I,
        )
        animal_re = re.compile(
            r"\b(?:" + "|".join(ANIMALS + [w + "s" for w in ANIMALS]) + r")\b", re.I
        )
        for match in anatomy.finditer(sentence):
            preceding = list(animal_re.finditer(sentence[: match.start()]))
            if preceding and preceding[-1].group().lower() in set(words):
                evidence.append(match.group())
    terms = []
    for span in evidence:
        for match in COLOR_RE.finditer(span):
            term = match.group().lower()
            # "Navy blue" names the navy shade once.
            if term == "blue" and re.search(r"navy\s+$", span[: match.start()], re.I):
                continue
            terms.append(term)
    labels = sorted({ALIASES.get(term, term) for term in terms})
    if labels:
        record.update(
            color_terms=sorted(set(terms)),
            color_labels=labels,
            evidence=sorted(set(evidence)),
            status="single" if len(labels) == 1 else "multiple",
            evidence_kind="explicit",
            rationale="Explicit color attached to the condition's target by the recorded lexical rule.",
        )
        modifiers = sorted(
            set(
                re.findall(
                    r"\b(light|dark|bright|pale|deep|royal|neon|fluorescent)[-\s]+(?:"
                    + "|".join(COLOR_WORDS)
                    + r")\b",
                    " ".join(evidence),
                    re.I,
                )
            )
        )
        record["shade"] = ", ".join(modifiers) or None
    elif not COLOR_RE.search(sentence):
        record.update(
            status="unspecified",
            rationale="The caption supplies no explicit color term; implied colors remain available for semantic annotation.",
        )
    if (
        record["status"] == "single"
        and set(words) & set(ANIMALS)
        and re.search(
            r"\b(?:dark|light)\s+(?:markings|spots|patches)\b", sentence, re.I
        )
    ):
        record["status"] = "unresolved"
        record["rationale"] = (
            "An additional coat marking has an unspecified dark/light hue."
        )
    return record


def prepare_cohort(dataset: Path, output: Path) -> dict:
    """Verify revision 1.1 and retain every color-related row and exact input."""
    rows = []
    source = {}
    for split, expected in SOURCE_HASHES.items():
        path = dataset / (split + ".json")
        if sha(path) != expected:
            raise ValueError("color cohort: source mismatch")
        source[split] = expected
        rows.extend(dict(row, split=split) for row in read(path))
    inventory = sorted({row["condition"] for row in rows})
    selected = {
        c
        for c in inventory
        if re.search(r"\b(colou?r\w*|hues?|shades?|pigmentation|complexion)\b", c, re.I)
    }
    decisions = [
        {
            "condition": c,
            "selected": c in selected,
            "rationale": "Explicit color-related condition vocabulary."
            if c in selected
            else "Condition does not name a color-related dimension.",
        }
        for c in inventory
    ]
    pairs, points = [], {}
    for row in rows:
        if row["condition"] not in selected:
            continue
        pair = dict(row)
        for side in (1, 2):
            text = row["sentence" + str(side)]
            pid = point_id(row["condition"], text)
            point = points.setdefault(
                pid,
                {
                    "point_id": pid,
                    "condition": row["condition"],
                    "sentence": text,
                    "group_id": row["group_id"],
                    "occurrences": [],
                },
            )
            if point["group_id"] != row["group_id"]:
                raise ValueError("color cohort: source mismatch")
            point["occurrences"].append(
                {"row_id": row["row_id"], "side": str(side), "split": row["split"]}
            )
            pair["point" + str(side) + "_id"] = pid
        pairs.append(pair)
    ordered = sorted(points.values(), key=lambda p: p["point_id"])
    write(output / "condition-filter.json", decisions)
    write(output / "pairs.json", pairs)
    write(output / "points.json", ordered)
    write(output / "color-labels.proposed.json", [annotate(p) for p in ordered])
    probe_points, probes = prepare_probes(ordered)
    write(output / "probe-points.json", probe_points)
    write(output / "switch-probe.json", probes)
    write(
        output / "color-aliases.json",
        {
            "aliases": ALIASES,
            "modifiers_stored_separately": True,
            "named_shades_kept_distinct": True,
        },
    )
    manifest = {
        "dataset_commit": "5dde4314e90f92eb4ac84b122e3b312402b18931",
        "exports": source,
        "pairs": len(pairs),
        "points": len(ordered),
        "row_counts": dict(Counter(p["split"] for p in pairs)),
        "conditions": len(selected),
        "source_groups": len({p["group_id"] for p in ordered}),
    }
    write(output / "cohort-manifest.json", manifest)
    return manifest


def prepare_probes(points: list[dict]) -> tuple[list[dict], list[dict]]:
    """Freeze alternate object-color conditions from explicit source phrases."""
    nouns = (
        ANIMALS
        + CLOTHING
        + VEHICLES
        + [
            "ball",
            "frisbee",
            "umbrella",
            "plate",
            "flower",
            "chair",
            "collar",
            "board",
            "surfboard",
            "toy",
            "hat",
            "helmet",
            "guitar",
            "sign",
        ]
    )
    expression = re.compile(
        r"\b("
        + "|".join(COLOR_WORDS)
        + r")\s+(?:tennis\s+|soccer\s+)?("
        + "|".join(sorted(set(nouns), key=len, reverse=True))
        + r")\b",
        re.I,
    )
    by_sentence = {p["sentence"]: p for p in points}
    existing = {p["point_id"] for p in points}
    additional, probes = {}, []
    for sentence in sorted(
        by_sentence, key=lambda s: hashlib.sha256(s.encode()).hexdigest()
    ):
        matches = list(expression.finditer(sentence))
        chosen = None
        for left in matches:
            for right in matches:
                a, b = (
                    ALIASES.get(left[1].lower(), left[1].lower()),
                    ALIASES.get(right[1].lower(), right[1].lower()),
                )
                if left[2].lower() != right[2].lower() and a != b:
                    left_label = annotate(
                        {
                            "point_id": "probe-left",
                            "condition": "color of " + left[2].lower(),
                            "sentence": sentence,
                        }
                    )
                    right_label = annotate(
                        {
                            "point_id": "probe-right",
                            "condition": "color of " + right[2].lower(),
                            "sentence": sentence,
                        }
                    )
                    if left_label["color_labels"] != [a] or right_label[
                        "color_labels"
                    ] != [b]:
                        continue
                    if (
                        sum(m[2].lower() == left[2].lower() for m in matches) > 1
                        or sum(m[2].lower() == right[2].lower() for m in matches) > 1
                    ):
                        continue
                    chosen = (left, right, a, b)
                    break
            if chosen:
                break
        if chosen is None:
            continue
        left, right, a, b = chosen
        parent = by_sentence[sentence]
        ids = []
        for match in (left, right):
            condition = "color of " + match[2].lower()
            pid = point_id(condition, sentence)
            ids.append(pid)
            if pid not in existing:
                additional[pid] = {
                    "point_id": pid,
                    "condition": condition,
                    "sentence": sentence,
                    "group_id": parent["group_id"],
                    "occurrences": parent["occurrences"],
                }
        probes.append(
            {
                "sentence": sentence,
                "group_id": parent["group_id"],
                "indices": ids,
                "colors": [a, b],
                "conditions": [
                    "color of " + left[2].lower(),
                    "color of " + right[2].lower(),
                ],
                "evidence": [left.group(), right.group()],
                "reviewer": "explicit distinct-object phrase rule; runtime assistant reviewed rule",
                "label_source": "original caption before model output",
            }
        )
        if len(probes) == 50:
            break
    return sorted(additional.values(), key=lambda p: p["point_id"]), probes


def validate_labels(points: list[dict], labels: list[dict]) -> None:
    """Require one reviewed source-backed annotation for each original input."""
    source = {p["point_id"]: p for p in points}
    if len(labels) != len(source) or {a["point_id"] for a in labels} != set(source):
        raise ValueError("color label: missing target evidence")
    for label in labels:
        if not label["reviewed"] or label["status"] not in {
            "single",
            "multiple",
            "unspecified",
            "unresolved",
        }:
            raise ValueError("color label: missing target evidence")
        if label["status"] in {"single", "multiple"}:
            if (
                not label["color_labels"]
                or not label["evidence"]
                or not label["rationale"]
            ):
                raise ValueError("color label: missing target evidence")
            if label["evidence_kind"] == "explicit" and any(
                span.lower() not in source[label["point_id"]]["sentence"].lower()
                for span in label["evidence"]
            ):
                raise ValueError("color label: missing target evidence")
            if (label["status"] == "single") != (len(label["color_labels"]) == 1):
                raise ValueError("color label: missing target evidence")


def resolve_encoder(manifest: dict) -> dict:
    """Verify immutable checkpoint identity and required extraction settings."""
    for field in (
        "checkpoint",
        "checkpoint_sha256",
        "source_repository",
        "source_commit",
        "config",
        "source_result",
    ):
        if not manifest.get(field):
            raise ValueError("encoder identity: checkpoint mismatch")
    if sha(Path(manifest["checkpoint"])) != manifest["checkpoint_sha256"]:
        raise ValueError("encoder identity: checkpoint mismatch")
    if manifest["config"].get("embedding_dimension") != 4096:
        raise ValueError("encoder identity: checkpoint mismatch")
    return manifest


def validate_vectors(vectors, count: int, dimension: int = 4096) -> None:
    """Require finite float32 unit vectors in the declared point order."""
    import numpy as np

    if (
        vectors.shape != (count, dimension)
        or vectors.dtype != np.float32
        or not np.isfinite(vectors).all()
        or not np.allclose(np.linalg.norm(vectors, axis=1), 1, atol=2e-5, rtol=0)
    ):
        raise ValueError("embedding cache: identity mismatch")


def encode_inputs(output: Path, manifest_path: Path) -> None:
    """Reuse exact archived vectors and encode only missing arm/input tuples."""
    import numpy as np
    import torch

    manifest = resolve_encoder(read(manifest_path))
    original_points = read(output / "points.json")
    validate_labels(original_points, read(output / "color-labels.json"))
    probe_points = read(output / "probe-points.json")
    points = original_points + probe_points
    sys.path.insert(0, manifest["source_repository"])
    from csts_pilot.baseline_models import (
        FitConfig,
        encode,
        load_backbone,
        load_tokenizer,
    )

    cfg = FitConfig.model_validate(manifest["config"])
    tokenizer = load_tokenizer(cfg)
    saved = torch.load(manifest["checkpoint"], map_location="cpu", weights_only=False)
    model = None
    try:
        for arm in ARMS:
            target = output / "embeddings" / (arm + ".npz")
            identity = {
                "points_sha256": sha(output / "points.json"),
                "probe_points_sha256": sha(output / "probe-points.json"),
                "model_manifest_sha256": hashlib.sha256(
                    json.dumps(
                        {
                            k: v
                            for k, v in manifest.items()
                            if k not in {"checkpoint", "source_repository"}
                        },
                        sort_keys=True,
                    ).encode()
                ).hexdigest(),
                "labels_sha256": sha(output / "color-labels.json"),
                "arm": arm,
                "prompt": UNCONDITIONED
                if arm.endswith("unconditioned")
                else CONDITIONED,
            }
            sidecar = target.with_suffix(".json")
            if target.exists() and sidecar.exists():
                previous = read(sidecar)
                if previous.get("identity") != identity:
                    raise ValueError("embedding cache: identity mismatch")
                existing = np.load(target)
                validate_vectors(existing["vectors"], len(original_points))
                probe_cache = np.load(target.with_name(arm + "-probes.npz"))
                validate_vectors(probe_cache["vectors"], len(probe_points))
                continue
            if model is not None:
                del model
                model = None
                gc.collect()
                torch.cuda.empty_cache()
            model = load_backbone(
                cfg, adapters=None if arm == "pretrained_conditioned" else cfg
            )
            if arm != "pretrained_conditioned":
                state_key = manifest["adapter_state_key"]
                loaded = model.load_state_dict(saved[state_key], strict=False)
                if loaded.unexpected_keys or any(
                    "lora_" in k for k in loaded.missing_keys
                ):
                    raise ValueError("encoder identity: checkpoint mismatch")
                current = model.state_dict()
                if any(
                    not torch.equal(current[k].cpu(), v)
                    for k, v in saved[state_key].items()
                ):
                    raise ValueError("encoder identity: checkpoint mismatch")
                del current
            model.eval()
            for parameter in model.parameters():
                parameter.requires_grad_(False)
            texts = [
                identity["prompt"].format(
                    condition=p["condition"], passage=p["sentence"]
                )
                for p in points
            ]
            tokens = tokenizer(
                texts, padding=False, truncation=False, add_special_tokens=False
            )["input_ids"]
            end = tokenizer.get_vocab()["<|endoftext|>"]
            sequences = [ids + [end] for ids in tokens]
            if max(map(len, sequences)) > cfg.max_length:
                raise ValueError("encoder identity: token ceiling exceeded")
            vectors = np.empty((len(points), 4096), dtype=np.float32)
            reused = 0
            archived = manifest.get("embedding_caches", {}).get(arm)
            missing = list(range(len(points)))
            if archived:
                cache = torch.load(
                    archived["path"], map_location="cpu", weights_only=False
                )
                if sha(Path(archived["path"])) != archived["sha256"]:
                    raise ValueError("embedding cache: identity mismatch")
                lookup = {
                    tuple(key): i for i, key in enumerate(cache[archived["keys_key"]])
                }
                missing = []
                cached_vectors = cache[archived["vectors_key"]]
                for i, point in enumerate(points):
                    key = (point["condition"], point["sentence"])
                    if key in lookup:
                        vectors[i] = cached_vectors[lookup[key]].float().numpy()
                        reused += 1
                    else:
                        missing.append(i)
            started = time.time()
            with torch.inference_mode():
                for start in range(0, len(missing), cfg.encode_batch_size):
                    indices = missing[start : start + cfg.encode_batch_size]
                    batch = tokenizer.pad(
                        {
                            "input_ids": [sequences[i] for i in indices],
                            "attention_mask": [
                                [1] * len(sequences[i]) for i in indices
                            ],
                        },
                        padding=True,
                        return_tensors="pt",
                    )
                    batch = {
                        k: v.to(cfg.device)
                        for k, v in batch.items()
                        if k in {"input_ids", "attention_mask"}
                    }
                    vectors[indices] = encode(model, batch).cpu().numpy()
                    write(
                        output / "status.json",
                        {
                            "stage": "embedding",
                            "arm": arm,
                            "completed": min(
                                start + cfg.encode_batch_size, len(missing)
                            ),
                            "missing": len(missing),
                            "reused": reused,
                            "seconds": round(time.time() - started, 1),
                        },
                    )
            validate_vectors(vectors, len(points))
            target.parent.mkdir(exist_ok=True)
            n = len(original_points)
            np.savez_compressed(
                target,
                point_ids=np.array([p["point_id"] for p in original_points]),
                vectors=vectors[:n],
            )
            np.savez_compressed(
                target.with_name(arm + "-probes.npz"),
                point_ids=np.array([p["point_id"] for p in probe_points]),
                vectors=vectors[n:],
            )
            write(
                sidecar,
                {
                    "identity": identity,
                    "vector_sha256": sha(target),
                    "reused": reused,
                    "encoded": len(missing),
                    "seconds": time.time() - started,
                },
            )
    finally:
        if model is not None:
            del model
        torch.cuda.empty_cache()


def select_k(records: list[dict], metric: str = "silhouette") -> int | None:
    """Select K solely by median cosine silhouette, preferring smaller ties."""
    import numpy as np

    if metric != "silhouette":
        raise ValueError("metric policy: unsupported selection")
    scores = defaultdict(list)
    for row in records:
        if row.get("silhouette") is not None:
            scores[row["k"]].append(row["silhouette"])
    if not scores:
        return None
    medians = {k: float(np.median(v)) for k, v in scores.items()}
    maximum = max(medians.values())
    return min(k for k, value in medians.items() if maximum - value <= 1e-6)


def validate_sweep(records: list[dict], grid: list[int]) -> None:
    """Require exactly twenty unique seeded results for every declared K."""
    expected = {(k, seed) for k in grid for seed in range(20)}
    actual = [(row["k"], row["seed"]) for row in records]
    if len(actual) != len(set(actual)) or set(actual) != expected:
        raise ValueError("kmeans sweep: incomplete grid")


def score_sweep(points: list[dict], pairs: list[dict], vectors, split: str) -> dict:
    """Reconnect retained original pairs and correlate their cosine with ratings."""
    import numpy as np
    from scipy.stats import spearmanr

    lookup = {p["point_id"]: i for i, p in enumerate(points)}
    cohort = [p for p in pairs if split == "pooled" or p["split"] == split]
    if any(p[key] not in lookup for p in cohort for key in ("point1_id", "point2_id")):
        raise ValueError("metric policy: unsupported selection")
    predictions = np.array(
        [
            float(vectors[lookup[p["point1_id"]]] @ vectors[lookup[p["point2_id"]]])
            for p in cohort
        ]
    )
    ratings = np.array([p["rating"] for p in cohort])
    rho = (
        float(spearmanr(predictions, ratings).statistic)
        if len(cohort) > 1
        else float("nan")
    )
    return {
        "pairs": len(cohort),
        "spearman": rho if np.isfinite(rho) else None,
        "undefined_reason": None
        if np.isfinite(rho)
        else "Insufficient pairs or constant scores/ratings.",
        "predictions": predictions.tolist(),
        "ratings": ratings.tolist(),
        "groups": [p["group_id"] for p in cohort],
    }


def validate_prototype_families(probe_group: str, families: set[str]) -> None:
    """Reject a color prototype that contains the probe's source family."""
    if probe_group in families:
        raise ValueError("condition switch: prototype overlap")


def score_condition_switch(output: Path, arm: str, vectors) -> dict:
    """Score source-derived alternate conditions using other-family prototypes."""
    import numpy as np

    points = read(output / "points.json")
    extra = read(output / "probe-points.json")
    if extra:
        probe_cache = np.load(output / "embeddings" / (arm + "-probes.npz"))
        if probe_cache["point_ids"].tolist() != [p["point_id"] for p in extra]:
            raise ValueError("embedding cache: identity mismatch")
        vectors = np.concatenate([vectors, probe_cache["vectors"]])
        points = points + extra
    labels = read(output / "color-labels.json")
    lookup = {p["point_id"]: i for i, p in enumerate(points)}
    prototypes = defaultdict(list)
    for label in labels:
        if label["status"] == "single":
            index = lookup[label["point_id"]]
            prototypes[label["color_labels"][0]].append(index)
    probes = (
        read(output / "switch-probe.json")
        if (output / "switch-probe.json").exists()
        else []
    )
    rows = []
    for probe in probes:
        indices = probe.get("indices", [])
        if len(indices) != 2 or any(pid not in lookup for pid in indices):
            rows.append(
                dict(
                    probe,
                    status="undefined",
                    reason="Alternate-condition vectors are unavailable.",
                )
            )
            continue
        means = []
        for color in probe["colors"]:
            selected = [
                i
                for i in prototypes[color]
                if points[i]["group_id"] != probe["group_id"]
            ]
            families = {points[i]["group_id"] for i in selected}
            validate_prototype_families(probe["group_id"], families)
            if len(families) < 5:
                break
            mean = vectors[selected].mean(axis=0)
            means.append(mean / np.linalg.norm(mean))
        if len(means) != 2:
            rows.append(
                dict(
                    probe,
                    status="undefined",
                    reason="Fewer than five other families represent a requested color.",
                )
            )
            continue
        a, b = (vectors[lookup[pid]] for pid in indices)
        margins = [
            float(a @ means[0] - a @ means[1]),
            float(b @ means[1] - b @ means[0]),
        ]
        rows.append(
            dict(
                probe,
                status="scored",
                margins=margins,
                mean_margin=sum(margins) / 2,
                both_positive=all(m > 0 for m in margins),
            )
        )
    scored = [r for r in rows if r["status"] == "scored"]
    return {
        "arm": arm,
        "selected": len(rows),
        "scored": len(scored),
        "mean_bidirectional_margin": float(np.mean([r["mean_margin"] for r in scored]))
        if scored
        else None,
        "both_directions_positive_rate": float(
            np.mean([r["both_positive"] for r in scored])
        )
        if scored
        else None,
        "rows": rows,
    }


def fit_sweep(output: Path) -> None:
    """Retain the full normalized-vector K sweep and paired source-family analysis."""
    import itertools
    from concurrent.futures import ThreadPoolExecutor

    import numpy as np
    from sklearn.cluster import KMeans
    from sklearn.metrics import adjusted_rand_score, silhouette_score
    from threadpoolctl import threadpool_limits

    threadpool_limits(limits=1)
    points, pairs = read(output / "points.json"), read(output / "pairs.json")
    labels = read(output / "color-labels.json")
    validate_labels(points, labels)
    by_id = {a["point_id"]: a for a in labels}
    results = {
        "cohorts": {},
        "pair_similarity": {},
        "switch": {},
        "runtime_versions": {
            name: importlib.metadata.version(name)
            for name in (
                "numpy",
                "scipy",
                "scikit-learn",
                "torch",
                "transformers",
                "peft",
            )
        },
    }
    all_vectors = {}
    for arm in ARMS:
        cache = np.load(output / "embeddings" / (arm + ".npz"))
        if cache["point_ids"].tolist() != [p["point_id"] for p in points]:
            raise ValueError("embedding cache: identity mismatch")
        all_vectors[arm] = cache["vectors"]
        validate_vectors(cache["vectors"], len(points))
        results["pair_similarity"][arm] = {
            split: score_sweep(points, pairs, cache["vectors"], split)
            for split in ("train", "validation", "test", "pooled")
        }
        results["switch"][arm] = score_condition_switch(output, arm, cache["vectors"])
    for split in ("validation", "train", "test", "pooled"):
        split_indices = [
            i
            for i, p in enumerate(points)
            if split == "pooled" or any(o["split"] == split for o in p["occurrences"])
        ]
        for kind in ("single", "all"):
            indices = [
                i
                for i in split_indices
                if kind == "all" or by_id[points[i]["point_id"]]["status"] == "single"
            ]
            truth_indices = [
                j
                for j, i in enumerate(indices)
                if by_id[points[i]["point_id"]]["status"] == "single"
            ]
            truth = [
                by_id[points[indices[j]]["point_id"]]["color_labels"][0]
                for j in truth_indices
            ]
            color_count = len(set(truth))
            cohort_name = split + "_" + kind
            cohort = {
                "split": split,
                "kind": kind,
                "points": len(indices),
                "labeled": len(truth),
                "colors": color_count,
                "color_counts": dict(Counter(truth)),
                "point_ids": [points[i]["point_id"] for i in indices],
                "arms": {},
            }
            results["cohorts"][cohort_name] = cohort
            if color_count < 2 or len(indices) < 3:
                cohort["undefined_reason"] = (
                    "Fewer than two represented colors or three points."
                )
                continue
            grid = list(range(2, min(2 * color_count, len(indices) - 1) + 1))
            for arm in ARMS:
                x = all_vectors[arm][indices]
                distances = np.maximum(0, 1 - x @ x.T)
                np.fill_diagonal(distances, 0)
                folder = output / "clusters" / cohort_name / arm
                folder.mkdir(parents=True, exist_ok=True)
                unique = len(np.unique(x, axis=0))

                def fit_one(job: tuple[int, int]) -> dict:
                    """Fit one independently seeded clustering and retain its full state."""
                    k, seed = job
                    path = folder / (str(k) + "-" + str(seed) + ".npz")
                    if path.exists():
                        saved_run = np.load(path)
                        return json.loads(str(saved_run["record"]))
                    record = {
                        "k": k,
                        "seed": seed,
                        "ari": None,
                        "silhouette": None,
                        "inertia": None,
                        "iterations": None,
                        "converged": None,
                        "undefined_reason": None,
                    }
                    if k > unique:
                        record["undefined_reason"] = (
                            "K exceeds the number of distinct input vectors."
                        )
                        return record
                    model = KMeans(
                        n_clusters=k,
                        init="k-means++",
                        n_init=1,
                        random_state=seed,
                        max_iter=500,
                        tol=1e-4,
                        algorithm="lloyd",
                    )
                    assigned = model.fit_predict(x)
                    observed = len(set(assigned))
                    record.update(
                        ari=float(adjusted_rand_score(truth, assigned[truth_indices])),
                        silhouette=float(
                            silhouette_score(distances, assigned, metric="precomputed")
                        )
                        if 1 < observed < len(x)
                        else None,
                        inertia=float(model.inertia_),
                        iterations=int(model.n_iter_),
                        converged=bool(model.n_iter_ < 500),
                    )
                    np.savez_compressed(
                        path,
                        point_ids=np.array(cohort["point_ids"]),
                        assignments=assigned,
                        centroids=model.cluster_centers_,
                        record=np.array(json.dumps(record)),
                    )
                    return record

                with ThreadPoolExecutor(
                    max_workers=min(4, os.cpu_count() or 1)
                ) as pool:
                    records = list(
                        pool.map(fit_one, itertools.product(grid, range(20)))
                    )
                validate_sweep(records, grid)
                selected = select_k(records)
                fixed = [
                    r for r in records if r["k"] == color_count and r["ari"] is not None
                ]
                stability = []
                if selected is not None:
                    assignments = [
                        np.load(folder / (str(selected) + "-" + str(seed) + ".npz"))[
                            "assignments"
                        ]
                        for seed in range(20)
                    ]
                    stability = [
                        adjusted_rand_score(a, b)
                        for a, b in itertools.combinations(assignments, 2)
                    ]
                cohort["arms"][arm] = {
                    "grid": grid,
                    "runs": records,
                    "k_star": selected,
                    "k_near_color_count": abs(selected - color_count)
                    <= max(1, int(np.ceil(0.25 * color_count)))
                    if selected is not None
                    else None,
                    "median_ari_at_C": float(np.median([r["ari"] for r in fixed]))
                    if fixed
                    else None,
                    "ari_at_C_iqr": np.percentile(
                        [r["ari"] for r in fixed], [25, 75]
                    ).tolist()
                    if fixed
                    else None,
                    "median_seed_stability": float(np.median(stability))
                    if stability
                    else None,
                }
                write(output / "metrics.partial.json", results)
                write(
                    output / "status.json",
                    {
                        "stage": "clustering",
                        "cohort": cohort_name,
                        "arm": arm,
                        "fits": len(records),
                        "colors": color_count,
                    },
                )
                print("clustered", cohort_name, arm, "fits", len(records), flush=True)
    results["paired_intervals"] = bootstrap_comparisons(
        output, results, points, all_vectors
    )
    write(output / "metrics.json", results)
    write(
        output / "status.json",
        {"stage": "complete", "cohorts": len(results["cohorts"])},
    )


def bootstrap_comparisons(
    output: Path, results: dict, points: list[dict], vectors: dict
) -> dict:
    """Rescore fixed validation fits under paired caption-component resampling."""
    import numpy as np
    from scipy.stats import spearmanr
    from sklearn.metrics import adjusted_rand_score

    rng = np.random.default_rng(20261104)
    cohort = results["cohorts"]["validation_single"]
    lookup = {p["point_id"]: p for p in points}
    labels = {a["point_id"]: a for a in read(output / "color-labels.json")}
    ids = cohort["point_ids"]
    groups = sorted({lookup[pid]["group_id"] for pid in ids})
    grouped = {
        g: [i for i, pid in enumerate(ids) if lookup[pid]["group_id"] == g]
        for g in groups
    }
    truth = np.array([labels[pid]["color_labels"][0] for pid in ids])
    assignments = {}
    k = cohort["colors"]
    for arm in ARMS:
        assignments[arm] = [
            np.load(
                output
                / "clusters"
                / "validation_single"
                / arm
                / (str(k) + "-" + str(seed) + ".npz")
            )["assignments"]
            for seed in range(20)
        ]
    pair = results["pair_similarity"][ARMS[0]]["validation"]
    pair_groups = sorted(set(pair["groups"]))
    pair_grouped = {
        g: [i for i, x in enumerate(pair["groups"]) if x == g] for g in pair_groups
    }
    values = {control: {"delta_ari": [], "delta_spearman": []} for control in ARMS[1:]}
    for _ in range(1000):
        ix = np.concatenate(
            [grouped[g] for g in rng.choice(groups, len(groups), replace=True)]
        )
        scores = {
            arm: float(
                np.median(
                    [adjusted_rand_score(truth[ix], a[ix]) for a in assignments[arm]]
                )
            )
            for arm in ARMS
        }
        px = np.concatenate(
            [
                pair_grouped[g]
                for g in rng.choice(pair_groups, len(pair_groups), replace=True)
            ]
        )
        rhos = {
            arm: float(
                spearmanr(
                    np.array(
                        results["pair_similarity"][arm]["validation"]["predictions"]
                    )[px],
                    np.array(pair["ratings"])[px],
                ).statistic
            )
            for arm in ARMS
        }
        for control in ARMS[1:]:
            values[control]["delta_ari"].append(scores[ARMS[0]] - scores[control])
            if np.isfinite(rhos[ARMS[0]]) and np.isfinite(rhos[control]):
                values[control]["delta_spearman"].append(rhos[ARMS[0]] - rhos[control])
    answer = {}
    for control, metrics in values.items():
        answer[control] = {
            name: {
                "valid_draws": len(vals),
                "interval_95": np.percentile(vals, [2.5, 97.5]).tolist()
                if len(vals) >= 950
                else None,
                "conditional_on_fixed_fits": True,
            }
            for name, vals in metrics.items()
        }
    return answer


def validate_report(metrics: dict) -> None:
    """Require all arms and every declared seeded fit before rendering a report."""
    primary = metrics.get("cohorts", {}).get("validation_single", {})
    if set(primary.get("arms", {})) != set(ARMS):
        raise ValueError("report: incomplete evidence")
    for data in metrics["cohorts"].values():
        for result in data["arms"].values():
            try:
                validate_sweep(result["runs"], result["grid"])
            except ValueError as error:
                raise ValueError("report: incomplete evidence") from error


def write_report(output: Path) -> None:
    """Build a measured report and curves from the complete retained sweep."""
    import matplotlib
    import numpy as np

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    metrics = read(output / "metrics.json")
    validate_report(metrics)
    cohort = metrics["cohorts"].get("validation_single", {})
    if set(cohort.get("arms", {})) != set(ARMS):
        raise ValueError("report: incomplete evidence")
    for data in metrics["cohorts"].values():
        for result in data["arms"].values():
            validate_sweep(result["runs"], result["grid"])
    lines = [
        "# C-STS COLOR Clustering Results",
        "",
        "The main analysis uses validation points with one reviewed source color. Training, test and pooled analyses are descriptive.",
        "",
        "| Arm | ARI at C, median | Silhouette-selected K | Near C | Color-pair Spearman |",
        "|---|---:|---:|---|---:|",
    ]
    for arm in ARMS:
        data = cohort["arms"][arm]
        rho = metrics["pair_similarity"][arm]["validation"]["spearman"]
        lines.append(
            f"| {arm} | {data['median_ari_at_C']:.4f} | {data['k_star']} | {data['k_near_color_count']} | {rho:.4f} |"
        )
    lines += [
        "",
        f"Primary cohort: {cohort['points']} points and {cohort['colors']} represented color labels.",
        "",
        "## Color Labels",
        "",
        "Annotations use reviewed explicit target-binding rules and retained source evidence. Ambiguous target assignments remain unresolved. Spelling variants are merged; named colors remain distinct and shade modifiers are recorded separately.",
        "",
        "## Paired Validation Comparisons",
        "",
        "Intervals resample connected-caption components and rescore the retained fits. Initialization variation is retained per seed.",
        "",
        "```json",
        json.dumps(metrics["paired_intervals"], indent=2),
        "```",
        "",
        "## Condition Switching",
        "",
        "| Arm | Scored probes | Mean bidirectional margin | Both directions positive |",
        "|---|---:|---:|---:|",
    ]
    for arm in ARMS:
        switch = metrics["switch"][arm]
        lines.append(
            f"| {arm} | {switch['scored']}/{switch['selected']} | {switch['mean_bidirectional_margin']} | {switch['both_directions_positive_rate']} |"
        )
    figures = output / "figures"
    figures.mkdir(exist_ok=True)
    fig, axes = plt.subplots(1, 2, figsize=(11, 4))
    for arm in ARMS:
        records = cohort["arms"][arm]["runs"]
        grid = cohort["arms"][arm]["grid"]
        for ax, metric in zip(axes, ("ari", "silhouette")):
            values = [
                [r[metric] for r in records if r["k"] == k and r[metric] is not None]
                for k in grid
            ]
            middle = [float(np.median(v)) if v else np.nan for v in values]
            ax.plot(grid, middle, label=arm.replace("_", " "))
            ax.set(xlabel="K", ylabel=metric)
            ax.axvline(cohort["colors"], color="gray", ls="--", lw=1)
        axes[0].legend(fontsize=7)
    fig.tight_layout()
    fig.savefig(figures / "validation-k-sweep.png", dpi=180)
    plt.close(fig)
    lines += [
        "",
        "![Validation K sweep](figures/validation-k-sweep.png)",
        "",
        "## Retained Evidence",
        "",
        "All split/cohort/arm/K/seed scores and undefined reasons are in `metrics.json`. Original pair links, source labels, model identities, vectors and cluster assignments are retained with the run.",
    ]
    (output / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    write(
        output / "run-receipt.json",
        {
            "status": "complete",
            "cohort_manifest_sha256": sha(output / "cohort-manifest.json"),
            "labels_sha256": sha(output / "color-labels.json"),
            "metrics_sha256": sha(output / "metrics.json"),
            "report_sha256": sha(output / "report.md"),
            "runtime_versions": metrics["runtime_versions"],
        },
    )


def main() -> None:
    """Run one explicit stage using its retained input paths."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("stage", choices=("prepare", "encode", "cluster", "report"))
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--dataset", type=Path)
    parser.add_argument("--model-manifest", type=Path)
    args = parser.parse_args()
    if args.stage == "prepare":
        print(json.dumps(prepare_cohort(args.dataset, args.output)))
    elif args.stage == "encode":
        encode_inputs(args.output, args.model_manifest)
    elif args.stage == "cluster":
        fit_sweep(args.output)
    else:
        write_report(args.output)


if __name__ == "__main__":
    main()
