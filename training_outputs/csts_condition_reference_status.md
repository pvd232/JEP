# Tranche 4: live validation scores — complete

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

[Full report](csts_condition_reference_report.md) · [Metrics and provenance](csts_condition_reference_results.json) · [Runner](../csts_pilot/condition_reference_run.py) · [Scoring code](../csts_pilot/condition_reference.py) · [Proposal](../plans/csts-tranche-4-condition-component.md) · [Derivations](../plans/csts-tranche-4-derivations.md)

