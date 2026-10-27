# Qwen proposition supervision followed by ratings

| Split / cohort | n | Groups | Ratings Spearman | Proposition Spearman | Difference [95% CI] |
|---|---:|---:|---:|---:|---|
| validation / all | 1576 | 680 | 0.876046 | 0.878013 | +0.001967 [-0.005433, +0.009122] |
| validation / appearance | 94 | 71 | 0.843984 | 0.862401 | +0.018416 [-0.041309, +0.100401] |
| validation / colour | 74 | 54 | 0.877947 | 0.868990 | -0.008957 [-0.062558, +0.040044] |
| test / all | 2430 | 1222 | 0.855719 | 0.854362 | -0.001357 [-0.008059, +0.005171] |
| test / appearance | 137 | 128 | 0.889000 | 0.860602 | -0.028398 [-0.055429, -0.005413] |
| test / colour | 120 | 113 | 0.916186 | 0.892748 | -0.023438 [-0.050512, -0.001494] |

Both arms share first-phase comparison exposure, initialization and update counts. The proposition arm receives generation supervision from the frozen partial training bank. Both arms then train on the full ratings training partition with the same learning rate and validation patience. The selected checkpoints were frozen before test scoring.

Rating errors use a separate positive affine calibration fitted on each arm's selected validation predictions. The JSON records raw and calibrated rating errors, group-held-out validation calibration error, exact cohort definitions and paired source-group intervals. Spearman uses the original scores and tie structure.

This experiment uses one training seed. The teacher fidelity assessment was model assisted and sampled. Results describe the available training targets and the fixed C-STS partitions.
