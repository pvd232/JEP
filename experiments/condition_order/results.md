# Condition-last ablation of the actual Qwen SOTA — verified result (November 7, 2026)

**Outcome: completed; condition-last performed worse.** This study does not supersede the previous state-of-the-art system.

The earlier seven-epoch **vanilla ratings-only LoRA** replay, which scored 0.781195 on a **different 2,620-row** test set, was not a valid comparison with the actual Qwen SOTA. The correct reference is the archived October 28 experiment using **proposition-then-similarity-trained Qwen3-Embedding-8B**, with frozen encoder states and learned symmetric comparisons. Its test performance was 0.863397667 for raw cosine and **0.865230290** mean test Spearman across three learned-comparator seeds.

## Matched held-out test result

All systems are compared on the exact **2,431-row test cohort** (1,222 connected source groups). Spearman and MSE use normalized targets on the same rows, with the new comparator checkpoints selected by the 1,576-row validation set before test access.

| Scorer | Original condition first | New condition last | Difference |
| --- | ---: | ---: | ---: |
| Frozen Qwen final-EOD vector, raw cosine — test Spearman | 0.8633976672 | 0.8405641124 | −0.0228335548 |
| Symmetric learned comparator, three-seed mean — test Spearman | **0.8652302903** | **0.8498507964** | **−0.0153794939** |
| Symmetric learned comparator, three-seed mean — test MSE | **0.0351311569** | **0.0417814761** | **+0.0066503192** |

| Comparator seed | Original test Spearman | New test Spearman | New selected validation Spearman | New selected epoch |
| --- | ---: | ---: | ---: | ---: |
| 7 | 0.8646716626 | 0.8498298111 | 0.8464470461 | 8 |
| 8 | 0.8653734262 | 0.8498890600 | 0.8463767854 | 8 |
| 9 | 0.8656457820 | 0.8498335181 | 0.8465351181 | 9 |

New test MSE by seed: seed 7 = 0.0415932848541931, seed 8 = 0.04205108576715282, seed 9 = 0.04170005775359416. New raw cosine test MSE = 0.04716910528715689.

**Interpretation:** Changing the prompt order at *inference* and refitting the comparator degrades the existing frozen proposition-trained encoder's performance. **This is not a comparison of two fully retrained encoders.** The historical Qwen weights were originally trained under condition-first prompts. Training a new proposition/similarity adapter under condition-last order would be a distinct, more expensive experiment, and its performance cannot be inferred from this result. No paired bootstrap or training-seed uncertainty has been computed specifically for this new ablation; do not label the difference statistically significant. The shared test set was examined in earlier studies, so these scores remain exploratory.

## Exact experimental identity

- Original full SOTA source: [October 28 report](../csts_readout_convergence_20261028/results.md) (frozen train/evaluation source commit `fdbcb3461f63cf44d7cb3cde4de27332594e452d`).
- Pretrained base: `Qwen/Qwen3-Embedding-8B`, revision `c90816d848505624c2434128dfc61132162a0ee9`.
- Fine-tuned source checkpoint: `proposition_final.pt`, SHA-256 `d30c00fc76e70ec639493b7121a8b8c9d7520745733857c1c49f0902fff00f4f`. Original LoRA factors remain frozen throughout the new ablation.
- Splits: 6,051 training, SHA-256 `9a9eac21ee73b9b029ca6f62584891dd13c74aa78e80efd764532a87665ae6a4`; 1,576 validation, `e42d9544b2aa6814708337d0ce38eba1d64124645b62489ed448c6784dbc71ff`; 2,431 test, `d6b40b7b891ed147befb30801c2f85a8787775adebdd98d134157cbb2a6e9f76`.
- Representations: original final attended EOD state, float32 unit normalization, full width 4,096, max input 160, identical two-pair extraction layout.
- Only altered representation input: original `Instruct: ... {condition}\nQuery: {passage}` becomes `Query: {passage}\nInstruct: ... {condition}`. No adapter or language-model pretraining/finetuning steps were run in the ablation.
- Comparator: `f(a,b) = aᵀb + w_dᵀ|a-b| + w_pᵀ(a⊙b) + c`; 8,193 extra parameters, initialized to zero. Three independent seeds (7, 8, 9), AdamW 0.001, weight decay 0.01, logical batch 32, clipping 1, constant schedule, patience 10, validation-only checkpoint selection. These fits use the same original scorer objective. This run stops each seed independently on patience rather than the historical multi-arm joint patience; this does not change the selected epoch under the recorded traces.
- Implemented and launched on Mantra GCE L4 `jep-csts-format-20261021` in `asia-northeast3-a`. GPU source code: [matched ablation](../../experiments/condition_order/sota_order_ablation.py). Executed source SHA-256 `1a1c601321c3d082ee20aa5d2aec0401e71d9ed1c687e49ba86f4be446c9de5b`. First command started 2026-11-07 02:45:37 UTC; numerical test completion 2026-11-07 02:56:54 UTC.

## Independent verification and archival

- Native trainer and archive creation returned exit code 0. There were exactly three saved comparator checkpoints, each selected without test-based tuning. Complete test predictions retained for all 2,431 rows per seed.
- The three test Spearman and MSE values were independently recomputed from the saved per-row predictions using a standalone standard-library average-rank implementation. The comparisons exactly agreed to floating-point precision. Prediction and checkpoint SHA-256 hashes matched the summary/selection files.
- The archived test evidence includes extracted SHA identities, full per-seed prediction tables, selected checkpoint states, epoch traces, source script, training log, CUDA utilization and selection manifest. The frozen encoder checkpoint and large train/validation/test vector tensors remain on the original 200 GB persistent disk.
- Portable evidence GCS location: `gs://mantra-mlfg-prod-uscentral1-8e7a/viper/pvd232/jep_sota_condition_last_20261107/results-evidence.tar.gz`. Exact size **582,924 bytes**, SHA-256 `8a0759652368dba384200649ab3462c3c1bf33641f61c3b53ff76235bf1a456f`. Downloaded back from GCS and confirmed byte-identical.
- The original GPU VM `jep-csts-format-20261021` was confirmed **TERMINATED** following collection. The previous `rico-source-l4-uswest4c` worker was preserved and remained stopped. No recurring ChatGPT monitoring was enabled.

## Scientific conclusion

The frozen SOTA's original **condition-first input** should remain the deployed form. There is no observed benefit to simply putting the condition after the passage, even if the 8,193-parameter symmetric comparison is retrained. This does **not** rule out conditional order as a separate training intervention if the encoder is retrained on that order from its original pretraining/proposition/ratings stages.
