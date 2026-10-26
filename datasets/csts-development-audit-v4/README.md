# C-STS development scope audit, version 4

This package contains **1,830 development-label dispositions**, including **1,572 usable comparisons across 678 source groups**, 257 invalid cases and one excluded case with unresolved entity scope. It is an assistant-model audit with three user-adjudicated anchors.

## Files and scope

`labels.json` provides stable source IDs, original ratings, revised ratings, dispositions, pair IDs and group IDs. Captions and conditions are obtained from the upstream source. The artifact covers the project's development partition drawn from the LivNLP released training split. Existing project training and Tu-reannotated test labels retain their prior versions.

## Source and attribution

- [Original C-STS](https://github.com/princeton-nlp/c-sts), Deshpande et al., EMNLP 2023.
- [Tu reannotation and guidelines](https://github.com/brandeis-llc/L-CSTS), Tu et al., ACL 2024.
- [LivNLP C-STS-Reannotated](https://huggingface.co/datasets/LivNLP/C-STS-Reannotated), pinned revision `058ac842f5f19d27b08ad54f6d4a2c50b3f9578b`.

The original C-STS distributor restricts public sharing of unencrypted captions. Tu distributes IDs and labels separately. This package follows that ID-and-label format. LivNLP's source card lists CC-BY-4.0. Obtain source text through its distributors and retain their access terms and attribution.

## Annotation procedure

Six isolated assistant contexts reviewed all 1,830 comparisons from captions and condition, recording entity scope and extracted values. Prior ratings and encoder predictions were withheld, with three user-adjudicated semantic anchors supplied. A second reader resolved 397 flagged cases using captions, the frozen rubric and shuffled interpretation options. Reader disagreement alone supplies no ambiguity exclusion. Final checks preserved 161 defensible calibration grades and adopted 16 explicit quality decisions about scope, direct context and color similarity. All semantic labels were frozen before encoder predictions were rescored.

The initial review's validity wording was clarified before final adjudication: a wholly unavailable requested attribute in one caption is invalid; partial recoverable feature values in both captions can support rating 3. Every reader revisited affected earlier judgments. Original versions and all raw judgments remain in the project audit archive.

Reviewer identity: runtime assistant model in isolated contexts. An immutable backend model snapshot and sampling controls are unavailable. The user directly adjudicated three anchors. This resource supports development evaluation and error analysis; independent human label-error estimates remain to be collected.

## Reconstruction

Obtain the pinned upstream CSVs through their distributors. Prepare the original project split with `python -m csts_pilot.data --source SOURCE_DIRECTORY --output csts_data`. The preparation module verifies both upstream CSV hashes and source-group isolation. Then apply this patch:

```python
import hashlib, json
from pathlib import Path

source_path = Path("csts_data/dev.json")
patch_path = Path("datasets/csts-development-audit-v4/labels.json")
patch = json.loads(patch_path.read_text())
assert hashlib.sha256(source_path.read_bytes()).hexdigest() == patch["source"]["prepared_development_sha256"]
source = json.loads(source_path.read_text())
lookup = {row["row_id"]: row for row in patch["labels"]}
assert len(lookup) == len(source) == patch["counts"]["dispositions"]
rows = []
for original in source:
    annotation = lookup[original["row_id"]]
    assert original["rating"] == annotation["original_rating"]
    if annotation["status"] in {"agreement", "adjudicated"}:
        row = dict(original)
        row["rating"] = float(annotation["rating"])
        row["target"] = (row["rating"] - 1.0) / 4.0
        rows.append(row)
output = (json.dumps(rows, ensure_ascii=False, indent=2) + "\n").encode()
assert hashlib.sha256(output).hexdigest() == patch["usable_rows_sha256"]
Path("dev_scope_audit_v4.json").write_bytes(output)
```

Reconstruction of all 1,572 usable rows was checked against the published SHA-256. Numeric target normalization is `(rating - 1) / 4`.

## Version changes

Version 4 restores 62 previously excluded examples, corrects 101 accepted ratings and excludes three previously accepted examples. All 29 earlier ambiguity exclusions receive ratings. The sole current ambiguity exclusion is `train_1693`, whose singular person-age condition leaves both a child and an adult as potential referents.

Current usable-row SHA-256: `87af4e9aee2513b2e948ad8669027f7c059c2cba00c64c054893d03bcf370e24`.

Frozen audit SHA-256: `e8ffe2bd973ce96a51a1f72b03e0d680bfdeb6e3932a19127f6d32cf4ef5a5ab`.
