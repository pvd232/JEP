# Audio-inspired prototype screen

**The tested prototype loss did not produce a better selected representation. Keep the existing Qwen + LoRA readout.** All six fits selected epoch zero after five epochs without validation improvement. The two selected methods therefore make identical predictions within each seed.

This is an English C-STS validation screen: 6,980 training comparisons and 1,830 validation comparisons in 688 validation source groups. Both arms use the same frozen Qwen + LoRA states and released rating supervision. Seeds 7, 8 and 9 vary the new projection/dictionary training, with the parent encoder fixed. No new backbone inference, benchmark-test evaluation, JEP human judgments, or certified edits ran.

The selected three-seed mean validation Spearman is **0.760061** for both methods. The unchanged parent readout's previously measured validation Spearman is **0.782575** on this cohort ([prior report](csts_overnight_final_report.md)). The added random 128-dimensional projection already loses ranking performance before further training; this experiment does not identify a single cause for that loss.

| Seed | Method | Selected epoch | Validation Spearman | MSE | Used codes: train / dev | Negative pairs sharing a code |
|---|---|---:|---:|---:|---:|---:|
| 7 | projection | 0 | 0.760622 | 0.038531 | 128 / 126 | 77 / 485 |
| 7 | prototype | 0 | 0.760622 | 0.038531 | 128 / 126 | 77 / 485 |
| 8 | projection | 0 | 0.762468 | 0.037977 | 128 / 128 | 69 / 485 |
| 8 | prototype | 0 | 0.762468 | 0.037977 | 128 / 128 | 69 / 485 |
| 9 | projection | 0 | 0.757093 | 0.038902 | 128 / 126 | 77 / 485 |
| 9 | prototype | 0 | 0.757093 | 0.038902 | 128 / 126 | 77 / 485 |

Mean paired prototype-minus-projection Spearman: **+0.000000**; source-group bootstrap interval **[+0.000000, +0.000000]**.

The zero-width bootstrap interval follows from identical selected predictions. It does **not** establish equivalence between trained model classes. The bootstrap holds the listed training seeds and chosen checkpoints fixed; validation selection is not corrected, and there is no fresh-test claim.

The control fits spherical k-means after its projection is selected. The prototype arm learns its dictionary during rating training using a straight-through quantization objective. Both retain continuous cosine as the primary score; quantized-score metrics and complete usage histograms are reported separately.

The 128 numeric prototypes are shared across condition-conditioned representations. This screen does not fit a separate dictionary for every sparsely repeated benchmark question. Prototype IDs have no assigned legal interpretation. JEP application requires claim-level or multiple assignments, explicit definitions, rare-demand checks, certified edits, and expert review.

## What changed during training

The fits optimized their training data: average rating MSE fell from approximately 0.042–0.045 in the first epoch to 0.0098–0.0111 in epoch five. Validation ranking stayed below the starting projection. Patience stopped each fit after five epochs, with 1,095 optimizer updates. The recorded six fitter elapsed times sum to 51.36 seconds; native preparation, process and verification overhead is separate.

Because the primary selections retained their initial weights, a separate **post-selection diagnostic** inspected the already-trained terminal states. Both arms ended at the same epoch/update count in every seed. The control's terminal dictionary was fitted to its terminal training representations; validation vectors did not fit its centers. No further optimizer steps or checkpoint selection occurred.

| Terminal diagnostic, three-seed mean | Projection + post-hoc k-means | Joint prototypes |
|---|---:|---:|
| Validation Spearman, continuous representation | 0.746478 | 0.749424 |
| Quantized cosine MSE | 0.091170 | 0.075666 |
| Low-rated pairs assigned the same code | 10.10% | 6.53% |
| High-rated pairs assigned the same code | 75.02% | 69.03% |
| Occupied codes in validation, out of 128 | 127.67 | 86.33 |

Low-rated means ratings 1–2 (485 pairs); high-rated means ratings 4–5 (718 pairs). All 1,830 rows remain in regression and ranking. These are means of seed-specific measurements, not measurements from an ensemble. The [terminal diagnostic](csts_codebook_terminal_diagnostics.json) retains each seed, parameter-state identities, source hashes and complete usage distributions.

Joint training changed the dictionary and reduced some low-rating code collisions. It also separated more high-rating pairs and used fewer codes. The two hard-assignment rates are not a comparison at matched recall, so fewer low-rating collisions alone do not establish better grouping. Its slightly higher terminal continuous Spearman also remains below both the selected initial projection and the existing encoder.

## Implication for JEP

This fixed rating/VQ objective provides no reason to replace the current encoder. The audio-inspired mechanism can change the partition, but a numeric partition is not yet an expert-readable codebook. The next useful evidence is whether candidate groups preserve distinct demands and support consistent expert definitions at matched coverage. This screen does not answer that question, establish rare-demand preservation, or rule out expert-guided, soft or multiple-prototype designs.

The exported [code exemplars](csts_codebook_review.json) belong to the primary selected checkpoints. Since those selected epoch zero, they illustrate the starting training-fitted dictionaries; they are not examples of successful rating-guided codebook learning. Expert labels and definitions remain blank.

## Verification and execution

Both cache preparations, the single native TRAIN containing all six fits, and development publication succeeded under source `2cd66d61b3c1a08e58b1a91b911574612a447ed4`. Final CPU EVAL succeeded under `b99056d226498be37e3423b63ce1b6d5168d18df`, with VIPER independently recomputing the paired metric from the prediction artifact. Checkpoint replay matched saved validation metrics exactly.

The first controller failed native EVAL construction because of reserved input bindings. The next EVAL computed its outputs but failed on an unnecessary manual recorder lookup for an artifact-recomputed metric. Both failures remain preserved. The final recovery reused the original four successful stages and unchanged frozen model bytes; it did not retrain, change settings, alter tolerances, or access benchmark-test data. [Execution history](csts_codebook_execution_history.json) records all three attempts and both native EVAL dispositions.

Thirteen focused tests, Ruff and scoped Pyrefly passed after the repairs. The directly reused data, diagnostic and patience observers also passed. [Review and exact commands](../plans/csts-codebook-review.md). Publication uses the existing independent queue; scoring did not wait for upload.

## Records

[Method and frozen settings](../plans/csts-codebook.md) · [Results](csts_codebook_results.json) · [Predictions](csts_codebook_predictions.json) · [Training traces](csts_codebook_trace.json) · [Native execution](csts_codebook_execution.json) · [Collected-data hashes](csts_codebook_artifacts.json)

Source commit: `b99056d226498be37e3423b63ce1b6d5168d18df`. All native stages use CPU compute. Publication is queued independently of training and scoring.
