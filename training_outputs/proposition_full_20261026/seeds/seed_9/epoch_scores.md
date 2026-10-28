# Qwen proposition comparison: per-epoch validation scores

Updated: **2026-10-28T00:31:40+00:00**. Run: `jep_csts_v1_full_propositions_seed9_20261027`.

Status: **complete**. Current stage: **none**.

Validation: **1,576 comparisons**, 680 source groups.

Source commit: `3ef6ba0616614632abc5bc0b2f2e2c71886c2f0e`.
Validation SHA-256: `e42d9544b2aa6814708337d0ce38eba1d64124645b62489ed448c6784dbc71ff`.
Training SHA-256: `9a9eac21ee73b9b029ca6f62584891dd13c74aa78e80efd764532a87665ae6a4`.

The proposition model writes answers from the full generated training bank until held-out proposition loss fails to improve for one epoch. Its best writing checkpoint determines the initial epoch count for the ratings control, which uses the same comparisons, batch size, and update count. Both then learn ratings from all 6,051 training comparisons with validation Spearman patience 1. Writing and ratings training have no epoch or wall-time stopping ceiling.

Rating loss measures error in predicted ratings on the 0–1 scale. Proposition-writing loss measures error in predicted text tokens. Each table counts optimizer updates from the beginning of that training step.

Appearance and colour scores are available in the final report. Native epoch traces contain overall validation scores. Values are provisional while the comparison is running.

## Ratings control: matched exposure on the full proposition-covered training comparisons

Status: **succeeded**. Completed epochs: **4**. Recorded optimizer updates: **736**.

Initial checkpoint used for the matched comparison: **epoch 3**. Extra speculative epochs remain recorded and are excluded from that checkpoint.

| Epoch | Optimizer updates | Validation Spearman | Validation MSE, 1–5 | Training loss | Patience counter |
|---:|---:|---:|---:|---:|---:|
| 1 | 184 | 0.852443 | 0.639540 | 0.073739 | — |
| 2 | 368 | 0.867465 | 0.547149 | 0.036949 | — |
| 3 | 552 | 0.873440 | 0.513154 | 0.029644 | — |
| 4 | 736 | 0.876737 | 0.503656 | 0.023635 | — |

Stop reason: `fixed_update_budget`.

## Proposition model: full-bank writing until held-out loss stops improving

Status: **succeeded**. Completed epochs: **4**. Recorded optimizer updates: **736**.

Initial checkpoint used for the matched comparison: **epoch 3**. Extra speculative epochs remain recorded and are excluded from that checkpoint.

| Epoch | Optimizer updates | Validation Spearman | Validation MSE, 1–5 | Training loss | Patience counter |
|---:|---:|---:|---:|---:|---:|
| 1 | 184 | 0.487839 | 4.131217 | 2.101534 | 0 |
| 2 | 368 | 0.449770 | 4.154146 | 0.362194 | 0 |
| 3 | 552 | 0.476101 | 4.095590 | 0.302926 | 0 |
| 4 | 736 | 0.489989 | 4.122852 | 0.269593 | 1 |

Held-out proposition loss selects the writing checkpoint:

| Epoch | Held-out proposition loss |
|---:|---:|
| 1 | 0.387605 |
| 2 | 0.330047 |
| 3 | 0.296606 |
| 4 | 0.298215 |

Stop reason: `proposition_validation_patience`.

## Ratings model: ratings on the full training set

Status: **succeeded**. Completed epochs: **4**. Recorded optimizer updates: **760**.

| Epoch | Optimizer updates | Validation Spearman | Validation MSE, 1–5 | Training loss | Patience counter |
|---:|---:|---:|---:|---:|---:|
| 1 | 190 | 0.872819 | 0.523876 | 0.025278 | 0 |
| 2 | 380 | 0.873232 | 0.507781 | 0.019579 | 0 |
| 3 | 570 | 0.874021 | 0.510511 | 0.015717 | 0 |
| 4 | 760 | 0.871896 | 0.525535 | 0.012457 | 1 |

Stop reason: `validation_patience`.

## Proposition model: ratings on the full training set

Status: **succeeded**. Completed epochs: **6**. Recorded optimizer updates: **1140**.

| Epoch | Optimizer updates | Validation Spearman | Validation MSE, 1–5 | Training loss | Patience counter |
|---:|---:|---:|---:|---:|---:|
| 1 | 190 | 0.859183 | 0.599825 | 0.063669 | 0 |
| 2 | 380 | 0.866427 | 0.545524 | 0.033401 | 0 |
| 3 | 570 | 0.873398 | 0.513159 | 0.026271 | 0 |
| 4 | 760 | 0.874353 | 0.512412 | 0.021394 | 0 |
| 5 | 950 | 0.876124 | 0.504217 | 0.017203 | 0 |
| 6 | 1140 | 0.874007 | 0.511839 | 0.014306 | 1 |

Stop reason: `validation_patience`.
