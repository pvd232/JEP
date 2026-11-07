# Condition-last vanilla LoRA replay — November 6, 2026

## Outcome

Training and numerical evaluation completed successfully. The trainer exited with code 0 at **2026-11-07 00:37:22 UTC (November 6, 7:37:22 p.m. America/New_York)** after starting at 2026-11-06 20:38:08 UTC. Elapsed controller-to-training-completion time was 3 h 59 min 14 s. It completed **seven total epochs and 1,533 optimizer updates**; the highest validation Spearman selected **epoch 4**, not the terminal epoch. The stopping reason was the specified replay epoch limit, not validation patience or demonstrated convergence.

Source: `23ccbf24f745ff7a81602d8427b596090b1eb3b8`. Protocol: [csts-lora-condition-order-replay.json](../configs/csts-lora-condition-order-replay.json). The only experimental change was passage first, condition last. No auxiliary pretraining or learned comparison head was added. The original Qwen revision, seed 7, LoRA settings, MSE objective, training/validation/test cohorts, effective batch 32, microbatch 2, first-epoch linear scheduler horizon, and subsequent constant-rate continuation were retained.

| Measurement | Original condition first | Replay condition last | Replay minus original |
| --- | ---: | ---: | ---: |
| Validation Spearman, 1,830 comparisons | 0.776790887947513 | 0.783556052352045 | +0.006765164404532 |
| Test Spearman, 2,620 comparisons | 0.778882382927249 | 0.781195231365891 | +0.002312848438642 |
| Test MSE on 0–1 scale | 0.072817277752418 | 0.072287903207259 | -0.000529374545159 |
| Validation-selected epoch | 5 | 4 | — |

The test MSE reduction is 0.7270% relative. Original baseline: [user-stopped seven-epoch continuation](csts_tranche2_operator_stop_report.md), not the earlier one-epoch result. The new result is a small observed improvement, not evidence that condition-last is generally superior.

## Independent verification and uncertainty

Both baseline and replay test Spearman/MSE were independently recomputed from their prediction files. All 2,620 input records, including sentence pair, condition, target, and group identifiers, matched exactly between them. Replay validation metrics were also independently recomputed. Both replay phase summaries matched the SHA-256 digests in the collected completion receipt. All recorded training/prediction/evaluation stages succeeded, and the selection record states validation-only checkpoint selection.

A paired percentile bootstrap resampled **1,241 source `group_id` clusters**, with replacement, for **2,000 draws** using Python random seed 61021. Ranks were recomputed within each draw.

- Test Spearman difference 95% interval: **[-0.0070001261, +0.0121620407]**.
- Test MSE difference 95% interval: **[-0.0025571157, +0.0014155420]**.

Both intervals include zero. These intervals reflect test-sample uncertainty conditional on one seed, fixed trained checkpoints, and the previously examined evaluation cohort; they do not estimate training-seed variability.

Validation Spearman by epoch: 1: 0.679866; 2: 0.773697; 3: 0.772979; **4: 0.783556**; 5: 0.782972; 6: 0.780028; 7: 0.775177. Fitting took approximately 1,808–1,833 seconds per epoch, with approximately 96–97 seconds of validation per epoch.

## Why utilization was around 50%

The original trainer is not throughput-optimized. Inspection of the exact executed source found:

1. Each microbatch contains two comparison pairs (four encoded passages). Sixteen such microbatches normally accumulate into one effective batch of 32 pairs.
2. `TokenPairs.scores` performs CPU padding, transfers tensors to CUDA, and converts `attention_mask.sum()` to a Python integer each microbatch.
3. The training loop branches on `torch.isfinite(loss)` and converts `loss.detach()` to a Python float each microbatch. It also converts the gradient norm to a Python float each optimizer step. These GPU-to-host scalar operations introduce synchronization.

These are concrete potential throughput bottlenecks; no kernel-level profile was captured, so the share of runtime attributable to each is unmeasured. Preserving the effective batch and optimization protocol did not require retaining all of the bookkeeping synchronizations. No implementation or microbatch changes were made during this replay.

Source locations: `csts_pilot/baseline_stages.py:394–419` and `csts_pilot/baseline_models.py:267–280, 420–445` at the pinned training commit. Tokenization was cached once; padding and host/device transfers occurred repeatedly.

The log sampled `nvidia-smi` every 30 seconds. Of 478 total samples, 463 had memory use above 14,000 MiB and nonzero utilization; their median utilization was 49%, mean 51.08%, and maximum 99%. This filter includes model loading, training, and evaluation, and is not an exact time-weighted training utilization estimate. Peak logged device memory use was 15,570 MiB. GPU activity utilization is distinct from VRAM occupancy and theoretical arithmetic throughput.

Primary references: [NVIDIA utilization definition](https://docs.nvidia.com/deploy/nvidia-smi/index.html); [PyTorch synchronization guidance](https://docs.pytorch.org/tutorials/recipes/recipes/tuning_guide.html).

## Preservation and shutdown

The Mantra L4 instance `jep-csts-format-20261021` stopped at **2026-11-07 00:55:39 UTC (November 6, 7:55:39 p.m. ET)**. A fresh inventory at verification also showed the original `rico-source-l4-uswest4c` instance terminated. No training was restarted during verification, and no recurring automation was created or enabled.

The original full native checkpoint/run archive was created successfully on the preserved GPU disk, but its secondary copy to the coordinator was interrupted. That is an archival-transfer failure, **not a training failure**. The original archive remains at `/home/machina/jep-condition-order-job-20261106/jep-condition-order-results-20261106.tar.gz` on the stopped VM's persistent disk. Expected size: 1,817,525,530 bytes; expected SHA-256 from the completion receipt: `e5e6e723b994923128c1e123f52ee7d075b9b68b61985f6b17c73ef8800b2e5a`. The partial secondary copy is 798,504,960 bytes and is not represented as a verified full checkpoint backup.

The complete numerical evidence (predictions, validation predictions, traces, selections, summaries, protocol, original receipt/logs, recomputation, and bootstrap) was recovered independently, uploaded, downloaded again, and byte-count/SHA-256 verified at 2026-11-07 01:39 UTC:

`gs://mantra-mlfg-prod-uscentral1-8e7a/viper/pvd232/jep_condition_order_replay_20261106/jep-condition-order-verified-evidence-20261106.tar.gz`

Size: **933,505 bytes**. SHA-256: **`05fd8a9576ec02c2eaf187ce3098aa986beabd047363cf06cc143256d846bfca`**. This evidence bundle excludes model and optimizer checkpoint bytes; full-checkpoint secondary export remains incomplete.

Selected replay checkpoint recorded SHA-256: `afb0b756ae63831752c988d298da07e7efba4fb8c30e89ba7f2b27dc9dca5d86`.
Replay test-predictions SHA-256: `8aa97bdde191d54b7c4e34b4093947b983c0147ef8aca5c2d726e6f3edcab74e`.
Replay trace SHA-256: `f4ec68558570b565b6d36a24767d475ae3a6b0ff37dd5dbf773f8160dd1d6070`.
Original selected-checkpoint test-predictions SHA-256: `d48c9c13ae8930c6fee3062c2f81404dc2df1d62fe735b839a8df006cd897357`.
