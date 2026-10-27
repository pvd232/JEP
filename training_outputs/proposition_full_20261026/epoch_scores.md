# Training with validation early stopping: jep-csts-v1

Training: **6,051** comparisons. Validation: **1,576**. Test: **2,430**.

Stop after consecutive non-improving validation checks: ratings control **2**; proposition model **1**. Keep each model's best validation checkpoint. Time and epoch limits are disabled.

[Earlier V4.1 comparison](v41_final_epoch_scores.md)

[Missing proposition generation progress](generation_progress.md)
# Qwen proposition comparison: per-epoch validation scores

Updated: **2026-10-27T13:11:54+00:00**. Run: `jep_csts_v1_proposition_patience1_completion_20261027`.

Status: **running**. Current stage: **evidence_ratings**.

Validation: **1,576 comparisons**, 680 source groups.

Source commit: `636cb33048f41eb8c0e839250df66d36cf46a101`.
Validation SHA-256: `e42d9544b2aa6814708337d0ce38eba1d64124645b62489ed448c6784dbc71ff`.
Training SHA-256: `9a9eac21ee73b9b029ca6f62584891dd13c74aa78e80efd764532a87665ae6a4`.

Both models start from the same pretrained weights. For the first 2 epochs, both see the comparisons covered by existing propositions. The ratings model learns ratings; the proposition model learns to write propositions. Both then learn ratings from the full training set. Ratings training stops after the configured consecutive non-improving checks: ratings control 2; proposition model 1. Training continues with time and epoch limits disabled.

Rating loss measures error in predicted ratings on the 0–1 scale. Proposition-writing loss measures error in predicted text tokens. Each table counts optimizer updates from the beginning of that training step.

Appearance and colour scores are available in the final report. Native epoch traces contain overall validation scores. Values are provisional while the comparison is running.

## Ratings model: first 2 epochs on the covered subset

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

Status: **succeeded**. Completed epochs: **6**. Recorded optimizer updates: **1140**.

| Epoch | Optimizer updates | Validation Spearman | Validation MSE, 1–5 | Training loss | Patience counter |
|---:|---:|---:|---:|---:|---:|
| 1 | 190 | 0.865165 | 0.567004 | 0.041376 | 0 |
| 2 | 380 | 0.873606 | 0.520572 | 0.031676 | 0 |
| 3 | 570 | 0.875774 | 0.503254 | 0.026145 | 0 |
| 4 | 760 | 0.875915 | 0.509393 | 0.021068 | 0 |
| 5 | 950 | 0.874875 | 0.522848 | 0.016535 | 1 |
| 6 | 1140 | 0.872287 | 0.525243 | 0.013873 | 2 |

Stop reason: `validation_patience`.

## Proposition model: ratings on the full training set

Status: **running**. Completed epochs: **5**. Recorded optimizer updates: **950**.

| Epoch | Optimizer updates | Validation Spearman | Validation MSE, 1–5 | Training loss | Patience counter |
|---:|---:|---:|---:|---:|---:|
| 1 | 190 | 0.847641 | 0.666094 | 0.072070 | 0 |
| 2 | 380 | 0.867966 | 0.541257 | 0.037314 | 0 |
| 3 | 570 | 0.873231 | 0.516411 | 0.030228 | 0 |
| 4 | 760 | 0.875049 | 0.500511 | 0.024943 | 0 |
| 5 | 950 | 0.873579 | 0.524837 | 0.020309 | 1 |

Stop reason: `validation_patience`.
