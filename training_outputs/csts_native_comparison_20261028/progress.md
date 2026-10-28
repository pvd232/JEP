# Inference from saved validation checkpoints

Training has stopped at the user request. Seeds 7 and 9 use their existing epoch 4 validation selections. Seed 8 test Spearman is **0.857118451** over 2,431 comparisons.

| Seed | Selected epoch | Best validation Spearman | Status |
| --- | --- | --- | --- |
| 7 | 4 | 0.878920452 | Saved model inference |
| 8 | 3 | 0.876898741 | Test score published; A100 stopped after Cloud verification |
| 9 | 4 | 0.877086745 | Saved model inference |

[Test scores](test-scores.md) · [Training budget amendment](stopping-amendment.json) · [Methods](../../plans/csts-native-comparison-methods.md)
