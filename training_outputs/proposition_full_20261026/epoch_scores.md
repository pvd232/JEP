# Four initial epochs: jep-csts-v1

<!-- three-model-comparison:start -->
## Test comparison: all three models

Dataset: **jep-csts-v1**, the same **2,430 test examples** for every full-test score. Encoder checkpoints were selected on validation before test scoring.

| Model | Full-test Spearman | Full-test MSE (0–1) | Test coverage |
|---|---:|---:|---:|
| Ratings model | 0.853227 | 0.039779 | 2,430/2,430 |
| Proposition model | 0.854075 | 0.039181 | 2,430/2,430 |
| GPT-6.1 Sol (max) | 0.919955 | 0.023513 | 2,430/2,430 |

Encoder scores above come from the completed **2-initial-epoch** comparison.
The four-initial-epoch follow-up is training; its test scores will replace the encoder rows after checkpoint selection and test evaluation finish.

[Sol capture status and protocol](gpt61_sol_max_jep_v1.md). Test scores do not control training, checkpoint selection or the proposition-generation decision.
<!-- three-model-comparison:end -->

Training: **6,051** comparisons. Validation: **1,576**. Test: **2,430**.

Stop after consecutive non-improving validation checks: ratings control **1**; proposition model **1**. Keep each model's best validation checkpoint. Time and epoch limits are disabled. Both models receive four matched initial epochs, then train ratings on all 6,051 comparisons. [Completed two-epoch comparison](two_epoch_phase1_scores.md).

[Earlier V4.1 comparison](v41_final_epoch_scores.md)

[Missing proposition generation progress](generation_progress.md)
# Qwen proposition comparison: per-epoch validation scores

Updated: **2026-10-27T17:14:12+00:00**. Run: `jep_csts_v1_four_initial_epochs_patience1_20261027`.

Status: **running**. Current stage: **predict_ratings**.

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

Status: **succeeded**. Completed epochs: **5**. Recorded optimizer updates: **950**.

| Epoch | Optimizer updates | Validation Spearman | Validation MSE, 1–5 | Training loss | Patience counter |
|---:|---:|---:|---:|---:|---:|
| 1 | 190 | 0.867862 | 0.553872 | 0.035847 | 0 |
| 2 | 380 | 0.871482 | 0.523937 | 0.028232 | 0 |
| 3 | 570 | 0.873098 | 0.522236 | 0.023194 | 0 |
| 4 | 760 | 0.876046 | 0.504905 | 0.018769 | 0 |
| 5 | 950 | 0.874538 | 0.526677 | 0.014946 | 1 |

Stop reason: `validation_patience`.

## Proposition model: ratings on the full training set

Training hardware: **NVIDIA A100-SXM4-40GB**. Overall batch: **32**; microbatch: **32**. Ratings control continues on the Asian L4. Both models keep patience 1 and their best validation checkpoints.

Status: **succeeded**. Completed epochs: **5**. Recorded optimizer updates: **950**.

| Epoch | Optimizer updates | Validation Spearman | Validation MSE, 1–5 | Training loss | Patience counter |
|---:|---:|---:|---:|---:|---:|
| 1 | 190 | 0.850552 | 0.653380 | 0.065883 | 0 |
| 2 | 380 | 0.868537 | 0.537077 | 0.036545 | 0 |
| 3 | 570 | 0.874755 | 0.504934 | 0.029097 | 0 |
| 4 | 760 | 0.878013 | 0.484305 | 0.023880 | 0 |
| 5 | 950 | 0.872995 | 0.530179 | 0.019706 | 1 |

Stop reason: `validation_patience`.

<!-- proposition-validation:start -->
## Proposition validation and full-training generation

Monitor: **complete**.

Training inputs captured: **11,909/11,909**; missing inputs requested: **9,413**. The current training bank remains frozen.

Held-out sample: **128 validation source groups**, one passage-condition input per group. References and generated answers are kept outside training. Evaluation uses the retained checkpoints; hardware and progress appear in the detailed status below.

| Proposition checkpoint | Held-out answer loss | Model-reviewed factual accuracy | Reviewed answers |
|---|---:|---:|---:|
| After 2 proposition-writing epochs | 0.451316 | 89.1% | 64 |
| After 4 proposition-writing epochs | 0.378650 | 93.8% | 64 |

Loss averages each answer's next-token cross-entropy, then averages answers. Factual checks use free-generated answers and two independent source-only model reviews; they report support, omissions, unsupported assertions and reviewer agreement. These measurements describe proposition writing and do not change the running experiment's stopping rule.

Earlier checkpoints were overwritten by the original trainer; epochs 2 and 4 have retained checkpoints. [Detailed status and results](proposition_validation.json).

Held-out reference review: **125/128** fully correct by both model reviewers; **0** flagged for unsupported assertions; reviewer agreement **99.2%**.

Training-generation review: **125/128** fully correct by both model reviewers; **1** flagged for unsupported assertions; reviewer agreement **99.2%**.
<!-- proposition-validation:end -->
