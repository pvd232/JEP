# Joint LoRA and comparison training

Status: preparing the initial seed 7 run. Execution authorized October 28, 2026.

[Methods](../../plans/csts-native-comparison-methods.md) · [Review](../../plans/csts-native-comparison-review.md) · [Configuration](../../configs/csts-native-comparison.json)

Training starts from the public Qwen3 Embedding 8B checkpoint with fresh LoRA and a zero initialized learned comparison. Rating MSE trains both components. The initial run uses seed 7. A selected validation Spearman above the saved control's 0.8718754731182672 releases seeds 8 and 9.

Eight focused integration tests passed in the existing L4 environment. The saved control covers the same 1,576 validation rows with identical text and targets.

The A100 high memory allocation returned Service Unavailable twice. The standard A100 request timed out locally and left a server assignment; recovery is in progress. The earlier Colab kernel logs confirm an A100 with 81,920 MiB. Hardware verification and fitting counters follow below.

Epoch checkpoints use VIPER Cloud publication asynchronously. All pending publications are checked before each owned runtime is shut down.

| Time (UTC) | Event | Seed | Epoch | Validation Spearman | Status |
| --- | --- | --- | --- | --- | --- |
