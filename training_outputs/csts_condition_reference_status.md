# Tranche 4: live validation scores

**All six validation arms scored. Native Qwen + LoRA is retained.** Every intervention missed the prespecified validation gate. Independent native CPU verification and geometry are being finalized.

Validation: **1,830 pairs**. Optimizer updates: **0**. All arms retain **90.11% recall**, using their own validation-derived cutoffs.

| Arm | Spearman | MSE | False-positive rate | False positives |
|---|---:|---:|---:|---:|
| Native Qwen + LoRA | 0.78257 | 0.03457 | 9.69% | 47/485 |
| Condition subtraction, unit-first | 0.69657 | 0.05236 | 21.86% | 106/485 |
| Condition subtraction, raw-first | 0.68956 | 0.05337 | 20.00% | 97/485 |
| Generic subtraction, unit-first | 0.77971 | 0.08445 | 9.69% | 47/485 |
| Generic subtraction, raw-first | 0.76699 | 0.10910 | 10.93% | 53/485 |
| Passage-only mean pooling | 0.20781 | 0.14479 | 78.14% | 379/485 |

Every arm has TP 647 and FN 71 out of 718 positives. Negatives are ratings 1–2; positives are ratings 4–5. The 627 rating-3 comparisons remain in Spearman and MSE.

The eligibility rule requires a false-positive-rate reduction of at least 2 percentage points and a Spearman loss of at most 0.005. The condition-reference arms worsened both measurements. Generic unit-first subtraction retained the same false-positive count with a small ranking loss. Passage-only pooling strongly reduced discrimination on this trained checkpoint.

The validation decision retains A. The plan stops here when no candidate qualifies; test scoring and conditional LoRA continuation remain unstarted.

The corrected extraction matches the saved native scores within **2.3842e-7** across all 1,830 comparisons (tolerance 0.001). It retains the original two-pair forward batch layout. Geometry uses one deterministic occurrence per unique passage–condition input. The initial sorted-unique extraction and the exact-reproduction probe are preserved.

Checks: **9 focused tests passed; Ruff passed; Pyrefly: 0 errors.**

[Runner](../csts_pilot/condition_reference_run.py) · [Scoring code](../csts_pilot/condition_reference.py) · [Proposal](../plans/csts-tranche-4-condition-component.md) · [Derivations](../plans/csts-tranche-4-derivations.md)

Extraction source: `c7f5bf04e18d4a4efced86a2533dcfd9c4a03858`. Model SHA-256: `8805f9a7241e4e19ffc481341ebad6f1ddb6dd6ff04bbf710f9f0896469e34ff`.
