# Qwen proposition supervision followed by ratings

| Split / cohort | n | Groups | Ratings Spearman | Proposition Spearman | Difference [95% CI] |
|---|---:|---:|---:|---:|---|
| validation / all | 1576 | 680 | 0.874021 | 0.876124 | +0.002104 [-0.006589, +0.011159] |
| validation / appearance | 94 | 71 | 0.833009 | 0.868262 | +0.035253 [-0.032892, +0.129607] |
| validation / colour | 74 | 54 | 0.888414 | 0.880398 | -0.008016 [-0.064791, +0.041777] |
| test / all | 2430 | 1222 | 0.853866 | 0.860513 | +0.006646 [-0.001141, +0.015000] |
| test / appearance | 137 | 128 | 0.877993 | 0.852483 | -0.025510 [-0.072896, +0.011728] |
| test / colour | 120 | 113 | 0.898848 | 0.881806 | -0.017042 [-0.068603, +0.019782] |

Both arms share first-phase comparison exposure, initialization and update counts. The proposition arm receives generation supervision from the frozen full generated training bank. Both arms then train on the full ratings training partition with the same learning rate and validation patience. The selected checkpoints were frozen before test scoring.

Rating errors use a separate positive affine calibration fitted on each arm's selected validation predictions. The JSON records raw and calibrated rating errors, group-held-out validation calibration error, exact cohort definitions and paired source-group intervals. Spearman uses the original scores and tie structure.

This experiment uses one training seed. The teacher fidelity assessment was model assisted and sampled. Results describe the available training targets and the fixed C-STS partitions.

[Three-seed summary](../../three_seed_replication.md). [Frozen protocol](../../replication_protocol.json).
