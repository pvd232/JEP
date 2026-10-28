# Joint LoRA and comparison training

Updated: 2026-10-28 17:14:16 EDT.

[Methods](../../plans/csts-native-comparison-methods.md) · [Review](../../plans/csts-native-comparison-review.md) · [Configuration](../../configs/csts-native-comparison.json)

Seed 7 passed the validation continuation rule at epoch 3: **0.875151**, compared with the saved ratings control **0.871875**. The sealed Cloud checkpoint released seeds 8 and 9. Each model starts from original pretrained Qwen, fresh LoRA and a zero initialized learned comparison. Rating MSE trains both components.

Seed 7 fitting source: `09e79e89a6373a083aafa165aad2dea7e6d1ee32`. Follow on fitting source: `15776f8e2110df648379eed65331c5decbd4dd8a`.

| Seed | Hardware | Optimizer updates | Completed epochs | Best validation Spearman | Sealed Cloud checkpoints | Status |
| --- | --- | --- | --- | --- | --- | --- |
| 7 | NVIDIA L4, 16352 MiB, 100 % | 850 | 4 | 0.8789204517574798 | 5 | running |
| 8 | A100 40 GB | 0 | 0 | pending | 0 | preparing |
| 9 | NVIDIA L4 | 225 | 1 | 0.859669 | 2 | running |

## Validation history

| Seed | Epoch | Spearman | Normalized MSE |
| --- | --- | --- | --- |
| 7 | 1 | 0.859860461 | 0.037323 |
| 7 | 2 | 0.871742952 | 0.032889 |
| 7 | 3 | 0.875151297 | 0.031849 |
| 7 | 4 | 0.878920452 | 0.029810 |
| 9 | 1 | 0.859669000 | 0.038450 |

VIPER publishes immutable epoch states asynchronously while fitting continues. Every selected model, terminal state, optimizer, trace and prediction artifact is checked through Cloud publication receipts before a worker is shut down. Final test evaluation follows frozen selection of all three models.
