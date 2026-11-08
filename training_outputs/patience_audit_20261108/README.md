# Validation-patience audit — 8 November 2026

The current full-data run uses **patience 1**. One validation epoch that fails to
beat the previous best ends the fit. The worker preserves the best validation
checkpoint. Its finite native-epoch setting leaves this stopping check active.

The replay found a Qwen8B LoRA trajectory whose observed best required patience 2.
A separate older frozen-Qwen projection trajectory required patience 4. The three
recent frozen-comparator seeds reached their recorded peaks with patience 1.

## Current rule

The [live protocol](../../configs/csts-full-data-prompt-20261107.json) specifies
patience 1 and a 24-epoch cap. The [production counter](../../csts_pilot/early_stopping.py)
uses strict validation-Spearman improvement with min_delta 0 and resets its counter
after each new best. Patience 2 permits one non-improving epoch before a recovery;
two consecutive failures exhaust it.

The [native worker](../../csts_pilot/full_data_prompt_worker.py) runs sealed epochs
and selects the checkpoint when validation patience is exhausted.

## Recorded evidence

All numbers below are within-run **validation Spearman** comparisons. Dataset,
architecture and schedule differences prevent treating scores across rows as a
model leaderboard.

| Recorded history | Patience-1 best | Best observed | Minimum patience for that observed peak |
| --- | ---: | ---: | ---: |
| older_qwen_lora_condition_last | 0.773697 (epoch 2) | 0.783556 (epoch 4) | 2 |
| csts_tranche2_projection_trace | 0.615148 (epoch 7) | 0.642421 (epoch 19) | 4 |
| recent_frozen_comparator_seed_7 | 0.846447 (epoch 8) | 0.846447 (epoch 8) | 1 |
| recent_frozen_comparator_seed_8 | 0.846377 (epoch 8) | 0.846377 (epoch 8) | 1 |
| recent_frozen_comparator_seed_9 | 0.846535 (epoch 9) | 0.846535 (epoch 9) | 1 |
| epoch_scores/ratings_ratings | 0.871875 (epoch 2) | 0.871875 (epoch 2) | 1 |
| epoch_scores/evidence_ratings | 0.877061 (epoch 4) | 0.877061 (epoch 4) | 1 |

The older Qwen LoRA run gives a direct recovery example:

| Epoch | Validation Spearman | Consequence under patience 1 |
| --- | ---: | --- |
| 2 | 0.773697 | Best so far |
| 3 | 0.772979 | Stop and retain epoch 2 |
| 4 | 0.783556 | Better recorded checkpoint, missed by that stop |

Patience 2 reaches epoch 4 and retains its score, a gain of **0.009859** over the
patience-1 selection on that recorded trajectory. This experiment used older
training/validation bytes, microbatch 2, and a schedule transition after epoch 1.
The current run uses different data, physical batch 32 and a constant schedule.
It provides evidence that a short dip can recover in Qwen LoRA; the optimal
patience for the current regime remains unresolved.

The three recent frozen-comparator histories ran for 18, 18 and 19 epochs, with
peaks at 8, 8 and 9. Patience 1 would select the same checkpoints and stop at 9,
9 and 10. Their additional **27 recorded epochs** produced no higher validation
peak. These are frozen-comparator epochs, with different compute costs from LoRA.

## Recommendation and limits

**Patience 2 is a reasonable small buffer for the current LoRA study.** It captures
the documented Qwen recovery. The evidence establishes a useful buffer, while
leaving the optimal value for this full-data setup open.

The recent ratings-only and proposition-trained full-data traces retain their
recorded best with patience 1. Several ended at that first dip. Their records stop
there, so a later recovery remains unobserved. Budget-limited one- or two-epoch
traces provide similarly limited evidence. This censoring prevents a claim that
waiting longer could never help.

Other historical architectures and auxiliary pretraining objectives are retained
as context. Some also recover after declines. Their behavior is separate from the
recommendation for this LoRA run. Current training and its approved protocol were
preserved during this review; this report proposes a change.

## Method and retained inputs

Collected at **2026-11-08T08:15:50.078649+00:00**. The audit contains 38 source histories
and 34 maximal trajectories after folding identical or exact-prefix
copies with matching model, phase, seed and split identities. They are related
records rather than independent experimental replications.

The [portable inputs](inputs.json) retain validation-only epoch sequences,
configuration, dataset hashes and source-file hashes. The [complete replay](audit.json)
records patience 1, 2, 3, 4, 5 and 10 for every trajectory. The current-rule replay
starts at epoch 1; older minimum-epoch restrictions, phase transitions and other
objectives remain scope limitations. Recorded peaks describe the available trace.

Reproduce from the repository root:

~~~bash
python -m scripts.full_data_prompt_20261107.audit_patience   --inputs training_outputs/patience_audit_20261108/inputs.json   --output training_outputs/patience_audit_20261108/audit.json
~~~

Only existing validation histories were replayed. Current held-out data stayed
sealed, and the running workers continued their existing fits.
