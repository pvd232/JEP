# Joint LoRA and comparison training

Status: A100 40 GB fallback verified; remote setup and fitting launcher started. Training progress confirmation is pending restoration of the Mac terminal connection. Execution authorized October 28, 2026.

[Methods](../../plans/csts-native-comparison-methods.md) · [Review](../../plans/csts-native-comparison-review.md) · [Configuration](../../configs/csts-native-comparison.json)

Training starts from the public Qwen3 Embedding 8B checkpoint with fresh LoRA and a zero initialized learned comparison. Rating MSE trains both components. The initial run uses seed 7. A selected validation Spearman above the saved control's 0.8718754731182672 releases seeds 8 and 9.

Eight focused integration tests passed in the existing L4 environment. The saved control covers the same 1,576 validation rows with identical text and targets.

The earlier Colab kernel logs confirm an A100 with 81,920 MiB. The allocation request uses `colab new --gpu A100 --high-mem`. Both high memory attempts returned Service Unavailable. The standard A100 request timed out locally; its server assignment was recovered and verified as NVIDIA A100 SXM4 40 GB with 40,960 MiB.

Scientific source: `09e79e89a6373a083aafa165aad2dea7e6d1ee32`. The pinned Qwen download and the dependency installation completed. The independent remote setup and fitting launcher started as process 3564. The Mac terminal connector then returned Session terminated; the alternate terminal connection also failed. Actual optimizer counters, checkpoint publication status and shutdown remain unconfirmed until access is restored.

The archived control validation predictions were sealed through the native VIPER Cloud file API. Training and validation input references are retained with their original hashes. The native training stage publishes immutable epoch states asynchronously and waits for its publications at completion. The external monitoring and shutdown controller still requires an active terminal connection.

Epoch checkpoints use VIPER Cloud publication asynchronously. All pending publications are checked before each owned runtime is shut down.

| Time (UTC) | Event | Seed | Epoch | Validation Spearman | Status |
| --- | --- | --- | --- | --- | --- |
