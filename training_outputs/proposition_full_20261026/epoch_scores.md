Both models completed two ratings epochs. The requested dataset switch follows this comparison.

# Qwen proposition comparison: per-epoch validation scores

Updated: **2026-10-27T05:32:18+00:00**. Run: `propositions_v41_full_after_indicative`.

Status: **completed_requested_two_epoch_comparison**. Current stage: **comparison_finished**.

Validation: **1,572 comparisons**, 678 source groups.

Source commit: `a6daf0eeea544716d7340f0f24de687e4ba93490`.
Validation SHA-256: `f186e86877e731c96ee9b1c819863b981074bc500dc9aa11c6951ba9fd56e2c9`.
Training SHA-256: `4058b7f63a5285ebdb5061f24f7f2907e76e2ddc7c99480bfd39fc69062a7d01`.

Both models start from the same pretrained weights. For the first two epochs, both see the comparisons covered by existing propositions. The ratings model learns ratings; the proposition model learns to write propositions. Both then learn ratings from the full training set. Ratings training uses validation patience 5 and an epoch ceiling of 24.

Rating loss measures error in predicted ratings on the 0–1 scale. Proposition-writing loss measures error in predicted text tokens. Each table counts optimizer updates from the beginning of that training step.

Appearance and colour scores are available in the final report. Native epoch traces contain overall validation scores. Values are provisional while the comparison is running.

## Ratings model: first two epochs on the covered subset

Status: **succeeded**. Completed epochs: **2**. Recorded optimizer updates: **144**.

| Epoch | Optimizer updates | Validation Spearman | Validation MSE, 1–5 | Training loss | Patience counter |
|---:|---:|---:|---:|---:|---:|
| 1 | 72 | 0.767297 | 1.114983 | 0.079459 | — |
| 2 | 144 | 0.814361 | 0.880899 | 0.038181 | — |

Stop reason: `fixed_update_budget`.

## Proposition model: writing propositions on the covered subset

Status: **succeeded**. Completed epochs: **2**. Recorded optimizer updates: **144**.

| Epoch | Optimizer updates | Validation Spearman | Validation MSE, 1–5 | Training loss | Patience counter |
|---:|---:|---:|---:|---:|---:|
| 1 | 72 | 0.453279 | 3.482882 | 4.552642 | — |
| 2 | 144 | 0.459184 | 4.074551 | 0.580284 | — |

Stop reason: `fixed_update_budget`.

## Ratings model: ratings on the full training set

Status: **stopped_by_user**. Completed epochs: **2**. Recorded optimizer updates: **575**.

| Epoch | Optimizer updates | Validation Spearman | Validation MSE, 1–5 | Training loss | Patience counter |
|---:|---:|---:|---:|---:|---:|
| 1 | 219 | 0.816749 | 0.932301 | 0.036532 | 0 |
| 2 | 438 | 0.821362 | 0.886504 | 0.030911 | 0 |

## Proposition model: ratings on the full training set

Status: **succeeded**. Completed epochs: **2**. Recorded optimizer updates: **438**.

| Epoch | Optimizer updates | Validation Spearman | Validation MSE, 1–5 | Training loss | Patience counter |
|---:|---:|---:|---:|---:|---:|
| 1 | 219 | 0.812601 | 0.958263 | 0.053901 | 0 |
| 2 | 438 | 0.821649 | 0.904781 | 0.032745 | 0 |

Stop reason: `epoch_budget`.
