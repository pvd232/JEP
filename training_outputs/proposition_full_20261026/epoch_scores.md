# Training with validation early stopping: jep-csts-v1

<!-- three-model-comparison:start -->
Both models train concurrently on the **80 GB A100** where their stages overlap. Each uses effective batch **32** and microbatch **32**. Writing checkpoint selection uses held-out proposition loss; ratings checkpoint selection uses validation Spearman.

## Test comparison: all three models

Dataset: **jep-csts-v1**, the same **2,430 test examples** for every full-test score. Encoder checkpoints were selected on validation before test scoring.

| Model | Full-test Spearman | Full-test MSE (0–1) | Test coverage |
|---|---:|---:|---:|
| Ratings model | 0.855719 | 0.038521 | 2,430/2,430 |
| Proposition model | 0.854362 | 0.038841 | 2,430/2,430 |
| GPT-6.1 Sol (max) | 0.919955 | 0.023513 | 2,430/2,430 |

Encoder scores above come from the completed **4-initial-epoch** comparison.
The full-bank comparison is training until validation patience is exhausted. Its test scores will replace the encoder rows after checkpoint selection and evaluation finish.

[Sol capture status and protocol](gpt61_sol_max_jep_v1.md). Test scores do not control training, checkpoint selection or the proposition-generation decision.
<!-- three-model-comparison:end -->

Training: **6,051** comparisons. Validation: **1,576**. Test: **2,430**.

Stop after consecutive non-improving validation checks: ratings control **1**; proposition model **1**. Keep each model's best validation checkpoint. Time and epoch limits are disabled.

[Earlier V4.1 comparison](v41_final_epoch_scores.md)

[Missing proposition generation progress](generation_progress.md)
# Qwen proposition comparison: per-epoch validation scores

Updated: **2026-10-27T18:48:59+00:00**. Run: `jep_csts_v1_full_propositions_converged_patience1_20261027`.

Status: **running**. Current stage: **evidence_pretrain**.

Validation: **1,576 comparisons**, 680 source groups.

Source commit: `3ef6ba0616614632abc5bc0b2f2e2c71886c2f0e`.
Validation SHA-256: `e42d9544b2aa6814708337d0ce38eba1d64124645b62489ed448c6784dbc71ff`.
Training SHA-256: `9a9eac21ee73b9b029ca6f62584891dd13c74aa78e80efd764532a87665ae6a4`.

The proposition model writes answers from the full generated training bank until held-out proposition loss fails to improve for one epoch. Its best writing checkpoint determines the initial epoch count for the ratings control, which uses the same comparisons, batch size, and update count. Both then learn ratings from all 6,051 training comparisons with validation Spearman patience 1. Writing and ratings training have no epoch or wall-time stopping ceiling.

Rating loss measures error in predicted ratings on the 0–1 scale. Proposition-writing loss measures error in predicted text tokens. Each table counts optimizer updates from the beginning of that training step.

Appearance and colour scores are available in the final report. Native epoch traces contain overall validation scores. Values are provisional while the comparison is running.

## Ratings control: matched exposure on the full proposition-covered training comparisons

Status: **running**. Completed epochs: **6**. Recorded optimizer updates: **1175**.

| Epoch | Optimizer updates | Validation Spearman | Validation MSE, 1–5 | Training loss | Patience counter |
|---:|---:|---:|---:|---:|---:|
| 1 | 184 | 0.851194 | 0.637961 | 0.073888 | — |
| 2 | 368 | 0.865684 | 0.551154 | 0.036752 | — |
| 3 | 552 | 0.869931 | 0.527240 | 0.029286 | — |
| 4 | 736 | 0.869917 | 0.525745 | 0.023787 | — |
| 5 | 920 | 0.867871 | 0.542020 | 0.018940 | — |
| 6 | 1104 | 0.868375 | 0.548501 | 0.015129 | — |

## Proposition model: full-bank writing until held-out loss stops improving

Status: **running**. Completed epochs: **6**. Recorded optimizer updates: **1104**.

| Epoch | Optimizer updates | Validation Spearman | Validation MSE, 1–5 | Training loss | Patience counter |
|---:|---:|---:|---:|---:|---:|
| 1 | 184 | 0.473837 | 4.145213 | 2.065912 | 0 |
| 2 | 368 | 0.456222 | 4.158023 | 0.362596 | 0 |
| 3 | 552 | 0.480442 | 4.088359 | 0.302398 | 0 |
| 4 | 736 | 0.497221 | 4.051999 | 0.269739 | 0 |
| 5 | 920 | 0.500324 | 4.027831 | 0.247407 | 0 |
| 6 | 1104 | 0.511156 | 3.865550 | 0.227567 | 1 |

Held-out proposition loss selects the writing checkpoint:

| Epoch | Held-out proposition loss |
|---:|---:|
| 1 | 0.383228 |
| 2 | 0.319839 |
| 3 | 0.297286 |
| 4 | 0.285763 |
| 5 | 0.275350 |
| 6 | 0.289219 |

Stop reason: `proposition_validation_patience`.

## Ratings model: ratings on the full training set

Status: **running**. Completed epochs: **0**. Recorded optimizer updates: **0**.

Awaiting the first completed epoch.

## Proposition model: ratings on the full training set

Status: **pending**. Completed epochs: **0**. Recorded optimizer updates: **0**.

Awaiting the first completed epoch.

## A100 and L4 timing comparison

Keep both models on the A100. The L4 control would become the slower arm and extend the projected time to finish both models.

Control tests used the same epoch-4 checkpoint, optimizer batch 32, and microbatch 32. Each control test measured 12 updates after 2 warmup updates. Writing rates came from the running experiment's trace windows.

| Work and device | Seconds per optimizer update |
|---|---:|
| Ratings control on A100 alongside proposition training | 2.074 |
| Ratings control alone on L4 | 3.971 |
| Proposition writing on shared A100 | 2.947 |
| Proposition writing alone on A100 | 1.347 |

All experiment checkpoints and optimizer/RNG state remain on the A100. Disposable timing weights were excluded from scientific results.

Short training-window estimate for 184 matched updates per arm; validation, checkpoint writes, transfer and startup add time. Actual stopping epochs depend on validation patience.

<!-- proposition-validation:start -->
## Proposition validation and full-training generation

Monitor: **complete**.

Training inputs captured: **11,909/11,909**; missing inputs requested: **9,413**. The complete generated bank is frozen for the current full-bank comparison.

Held-out sample: **128 validation source groups**, one passage-condition input per group. References and generated answers are kept outside training. Evaluation uses the retained checkpoints; hardware and progress appear in the detailed status below.

| Proposition checkpoint | Held-out answer loss | Model-reviewed factual accuracy | Reviewed answers |
|---|---:|---:|---:|
| Earlier subset model: epoch 2 | 0.451316 | 89.1% | 64 |
| Earlier subset model: epoch 4 | 0.378650 | 93.8% | 64 |

Loss averages each answer's next-token cross-entropy, then averages answers. Factual checks use free-generated answers and two independent source-only model reviews; they report support, omissions, unsupported assertions and reviewer agreement. These measurements describe proposition writing and do not change the running experiment's stopping rule.

Earlier checkpoints were overwritten by the original trainer; epochs 2 and 4 have retained checkpoints. [Detailed status and results](proposition_validation.json).

Held-out reference review: **125/128** fully correct by both model reviewers; **0** flagged for unsupported assertions; reviewer agreement **99.2%**.

Training-generation review: **125/128** fully correct by both model reviewers; **1** flagged for unsupported assertions; reviewer agreement **99.2%**.
<!-- proposition-validation:end -->
