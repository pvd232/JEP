# Four initial epochs: jep-csts-v1

Training: **6,051** comparisons. Validation: **1,576**. Test: **2,430**.

Stop after consecutive non-improving validation checks: ratings control **1**; proposition model **1**. Keep each model's best validation checkpoint. Time and epoch limits are disabled. Both models receive four matched initial epochs, then train ratings on all 6,051 comparisons. [Completed two-epoch comparison](two_epoch_phase1_scores.md).

[Earlier V4.1 comparison](v41_final_epoch_scores.md)

[Missing proposition generation progress](generation_progress.md)
# Qwen proposition comparison: per-epoch validation scores

Updated: **2026-10-27T15:42:03+00:00**. Run: `jep_csts_v1_four_initial_epochs_patience1_20261027`.

Status: **running**. Current stage: **ratings_ratings**.

Validation: **1,576 comparisons**, 680 source groups.

Source commit: `67f816407f786ea038415422a9aefd57d30c92fb`.
Validation SHA-256: `e42d9544b2aa6814708337d0ce38eba1d64124645b62489ed448c6784dbc71ff`.
Training SHA-256: `9a9eac21ee73b9b029ca6f62584891dd13c74aa78e80efd764532a87665ae6a4`.

Both models start from the same pretrained weights. For the first 4 epochs, both see the comparisons covered by existing propositions. The ratings model learns ratings; the proposition model learns to write propositions. Both then learn ratings from the full training set. Ratings training stops after the configured consecutive non-improving checks: ratings control 1; proposition model 1. Training continues with time and epoch limits disabled.

Rating loss measures error in predicted ratings on the 0–1 scale. Proposition-writing loss measures error in predicted text tokens. Each table counts optimizer updates from the beginning of that training step.

Appearance and colour scores are available in the final report. Native epoch traces contain overall validation scores. Values are provisional while the comparison is running.

## Ratings model: first 4 epochs on the covered subset

Status: **succeeded**. Completed epochs: **4**. Recorded optimizer updates: **268**.

| Epoch | Optimizer updates | Validation Spearman | Validation MSE, 1–5 | Training loss | Patience counter |
|---:|---:|---:|---:|---:|---:|
| 1 | 67 | 0.810656 | 0.867627 | 0.118955 | — |
| 2 | 134 | 0.845369 | 0.670799 | 0.047767 | — |
| 3 | 201 | 0.850862 | 0.646784 | 0.035938 | — |
| 4 | 268 | 0.855431 | 0.606814 | 0.028899 | — |

Stop reason: `fixed_update_budget`.

## Proposition model: writing propositions on the covered subset

Status: **succeeded**. Completed epochs: **4**. Recorded optimizer updates: **268**.

| Epoch | Optimizer updates | Validation Spearman | Validation MSE, 1–5 | Training loss | Patience counter |
|---:|---:|---:|---:|---:|---:|
| 1 | 67 | 0.458204 | 3.295591 | 4.893944 | — |
| 2 | 134 | 0.484417 | 3.948340 | 0.611994 | — |
| 3 | 201 | 0.437921 | 4.090336 | 0.414507 | — |
| 4 | 268 | 0.430437 | 4.000323 | 0.349306 | — |

Stop reason: `fixed_update_budget`.

## Ratings model: ratings on the full training set

Status: **running**. Completed epochs: **3**. Recorded optimizer updates: **570**.

| Epoch | Optimizer updates | Validation Spearman | Validation MSE, 1–5 | Training loss | Patience counter |
|---:|---:|---:|---:|---:|---:|
| 1 | 190 | 0.867862 | 0.553872 | 0.035847 | 0 |
| 2 | 380 | 0.871482 | 0.523937 | 0.028232 | 0 |
| 3 | 570 | 0.873098 | 0.522236 | 0.023194 | 0 |

## Proposition model: ratings on the full training set

Status: **pending**. Completed epochs: **0**. Recorded optimizer updates: **0**.

Awaiting the first completed epoch.
