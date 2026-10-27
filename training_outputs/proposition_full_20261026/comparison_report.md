# Completed full-bank proposition comparison

## Test comparison: all three models

Dataset: **jep-csts-v1**. All models are scored on the same **2,430 test examples**. Encoder checkpoints were frozen using validation scores before test evaluation.

| Model | Full-test Spearman | Raw MSE (0–1) | Test coverage |
|---|---:|---:|---:|
| Ratings model | 0.855375 | 0.038359 | 2,430/2,430 |
| Proposition model | 0.863398 | 0.035584 | 2,430/2,430 |
| GPT-6.1 Sol (max) | 0.919955 | 0.023513 | 2,430/2,430 |

The full-bank comparison is complete. Both first-phase parents use epoch **5**, with **920 optimizer updates**. Ratings validation selected control epoch **2** and proposition epoch **4**. The Sol score is the existing completed baseline on this same frozen test split.

[Detailed comparison and paired intervals](comparison_report.md). [Sol protocol](gpt61_sol_max_jep_v1.md).

Test Spearman difference (proposition minus ratings): **+0.008024**, paired 95% interval **[-0.000163, +0.015949]**. The interval includes zero.

# Qwen proposition supervision followed by ratings

| Split / cohort | n | Groups | Ratings Spearman | Proposition Spearman | Difference [95% CI] |
|---|---:|---:|---:|---:|---|
| validation / all | 1576 | 680 | 0.871875 | 0.877061 | +0.005185 [-0.004414, +0.015090] |
| validation / appearance | 94 | 71 | 0.821293 | 0.852249 | +0.030956 [-0.036712, +0.117266] |
| validation / colour | 74 | 54 | 0.883620 | 0.855625 | -0.027995 [-0.093561, +0.022353] |
| test / all | 2430 | 1222 | 0.855375 | 0.863398 | +0.008024 [-0.000163, +0.015949] |
| test / appearance | 137 | 128 | 0.882614 | 0.842728 | -0.039886 [-0.086671, -0.005679] |
| test / colour | 120 | 113 | 0.909812 | 0.871742 | -0.038070 [-0.083955, -0.002712] |

Both arms share first-phase comparison exposure, initialization and update counts. The proposition arm receives generation supervision from the frozen full generated training bank. Both arms then train on the full ratings training partition with the same learning rate and validation patience. The selected checkpoints were frozen before test scoring.

Rating errors use a separate positive affine calibration fitted on each arm's selected validation predictions. The JSON records raw and calibrated rating errors, group-held-out validation calibration error, exact cohort definitions and paired source-group intervals. Spearman uses the original scores and tie structure.

This experiment uses one training seed. The teacher fidelity assessment was model assisted and sampled. Results describe the available training targets and the fixed C-STS partitions.

## Run and recovery provenance

Writing stopped at epoch 6 and selected epoch 5. The matched ratings parent uses the same 920 updates. Ratings training stopped after 3 epochs for the control and 5 for the proposition model; validation selected epochs 2 and 4. Both checkpoints were frozen before test scoring.


Both selected first-phase parents use epoch 5. The control’s speculative epochs 6–7 remain recorded and were excluded from the matched parent. The writing metadata fix is reviewable in [PR #13](https://github.com/pvd232/JEP/pull/13). The original test index was restored byte for byte from a previously sealed artifact before scoring.

Selected model weights and frozen inputs are preserved in `/home/machina/jep-full-propositions-20261027-operator/checkpoints/selected_checkpoints.tar` on the JEP VM. Archive SHA-256: `2e8e8efe52687edb10b85f000f6a2f77637677f59ae95729ee1c254d11c37d9d`. The JSON includes checkpoint hashes, raw and calibrated errors, cohort definitions, and 2,000 paired bootstrap draws.
