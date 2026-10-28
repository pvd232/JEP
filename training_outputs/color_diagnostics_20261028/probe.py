"""Build color probes and preserve the provenance of proposed labels."""

import argparse
import hashlib
import json
import re
from collections import Counter
from pathlib import Path


COLORS = ["red", "blue", "green", "yellow", "orange", "purple", "pink", "brown", "black", "white"]
OBJECTS = [
    ("lantern", "on a workshop shelf", "beside a tool chest"),
    ("suitcase", "near a station bench", "beside a ticket machine"),
    ("watering can", "inside a greenhouse", "next to a seed tray"),
    ("kite", "above a quiet meadow", "above a sandy beach"),
    ("teapot", "on a kitchen counter", "on a breakfast table"),
    ("helmet", "inside a bicycle basket", "beside a bicycle wheel"),
    ("scarf", "on a coat hook", "across a chair back"),
    ("backpack", "under a classroom desk", "beside a classroom door"),
    ("umbrella", "inside a hallway stand", "against a porch railing"),
    ("vase", "on a windowsill", "on a mantel"),
    ("bucket", "beside a garden gate", "beside a potting bench"),
    ("sweater", "on a bedroom chair", "inside an open closet"),
    ("canoe", "on a lake shore", "beside a wooden dock"),
    ("ribbon", "around a gift box", "on a gift bag"),
    ("cushion", "on a patio chair", "on a porch swing"),
    ("wagon", "under an apple tree", "near a garden shed"),
    ("boot", "beside a cabin door", "under a cabin bench"),
    ("jacket", "on a locker hook", "over a locker door"),
    ("banner", "above a market stall", "above a theater entrance"),
    ("apron", "on a bakery hook", "across a bakery stool"),
    ("mug", "beside a notebook", "beside a reading lamp"),
    ("blanket", "across a park bench", "over a picnic chair"),
    ("basket", "under a fruit stand", "beside a market scale"),
    ("paddle", "inside a boathouse", "outside a boathouse"),
    ("glove", "on a workbench", "inside a toolbox"),
    ("tent", "beside a hiking trail", "beside a mountain stream"),
    ("flag", "above a harbor office", "above a marina gate"),
    ("stool", "beside an easel", "beside a pottery wheel"),
    ("bottle", "inside a lunch bag", "beside a lunch tray"),
    ("folder", "on a reception desk", "inside a document rack"),
]
PAIRS = [
    ("cup", "saucer", "on a cafe table"), ("coat", "hat", "on a hallway rack"),
    ("chair", "desk", "inside an office"), ("pail", "shovel", "on a beach"),
    ("truck", "trailer", "beside a warehouse"), ("plate", "bowl", "on a dining table"),
    ("candle", "holder", "on a mantel"), ("pen", "notebook", "on a library desk"),
    ("shoe", "sock", "on a bedroom rug"), ("guitar", "case", "beside a stage"),
    ("bicycle", "helmet", "near a park gate"), ("pot", "watering can", "in a greenhouse"),
    ("bag", "wallet", "on a shop counter"), ("bench", "planter", "on a patio"),
    ("pillow", "blanket", "on a sofa"), ("door", "mailbox", "at a cottage"),
    ("sail", "hull", "at a marina"), ("racket", "ball", "on a tennis court"),
    ("ladder", "bucket", "beside a barn"), ("violin", "stand", "in a rehearsal room"),
    ("tray", "teapot", "at a tea shop"), ("scarf", "jacket", "inside a wardrobe"),
    ("ribbon", "box", "on a wrapping table"), ("wagon", "wheelbarrow", "beside a shed"),
    ("stool", "cabinet", "inside an art studio"), ("umbrella", "boots", "near a porch"),
    ("lantern", "tent", "at a campsite"), ("basket", "vase", "at a flower stall"),
    ("mug", "thermos", "at a picnic"), ("kite", "spool", "beside a meadow"),
]
# Proposed defaults require independent human review before confirmatory use.
DEFAULTS = [
    ("freshly fallen snow", "snow", "white"), ("plain whole milk", "milk", "white"),
    ("granulated table sugar", "sugar", "white"), ("fresh cotton fiber", "cotton", "white"),
    ("the inside of a fresh coconut", "coconut flesh", "white"),
    ("a piece of charcoal", "charcoal", "black"), ("a patch of soot", "soot", "black"),
    ("a pool of fresh printer ink from a monochrome cartridge", "ink", "black"),
    ("a piece of obsidian", "obsidian", "black"), ("an adult raven", "raven", "black"),
    ("a ripe strawberry", "strawberry", "red"), ("a ripe tomato", "tomato", "red"),
    ("a ripe cranberry", "cranberry", "red"), ("a ripe raspberry", "raspberry", "red"),
    ("the cut flesh of a ripe watermelon", "watermelon flesh", "red"),
    ("a ripe banana peel", "banana peel", "yellow"), ("a ripe lemon peel", "lemon peel", "yellow"),
    ("a fresh egg yolk", "egg yolk", "yellow"), ("a fresh butter pat", "butter", "yellow"),
    ("a ripe corn kernel", "corn kernel", "yellow"),
    ("healthy lawn grass", "grass", "green"), ("fresh spinach leaves", "spinach", "green"),
    ("a fresh broccoli floret", "broccoli", "green"), ("fresh basil leaves", "basil", "green"),
    ("fresh cucumber skin", "cucumber skin", "green"),
    ("an unwrapped milk chocolate bar", "chocolate", "brown"),
    ("a roasted coffee bean", "coffee bean", "brown"), ("loose cocoa powder", "cocoa", "brown"),
    ("a cinnamon stick", "cinnamon", "brown"), ("a dried walnut shell", "walnut shell", "brown"),
]


def canonical(value):
    return (json.dumps(value, sort_keys=True, indent=2, ensure_ascii=False) + "\n").encode()


def digest(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for chunk in iter(lambda: f.read(8 * 1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def labels(index):
    if index < 10:
        return [COLORS[index]], [COLORS[(index + 1) % 10]]
    if index < 20:
        if index % 10 == 8:
            return ["black"], ["white"]
        if index % 10 == 9:
            return ["white"], ["black"]
        if index % 10 == 7:
            return ["dark brown"], ["white"]
        return ["dark " + COLORS[index % 10]], ["light " + COLORS[(index + 1) % 10]]
    return [COLORS[index % 10], COLORS[(index + 1) % 10]], [COLORS[(index + 2) % 10], COLORS[(index + 3) % 10]]


def build():
    families, inputs = [], []

    def add(fid, variant, caption, condition, role, literal, pragmatic=None, distractor=None, distractor_role=None):
        uid = f"{fid}:{variant}:{role}"
        inputs.append(dict(id=uid, family=fid, variant=variant, caption=caption,
                           condition=condition, role=role, literal_colors=sorted(literal),
                           pragmatic_colors=sorted(literal if pragmatic is None else pragmatic),
                           distractor_colors=sorted(distractor or []), distractor_role=distractor_role))
        return uid

    for n, (noun, scene0, scene1) in enumerate(OBJECTS):
        fid, (v0, v1) = f"explicit_{n:02}", labels(n)
        ids = []
        for a, colors in enumerate([v0, v1]):
            for b, scene in enumerate([scene0, scene1]):
                ids.append(add(fid, f"{a}{b}", f"A {' and '.join(colors)} {noun} is {scene}.",
                               f"color of the {noun}", noun, colors))
        families.append(dict(id=fid, stratum="explicit", ids=ids, grid=ids))

    for n, (left, right, scene) in enumerate(PAIRS):
        # Both query roles occur equally often as the margin's target.
        target, other = (left, right) if n % 2 == 0 else (right, left)
        fid = f"multiple_{n:02}"
        tcolors = [[COLORS[n % 10]], [COLORS[(n + 1) % 10]]]
        dcolors = [[COLORS[(n + 4) % 10]], [COLORS[(n + 5) % 10]]]
        grids = [[], []]
        for a in range(2):
            for b in range(2):
                if target == left:
                    lc, rc = tcolors[a][0], dcolors[b][0]
                else:
                    lc, rc = dcolors[b][0], tcolors[a][0]
                caption = f"A {lc} {left} and a {rc} {right} are {scene}."
                for r, (role, gold, distractor, dr) in enumerate([
                    (target, tcolors[a], dcolors[b], other),
                    (other, dcolors[b], tcolors[a], target),
                ]):
                    grids[r].append(add(fid, f"{a}{b}", caption, f"color of the {role}", role,
                                        gold, distractor=distractor, distractor_role=dr))
        families.append(dict(id=fid, stratum="multiple", ids=grids[0]+grids[1],
                             grid=grids[0], distractor_grid=grids[1]))

    for n, (phrase, role, color) in enumerate(DEFAULTS):
        fid = f"implied_{n:02}"
        foil = COLORS[(COLORS.index(color) + 3) % 10]
        condition = f"color of the {role}"
        captions = [
            f"A photographer takes a close-up picture of {phrase}.",
            f"A photographer takes a close-up picture of {phrase}; the {role} is {color}.",
            f"A paint sample shows a uniform {color} surface under neutral studio lighting.",
            f"A paint sample shows a uniform {foil} surface under neutral studio lighting.",
        ]
        ids = [add(fid, str(v), x, condition, role, [] if v == 0 else [color if v < 3 else foil],
                   pragmatic=[color if v < 3 else foil]) for v, x in enumerate(captions)]
        # Reference captions name the queried entity, avoiding an absent-role condition.
        for v in [2, 3]:
            inputs[-4+v]["caption"] = f"A reference card depicts the {role} as entirely {color if v == 2 else foil}."
        families.append(dict(id=fid, stratum="implied", ids=ids, implicit=ids[0],
                             explicit=ids[1], positive=ids[2], negative=ids[3]))

    for n, (noun, scene0, scene1) in enumerate(OBJECTS[:10]):
        fid, ids = f"unspecified_{n:02}", []
        for v, scene in enumerate([scene0, scene1, scene0, scene1]):
            caption = f"A {noun} is {scene}." if v < 2 else f"The photograph shows a {noun} {scene}."
            ids.append(add(fid, str(v), caption, f"color of the {noun}", noun, []))
        families.append(dict(id=fid, stratum="unspecified", ids=ids))

    return dict(schema_version=1, human_review="pending", label_source="single_model_author_proposals",
                families=families, inputs=inputs)


COLOR_RE = re.compile(r"\b(?:(dark|light|bright|pale|deep)\s+)?(red|blue|green|yellow|orange|purple|pink|brown|black|white|gr[ae]y|tan|beige|navy|cyan|magenta|violet|turquoise|gold|silver)\b", re.I)
UNCERTAIN = re.compile(r"\b(maybe|perhaps|possibly|probably|likely|might|could|unsure|uncertain|not|isn't|aren't|either|or)\b", re.I)
ABSTENTION = re.compile(r"\b(not specified|not mentioned|not stated|not given|not available|unspecified|unknown|undetermined|cannot be determined|can't be determined|no color|does not (?:state|specify|mention)|doesn't (?:state|specify|mention))\b", re.I)


def parse_answer(text, item):
    clean = re.sub(r"[-‐‑–]", " ", text.lower())
    colors = sorted(set(((q + " ") if q else "") + c.replace("grey", "gray") for q, c in COLOR_RE.findall(clean)))
    other = item.get("distractor_role")
    wrong_role = bool(other and re.search(r"\b"+re.escape(other)+r"\b", clean))
    return dict(colors=colors, qualified_or_uncertain=bool(colors and UNCERTAIN.search(clean)),
                other_role_named=wrong_role,
                explicit_abstention=bool(not colors and ABSTENTION.search(clean)))


def is_correct(parsed, item, gold="literal_colors"):
    return (parsed["colors"] == item[gold] and (bool(item[gold]) or parsed["explicit_abstention"])
            and not parsed["qualified_or_uncertain"]
            and not parsed["other_role_named"])


def validate(probe):
    assert Counter(f["stratum"] for f in probe["families"]) == dict(explicit=30, multiple=30, implied=30, unspecified=10)
    assert len(probe["inputs"]) == 520
    assert len({x["id"] for x in probe["inputs"]}) == 520
    for f in probe["families"]:
        items = [x for x in probe["inputs"] if x["family"] == f["id"]]
        assert len({x["caption"] for x in items}) == 4
        if f["stratum"] == "multiple":
            assert all(set(x["literal_colors"]).isdisjoint(x["distractor_colors"]) for x in items)
    return dict(families=100, captions=400, conditioned_inputs=520, model_states=13, generation_calls=6760)


def reviewed(probe, paths):
    records = [json.loads(Path(p).read_text()) for p in paths]
    assert len(records) == 2
    assert len({r["rater_id"] for r in records}) == 2
    expected = hashlib.sha256(canonical(probe)).hexdigest()
    lookup = []
    for r in records:
        assert r["rater_type"] == "human" and r["probe_sha256"] == expected
        rows = {x["id"]: x for x in r["judgments"]}
        assert set(rows) == {x["id"] for x in probe["inputs"]}
        assert all(isinstance(x.get(k), list) for x in rows.values() for k in ["literal_colors", "pragmatic_colors"])
        lookup.append(rows)
    for x in probe["inputs"]:
        for field in ["literal_colors", "pragmatic_colors"]:
            a, b = [sorted(z[x["id"]][field]) for z in lookup]
            if a != b:
                raise ValueError(f"Human adjudication required: {x['id']} {field}")
            x[field] = a
    probe["human_review"] = dict(status="two_humans_agree", raters=[r["rater_id"] for r in records],
                                  source_sha256=[digest(p) for p in paths])
    probe["label_source"] = "two_human_raters"
    return probe


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--output", type=Path, required=True)
    args = p.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    probe = build()
    counts = validate(probe)
    (args.output/"probe.json").write_bytes(canonical(probe))
    for n in [1, 2]:
        form = dict(rater_id=f"REPLACE_WITH_RATER_{n}_ID", rater_type="human",
                    probe_sha256=digest(args.output/"probe.json"), judgments=[dict(
                        id=x["id"], caption=x["caption"], condition=x["condition"],
                        literal_colors=None, pragmatic_colors=None) for x in probe["inputs"]])
        (args.output/f"rater_{n}_template.json").write_bytes(canonical(form))
    (args.output/"counts.json").write_bytes(canonical(counts))
    print(json.dumps(counts))


if __name__ == "__main__":
    main()
