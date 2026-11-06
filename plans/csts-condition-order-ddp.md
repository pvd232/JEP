# External distributed condition-order replay

**Status: retained implementation, not executed or GPU validated.** The distributed math and completed-epoch recovery checks below passed. Native numerical-control parity and a real CUDA/NCCL run remain launch gates. The active replay uses the separate published single-GPU path.

This branch adds one explicitly external PyTorch DistributedDataParallel execution path for the condition-last Qwen LoRA replay. The published single-GPU replay at `23ccbf24f745ff7a81602d8427b596090b1eb3b8` remains unchanged. The new command does not create or claim a native VIPER TRAIN receipt: pinned VIPER 0.1.2 supports only one GPU per native CUDA stage. Its resume-state serialization is reused directly.

## Training contract

`configs/csts-lora-condition-order-ddp.json` binds the distributed execution to the original, SHA-pinned standalone LoRA settings already recorded in `configs/csts-lora-condition-order-replay.json`. Both ranks use the exact original 6,980 training rows and original validation/test split bytes. There is no evidence/proposition phase, auxiliary pretraining, learned comparison head, or condition-dependent subset.

The only encoder-input change is the existing condition-last literal prompt:

```text
Query: {passage}
Instruct: Represent the passage for semantic similarity with respect to this condition: {condition}
```

The explicit EOD token, causal attention, last-attended-token pooling, unit normalization, raw cosine score, and rating target transformation remain in the original model helpers. The pinned Qwen revision, BF16 operations, token ceiling 160, LoRA rank/alpha 32, dropout 0.05, q/k/v/o target modules, AdamW learning rate 2e-5, weight decay 0.01, and gradient norm cap 1 remain the original settings.

| Property | Distributed execution |
| --- | --- |
| World size | Exactly 2 processes, one visible GPU each |
| Adapter initialization | Seed 7 on both ranks before DDP synchronization |
| Global sampler | The original CPU generator seeded 107, with its state carried across epochs |
| Effective optimizer batch | 32 original comparisons across both ranks |
| Microbatch | 2 comparisons, retaining original consecutive chunks |
| Rank assignment | Alternate consecutive microbatches between ranks |
| Last global batch | 4 comparisons, 2 per rank; no padding, duplication, or dropping |
| Loss scaling | Each rank accumulates 2 × local squared-error sum / actual global batch size; DDP averages the gradients |
| Update order | Synchronize final microbatch gradient, clip once, then optimizer and scheduler step |
| Updates per epoch | 219 |
| Initial phase | Epoch 1 with the original 24-epoch linear horizon: 5,256 planned updates and 526 warmup updates |
| Continuation | Epochs 2–7 at constant 2e-5, preserving AdamW moments and sampler state |
| Stopping | Earlier of five validation checks without improvement or the seven-epoch replay ceiling |
| Selection | Highest validation Spearman; retain the earlier checkpoint on ties |
| Test access | Rank 0 scores the validation-selected checkpoint after fitting finishes |

Distributed execution changes the partition of dropout random streams and the floating-point reduction order. It is not a bitwise reproduction of the original single-GPU run. Rank 0 retains the post-initialization seed-7 stream; rank 1 starts its declared training stream at seed 8. Each process saves and restores its own Python, NumPy, CPU Torch, and visible-GPU RNG state. The global batch order, objective, optimizer settings, and learning-rate clocks remain fixed.

## Launch interface

The infrastructure controller supplies `MASTER_ADDR`, `MASTER_PORT`, `RANK`, `WORLD_SIZE=2`, and a distinct `CUDA_VISIBLE_DEVICES` assignment. Both processes execute the same committed source and package environment. One physical host with two GPUs or two hosts with one GPU each are supported. Each process must see exactly one GPU and use its own persistent output directory outside the source checkout. An exclusive advisory lock is held on that directory for the complete run, including initialization and test scoring, so recovery cannot create a second local writer while the previous process is still alive.

```bash
python -m csts_pilot.ddp_order_replay \
  --execute \
  --root /path/to/clean/committed/checkout \
  --run-dir /persistent/path/for/this/rank
```

Review the protocol without model execution by omitting `--execute`. Use `--resume` on both ranks to recover an existing run. Resume requires the identical source commit, source tree, protocol, input hashes, and runtime topology. The default collective timeout is 600 seconds to cover rank-0-only validation and test prediction; the launcher may set `--collective-timeout-seconds` explicitly.

The launcher owns instance lifecycle, bounded recovery, and shutdown of every allocated worker. This command does not allocate instances, modify firewall rules, or stop a host while its peer is still scoring or saving artifacts.

## Completed-epoch recovery

Each rank writes an immutable epoch directory on its persistent disk containing its local adapter model, optimizer/scheduler state, RNG/sampler state, and common training history. Rank 0 also snapshots the validation-selected model and predictions. Files are flushed and atomically renamed before their SHA-256/size receipts are exchanged.

An epoch is eligible for recovery only when the same common manifest is durable on both ranks. The manifest includes both ranks' file receipts, the shared epoch and optimizer step, the protocol identity, and the synchronized adapter-state digest. Manifest filenames include their content identity, so an interrupted one-sided commit can coexist with a later successful replay of that epoch.

On restart, both workers select the highest epoch whose manifest filename and bytes are present identically on both disks. A newer manifest present on only one rank is ignored and preserved. Partial epochs are never continued: both ranks return to the last shared completed epoch. If there is no shared completed epoch, the run explicitly restarts from fresh seed-7 initialization. Restoring epoch 1 loads its saved linear schedule and optimizer first, then initializes the constant-rate phase before update 220.

`status.json` records advancing optimizer steps and completion/failure. `committed/` and `epochs/` retain the recovery evidence. `identity.json`, per-rank runtime receipts, and `workers.json` identify source, inputs, package versions, Python/CUDA versions, GPU assignments, and the declared external execution. Rank 0 writes `results.json` and `test_predictions.json`; both ranks receive the final result. Every result explicitly sets `native_train_receipt: false`.

## Verification boundary

`tests/test_csts_distributed_lora.py` exercises the production update helper with real two-process CPU Gloo collectives. It compares full and four-comparison tail batches to a separate serial mean-loss reference, with gradients both below and above the clipping threshold. It also checks per-rank dropout/RNG and AdamW continuation, the original scheduler clock, and incomplete or mixed checkpoint rejection. A runtime GPU/NCCL probe and observation of the first advancing optimizer steps remain the launch controller's responsibility.

### Observed validation scope

The original 14-case core snapshot passed in 37.67 seconds, including actual two-process Gloo gradient, dropout/RNG, optimizer, and schedule checks. The final test module contains 20 cases, but the complete 20-case module has not been collected or executed. Its six added cases cover SHA format, orphan/retry recovery, corruption, and competing-process exclusion.

A separate stdlib-only probe on Columbia compiled the unchanged production coordinator, file, lock, and receipt-validation function definitions, replaced only the peer-inventory communication, and used real files and subprocesses. It passed all six requested counterexamples: both-rank fallback from a one-sided newer manifest; a successful same-epoch retry beside the orphan; rejection of differing bytes under a common manifest name; rejection of altered local artifacts; rejection of equal invalid model hashes; and exclusive lock ownership with successful acquisition after release. This probe did not import or modify the active Colab training environment.

No Qwen update or CUDA/NCCL collective has executed through this distributed path. Its pending numerical-control gate is substantive: the current external runner resets seeds, but does not yet apply and observe the native run's complete reproducibility policy. The pinned VIPER source defines the native default as reproducible mode: deterministic algorithms enabled, warn-only disabled, cuDNN deterministic enabled and benchmarking disabled, cuBLAS workspace :4096:8, highest float32 matmul precision, cuDNN TF32 disabled, outer autocast disabled, and one Torch intra-op/inter-op thread. Native startup also supplies PYTHONHASHSEED, OMP_NUM_THREADS and MKL_NUM_THREADS. The original model helper still applies its own BF16 autocast internally. Before any future distributed launch, apply the same numerical and startup controls, record their observed values per rank, and perform the bounded GPU/NCCL check. See the pinned [runtime policy implementation](https://github.com/pvd232/viper/blob/e4ce91fa0a9330e769644aba0fccdfe062d5d821/src/viper/runtime.py) and [native plan default](https://github.com/pvd232/viper/blob/e4ce91fa0a9330e769644aba0fccdfe062d5d821/src/viper/authoring.py).
