# Tranche 4: live validation scores

**Status: corrected native-batch extraction running.** Optimizer updates: **0**. Validation cohort: **1,830 pairs**.

| Arm | Spearman | MSE | False-positive rate | Recall | Source/status |
|---|---:|---:|---:|---:|---|
| A: native Qwen + LoRA | 0.78257 | 0.03457 | 9.69% | 90.11% | Saved selected-checkpoint validation predictions; full rerun verification pending |
| B_u: condition subtraction, unit-first | — | — | — | — | Extraction running |
| B_r: condition subtraction, raw-first | — | — | — | — | Extraction running |
| C_u: generic subtraction, unit-first | — | — | — | — | Extraction running |
| C_r: generic subtraction, raw-first | — | — | — | — | Extraction running |
| D: passage-only mean pooling | — | — | — | — | Extraction running |

Each arm uses its own largest validation cutoff retaining at least 90% positive recall. Negatives: ratings 1–2; positives: ratings 4–5. The native cutoff is `0.5334962606430054`; confusion counts: TP 647, FN 71, FP 47, TN 438. Rating 3 remains in Spearman and MSE.

The original two-pair batch layout reproduced all 16 probed native scores exactly. The full extraction retains that layout; all six arms share its states. Geometry uses one deterministic occurrence per unique passage–condition input. The initial sorted-unique cache is preserved; its maximum native-score discrepancy was 0.02138, above the 0.001 gate.

Checks: **9 focused tests passed; Ruff passed; Pyrefly: 0 errors.**

[Runner](../csts_pilot/condition_reference_run.py) · [Scoring code](../csts_pilot/condition_reference.py) · [Proposal](../plans/csts-tranche-4-condition-component.md) · [Derivations](../plans/csts-tranche-4-derivations.md)

Corrected source: `c7f5bf04e18d4a4efced86a2533dcfd9c4a03858`.
