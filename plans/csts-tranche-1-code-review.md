# Tranche 1 code walkthrough

**Status: collaborative review open. Experiment execution awaits the user's code review.**

The first implementation is commit `50e266e53c6d144de1bf33ac3a102844b1ae8b18`, compared with plan commit `18a1509d7fd3fdabaea78697fff997f41080322f`. The scientific design is in [the plan](csts-tranche-1.md); the concrete parameters are in [the frozen settings](../configs/csts-tranche-1.json).

## First slice: the two rating losses

Review [`rating_loss` in joint.py](../csts_pilot/joint.py). It receives one batch of cosine scores, the matching rescaled human/LLM training targets and the chosen objective.

The invariant is simple: given the same scores and targets, the experimental difference is the objective. Both branches calculate their loss using float32 arithmetic.

- MSE averages squared prediction errors.
- Pearson subtracts each batch mean, computes the centered dot product and divides by stabilized vector lengths. The returned loss is one minus that correlation.
- Each squared vector length receives the predeclared epsilon of `1e-8` before its square root.
- A constant-target batch returns Pearson loss 1 and zero data gradient. The training loop still performs its ordinary optimizer and schedule step.

The small observers cover hand-computable loss values, analytic gradients, constant targets, constant predictions, BF16 inputs and gradient flow through a real small T5 encoder and its projection. The historical rating loop retains MSE as its objective.

**Loss-slice finding:** none identified in these cases. Author judgment on the intended comparison is pending. This finding covers the loss function and its immediate callers; the rest of the collaborative review remains open.

## Remaining slices

1. **Training and checkpoint selection:** [`convergence.py`](../csts_pilot/convergence.py). Native VIPER `@train` stages restore the shared initialization, use the common pair permutations and retain the best validation checkpoint from each window. Final weights and optimizer state are saved separately from the selected checkpoints.
2. **Ordering and recovery:** [`convergence_run.py`](../csts_pilot/convergence_run.py). Both arms finish before selection and calibration are frozen. Identical checkpoint bytes share test predictions. Resume reuses successful native references; an uncertain invocation requires reconciliation.
3. **Test scoring:** [`test_checkpoint`](../csts_pilot/convergence.py). A native VIPER `@eval` stage checks checkpoint, selection and test-input hashes before scoring. Independent VIPER metric workers recompute MSE and Spearman from the saved predictions.
4. **Calibration and uncertainty:** [`convergence_analysis.py`](../csts_pilot/convergence_analysis.py). Positive affine fits use validation caption groups. The paired bootstrap resamples connected test-caption groups, sharing each sample across the four candidates.
5. **Reporting and compute:** [`convergence_report.py`](../csts_pilot/convergence_report.py). CPU reporting checks saved labels and calibration, recomputes metrics and intervals, exports epoch traces and renders common learning curves. GPU-stage wall time, including native publication, counts toward the common ceiling.

## Mechanical evidence

- 30 focused tests passed; one existing CUDA precision regression was skipped on the Mac.
- Pyrefly passed for training and orchestration using the existing task environment and VIPER source pinned to `e4ce91fa0a9330e769644aba0fccdfe062d5d821`.
- Pyrefly passed for analysis and reporting using the existing CPU report environment.
- Ruff lint and formatting checks passed. Plan references, prose, math delimiters and Git whitespace checks passed.
- The actual CPU report command completed on explicitly synthetic fixtures and rendered its curves.
- The default runner command displayed settings and created zero experiment state.

Actual L4 execution, native runtime verification, resource accounting on the VM and operator startup/shutdown checks remain for the execution phase after review. Prior studies and their saved artifacts retain their existing identities.

**Overall verdict: incomplete.** The first code snapshot and its mechanical checks are ready for discussion; the remaining slices and the user's judgment are pending.
