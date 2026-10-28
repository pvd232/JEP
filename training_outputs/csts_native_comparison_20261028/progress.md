# Joint LoRA and comparison training

Updated: 2026-10-28 18:11:31 EDT.

[Methods](../../plans/csts-native-comparison-methods.md) · [Review](../../plans/csts-native-comparison-review.md) · [Configuration](../../configs/csts-native-comparison.json)

Seed 7 passed the validation continuation rule at epoch 3: **0.875151**, compared with the saved ratings control **0.871875**. The sealed Cloud checkpoint released seeds 8 and 9. Each model starts from original pretrained Qwen, fresh LoRA and a zero initialized learned comparison. Rating MSE trains both components.

Seed 7 fitting source: `09e79e89a6373a083aafa165aad2dea7e6d1ee32`. Follow on fitting source: `15776f8e2110df648379eed65331c5decbd4dd8a`.

| Seed | Hardware | Optimizer updates | Completed epochs | Best validation Spearman | Sealed Cloud checkpoints | Status |
| --- | --- | --- | --- | --- | --- | --- |
| 7 | NVIDIA L4, 16352 MiB, 90 % | 1775 | 9 | 0.8789204517574798 | 10 | running |
| 8 | NVIDIA A100-SXM4-40GB | 2450 | 13 | 0.8768987411388853 | 13 | succeeded |
| 9 | NVIDIA L4 | 1125 | 6 | 0.877087 | 6 | running |

## Validation history

| Seed | Epoch | Spearman | Normalized MSE |
| --- | --- | --- | --- |
| 7 | 1 | 0.859860461 | 0.037323 |
| 7 | 2 | 0.871742952 | 0.032889 |
| 7 | 3 | 0.875151297 | 0.031849 |
| 7 | 4 | 0.878920452 | 0.029810 |
| 7 | 5 | 0.877367894 | 0.030299 |
| 7 | 6 | 0.877312662 | 0.031826 |
| 7 | 7 | 0.876534619 | 0.031127 |
| 7 | 8 | 0.872750912 | 0.032820 |
| 7 | 9 | 0.874183621 | 0.032465 |
| 8 | 1 | 0.858764000 | 0.043982 |
| 8 | 2 | 0.868667000 | 0.035412 |
| 8 | 3 | 0.876899000 | 0.033206 |
| 8 | 4 | 0.874992000 | 0.031252 |
| 8 | 5 | 0.875583000 | 0.033537 |
| 8 | 6 | 0.872982000 | 0.034048 |
| 8 | 7 | 0.875681000 | 0.031366 |
| 8 | 8 | 0.869135000 | 0.033846 |
| 8 | 9 | 0.874076000 | 0.032357 |
| 8 | 10 | 0.872898000 | 0.034396 |
| 8 | 11 | 0.870049000 | 0.035566 |
| 8 | 12 | 0.871052000 | 0.034132 |
| 8 | 13 | 0.870941000 | 0.034114 |
| 9 | 1 | 0.859669000 | 0.038450 |
| 9 | 2 | 0.871050000 | 0.033351 |
| 9 | 3 | 0.875347000 | 0.031563 |
| 9 | 4 | 0.877087000 | 0.031273 |
| 9 | 5 | 0.876133000 | 0.030806 |
| 9 | 6 | 0.872990000 | 0.033427 |

VIPER publishes immutable epoch states asynchronously while fitting continues. Every selected model, terminal state, optimizer, trace and prediction artifact is checked through Cloud publication receipts before a worker is shut down. Seed 8 resumed its complete epoch 2 state after its first A100 assignment became unavailable. Each reported test score uses a completed fit and its frozen selected model. Remaining fits continue under the committed validation rule. The aggregate report follows completion of all three fits.
