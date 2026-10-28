# Reproduce the validation screen offline

The archive contains the three frozen origin implementations and captures, the original KnowCoder diagnostic, source-only references, the sealed review panel, both collected reviews, failed attempts, recovery receipts, author-example controls and a SHA-256 member index. Model weights are excluded. Scoring requires Python's standard library; it makes no model or network calls.

Archive: [csts_extraction_screen_artifacts_20261028.tar.gz](csts_extraction_screen_artifacts_20261028.tar.gz)

SHA-256: `02ac804d78e54549fe057c2c7086c43fa16555a9a6ea7c5f483b72c9fd91b472`

From the repository root, extract into a fresh directory and relocate only the local origin paths:

```bash
python3 - <<'PY'
from pathlib import Path
import hashlib, json, tarfile

archive = Path('training_outputs/csts_extraction_screen_artifacts_20261028.tar.gz')
assert hashlib.sha256(archive.read_bytes()).hexdigest() == '02ac804d78e54549fe057c2c7086c43fa16555a9a6ea7c5f483b72c9fd91b472'
root = Path('/tmp/jep-screen-replay-20261028')
root.mkdir(exist_ok=False)
with tarfile.open(archive) as tar:
    index = json.load(tar.extractfile('artifact-index.json'))
    for name, expected in index.items():
        assert hashlib.sha256(tar.extractfile(name).read()).hexdigest() == expected['sha256']
    tar.extractall(root, filter='data')
spec = json.loads((root / 'analysis/assembly-spec.json').read_text())
for arm, name in [('gpt_propositions', 'gpt-v2'), ('knowcoder', 'knowcoder-v4'), ('gollie', 'gollie-v3')]:
    spec['arms'][arm]['run'] = str(root / 'origins' / name / 'run')
    spec['arms'][arm]['code'] = str(root / 'origins' / name / 'code')
(root / 'relocated-spec.json').write_text(json.dumps(spec, indent=2) + '\n')
PY

python3 scripts/csts_extraction_screen_assembly.py prepare --spec /tmp/jep-screen-replay-20261028/relocated-spec.json --output /tmp/jep-screen-replay-20261028/reproduced-analysis
python3 scripts/csts_extraction_screen_assembly.py summarize --output /tmp/jep-screen-replay-20261028/reproduced-analysis --reviews /tmp/jep-screen-replay-20261028/reviews/review-a-collected/reviews.json /tmp/jep-screen-replay-20261028/reviews/review-b-collected/reviews.json
```

Expected joint acceptance counts are GPT 219, KnowCoder 21 and GoLLIE 22, each out of 239. Expected packet SHA-256 is `6283c270309bf60bacf3c6e66d4f1d7655447923d1c10556ab937cfeecfefda7`. The relocated origin manifest and seal hashes change because they record local paths; original request, capture, protocol and review bytes remain unchanged.

The parser amendment under `parser-amendment/` supplies the 120-pair direct baseline without rerunning inference. It preserves the first validator's original decisions and the unchanged primary review packet. The artifact was extracted independently, all 6,095 indexed members were verified, and its packet, counts, intervals and disagreements reproduced exactly offline.
