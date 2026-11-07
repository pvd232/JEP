# Ratings-only Qwen3-Embedding-8B LoRA — condition-order retraining

**Completed:** November 7, 2026. **Status:** training, held-out inference, independent metric verification, checkpoint backup, and GPU shutdown complete.

## Research question and verdict

Does fully **retraining** the existing high-performing *ratings-only* Qwen3-Embedding-8B LoRA encoder with the condition placed **after** the passage outperform the matched condition-first control? This does **not** test the later proposition-trained encoder or its learned comparator.

**Observed answer: yes, narrowly on the existing held-out test cohort.** Condition-last improves test Spearman by **+0.005519**, despite slightly lower validation Spearman. A paired source-group bootstrap interval includes zero, so this is not a conclusive advantage.

| Metric | Historical condition-first control | Retrained condition-last | Difference |
|---|---:|---:|---:|
| Validation Spearman (1,576 rows) | 0.871875 | **0.869352418560** | −0.002523 |
| **Test Spearman (2,430 rows)** | **0.855374781338** | **0.860893780560** | **+0.005518999223** |
| Test MSE, normalized 0–1 | 0.038359250026 | **0.036373474782** | **−0.001985775244** |
| Validation-selected full-ratings epoch | 2 | 2 | matched |

Test MSE decreased by about **5.18%** relative to the original. The comparison uses **exactly the same 2,430 test records and 1,222 connected source groups**. All row identifiers, sentences, conditions, targets, ratings, pair IDs, and group IDs matched one-for-one.

The selected checkpoint was chosen exclusively using validation Spearman. Its SHA-256 is `b8fde4f1f0b9c62edfec6fce53d0efe12602227eec400b31f4fd2ee1adfd184b`.

## Controlled protocol

The starting model is **pretrained `Qwen/Qwen3-Embedding-8B`**, exact base revision `c90816d848505624c2434128dfc61132162a0ee9`, **not** `proposition_final.pt`. A fresh rank-32 LoRA adapter was initialized using seed 7. Both phases optimized **rating MSE only**; there was **no evidence-quotation or proposition-generation gradient**.

The sole semantic intervention is the prompt ordering:

**Original**

```text
Instruct: Represent the passage for semantic similarity with respect to this condition: {condition}
Query: {passage}
```

**Ablation**

```text
Query: {passage}
Instruct: Represent the passage for semantic similarity with respect to this condition: {condition}
```

Both end in the attended `<|endoftext|>` token. Qwen remains decoder-derived with its original causal mask; final-EOD pooling and float32 unit normalization are unchanged.

The original **five-epoch ratings-only prefix** trained on exactly **5,885 comparisons** selected from the common proposition-covered subset. Importantly, this subset choice does *not* imply proposition training: this control received ratings loss only. The first phase completed 920 optimizer updates. The second phase trained ratings on all **6,051 training comparisons** until one consecutive non-improving validation epoch; the best epoch was 2 of 3 completed. Training kept the original effective and physical batch size 32, AdamW learning rate `2e-5`, weight decay 0.01, LoRA rank/alpha 32/32, dropout 0.05, and target modules `q_proj,k_proj,v_proj,o_proj`. No scheduler or training objective change.

### Validation trajectory at matched epochs

| Phase | Epoch | Original condition first | Retrained condition last |
|---|---:|---:|---:|
| Ratings-only prefix | 1 | 0.851194 | 0.850490 |
| Ratings-only prefix | 2 | 0.865684 | 0.863096 |
| Ratings-only prefix | 3 | 0.869931 | **0.871637** |
| Ratings-only prefix | 4 | 0.869917 | 0.867056 |
| Ratings-only prefix | 5 | 0.867871 | **0.868801** |
| Full ratings | 1 | **0.870251** | 0.865307 |
| Full ratings | **2 (selected)** | **0.871875** | 0.869352 |
| Full ratings | 3 | 0.866908 | **0.867783** |

## Reproducibility and uncertainty

The original controls and pinned splits are documented by [the original 2026 control report](proposition_full_20261026/comparison_report.md). See also [replay configuration](../configs/csts-ratings-only-condition-last-replay.json) and [native VIPER replay runner](../csts_pilot/ratings_only_order_replay.py).

- **Training source commit:** `609e2d3bd6521af1372aee067c1db1ef84d85d52`.
- **Evaluation binding-only repair commit:** `e60e718cb8feb569a451fc07639a93d5724455f4`. The original training stages were reused, **not retrained**, during evaluation recovery.
- **Prefix prepared subset hash:** `0b63e159ecb8eb211636b9b509baf6035dc1e22b81f5404c1caaecc78203f67f`; reconstructed byte-for-byte from the archived historical preparation.
- **Training split SHA:** `9a9eac21ee73b9b029ca6f62584891dd13c74aa78e80efd764532a87665ae6a4`.
- **Validation split SHA:** `e42d9544b2aa6814708337d0ce38eba1d64124645b62489ed448c6784dbc71ff`.
- **Test split SHA:** `52a9c0d6b8d9f3fc81e698bae1e2564051cf7ec29e8dc1cb4d68167910bb968d`.
- **Original test predictions SHA:** `031ce3e9f694dbd6a23abd863114f5eff526d93a643c238ac909c2cff5ae5bad`.
- **New test predictions SHA:** `f82228f42eac932a469575e8614d9d1aa63a7f9772931a7c098ed94b24874016`.

The initial training completed successfully. Its first evaluation attempt failed **after checkpoint selection**, owing to an invalid explicit `data_role` on an existing VIPER artifact input. The subsequent evaluation-only native invocation fixed the binding, reused both completed training stages, generated the 2,430 held-out predictions, and exited successfully. The trained model bytes and selection were unchanged.

The test metrics were **independently recomputed from both archived prediction files**, after requiring exact row identity. A paired percentile bootstrap resampled **1,222 source-group clusters**, with replacement, for **2,000 draws** using seed **61024**:

| Replay minus original | Point estimate | 95% paired group-bootstrap interval |
|---|---:|---:|
| Test Spearman | **+0.005519** | **[−0.003696, +0.015723]** |
| Test MSE | **−0.001986** | **[−0.005430, +0.001168]** |

**Both intervals contain zero.** These are fixed-checkpoint, fixed-training-seed intervals on a previously examined test set. They do not assess variation across LoRA training seeds, so the result warrants a fresh reserved test set or a multi-seed replication.

## Cloud preservation

All numerical evaluation evidence, the recovered benchmark reference predictions, independent verification, and the **selected 122,764,915-byte model checkpoint** are retained under:

`gs://mantra-mlfg-prod-uscentral1-8e7a/viper/pvd232/jep_ratings_only_condition_last_20261107/`

The new evidence archive SHA-256 is `44d01b94c91881dc544228141f5b7aaa58062f1741de670cc9564354ceacdabd`; selected model checkpoint SHA-256 is `b8fde4f1f0b9c62edfec6fce53d0efe12602227eec400b31f4fd2ee1adfd184b`. **Both cloud objects were downloaded again and matched their local SHA-256 digests byte-for-byte.** The original full native VIPER run and optimizer/resume artifacts remain on the preserved VM persistent disk. The Mantra L4 VM `jep-csts-format-20261021` is **TERMINATED**.

**Scope warning:** the project's later **0.865230** test Spearman came from a *different*, proposition-trained frozen encoder plus a learned symmetric comparator. It must not be substituted for the **0.855375** ratings-only matched baseline here.
