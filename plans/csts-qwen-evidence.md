# Qwen evidence pretraining followed by rating training

## Question

Does evidence supervision improve the Qwen3-Embedding-8B encoder beyond additional rating training? The existing rating-only model scored 0.778882 test Spearman. That historical score is a reference; the causal comparison is between the two new matched arms.

## Arms and training

| Arm | Phase A: two fixed epochs | Phase B: at most 24 epochs |
|---|---|---|
| Rating control | Rating MSE on comparisons with accepted evidence | Rating MSE on the full training partition |
| Evidence | Predict accepted condition-specific evidence tokens | Rating MSE on the full training partition |

Both arms begin with the original pinned Qwen embedding checkpoint and fresh attention LoRA adapters, seed 7, rank/alpha 32, dropout 0.05. Adapter initialization, phase-A comparison subset, batch order and update count are identical. Phase B restores terminal phase-A weights, resets AdamW and RNG identically, and shares the same data, schedule and checkpoint rule. Neither arm starts from the already rating-trained checkpoint.

Both phases use constant learning rate 2e-5, weight decay 0.01, effective batch size 32 comparisons and two-comparison microbatches. Phase A completes its fixed two epochs without early stopping; phase B selects by validation Spearman, with strict-improvement patience five and a 24-epoch ceiling. The first phase is a short transfer screen, rather than a repetition of the six-epoch FLAN experiment. A truncated phase A invalidates the matched comparison.

Evidence training processes additional answer tokens. We match comparison exposure and optimizer updates, not exact token counts or GPU time; both costs are recorded. Phase-B stopping epochs may differ under the common patience rule.

## Evidence objective and output head

The input prefix is exactly the existing condition/passage prompt followed by the explicit EOD token. Evidence answer tokens and a final EOD are appended during auxiliary training. The causal loss predicts each answer token from earlier tokens, masking all prefix and padding labels. Losses are averaged over tokens within each answer, then over accepted answers, with exact weighting across microbatches. Only annotated, teacher-accepted training answers contribute. Validation evidence is never used for training.

The public embedding checkpoint omits its vocabulary projection. Restore that frozen BF16 matrix from `Qwen/Qwen3-8B-Base`, revision `49e3418fbbbca6ecbdf9608b4d22e5a407081db4`. Verify that every supported embedding-token ID has exactly the same identity in the source tokenizer, retain the corresponding 151,665 rows, and bind the resulting file by SHA-256. The head is used only in evidence training and is absent from saved encoder adapters and embedding inference.

Evidence gradients must reach the shared attention adapters. A training-only CUDA preflight must show finite nonzero gradients, at least a one-percent reduction in a tiny batch's deterministic evidence loss, and sufficient GPU memory margin. Its fitted adapters are discarded. The preflight measures feasibility, not evidence quality or held-out performance.

## Evaluation and execution

Retain the existing 6,980 training, 1,830 validation and 2,620 test comparisons and their pinned hashes. Freeze both validation-selected rating checkpoints before publishing test inputs. Reuse the existing native prediction capture and independently checked CPU EVAL. Report Spearman, MSE, condition ordering and the paired source-group bootstrap interval for evidence minus ratings. Record a one-seed, previously examined-benchmark limitation explicitly.

The fixed phase-A allowance is two hours per arm; the rating allowance is sixteen hours per arm, permitting the full 24-epoch ceiling at the earlier measured throughput. The aggregate ceiling is 38 GPU-stage hours including prediction capture. Preflight throughput must be checked against these allowances before launch. Resource-budget stops are reported separately from validation-patience stops.

Native runs seal locally. Existing VIPER workers publish independently; training, scoring and result reporting never wait for cloud upload. Source and data hashes, native attempt IDs, live traces and the detached launch receipt are retained. Existing attempts are never retried blindly.
