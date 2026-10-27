# Qwen proposition comparison: per-epoch validation scores

Updated: **2026-10-27T04:12:05+00:00**. Run: `propositions_v41_full_after_indicative`.

Publication: **automatic; VM publisher with 30-second checks**.

Status: **running**. Current stage: **evidence_ratings**.

Validation: **1,572 comparisons**, 678 source groups.

Source commit: `a6daf0eeea544716d7340f0f24de687e4ba93490`.
Validation SHA-256: `f186e86877e731c96ee9b1c819863b981074bc500dc9aa11c6951ba9fd56e2c9`.
Training SHA-256: `4058b7f63a5285ebdb5061f24f7f2907e76e2ddc7c99480bfd39fc69062a7d01`.

Both arms use the same initialization, sampled comparisons, optimizer schedule and phase-specific batch order. Auxiliary training lasts two epochs. Ratings training uses validation patience of five epochs and a 24-epoch ceiling.

Auxiliary control loss is rating MSE on the 0–1 scale. Proposition auxiliary loss is token cross-entropy. The loss magnitudes have different meanings. Each table resets its optimizer-update counter at the phase boundary.

Appearance and colour scores are available in the final report. Native epoch traces contain overall validation scores. Values are provisional while the comparison is running.

## Ratings arm: auxiliary phase

Publication: **automatic; VM publisher with 30-second checks**.

Status: **succeeded**. Completed epochs: **2**. Recorded optimizer updates: **144**.

| Epoch | Optimizer updates | Validation Spearman | Validation MSE, 1–5 | Training loss | Patience counter |
|---:|---:|---:|---:|---:|---:|
| 1 | 72 | 0.767297 | 1.114983 | 0.079459 | — |
| 2 | 144 | 0.814361 | 0.880899 | 0.038181 | — |

Stop reason: `fixed_update_budget`.

## Proposition arm: auxiliary phase

Publication: **automatic; VM publisher with 30-second checks**.

Status: **succeeded**. Completed epochs: **2**. Recorded optimizer updates: **144**.

| Epoch | Optimizer updates | Validation Spearman | Validation MSE, 1–5 | Training loss | Patience counter |
|---:|---:|---:|---:|---:|---:|
| 1 | 72 | 0.453279 | 3.482882 | 4.552642 | — |
| 2 | 144 | 0.459184 | 4.074551 | 0.580284 | — |

Stop reason: `fixed_update_budget`.

## Ratings arm: ratings phase

Publication: **automatic; VM publisher with 30-second checks**.

Status: **stopped_by_user**. Completed epochs: **2**. Recorded optimizer updates: **575**.

| Epoch | Optimizer updates | Validation Spearman | Validation MSE, 1–5 | Training loss | Patience counter |
|---:|---:|---:|---:|---:|---:|
| 1 | 219 | 0.816749 | 0.932301 | 0.036532 | 0 |
| 2 | 438 | 0.821362 | 0.886504 | 0.030911 | 0 |

## Proposition arm: ratings phase

Publication: **automatic; VM publisher with 30-second checks**.

Status: **running**. Completed epochs: **0**. Recorded optimizer updates: **50**.

Awaiting the first completed epoch.
