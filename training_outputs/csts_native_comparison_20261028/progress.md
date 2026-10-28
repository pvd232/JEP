# Joint LoRA and comparison training

Updated: 2026-10-28 16:30:29 EDT.

[Methods](../../plans/csts-native-comparison-methods.md) · [Review](../../plans/csts-native-comparison-review.md) · [Configuration](../../configs/csts-native-comparison.json)

Scientific fitting source: `09e79e89a6373a083aafa165aad2dea7e6d1ee32`.

Seed 7 starts from the original pretrained Qwen with fresh LoRA and a zero initialized symmetric comparison. Rating MSE trains both components. The saved ratings control has validation Spearman 0.8718754731182672 on the identical 1,576 rows. A positive result releases seeds 8 and 9.

The previous Colab A100 assignment disappeared during the terminal interruption. Seed 7 is running on the cached GCE L4 while a replacement A100 is requested. GPU readings and optimizer counters below are observed directly from the worker.

| Seed | Hardware observation | Optimizer updates | Completed epochs | Best validation Spearman | Sealed Cloud checkpoints | Native run status |
| --- | --- | --- | --- | --- | --- | --- |
| 7 | NVIDIA L4, 16322 MiB, 90 % | 150 | 0 | 0.2683437738750382 | 1 | running |

## Completed epochs

| Epoch | Updates | Training MSE | Validation Spearman | Validation MSE | Selected epoch |
| --- | --- | --- | --- | --- | --- |

Epoch checkpoint copies publish through the native VIPER Cloud file API on a background thread. The fitting stage checks every pending publication at completion. Each task owned GPU is shut down after its required uploads and evaluation work complete.
