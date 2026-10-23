# Tranche 1 code walkthrough

**Status: collaborative review open; execution authorized on October 23, 2026.** The user explicitly instructed “yes. run it” after the loss discussion. Execution authorization and walkthrough completion are recorded separately.

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

The actual pinned L4 environment passed 22 focused checks, including CUDA precision, before launch. Both 24-epoch arms completed and their matched initialization, RNG, permutations and update counts passed verification. Prior studies and their saved artifacts retain their existing identities. Shutdown checks remain for closeout.

**Overall verdict: incomplete.** The first code snapshot and its mechanical checks are ready for discussion; the remaining slices and the user's judgment are pending.

## Execution repair: canonical model handoff

The first prefix evaluation produced predictions and independent metric receipts, then failed final VIPER verification: a stored EVAL model must select an artifact named `model`. The frozen prefix checkpoint was stored as `prefix_model`. The failed native run remains failed and its evidence is preserved.

The repair adds a CPU BUILD stage that copies the frozen prefix checkpoint to canonical `model`, checking the same SHA-256 before and after copying. Full-window checkpoints already have the required name. The EVAL implementation, predictions, metric definitions and selection rules remain fixed.

The separate `convergence_evaluate` command has an evaluation-only entry point. It verifies completed native runs, matched arms, frozen settings, selection hash and checkpoint bytes; preserves the original failed summary and sealed references; and charges further scoring against the original remaining GPU-stage budget. It contains zero training-stage execution calls. Training and evaluation source commits are retained separately.

Repair checks: 21 focused loss, native model-selection, failure-reconciliation and report tests passed; Ruff and Pyrefly passed. The native-selection regression reproduces the original rejection and accepts the canonical handoff. The first-pass diff review also caught and removed an accidental extra argument in the untouched initialization call.

## Completed execution evidence

Both 24-epoch training arms and all four fixed-checkpoint evaluations completed. Ten successful native runs and 152 measurements passed VIPER verification. The failed first prefix invocation remains separately preserved. The successful prefix prediction artifact is byte-identical to the failed invocation's predictions.

Independent CPU reporting matched all native test metric events within 1e-12. It checked 2,620 aligned test rows, 1,241 source groups, frozen calibration and 2,000 shared component-bootstrap draws. The rendered learning curves were inspected. The 132-file transferred archive passed its SHA-256 and per-file manifest checks. GPU-stage accounting, including the failed attempt, totaled 1,678.29 seconds against the 1,800-second ceiling.

The [full report](../training_outputs/csts_tranche1_report.md), [native verification](../training_outputs/csts_tranche1_native_verification.json), [recovery evidence](../training_outputs/csts_tranche1_recovery.json), and [timing breakdown](../training_outputs/csts_tranche1_evaluation_timing.json) preserve the result and its limits. CPU report regressions, Ruff and Pyrefly passed for the report update and native CPU publication module. The actual pinned VM also passed all three new handoff and reconciliation checks before recovery.

Mechanical execution and author inspection of the results are complete. The collaborative code walkthrough remains open.

## Publication and cloud closeout

The [native CPU report receipt](../training_outputs/csts_tranche1_report_publication.json) records successful graph verification and exact-byte restoration. The [cloud receipt](../training_outputs/csts_tranche1_shutdown.json) confirms both VMs TERMINATED and removal of this invocation's new scoped NAT. The [closeout record](../training_outputs/csts_tranche1_closeout.md) distinguishes 49.16 minutes of VM lifecycle time from the 27.97-minute native GPU-stage counter and documents the Mac CPU publication fallback.
