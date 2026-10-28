# GPT evidence formats with the trained JEP reader

JSON and Python evidence showed no clear gain over propositions. Original text had the best point estimate.

| Input | Spearman ↑ | MSE, 1–5 ↓ | Sources using raw-text fallback |
| --- | ---: | ---: | ---: |
| Original text | 0.8955 | 0.3709 | 0 |
| Propositions | 0.8922 | 0.4148 | 21/239 |
| Entity/fact JSON | 0.8815 | 0.4641 | 25/239 |
| Python objects | 0.8741 | 0.4896 | 30/239 |
| Direct GPT-6.1 reference | 0.8864 | 0.4776 | — |

All 120 validation pairs remained. GPT-6.1 Sol at max reasoning generated 239 fresh outputs per format in 19 matched batches. The three evidence arms used identical source membership and order; companion passages and repeated conditions never shared a batch. All 717 outputs parsed successfully. JSON had one unresolved local reference and Python had four; those sources used fallback. No input exceeded the 160-token ceiling.

The saved proposition-trained LoRA checkpoint, original condition prompt, pooling and cosine scorer stayed fixed. Unavailable evidence fell back to original text per side. No training or calibration occurred. MSE uses the unclipped cosine mapped to the 1–5 rating scale.

| Primary Spearman difference | Estimate | Paired 95% interval |
| --- | ---: | ---: |
| JSON − propositions | −0.0107 | [−0.0333, +0.0099] |
| Python − propositions | −0.0182 | [−0.0426, +0.0025] |
| Python − JSON | −0.0075 | [−0.0261, +0.0072] |

These exploratory intervals use 2,000 resamples of 110 connected source groups. They condition on the frozen outputs and omit generation variability and dependence within batches. The examples are previously exposed validation data. Valid syntax does not establish faithful extraction.

Keep the current trained reader's raw-text inference path. This run gives no reason to add structured evidence there. It does not test changes to proposition supervision through retraining or rank UIE models generally.

A100 scoring completed in 39 seconds after removing an incompatible, unused `torchao` package. The failed attempt and repair are retained. Independent replay verified the frozen weights, joins, token IDs, vectors, metrics and bootstrap intervals. Generation and GPU artifacts passed full Viper Cloud read-back checks; uploads ran asynchronously.

[Results](csts_gpt_format_comparison_20261028/results.json) · [Independent audit](csts_gpt_format_comparison_20261028/independent_audit.json) · [Artifacts](csts_gpt_format_comparison_20261028/artifacts.json) · [Design and code review](../plans/csts-gpt-format-comparison-review-20261028.md)
