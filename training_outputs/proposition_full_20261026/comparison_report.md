# Qwen proposition supervision followed by ratings

| Split / cohort | n | Groups | Ratings Spearman | Proposition Spearman | Difference [95% CI] |
|---|---:|---:|---:|---:|---|
| validation / all | 1576 | 680 | 0.875915 | 0.875049 | -0.000866 [-0.007245, +0.005344] |
| validation / appearance | 94 | 71 | 0.826893 | 0.859122 | +0.032229 [-0.026617, +0.113614] |
| validation / colour | 74 | 54 | 0.863625 | 0.877269 | +0.013643 [-0.040378, +0.081452] |
| test / all | 2430 | 1222 | 0.853227 | 0.854075 | +0.000848 [-0.006047, +0.008103] |
| test / appearance | 137 | 128 | 0.889015 | 0.834827 | -0.054188 [-0.111817, -0.014430] |
| test / colour | 120 | 113 | 0.914643 | 0.862670 | -0.051972 [-0.116766, -0.009414] |

Both arms share first-phase comparison exposure, initialization and update counts. The proposition arm receives generation supervision from the frozen partial training bank. Both arms then train on the full ratings training partition with the same learning rate and validation patience. The selected checkpoints were frozen before test scoring.

Rating errors use a separate positive affine calibration fitted on each arm's selected validation predictions. The JSON records raw and calibrated rating errors, group-held-out validation calibration error, exact cohort definitions and paired source-group intervals. Spearman uses the original scores and tie structure.

This experiment uses one training seed. The teacher fidelity assessment was model assisted and sampled. Results describe the available training targets and the fixed C-STS partitions.
