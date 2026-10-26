# Tranche 4: condition-reference diagnostic

**Status: original native batch layout reproduced exactly.** All 16 probed rows (including the eight largest discrepancies) matched their saved scores exactly. The extractor now preserves the original two-pair forward batches. Optimizer updates: **0**.

The initial sorted-unique extraction is preserved as a diagnostic artifact. Its maximum baseline difference was 0.02138. Full-cohort arm scores follow the corrected extraction and the unchanged 0.001 agreement requirement.

Validation: 1,830 pairs. All six arms share the captured contextual states. Geometry uses one deterministic occurrence for each unique passage–condition input. Test scoring follows the prespecified validation gate.

[Runner](../csts_pilot/condition_reference_run.py) · [Scoring code](../csts_pilot/condition_reference.py) · [Proposal](../plans/csts-tranche-4-condition-component.md) · [Derivations](../plans/csts-tranche-4-derivations.md)
