# Proposition similarity comparison

GPT propositions improved the frozen Qwen similarity scorer on the existing 120 validation pairs.

| Input and scorer | Spearman |
| --- | ---: |
| Original text → Qwen cosine | 0.368 |
| GPT propositions → same Qwen cosine, with fallback | 0.584 |
| Direct GPT-6.1 similarity judgment | 0.886 |

The proposition gain was **+0.216**, with a paired 95% interval of **[+0.068, +0.370]** from 2,000 bootstrap resamples of the 110 connected source groups. Direct GPT exceeded the proposition pipeline by 0.303; the corresponding interval was [0.196, 0.420].

Both embedding arms used identical frozen Qwen3-Embedding-8B weights, condition instructions, final-token pooling and cosine scoring. All 120 pairs remained; 12 used original-text fallback because proposition evidence was unspecified. On the other 108 pairs, correlations were 0.389 for original text, 0.613 for propositions and 0.901 for direct GPT. No training, calibration or new GPT calls occurred.

**Conclusion:** explicit evidence helped this frozen scorer. Direct GPT remained substantially more accurate. These are previously exposed validation examples; this comparison establishes neither fresh-test performance nor the value of training a proposition student.

The GPU saved every embedding and prediction before a receipt serialization error. CPU replay reproduced all 120 predictions exactly; no model inference was repeated. The reporting bug is fixed. Eleven tests passed on Colab; the additional serialization regression passed locally.

[Results and intervals](csts_proposition_similarity_120_20261028/results.json) · [Predictions](csts_proposition_similarity_120_20261028/predictions.json) · [Artifacts and hashes](csts_proposition_similarity_120_20261028/artifacts.json) · [Frozen plan](../plans/csts-proposition-similarity-120-20261028.md) · [Code](../csts_pilot/proposition_similarity.py)

For CPU metric reproduction:

```bash
python -m csts_pilot.proposition_similarity evaluate \
  --inputs training_outputs/csts_proposition_similarity_120_20261028/inputs.json \
  --predictions training_outputs/csts_proposition_similarity_120_20261028/predictions.json \
  --labels training_outputs/csts_proposition_similarity_120_20261028/labels.json \
  --direct training_outputs/csts_proposition_similarity_120_20261028/direct.json \
  --output /tmp/csts-proposition-similarity-results.json
```

MSE values in the JSON use unclipped cosine against normalized ratings, with no fitted calibration. The retained GPU archive contains token IDs, embeddings, the executed code, tests and original failure logs. Input preparation reuses the GPT captures and parser amendment in the earlier [screen archive](csts_extraction_screen_artifacts_20261028.tar.gz).
