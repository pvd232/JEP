# Training to patience 2: jep-csts-v1

Training: **6,051** comparisons. Validation: **1,576**. Test: **2,430**.

Both models resume their saved training state after epoch four and continue until two successive validation checks fail to improve Spearman. Time and epoch limits are disabled. [Earlier four-epoch pilot](four_epoch_pilot_scores.md).

[Earlier V4.1 comparison](v41_final_epoch_scores.md)
# Qwen proposition comparison: per-epoch validation scores

Updated: **2026-10-27T11:49:37+00:00**. Run: `jep_csts_v1_patience2_completion_20261027`.

Status: **running**. Current stage: **ratings_ratings**.

Validation: **1,576 comparisons**, 680 source groups.

Source commit: `1719cf9c003a331864da5d3c95f9a2bd32dd51ac`.
Validation SHA-256: `e42d9544b2aa6814708337d0ce38eba1d64124645b62489ed448c6784dbc71ff`.
Training SHA-256: `9a9eac21ee73b9b029ca6f62584891dd13c74aa78e80efd764532a87665ae6a4`.

Both models start from the same pretrained weights. For the first two epochs, both see the comparisons covered by existing propositions. The ratings model learns ratings; the proposition model learns to write propositions. Both then learn ratings from the full training set. Ratings training continues until validation patience 2 is exhausted, with time and epoch limits disabled.

Rating loss measures error in predicted ratings on the 0–1 scale. Proposition-writing loss measures error in predicted text tokens. Each table counts optimizer updates from the beginning of that training step.

Appearance and colour scores are available in the final report. Native epoch traces contain overall validation scores. Values are provisional while the comparison is running.

## Ratings model: first two epochs on the covered subset

Status: **succeeded**. Completed epochs: **2**. Recorded optimizer updates: **134**.

| Epoch | Optimizer updates | Validation Spearman | Validation MSE, 1–5 | Training loss | Patience counter |
|---:|---:|---:|---:|---:|---:|
| 1 | 67 | 0.810656 | 0.867627 | 0.118955 | — |
| 2 | 134 | 0.845369 | 0.670799 | 0.047767 | — |

Stop reason: `fixed_update_budget`.

## Proposition model: writing propositions on the covered subset

Status: **succeeded**. Completed epochs: **2**. Recorded optimizer updates: **134**.

| Epoch | Optimizer updates | Validation Spearman | Validation MSE, 1–5 | Training loss | Patience counter |
|---:|---:|---:|---:|---:|---:|
| 1 | 67 | 0.458204 | 3.295591 | 4.893944 | — |
| 2 | 134 | 0.484417 | 3.948340 | 0.611994 | — |

Stop reason: `fixed_update_budget`.

## Ratings model: ratings on the full training set

Status: **running**. Completed epochs: **4**. Recorded optimizer updates: **875**.

| Epoch | Optimizer updates | Validation Spearman | Validation MSE, 1–5 | Training loss | Patience counter |
|---:|---:|---:|---:|---:|---:|
| 1 | 190 | 0.865165 | 0.567004 | 0.041376 | 0 |
| 2 | 380 | 0.873606 | 0.520572 | 0.031676 | 0 |
| 3 | 570 | 0.875774 | 0.503254 | 0.026145 | 0 |
| 4 | 760 | 0.875915 | 0.509393 | 0.021068 | 0 |

## Proposition model: ratings on the full training set

Status: **pending**. Completed epochs: **4**. Recorded optimizer updates: **760**.

| Epoch | Optimizer updates | Validation Spearman | Validation MSE, 1–5 | Training loss | Patience counter |
|---:|---:|---:|---:|---:|---:|
| 1 | 190 | 0.847641 | 0.666094 | 0.072070 | 0 |
| 2 | 380 | 0.867966 | 0.541257 | 0.037314 | 0 |
| 3 | 570 | 0.873231 | 0.516411 | 0.030228 | 0 |
| 4 | 760 | 0.875049 | 0.500511 | 0.024943 | 0 |

Stop reason: `resource_budget`.
