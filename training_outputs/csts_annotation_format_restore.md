# Restore the completed annotation-format pilot

Training source is pinned to `47864845b6520ae49676c27d0224513ac161388a`; native VIPER is pinned to `e4ce91fa0a9330e769644aba0fccdfe062d5d821`. Use the authenticated Google account with access to project `mantra-477901`. Credentials are supplied by the existing session and are not part of these files.

`csts_annotation_format_native_verification.json` records every native run, resolved stage spec, sealed artifact address, SHA-256 and byte count. The six checkpoints and resume states remain at those exact addresses. `csts_annotation_format_evidence/selection.json` identifies the three checkpoints fixed before evaluation.

For example, restore the JSON-arm predictions through VIPER's seal and checksum validation:

```python
import hashlib
import json
from pathlib import Path

from google.cloud import storage
from viper.gcs import GcsProvider
from viper.references import GcsFileRef

records = json.loads(Path('csts_annotation_format_native_verification.json').read_text())
run = next(item for item in records if item['name'] == 'evaluate_record')
stage = next(item for item in run['stages'] if item['stage_id'] == 'eval')
artifact = stage['artifacts']['predictions']
reference = artifact['stored_at']
root = Path('restored')
root.mkdir(exist_ok=True)
provider = GcsProvider(root, reference['bucket'], client=storage.Client(project='mantra-477901'))
raw = provider.fetch(GcsFileRef.model_validate(reference))
assert len(raw) == artifact['bytes']
assert hashlib.sha256(raw).hexdigest() == artifact['sha256']
(root / 'record_predictions.json').write_bytes(raw)
```

The same procedure restores any small artifact. Checkpoint artifacts are named `model` and `resume_state` in each training stage. For large files use VIPER's `fetch_to_path` streaming interface with the recorded file identity.

The final report bundle has its own native reference in `csts_annotation_format_report_publication.json`. Its `artifact` entry is directly compatible with the restore procedure above. It contains the report, numeric results, intervals, all three sets of predictions and epoch traces, the 96 common generation records, provenance and reproducibility scripts. Shutdown confirmation is published separately after the bundle is durable.
