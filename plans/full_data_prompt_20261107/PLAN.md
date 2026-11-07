# Qwen3-Embedding-8B: full-data prompt-formulation experiment

**State: DRAFT — show the user before execution. No GPU training authorized by this packet.**

## Decision and scope

Run a new matched three-arm, five-seed study, training on **all 6,051 training comparisons from the first optimizer update**. Delete the historical five-epoch 5,885-row subset phase and its optimizer reset. Every fit starts from the pinned pretrained Qwen3-Embedding-8B and newly initialized LoRA adapters. No completed ratings adapter or proposition/evidence adapter is a starting checkpoint.

This replaces the old curriculum for **all arms**; the historical 0.855375 and 0.860894 scores are context, not the control measurements for this study. The new condition-first control must be retrained.

The user's requested order is: plan/code → ten independent reviews → user sees plan/findings → execution. This packet deliberately has no resource-provisioning or training-execution command. Native plan builders construct graphs; they do not call `execution.run`.

## Questions and exact interventions

**Primary comparisons:** B−A tests moving the existing instruction block after the passage. C−A tests a CASE-inspired prompt formulation that makes the condition the target text. **Secondary:** C−B compares the two alternatives. Because C changes both target/context roles and instruction wording, C−B is **not** an isolated causal estimate of target-role reversal.

For each sentence of a pair separately, under the same condition, use one of:

### A — condition first; passage is the target

```text
Instruct: Represent the passage for semantic similarity with respect to this condition: {condition}
Query: {passage}
<EOD>
```

### B — order only; passage remains the target

```text
Query: {passage}
Instruct: Represent the passage for semantic similarity with respect to this condition: {condition}
<EOD>
```

### C — CASE-inspired; condition is the target, passage is context

```text
Instruct: Retrieve semantically similar texts to a given Condition, given the Sentence: {passage}
Query: {condition}
<EOD>
```

`<EOD>` above denotes the tokenizer's existing attended `<|endoftext|>` token, appended once by code, not literal text added to the templates. Input tensors preserve causal attention and left padding. Read the last attended EOD hidden state, cast to float32, normalize to unit length, and compute cosine similarity. Keep all 4,096 coordinates. Train rating mean-squared error, with labels normalized as `(rating−1)/4`.

CASE §3.1 prefers encoding the condition given the sentence. Its full method additionally freezes the LLM, subtracts an unconditional condition embedding, and trains a projection. **C adopts the prompt direction, not that entire pipeline.** Our LoRA parameters are trained, pooling is held fixed across arms, and there is no subtraction, extra projection, learned comparator, token-quotation loss, or proposition-generation phase. This preserves the user's architectural question rather than introducing several simultaneous changes.

## Fixed training design

| Item | Predeclared value |
|---|---|
| Base | `Qwen/Qwen3-Embedding-8B` |
| Immutable model/tokenizer revision | `c90816d848505624c2434128dfc61132162a0ee9` |
| Trials | A, B, C × seeds **7, 8, 9, 10, 11** = **15 new full LoRA fits** |
| Initial state | Fresh pretrained base + freshly initialized LoRA for every arm/seed |
| Paired seeds | Same seed, initialization procedure, and row-order generator across A/B/C |
| LoRA | rank 32; alpha 32; dropout 0.05; q/k/v/o projections; base frozen |
| Optimizer | AdamW; learning rate 2e−5; weight decay 0.01; clip norm 1 |
| Batch | 32 comparisons = 64 conditioned passages; microbatch 32 initially |
| Schedule | Constant LR, no warmup, no scientific phase boundary or optimizer reset |
| Stopping | Validate after every complete epoch; one consecutive non-improvement, as in the original ratings protocol |
| Selection | First strictly best validation Spearman; never test-based |
| Safety ceiling | 24 epochs; hitting the ceiling is **censored**, not convergence or an automatic success |
| Token ceiling | 160 including EOD; no truncation or row deletion |
| Precision | Pinned original BF16 backbone/SDPA; FP32 pooling, norm and rating loss |

A shared seed does not guarantee identical dropout masks or arithmetic across prompt lengths or GPU models. Record actual initial adapter hashes and batch-order hashes; match GPU type/runtime within each seed block. Do not attribute GPU differences to prompt formulation.

Before GPU training, tokenize **all A/B/C training and validation inputs** with the pinned tokenizer. Fail if any exceeds 160. Changing the common ceiling would require an explicit amendment for every arm; do not silently truncate or increase it for only C. At test time, the same fixed ceiling applies and any violation stops evaluation without dropping rows.

## Data and holdout discipline

| Split | Comparisons | Source groups | SHA-256 |
|---|---:|---:|---|
| Training | 6,051 | 2,635 | `9a9eac21ee73b9b029ca6f62584891dd13c74aa78e80efd764532a87665ae6a4` |
| Validation | 1,576 | 680 | `e42d9544b2aa6814708337d0ce38eba1d64124645b62489ed448c6784dbc71ff` |
| Test | 2,430 | 1,222 | `52a9c0d6b8d9f3fc81e698bae1e2564051cf7ec29e8dc1cb4d68167910bb968d` |

Reuse these original bytes, not the separate 2,431-row readout cohort. Hash test bytes during preflight without loading labels. No teacher records/preparation bank are inputs to training. Check training/validation row and source-group separation. The original source split provenance remains a prerequisite; do not repartition to improve scores.

Complete and freeze **all 15 validation-selected checkpoints** before test scoring. Bind each selection to arm, seed, source revision, protocol, data and checkpoint hashes, native references, and stop reason. A failed or censored run cannot silently disappear from the matrix. Evaluate every checkpoint on identical ordered test rows, then recompute metrics independently from saved predictions.

The existing test set has already been examined. Describe the outcome as an exploratory replication on that set, not a newly untouched confirmatory evaluation. A fresh source-group-disjoint evaluation would be a later study, not an unannounced addition here.

## Analysis fixed before results

Report validation and test Spearman, normalized MSE, selected epoch, total optimizer updates, tokens processed, GPU time, estimated cost and interruption/recovery count for **every arm and seed**, including failures.

For each seed compute `rho_B − rho_A`, `rho_C − rho_A`, and `rho_C − rho_B`. Report paired differences, their mean, sample SD, median, range and number of positive differences. Do not compare the best new seed with an old single seed, and do not treat 5 × 2,430 predictions as independent examples.

For test-sample uncertainty, use 10,000 paired source-group bootstrap draws, resampling the same 1,222 group identities for every model in a draw and averaging the within-seed differences. Record seed 610707. Label these intervals as conditional on the trained checkpoints; show training-seed variation separately. A seed-and-source-group hierarchical bootstrap may be reported as a sensitivity analysis, but five seed pairs provide an unstable estimate of training-population uncertainty.

Five paired seeds are a practical screen, not a guarantee of significance. With five nonzero pairs, even unanimous signs cannot yield a two-sided exact sign-test p-value below 2/32 = 0.0625. Primary comparisons are B−A and C−A; do not make unadjusted confirmatory claims across multiple comparisons. No post-hoc training extension based on test scores. Predeclare any larger-seed confirmation separately.

## Efficient execution, after review and user approval

**Parallelize independent fits, not gradients across cloud regions.** Use at most two task-owned Mantra GPUs, one active fit per GPU. Keep the model/tokenizer revision cached on each worker and tokenize once per arm/dataset per worker. Do not cache frozen embeddings for LoRA training: the encoder changes during fitting.

Allocate work by seed block: all three arms of a seed use the same GPU type and pinned runtime. Counterbalance arm order (A/B/C; B/C/A; C/A/B; repeat) to reduce systematic order/time confounding. Two workers can process different seed blocks concurrently. Colab A100, when actually allocated and verified, may take a whole seed block; never run only A on L4 and B/C on A100 within a seed. Do not move an interrupted scientific run to a different GPU type and call it an exact continuation without a separate recovery validation.

### Preferred compute routes

1. **Mantra Spot L4 workers:** inspect live account/project/quota/inventory first. Prefer the existing Seoul route (`asia-northeast3`), then eligible Tokyo/Taiwan zones (`asia-northeast1`, `asia-east1`). User experience motivates this order; current capacity and interruption rates are not guaranteed. Check both regional/family and global enforced quotas. Two global L4 entitlements do not establish two Spot GPUs in one region. Do not issue more quota requests in this preparation phase.
2. **Existing standard Mantra workers:** a fallback only if Spot is unavailable and the cost envelope has been approved. Preserve the stopped historical worker and its 200 GB disk. Use task-specific scratch resources; do not convert/delete historical resources merely to get Spot pricing.
3. **Colab A100:** inspect existing sessions and paid compute-unit availability through the supported CLI. A requested A100 is not an allocated A100: confirm `nvidia-smi`, memory, runtime version, and actual usage rate. No repeated allocation storm and no workarounds for account/resource limits. A missing A100 must not stall otherwise available Mantra work.

No resource has been allocated for this packet. On this inspection, the existing cloud user login needs reauthentication and the Mac/Colab path is offline; live quota/capacity/A100 availability therefore remain **unverified**.

### Spot-safe checkpoints and shutdown

The inherited trainer writes full optimizer/RNG resume state at stage completion, not continuously. The draft therefore packages one **full-data epoch** as a sealed native segment and restores its optimizer, scheduler, dataloader generator, CPU/CUDA RNG, selected incumbent and patience state on the next segment. This is a persistence boundary, **not** the old subset training phase and **not** a fresh optimizer. The default patience is one; a completed non-improving epoch stops the trial.

After each segment: retain native artifacts locally, create an immutable generation manifest, upload checkpoint/model/optimizer/RNG/trace/predictions to Mantra storage, verify hashes, then publish the authoritative resume pointer. Never overwrite the last verified generation. If preempted during an epoch, resume the preceding verified boundary and replay that epoch; do not mix weights and optimizer state from different boundaries. Cross-host native artifact restoration/publication and interrupted-write recovery must pass integration tests before using Spot.

This segmentation incurs model-loading overhead. Measure it against useful training time during the common pilot. Only replace it with a persistent-worker, intra-epoch checkpoint path after a dropout/RNG-enabled interruption equivalence test passes; do not improvise resume code to save startup time.

Benchmark representative **training** batches (forward, backward and optimizer step), not inference alone. Keep batch/microbatch, precision, row order and kernels common across arms. Remove avoidable Python/GPU bookkeeping synchronizations only with numerical-equivalence and RNG checks. Do not enable TF32, quantization, packing, altered sequence lengths, larger microbatches, a different attention kernel or `torch.compile` for just one arm. Avoid hot-loop `.item()` calls for metrics; cache tokens, not activations.

Before a worker is released for training: validate storage write/read canary, source revision, fixed data/model hashes, real GPU, exact environment, no competing process, free disk/RAM, ownership lease, per-job deadline and task-only shutdown handler. Set teardown before starting training. Failure or completion releases the **task GPU**, not the Columbia CPU connector. Preserve persistent disks and original experiments. Collect selected adapters, native traces, predictions and receipts independently of the chat; verify archive SHA after transfer. Do not keep a GPU idle waiting for report generation.

## Code delivered for review

- `configs/csts-full-data-prompt-20261107.json`: fixed design, launch-disabled status.
- `csts_pilot/full_data_prompt_protocol.py`: exact prompts, 15-fit matrix, corpus identities, approval/reviewer checks, global test-release guard. Dependency-free; does not execute training.
- `csts_pilot/full_data_prompt_native.py`: native epoch/resume and test-capture graph builders; reuses `fit_lora`, `fit_neural`, cosine pooling and original output contracts. No provisioning or `execution.run` call.
- `csts_pilot/baseline_models.py`: optional per-run `prompt_template` persisted in config, tokenizer and encoder metadata. Legacy `None` keeps old artifact behavior; no unsafe global prompt mutation between concurrent arms.
- `tests/test_full_data_prompt_protocol.py`: CPU checks, with results in `cpu-tests.log`.
- `reviews/`: ten separate reviewer task briefs, honest completion state, and author findings.

**Not yet verified:** actual native VIPER compilation in the pinned GPU environment; full train/dev tokenizer length scan; real interruption/resume parity with dropout; cloud checkpoint restoration and atomic publication; matched initial-state hashes across arms; supervised gradient reach and frozen-base checks on actual Qwen; real performance measurements; current Spot/A100 allocation. These are release gates, not accomplished facts.

## Independent review gate

Ten independent reviewer executions were requested. **Completed: 0/10.** The available CLI has no authenticated session; a real probe returned `Not logged in`, with zero model input/output tokens. The local Mac connection is offline. No self-review was relabeled as an independent subagent review and no scheduled automation was created to substitute for it.

The supplied ten briefs cover experimental design, CASE semantics, gradients, data, RNG, Spot recovery, VIPER contracts, statistics, performance and lifecycle/security. Each reviewer must inspect the same frozen revision, cite file/line counterexamples, return an attributable execution receipt, and not launch training. Any substantive repair invalidates affected approvals until re-reviewed. The author audit and 39 passing CPU tests are useful evidence, **not substitutes for these ten reviews**.

## Primary sources

- Zhang, Zhou and Bollegala (2026), CASE, §3.1–3.2: https://aclanthology.org/2026.eacl-long.231/
- Original ratings-only source and two-phase control: `3ef6ba0616614632abc5bc0b2f2e2c71886c2f0e`; previous replay `609e2d3bd6521af1372aee067c1db1ef84d85d52`. Historical scores are not new controls.
- Google Compute Engine, Spot VM behavior: https://docs.cloud.google.com/compute/docs/instances/spot
- Google Spot pricing (variable by machine/region/time): https://cloud.google.com/spot-vms/pricing
- Google Colab resource limits and GPU availability: https://research.google.com/colaboratory/faq.html
