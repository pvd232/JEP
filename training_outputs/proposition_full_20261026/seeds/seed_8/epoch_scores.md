# Qwen proposition comparison: per-epoch validation scores

Updated: **2026-10-27T23:11:32+00:00**. Run: `jep_csts_v1_full_propositions_seed8_20261027`.

Status: **complete**. Current stage: **none**.

Validation: **1,576 comparisons**, 680 source groups.

Source commit: `3ef6ba0616614632abc5bc0b2f2e2c71886c2f0e`.
Validation SHA-256: `e42d9544b2aa6814708337d0ce38eba1d64124645b62489ed448c6784dbc71ff`.
Training SHA-256: `9a9eac21ee73b9b029ca6f62584891dd13c74aa78e80efd764532a87665ae6a4`.

The proposition model writes answers from the full generated training bank until held-out proposition loss fails to improve for one epoch. Its best writing checkpoint determines the initial epoch count for the ratings control, which uses the same comparisons, batch size, and update count. Both then learn ratings from all 6,051 training comparisons with validation Spearman patience 1. Writing and ratings training have no epoch or wall-time stopping ceiling.

Rating loss measures error in predicted ratings on the 0–1 scale. Proposition-writing loss measures error in predicted text tokens. Each table counts optimizer updates from the beginning of that training step.

Appearance and colour scores are available in the final report. Native epoch traces contain overall validation scores. Values are provisional while the comparison is running.

## Ratings control: matched exposure on the full proposition-covered training comparisons

Status: **succeeded**. Completed epochs: **7**. Recorded optimizer updates: **1288**.

Initial checkpoint used for the matched comparison: **epoch 6**. Extra speculative epochs remain recorded and are excluded from that checkpoint.

| Epoch | Optimizer updates | Validation Spearman | Validation MSE, 1–5 | Training loss | Patience counter |
|---:|---:|---:|---:|---:|---:|
| 1 | 184 | 0.849709 | 0.636958 | 0.073855 | — |
| 2 | 368 | 0.866598 | 0.546728 | 0.036488 | — |
| 3 | 552 | 0.867277 | 0.535075 | 0.028877 | — |
| 4 | 736 | 0.871437 | 0.523993 | 0.023501 | — |
| 5 | 920 | 0.870234 | 0.526020 | 0.018227 | — |
| 6 | 1104 | 0.865055 | 0.563833 | 0.014515 | — |
| 7 | 1288 | 0.868047 | 0.554886 | 0.011873 | — |

Stop reason: `fixed_update_budget`.

## Proposition model: full-bank writing until held-out loss stops improving

Status: **succeeded**. Completed epochs: **7**. Recorded optimizer updates: **1288**.

Initial checkpoint used for the matched comparison: **epoch 6**. Extra speculative epochs remain recorded and are excluded from that checkpoint.

| Epoch | Optimizer updates | Validation Spearman | Validation MSE, 1–5 | Training loss | Patience counter |
|---:|---:|---:|---:|---:|---:|
| 1 | 184 | 0.432202 | 4.107600 | 2.048675 | 0 |
| 2 | 368 | 0.434779 | 4.201625 | 0.364377 | 0 |
| 3 | 552 | 0.465303 | 4.147225 | 0.303627 | 0 |
| 4 | 736 | 0.486878 | 4.058281 | 0.271162 | 0 |
| 5 | 920 | 0.491323 | 4.015090 | 0.248212 | 0 |
| 6 | 1104 | 0.499551 | 3.943057 | 0.228131 | 0 |
| 7 | 1288 | 0.489871 | 3.943261 | 0.209730 | 1 |

Held-out proposition loss selects the writing checkpoint:

| Epoch | Held-out proposition loss |
|---:|---:|
| 1 | 0.386120 |
| 2 | 0.321024 |
| 3 | 0.294547 |
| 4 | 0.284399 |
| 5 | 0.274545 |
| 6 | 0.270777 |
| 7 | 0.272763 |

Stop reason: `proposition_validation_patience`.

## Ratings model: ratings on the full training set

Status: **succeeded**. Completed epochs: **2**. Recorded optimizer updates: **380**.

| Epoch | Optimizer updates | Validation Spearman | Validation MSE, 1–5 | Training loss | Patience counter |
|---:|---:|---:|---:|---:|---:|
| 1 | 190 | 0.870685 | 0.528384 | 0.013223 | 0 |
| 2 | 380 | 0.867474 | 0.555488 | 0.010459 | 1 |

Stop reason: `validation_patience`.

## Proposition model: ratings on the full training set

Status: **succeeded**. Completed epochs: **3**. Recorded optimizer updates: **570**.

| Epoch | Optimizer updates | Validation Spearman | Validation MSE, 1–5 | Training loss | Patience counter |
|---:|---:|---:|---:|---:|---:|
| 1 | 190 | 0.863435 | 0.571146 | 0.058871 | 0 |
| 2 | 380 | 0.873187 | 0.510313 | 0.030690 | 0 |
| 3 | 570 | 0.870960 | 0.523131 | 0.024137 | 1 |

Stop reason: `validation_patience`.
