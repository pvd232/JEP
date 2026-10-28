# Fresh Qwen LoRA and learned comparison

Saved validation selections received test inference. The user ended the remaining training budgets after seed 8 test reporting.

| Seed | Test Spearman | Normalized MSE | Selected epoch | Retained epoch |
| --- | --- | --- | --- | --- |
| 7 | 0.858644033 | 0.037841995 | 4 | 11 |
| 8 | 0.857118451 | 0.040215428 | 3 | 13 |
| 9 | 0.855354378 | 0.039432802 | 4 | 8 |
| Mean | 0.857038954 | 0.039163408 | | |

On 2,430 verified common test rows, mean Spearman gain over the saved ratings control is **0.001627**, with paired source group 95% interval **[-0.003210, 0.007040]** from 2,000 draws.

The user ended seeds 7 and 9 after seed 8 test reporting and requested inference from their existing validation selections. Seed 8 completed the original stopping rule. The three seed summary is conditional on the initial validation decision. Intervals describe test source uncertainty for these retained models. The historical control retains its original training history.

[Methods](../../plans/csts-native-comparison-methods.md) · [Diagnostics](results.json) · [Fit traces](fit-traces.json) · [Cloud receipts](cloud-receipts.json)
