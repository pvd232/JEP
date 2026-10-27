# Overnight pilot: jep-csts-v1

Training: **6,051** comparisons. Validation: **1,576**. Test: **2,430**.

Both models use validation patience **2**, with an equal **8,100-second** ratings-training budget per model. The morning report deadline is **8:00 a.m. ET, October 27**.

[Earlier V4.1 comparison](v41_final_epoch_scores.md)
# Qwen proposition comparison: per-epoch validation scores

Updated: **2026-10-27T05:33:17+00:00**. Run: `jep_csts_v1_existing_propositions_patience2_20261027`.

Status: **running**. Current stage: **prepare**.

Validation: **1,576 comparisons**, 680 source groups.

Source commit: `8df0a1039bb5be8ddfd8407bdd32aa64a102018a`.
Validation SHA-256: `e42d9544b2aa6814708337d0ce38eba1d64124645b62489ed448c6784dbc71ff`.
Training SHA-256: `9a9eac21ee73b9b029ca6f62584891dd13c74aa78e80efd764532a87665ae6a4`.

Both models start from the same pretrained weights. For the first two epochs, both see the comparisons covered by existing propositions. The ratings model learns ratings; the proposition model learns to write propositions. Both then learn ratings from the full training set. Ratings training uses validation patience 2 and an epoch ceiling of 24.

Rating loss measures error in predicted ratings on the 0–1 scale. Proposition-writing loss measures error in predicted text tokens. Each table counts optimizer updates from the beginning of that training step.

Appearance and colour scores are available in the final report. Native epoch traces contain overall validation scores. Values are provisional while the comparison is running.

## Ratings model: first two epochs on the covered subset

Status: **pending**. Completed epochs: **0**. Recorded optimizer updates: **0**.

Awaiting the first completed epoch.

## Proposition model: writing propositions on the covered subset

Status: **pending**. Completed epochs: **0**. Recorded optimizer updates: **0**.

Awaiting the first completed epoch.

## Ratings model: ratings on the full training set

Status: **pending**. Completed epochs: **0**. Recorded optimizer updates: **0**.

Awaiting the first completed epoch.

## Proposition model: ratings on the full training set

Status: **pending**. Completed epochs: **0**. Recorded optimizer updates: **0**.

Awaiting the first completed epoch.
