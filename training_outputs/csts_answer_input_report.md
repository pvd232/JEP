# Answer-as-input experiment — 26 October 2026

**Retain the saved Qwen model. All three candidates missed the fixed validation gate.** Native runs completed successfully and independent CPU verification passed. No new candidate test evaluation ran.

## Results

All systems use the same **1,830 validation comparisons in 688 source groups**. Ratings 4–5 define positives and 1–2 negatives for the operating point; rating 3 remains in regression and ranking. Every operating cutoff retains **647/718 positives (90.11% recall)**.

| System | Spearman | MSE, 0–1 scale | Condition ordering | False-positive rate |
|---|---:|---:|---:|---:|
| Saved Qwen + LoRA | **0.782575** | **0.034574** | **90.15%** | **9.69% (47/485)** |
| Cached answer, original condition | 0.735916 | 0.041714 | 89.04% | 16.70% (81/485) |
| Cached answer, generic condition | 0.603559 | 0.061040 | 81.14% | 38.97% (189/485) |
| Conditioned answers + trained projection | 0.723444 | 0.050707 | 89.04% | 17.53% (85/485) |

Paired source-group validation bootstrap intervals, 2,000 draws:

| Candidate minus saved Qwen | Spearman difference | 95% interval |
|---|---:|---:|
| Conditioned cached answers | −0.046659 | [−0.057964, −0.036110] |
| Generic cached answers | −0.179016 | [−0.206481, −0.152247] |
| Trained answer projection | −0.059131 | [−0.072787, −0.045271] |

These are validation diagnostics for the selected systems at one seed; they do not measure fresh-test performance or seed uncertainty. Eligibility required a 0.005 ranking gain and at most one percentage point worse FPR or condition ordering.

## What ran

Each independently generated, accepted cached evidence answer replaced its passage input. Missing or rejected answers retained the original passage and condition. Validation coverage was **909 pairs with two answers, 545 with one, 376 with neither**. Frozen arms retained saved native scores on neither-answer pairs. The generic arm used “overall meaning” only for accepted answers, so one-answer pairs compare different instruction types.

The trained candidate was declared before frozen scores. It used all **6,980 training comparisons** and the unchanged native projection trainer: fixed selected Qwen+LoRA features, bias-free **4096→128** projection, cosine-MSE, AdamW, seed 7, learning rate 0.001, batch 32, weight decay 0.01, patience 5, ceilings of 48 epochs and 600 fitting seconds. The learned projection applied to all inputs, including original-passage fallbacks. No new native control head or baseline rerun was performed.

The selected checkpoint was **epoch 3, step 657**. Training stopped after **epoch 8 / 1,752 updates** through validation patience. Online training MSE fell from **0.049263 at epoch 1 to 0.009895 at epoch 8** while validation ranking failed to recover. This stopping rule does not establish a stationary loss minimum.

## What the errors reveal

Loss persists when both answers exist: conditioned frozen-answer Spearman is **0.723040**, versus **0.788620** for saved Qwen on those same 909 pairs.

The cached extractor sometimes removes relevant information. In one animal-type comparison, horseback riders pursuing a bull and a bull rider both became **“a bull.”** The reference rating is 2, but identical input representations have cosine 1. Other inspected errors omit the bike from a mountain-biking answer, select location for a performance-medium question, or mishandle an explicitly mentioned additional woman.

There are **68 exact same-answer pairs** with two accepted answers: 51 rated 5, 16 rated 4 and one rated 2. The imperfect-rating collisions impose a full-cohort cosine-MSE contribution of **0.000854** for any deterministic nonzero shared embedding. That confirms one information-loss mechanism; it is too small to explain the entire observed deficit. The error inspection is targeted and does not estimate the overall extractor error rate.

## Decision and scope

Stop this cached-span construction. Further projection tuning cannot restore details removed from identical inputs. The next answer-based experiment should first improve and audit the extraction target: preserve all relevant entities, roles, relations, counts, polarity and qualifications. For JEP, source-grounded claim units should retain actor, demand, beneficiary and attribution.

This experiment tests **cached extractive answers with fallback**, including one trained projection. It does not test reliable generated propositions, full Tu encoder fine-tuning, or Spanish JEP codebook quality. It therefore narrows the answer-input design rather than rejecting every answer bottleneck.

## Verification and records

Both frozen arms replayed exactly from saved CPU vectors (maximum score error **0.0**). Independent checks confirmed every original/transformed row binding, the selected projection checkpoint and trace hashes, training-input hashes, and recomputed metrics. Both code increments passed **18 focused tests**, Ruff, Pyrefly and independent code review. No CUDA compute process remained at closeout. Native artifacts are sealed; publication proceeds asynchronously.

- [Trained result and native references](csts_answer_projection_results.json).
- [Verification record](csts_answer_input_verification.json).
- [Plan](../plans/csts-tranche-7-answer-input.md), [frozen review](../plans/csts-tranche-7-review.md), [trained review](../plans/csts-tranche-7-projection-review.md).
- Sources: frozen `2540590c72dbd197addf40bfef3da66d91c52d93`; trained `775b315f533acee2435d97d4cbeb599a4f11f524`.
- Selected projection SHA-256: `9b4b8b4a6f101b6b00ffd2063b08771ad8f1a1db8302349ddd495463d3f2d440`.
