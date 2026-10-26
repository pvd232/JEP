# Tranche 4: condition-reference and pooling diagnostic

**Independent native verification passed. Native Qwen + LoRA is retained.**

Validation: **1,830 pairs**. Optimizer updates: **0**. Each arm retains **90.11% recall** at its validation-derived cutoff.

| Arm | Spearman | MSE | False-positive rate | False positives |
|---|---:|---:|---:|---:|
| Native Qwen + LoRA | 0.78257 | 0.03457 | 9.69% | 47/485 |
| Condition subtraction, unit-first | 0.69657 | 0.05236 | 21.86% | 106/485 |
| Condition subtraction, raw-first | 0.68956 | 0.05337 | 20.00% | 97/485 |
| Generic subtraction, unit-first | 0.77971 | 0.08445 | 9.69% | 47/485 |
| Generic subtraction, raw-first | 0.76699 | 0.10910 | 10.93% | 53/485 |
| Passage-only mean pooling | 0.20781 | 0.14479 | 78.14% | 379/485 |

**Every intervention missed the validation gate.** The experiment stops here under the proposal. Test scoring and training continuation remain unstarted. The GPU is idle.

The corrected extraction matches the saved baseline within **2.3842e-7**. Condition unit-first subtraction reduced global average pairwise cosine from **0.146 to 0.121** and raised false positives from **47 to 106**.

Checks: **9 focused tests passed; Ruff passed; Pyrefly: 0 errors.** Native CPU EVAL succeeded. Cloud promotion is queued independently.

[Metrics and provenance](csts_condition_reference_results.json) · [Runner](../csts_pilot/condition_reference_run.py) · [Scoring code](../csts_pilot/condition_reference.py) · [Proposal](../plans/csts-tranche-4-condition-component.md) · [Derivations](../plans/csts-tranche-4-derivations.md)

## Geometry

Geometry uses **3,591 unique passage–condition inputs**, taking the first occurrence in original comparison order. The output width is 4,096 and the global sample covariance rank ceiling is 3,590. Within-condition geometry covers 31 conditions with at least 16 unique inputs. Every arm uses identical keys.

| Arm | Mean pairwise cosine | Mean-vector norm | Variance participation rank | Leading variance share |
|---|---:|---:|---:|---:|
| A | 0.145926 | 0.382314 | 96.82 | 4.94% |
| B_u | 0.120724 | 0.347806 | 109.11 | 5.69% |
| B_r | 0.122136 | 0.349829 | 107.32 | 5.79% |
| C_u | 0.517311 | 0.719337 | 101.37 | 4.51% |
| C_r | 0.608282 | 0.779994 | 108.00 | 4.15% |
| D | 0.555990 | 0.745730 | 56.94 | 8.91% |

The condition references reduced global alignment and raised false-positive counts. These reference directions damaged discrimination on the trained checkpoint. Generic subtraction and passage averaging increased global average pairwise cosine to 0.517–0.608.

Passage-only averaging changes the trained EOD readout. Its observed Spearman was 0.20781 and false-positive count was 379. The condition remains available through the contextual token states in this arm.

The condition-reference norm divided by passage norm averaged 1.0246, with 5th–95th percentiles 0.8658–1.2066. Passage/reference cosine averaged 0.3899. Passage masks contained 8–37 tokens, averaging 16.26. All vectors, masks, and residuals passed full-cohort coverage and finite-norm checks.

## Decision rule and cohort

Negatives are ratings 1–2 (485 comparisons); positives are ratings 4–5 (718 comparisons). Every arm retained 647 positives and missed 71. The 627 rating-3 comparisons contribute to Spearman and MSE. The validation cohort contains 688 connected source groups.

Eligibility required a false-positive-rate reduction of at least 2 percentage points and a Spearman decrease of at most 0.005. The selected arm is A. Tranches C and D remain unstarted under the prespecified stopping rule.

## Reproduction and recovery

The first sorted-unique extraction changed batching and exceeded the native-agreement gate: maximum difference 0.021379143. It is preserved. A probe covering the eight largest discrepancies and their batch partners reproduced all 16 saved scores exactly with the original two-pair layout. The corrected extraction retains that layout, captures each passage occurrence, and stores explicit comparison-to-state indices. Geometry selects the first occurrence per unique input.

The maximum native-score difference across all 1,830 validation pairs is 2.384185791015625e-7 against tolerance 0.001. Adapter tensor digests before and after extraction match. Raw EOD states and passage means share the same forwards; subtraction variants share 918 condition/generic reference inputs.

The CPU wrapper was corrected to declare its objective and consume canonical stored cohort/indices inputs. Independent native EVAL reused the saved extraction and sealed the predictions, report, full covariance spectra, and geometry. Extraction worker time was 200.37 seconds; native extraction wall time was 237.41 seconds. Native CPU EVAL wall time was 89.23 seconds.

## Provenance

- Backbone: `Qwen/Qwen3-Embedding-8B`, revision `c90816d848505624c2434128dfc61132162a0ee9`.
- Adapter checkpoint SHA-256: `8805f9a7241e4e19ffc481341ebad6f1ddb6dd6ff04bbf710f9f0896469e34ff`.
- Extraction source: `c7f5bf04e18d4a4efced86a2533dcfd9c4a03858`.
- Final evaluator source: `7fca57e9741702e6484b5ffc133642f18b40e4dd`.
- Original plan SHA-256: `3eaf1b31528f7af61fd30efaefd8c20d5810df46e5d4008c99fc203898a19520`.
- Selection SHA-256: `0d724b35b83676333afac4b41b1db7f418f1a5f7d5a2488ae27625d35215d0e1`.

[Machine-readable results](csts_condition_reference_results.json) include all arm metrics, per-condition geometry summaries, reference alignments, native run references, artifact hashes, the selection, and the reproduction probe. Full spectra and per-row predictions remain sealed in the referenced native artifacts.

