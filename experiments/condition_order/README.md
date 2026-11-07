# Condition-order ablation against the actual JEP Qwen SOTA

The previous 7-epoch standalone ratings-LoRA replay was **not** a comparison with the current leading system. The archived leading system used the proposition- and similarity-trained Qwen3-Embedding-8B adapter, followed by a learned symmetric pairwise comparator. Its average held-out **test** Spearman was **0.865230** across three independently trained comparator seeds, versus **0.863398** for raw cosine. The original comparator report is `training_outputs/csts_readout_convergence_20261028/results.md`.

## Matched experiment

Only the **input presentation** changes: the condition is moved after the passage. The same frozen Qwen checkpoint, adapter state, tokenizer, original 160-token ceiling, attended final EOD, BF16 backbone, FP32 unit-normalized 4,096-dimensional output, original source-group splits, comparator architecture and optimizer settings are retained.

| Control | Identity |
| --- | --- |
| Base model | `Qwen/Qwen3-Embedding-8B` revision `c90816d848505624c2434128dfc61132162a0ee9` |
| Fine-tuned Qwen state | `proposition_final.pt` SHA-256 `d30c00fc76e70ec639493b7121a8b8c9d7520745733857c1c49f0902fff00f4f` |
| Original methods source | `fdbcb3461f63cf44d7cb3cde4de27332594e452d` |
| Training comparisons | 6,051, SHA-256 `9a9eac21ee73b9b029ca6f62584891dd13c74aa78e80efd764532a87665ae6a4` |
| Validation comparisons | 1,576, SHA-256 `e42d9544b2aa6814708337d0ce38eba1d64124645b62489ed448c6784dbc71ff` |
| Held-out test comparisons | 2,431, SHA-256 `d6b40b7b891ed147befb30801c2f85a8787775adebdd98d134157cbb2a6e9f76` |

**Original prompt:**

```
Instruct: Represent the passage for semantic similarity with respect to this condition: {condition}
Query: {passage}
```

**Ablation prompt:**

```
Query: {passage}
Instruct: Represent the passage for semantic similarity with respect to this condition: {condition}
```

Every input retains its attended EOD token. The modified ordering changes the token context of the final representation, but no original encoder weights are updated in this controlled ablation.

For seeds 7, 8 and 9 independently, train the original symmetric comparator:

\[
f_\phi(a,b) = a^\top b + w_d^\top |a-b| + w_p^\top(a\odot b) + c.
\]

The extra 8,193 coefficients are zero-initialized, so the initial score is cosine. Retain AdamW learning rate 0.001, weight decay 0.01, batch size 32, gradient clipping at 1 and the original training order seed `seed + 10000`. Select each checkpoint using validation Spearman only, with patience 10 and maximum 256 epochs. Open the 2,431 test rows for scoring **after all three comparator checkpoints are frozen**. Report per-seed and mean Spearman, normalized MSE, and the raw cosine result.

The executable is [`sota_order_ablation.py`](sota_order_ablation.py). It records and checks the checkpoint/input hashes, retains extracted vectors and per-epoch optimizer state on the original persistent Mantra VM disk, writes comparator selections and test predictions, and emits a checksum-verifiable evidence archive. The one-shot collector publishes results to the existing Mantra VIPER GCS bucket before shutting down the task GPU. The archived baseline seed Spearman scores are 0.864672, 0.865373, 0.865646.

**Scope:** This is a matched **inference-order and comparator-refit ablation on the fixed SOTA encoder**. It is not a new end-to-end proposition-pretraining-plus-LoRA training run. Such a retraining study would be a distinct experiment with its own separately initialized starting checkpoint and training history.
