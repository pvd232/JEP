# Condition-last replay of the original standalone Qwen LoRA

This run changes the order of the condition and passage in the original standalone
Qwen LoRA cosine experiment. It starts from the pinned pretrained embedding model
with fresh adapters and trains only against similarity ratings. It uses all 6,980
original training comparisons. There is no proposition-writing objective,
proposition-dependent row subset, or learned comparison head.

The reference is the original Tranche 2 continuation, which completed seven total
epochs before the user stopped it. Validation selected epoch 5; test Spearman was
0.7788823829272487 on 2,620 comparisons. The later JEP-v1 controls used different
rows and training histories. Their scores are not the reference for this replay.
The exact historical configuration hashes and reference checkpoint identity are
in [the replay configuration](../configs/csts-lora-condition-order-replay.json).

## One representation change

Original input:

```text
Instruct: Represent the passage for semantic similarity with respect to this condition: {condition}
Query: {passage}<|endoftext|>
```

Replay input:

```text
Query: {passage}
Instruct: Represent the passage for semantic similarity with respect to this condition: {condition}<|endoftext|>
```

The literal instruction and query wording is retained. The tokenizer still adds
no automatic special tokens, appends an attended EOD token, pads on the left, and
rejects sequences exceeding 160 tokens. Qwen keeps its causal mask. The scorer
pools the last attended EOD state into a float32 normalized 4,096-dimensional
vector and uses raw cosine. This is an order-only ablation; improvement remains
to be measured.

## Evidence for testing this order

[CASE (EACL 2026)](https://aclanthology.org/2026.eacl-long.231.pdf), section
3.1, encodes the condition after the sentence context. Tables 1 and 10 report
higher frozen GTE Spearman for condition encoding than sentence encoding
(16.58 versus 7.16, before subtraction). That makes the existing condition-first
layout a plausible target for an ablation, not a demonstrated Qwen LoRA defect:
CASE also changes prompt roles and the target being encoded, and it does not
report a within-Qwen3 LoRA order comparison. The attended final EOD token can
see both fields in either layout, so this is not a causal-mask visibility bug.

This replay deliberately tests only the literal field-order change while
retaining the original words, pooling, cosine objective and training history.
It does not add CASE's subtraction or comparison network.

## Replay protocol

| Setting | Value |
|---|---|
| Base model | `Qwen/Qwen3-Embedding-8B` |
| Model and tokenizer revision | `c90816d848505624c2434128dfc61132162a0ee9` |
| Seed | 7 |
| LoRA | rank 32, alpha 32, dropout 0.05, q/k/v/o projections, no bias |
| Loss | MSE of cosine against `(rating - 1) / 4` |
| AdamW | learning rate 0.00002, weight decay 0.01; existing defaults retained |
| Gradient clipping | norm 1.0 |
| Logical batch / microbatch | 32 / 2 comparisons, including exact partial-batch weighting |
| Validation selection | greatest Spearman, retaining the earlier checkpoint on ties |
| Validation patience | five successive checks without a strict improvement |
| Training / validation / test | 6,980 / 1,830 / 2,620 comparisons, original byte hashes |

The initial phase keeps the original 24-epoch linear schedule with 10% warmup.
There are 219 updates per epoch, so the declared horizon is 5,256 updates and the
warmup is 526 updates. The replay ends this phase after exactly one completed
epoch, matching the original resource-limited result.

The continuation restores the initial phase's terminal adapters, AdamW state,
random number state, next comparison permutation and incumbent validation
checkpoint through the existing native producer references. It switches to
constant learning rate 0.00002 with no new warmup, as the original continuation
did. It stops after total epoch 7, or earlier if validation patience is exhausted.
The selected checkpoint can differ from the original epoch 5.

`stop_after_epoch` supplies these deterministic replay boundaries while leaving
the scheduler's `max_epochs` unchanged. Original wall-time budgets are retained
as execution guards. A resource-budget stop is reported as an incomplete replay.
No original checkpoint is used to initialize the new run.

## Execution and retained results

The runner loads the two unchanged historical JSON configurations and verifies
their SHA-256 hashes before adding the epoch limits, observed GPU model and
runtime lockfile from the replay manifest.
It uses the existing native TRAIN, BUILD prediction and CPU EVAL stages for both
phases. Each selection is frozen before that phase's test access. Test results
do not change the declared continuation or checkpoint-selection policy.

Review the plan and verify supplied input bytes:

```bash
python -m csts_pilot.lora_order_replay --check-inputs
```

Run on the observed GPU, for example an 80 GB A100:

```bash
python -m csts_pilot.lora_order_replay --execute --check-inputs \
  --gpu-model "NVIDIA A100-SXM4-80GB"
```

The default is the original `"NVIDIA L4"`; the logical and microbatch sizes remain
32 and 2 on either device. The runtime environment must use the pinned repository
dependencies and local VIPER storage. Native environment provenance binds
`condition_order_requirements.txt`; ordinary baseline runs retain their original
`tranche2_requirements.txt` default.

Results are written under:

- `baseline_results/lora/condition_last_20261106_initial/`
- `baseline_results/lora/condition_last_20261106_continuation/`
- `baseline_results/lora/condition_last_20261106/replay.json`

Native model weights, terminal state, optimizer/RNG state, traces and predictions
remain in their sealed run directories. Cloud publication is queued
asynchronously. A queued publication is not a verified cloud receipt. The
existing GPU lock prevents concurrent controllers in the same checkout.
`--resume` reuses verified completed stages under the same source and settings;
an interrupted native invocation requires inspection before another launch.

## Historical evidence

- [Original initial configuration](https://github.com/pvd232/JEP/blob/5bb506d33f55942ea72b04e86b926abfc53dc819/configs/csts-tranche-2.json).
- [Original continuation configuration](https://github.com/pvd232/JEP/blob/5bb506d33f55942ea72b04e86b926abfc53dc819/configs/csts-tranche-2-lora-continuation.json).
- [Continuation launch and parent epoch](https://github.com/pvd232/JEP/blob/5bb506d33f55942ea72b04e86b926abfc53dc819/training_outputs/csts_tranche2_lora_continuation_launch.json).
- [Original user-stopped result](https://github.com/pvd232/JEP/blob/5bb506d33f55942ea72b04e86b926abfc53dc819/training_outputs/csts_tranche2_operator_stop_report.md).
