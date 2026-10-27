# Qwen proposition supervision followed by ratings

| Split / cohort | n | Groups | Ratings Spearman | Proposition Spearman | Difference [95% CI] |
|---|---:|---:|---:|---:|---|
| validation / all | 1576 | 680 | 0.870685 | 0.873187 | +0.002502 [-0.009049, +0.014628] |
| validation / appearance | 94 | 71 | 0.839792 | 0.842255 | +0.002463 [-0.054381, +0.049287] |
| validation / colour | 74 | 54 | 0.899853 | 0.863949 | -0.035903 [-0.133097, +0.027841] |
| test / all | 2430 | 1222 | 0.853183 | 0.854933 | +0.001750 [-0.006235, +0.009733] |
| test / appearance | 137 | 128 | 0.883811 | 0.816561 | -0.067250 [-0.141307, -0.013906] |
| test / colour | 120 | 113 | 0.909866 | 0.845153 | -0.064712 [-0.142858, -0.012058] |

Both arms share first-phase comparison exposure, initialization and update counts. The proposition arm receives generation supervision from the frozen full generated training bank. Both arms then train on the full ratings training partition with the same learning rate and validation patience. The selected checkpoints were frozen before test scoring.

Rating errors use a separate positive affine calibration fitted on each arm's selected validation predictions. The JSON records raw and calibrated rating errors, group-held-out validation calibration error, exact cohort definitions and paired source-group intervals. Spearman uses the original scores and tie structure.

This experiment uses one training seed. The teacher fidelity assessment was model assisted and sampled. Results describe the available training targets and the fixed C-STS partitions.

[Three-seed summary](../../three_seed_replication.md). [Frozen protocol](../../replication_protocol.json).
