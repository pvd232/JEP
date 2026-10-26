# Train-only iterative target refresh

## Review status and question

Draft experiment implementation for review. No experiment training, feature extraction, paid generation, or test evaluation has been launched. CPU fixture tests exercise synthetic data only.

Does periodically refreshing a train-derived cluster teacher improve a C-STS projection compared with keeping its initial cluster teacher fixed, under identical rating supervision, masking, optimizer updates, and validation-selection opportunities?

[HuBERT](https://arxiv.org/abs/2106.07447) motivates provisional offline clusters and learning to predict targets from corrupted inputs. This experiment is a **masked-feature cluster-prediction self-supervised adaptation**. It masks coordinates in already pooled, frozen condition-conditioned embeddings. It has no temporal speech spans or contextual acoustic prediction task, and does not reproduce HuBERT. Its cluster cross-entropy is applied to each corrupted pooled view. The original rating objective remains unmasked. Masking and each numerical setting below are local, predeclared choices.

No expert correction data is supplied. The only correction signal is the released training rating plus the evolving training representations. The result cannot establish that a cluster corresponds to an expert-defined JEP claim, or that iterative unsupervised labels are expert corrections. A future expert-correction experiment needs separately supplied, source-linked train-only adjudications and a frozen schema before implementation or execution; this draft manufactures none.

## Reused inputs and matched arms

Reuse the original 6,980 training / 1,830 validation comparisons and frozen Qwen + LoRA states from the [previous prototype screen](csts-codebook.md). Parent checkpoint SHA-256 is `8805f9a7241e4e19ffc481341ebad6f1ddb6dd6ff04bbf710f9f0896469e34ff`. Row digests are pinned in [the config](../configs/csts-iterative-codebook.json). Native producer references, raw-cache identity, compact-cache byte hashes, row digests, source commit and model identity are recorded and checked before launch. Each native TRAIN input is hashed again at consumption. Both partitions must have disjoint source groups and canonical captions. No test cache or test labels are accepted.

Both arms learn a bias-free 4096-to-128 projection and a normalized 128-vector classifier. One shared dictionary across condition-conditioned embeddings avoids requiring 128 well-supported clusters for every sparse condition string. Primary scoring uses **unmasked continuous cosine**.

| Item | Fixed teacher | Refreshed teacher |
|---|---|---|
| Initial projection and teacher | Identical per seed | Identical per seed |
| Target labels | Initial training k-means partition throughout | Refit on terminal unmasked training representations before epochs 3, 5, 7, ... |
| Classifier reset | Initial teacher centers at every round boundary | Current teacher centers at every round boundary |
| AdamW reset | Every round boundary | Same boundaries |
| Primary rating loss and masked cluster prediction | Same | Same |
| Data, batch ordering, input masks, updates and validation checks | Same | Same |

Initial and refreshed teachers fit seeded spherical k-means to **one first occurrence per unique training `(condition, passage)` key**. They assign one numeric target per key, then broadcast it to every occurrence. Duplicate occurrences cannot receive conflicting targets. No validation vector initializes a center or receives a teacher pseudo-target. The refreshed teacher uses the current terminal projection, not the validation-selected checkpoint. K-means uses the same seed and ten Lloyd iterations each time. Empty centers are retained.

Classifier IDs may permute after re-clustering. Resetting the classifier to teacher centers and resetting AdamW in **both** arms prevents stale class-specific optimizer history from becoming an uncontrolled advantage. Projections continue from terminal weights. The fixed teacher deliberately retains its original centers and targets. The treatment includes the additional cost of repeated clustering; it receives no additional examples, optimizer steps or validation checks. Elapsed time is logged. This draft does not claim equal FLOPs.

## Objective, masking and stopping

For normalized `z = normalize(W h)`, released target `y=(rating-1)/4`, teacher label `c`, mask `m`, normalized classifier vectors `p`, both arms minimize

$$
\mathcal L = \operatorname{MSE}(z_1^\top z_2,y) + 0.1\operatorname{CE}\left(\frac{\operatorname{normalize}(W(m\odot h))p^\top}{0.1},c\right).
$$

Every occurrence has exactly `max(1, floor(0.1 * input_width))` coordinates removed, sampled without replacement from a shared CPU generator. Each batch's **same mask tensor** is passed to both arms. Epoch mask hashes and batch-order hashes are recorded. The mask distribution is independent of ratings and cluster labels. A mask that erases an entire nonzero vector fails explicitly rather than silently substituting an unmasked view. The primary rating loss and all validation/diagnostic scoring use unmasked inputs. These controls isolate target refresh within this masking design; they do not establish that masked coordinates preserve condition-relevant information, or that feature masking improves over no masking.

Seeds 7, 8 and 9 each run one paired fit. AdamW uses constant rate 0.001, projection decay 0.01, classifier decay zero, batch size 32 and clip norm 1.0. Rounds last two epochs. The cap is 48 epochs and 1,200 seconds per seed pair. Exceeding the time budget is a failed attempt and publishes no selected research result.

The two arms run in lockstep with exactly equal optimizer updates and validation-selection opportunities. Epoch zero is eligible. An arm's selected snapshot changes only on a strict new best continuous validation Spearman. **Shared patience five** ends the pair after five consecutive epochs in which neither arm improves its own best. Improvement by either arm resets shared patience. Both arms receive every comparison and every validation check through the same stopping epoch. This paired rule is intentionally different from independently early-stopping each arm.

## Outputs and interpretation

Native TRAIN artifacts contain both selected models for every seed, their associated teacher states, and complete terminal projection/classifier/optimizer/teacher/RNG states. The independent native development EVAL restores the sealed selected models, verifies exact replay of their saved validation metrics and exports scores plus the primary paired summary. Its declared native metric independently recomputes mean gain from the sealed prediction artifact, without an in-stage metric recorder. The trace contains every epoch's unmasked validation metrics, training objective components, exposure counters, round resets, target-label hashes, all target usage counts and permutation-invariant Rand partition agreement at refreshes. Selected-checkpoint diagnostics reuse complete usage histograms, occupied/effective codes, distortion, low-rating collisions and quantized scoring from the existing codebook implementation. They retain all observations and unused centers.

Primary comparison is the arithmetic mean of the three seed-specific refreshed-minus-fixed **selected validation Spearman** differences, with each difference and sample standard deviation reported. This is a development mechanism screen after validation selection. There is no automatic success threshold, hyperparameter search, promotion, fresh-test claim or inferential confidence interval in this draft. Inspect seed consistency, target/collapse diagnostics and runtime alongside the mean before deciding on a separately frozen confirmation.

Numeric cluster assignment is not expert single-label JEP coding. No uniform occupancy loss, frequency pruning or forced claim coverage is introduced. Low occupancy may reflect rarity or failure; it is not grounds to delete a claim. Unassigned expert concepts remain unknown because this experiment has no expert concept schema. Multiple-claim annotation and rare-demand audit remain separate evidence requirements.

## Native execution after review

The controller consumes the successful `prepare_training` and `prepare_validation` native records and the already published `publish_validation` record from the earlier audio-codebook execution summary. Those records must resolve to accessible immutable artifacts in the owner runtime; the tracked summary's original host-local paths alone do not copy data. The controller validates schemas/cohort identities, computes and records exact compact-cache hashes, constructs canonical VIPER TRAIN and EVAL stages, declares CPU compute, records observed environment plus the existing requirements source, seals locally, and queues each successful stage for cloud publication asynchronously. EVAL reuses the existing native published development rows/indices through reserved `model`, `test` and `holdout` bindings; the reserved name `test` identifies development rows in this screen. Every attempt has a new directory; failed attempts are preserved and never automatically restarted. No new BUILD, backbone inference or benchmark test-partition access is launched by this controller.

```bash
python -m csts_pilot.iterative_codebook_run \
  --prepared-summary /path/to/accessible/csts_codebook_execution.json --preflight
python -m csts_pilot.iterative_codebook_run \
  --prepared-summary /path/to/accessible/csts_codebook_execution.json --name initial
```

Preflight loads and validates existing CPU feature artifacts and builds the native training stage; it does not train. Full native execution awaits user review of this PR. The independent code-review record must identify the exact reviewed snapshot and repair any actionable findings before finalizing the draft for review.
