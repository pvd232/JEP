# C-STS validation scope audit, version 4.1

This package contains **1,830 label dispositions**, including **1,572 usable validation comparisons across 678 source groups**, 257 invalid cases and one scope exclusion. Labels come from assistant-model review with three user-adjudicated anchors.

Version 4.1 repairs 22 calibration-only ratings to enforce the previously specified preservation rule. It retains version 4's usable-example membership and semantic scope/value extractions. Relative to version 3, it restores 62 exclusions, revises 79 accepted ratings and excludes three prior accepted cases.

## Source and attribution

Source: [LivNLP/C-STS-Reannotated](https://huggingface.co/datasets/LivNLP/C-STS-Reannotated), revision `058ac842f5f19d27b08ad54f6d4a2c50b3f9578b`, released training CSV. The original [C-STS](https://github.com/princeton-nlp/c-sts) distributor restricts unencrypted caption redistribution. [Tu's reannotation](https://github.com/brandeis-llc/L-CSTS) distributes source IDs and labels separately. This package provides IDs and annotation values, while source captions remain with upstream distributors. LivNLP's source card lists CC-BY-4.0; retain upstream access terms and attribution.

The original project training and held-out test references retain their existing versions. Independent human label-error estimates remain to be collected. Exact backend reviewer snapshot and sampling controls are unavailable. Original version-4 results were known during the implementation repair; per-comparison predictions were withheld from repair classification.

## Reconstruction

Obtain the pinned upstream CSVs and run `python -m csts_pilot.data --source SOURCE_DIRECTORY --output csts_data`. The module verifies source CSV hashes and source-group isolation. Apply this label patch to the resulting original validation partition:

```python
import hashlib, json
from pathlib import Path

source_path = Path("csts_data/dev.json")
patch_path = Path("datasets/csts-validation-audit-v4-1/labels.json")
patch = json.loads(patch_path.read_text())
assert hashlib.sha256(source_path.read_bytes()).hexdigest() == patch["source"]["prepared_validation_sha256"]
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
Path("validation_scope_audit_v4_1.json").write_bytes(output)
```

The example reproduces the exact 1,572-row current validation reference. Targets use `(rating - 1) / 4`.

Usable rows SHA-256: `f186e86877e731c96ee9b1c819863b981074bc500dc9aa11c6951ba9fd56e2c9`.

Audit SHA-256: `845ed43db26743496fbd73dd4e6453d7dd18fb54002f3d8b2a07d3fd7655c412`.
