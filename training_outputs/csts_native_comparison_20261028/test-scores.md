# Test scores from completed fits

| Seed | Test rows | Spearman | Normalized MSE | Selected epoch | Terminal epoch |
| --- | --- | --- | --- | --- | --- |
| 8 | 2431 | 0.857118451 | 0.040215428 | 3 | 13 |

Seed 8 completed the committed validation stopping rule. This score uses its frozen selected model. Seeds 7 and 9 continue under their committed validation rule. The final report will give the three seed mean, paired historical comparisons and source group intervals.

[Methods](../../plans/csts-native-comparison-methods.md) · [Score and selection](seed8-test.json) · [Cloud receipts](seed8-test-cloud-receipts.json)

On the 2430 verified common test rows, seed 8 has Spearman 0.857082835 and the saved ratings control has 0.855374781. The paired gain is **0.001708**, with source group 95% interval **[-0.003630, 0.007491]** from 2,000 draws.

[Paired comparison and provenance](seed8-paired-comparison.json)
