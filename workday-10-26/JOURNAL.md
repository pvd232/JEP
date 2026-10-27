# Overnight experiment, October 26–27

Deliverable: compare ratings supervision with proposition supervision on the published jep-csts-v1 exports. Publish the result by 8:00 a.m. Eastern on October 27 at the existing epoch score-table path.

## Dataset and inputs

The published dataset package comes from main commit `61a48b2fa580c7457155535bcfafde10426dab83`. Its manifest binds 6,051 training, 1,576 validation, and 2,430 test comparisons. Reconstruction and export hashes were checked before preparing training inputs.

The pilot freezes 2,496 existing, source-matched proposition inputs with replayed raw generation receipts. These cover 2,135 training comparisons for the initial two epochs. Both models see those same comparisons during this step. Both models then train on all 6,051 ratings comparisons. The remaining 9,413 unique proposition inputs are reserved for generation after a positive pilot decision.

## Execution order and time limits

1. Finish exactly two old-data ratings epochs for the proposition model; preserve both models' old-data results and native artifacts.
2. Archive the old score table beside the existing live table.
3. Start both updated-data models from the same pretrained initialization, using seed 7, the same fixed first-step exposure, learning rate, and ratings data.
4. Train each model with validation patience 2. Each initial two-epoch step has an 1,800-second budget; each full-data ratings step has an equal 8,100-second budget and a 24-epoch ceiling. The aggregate GPU budget is 21,600 seconds, including scoring allowance. The observed completion time depends on GPU throughput and native sealing overhead.
5. Freeze the two selected validation checkpoints before scoring test predictions. Keep predictions as separately sealed native artifacts.
6. Publish selected validation/test scores, epoch histories, and paired source-group intervals. A separate deadline process publishes retained progress if the suite remains incomplete at 8:00 a.m.
7. Queue and execute missing-input generation only when the selected proposition-model validation Spearman exceeds the selected ratings-control validation Spearman. A tie or negative difference leaves generation unqueued. Checkpoint selection and the generation trigger use validation scores. Report this as a one-seed screening comparison.

The GPU host publishes changed trace snapshots after 30-second checks. Training and the deadline publisher run independently of this chat. The local transition controller waits for the native decision and performs conditional generation using the existing authenticated generation tool. Completed requests remain reusable if a downstream step fails. Preventing local idle sleep keeps that conditional queue available.

## Validation boundary

Changed claims and observers:

- Patience 2 and revised split counts: `tests/test_proposition_pilot.py`, actual settings validation.
- Validation-only generation decision and incomplete-run rejection: `tests/test_proposition_pilot.py`.
- Published stopping policy and native trace preservation: `tests/test_export_proposition_epoch_scores.py`.
- Partial proposition coverage and frozen source bindings: `tests/test_csts_proposition_pretraining.py`.
- Revised test-label wording and paired reporting: `tests/test_csts_proposition_evidence_report.py`.
- Explicit pilot scoring at a resource-budget stop, with strict rejection preserved by default: `tests/test_csts_qwen_evidence.py`. Report each model's actual stopping reason beside the selected scores.
- The local transition's two-epoch boundary, publication archival, source-only inputs, and authorized quota-reset boundary: the external controller's focused tests.

Run Ruff import fixes and formatting at actual execution paths, then Pyrefly, the affected tests, and final Ruff checks. Preserve the immutable published dataset scripts byte-for-byte; their package manifest records their digests. Inspect the live native launch and public score table after publication. Broader model benchmarks and additional seeds remain outside this bounded overnight pilot.

## Replanning and shutdown

On a native stage failure, retain completed artifacts and publish the failure. Repair downstream analysis or publication using the existing measurements. A deadline miss produces an explicit incomplete report with the latest scores. The local checkout and GPU checkout remain attached to this active experiment until the training and conditional-generation work finish.

The authorized October 29 earned reset is monitored separately and redeemed only after the current Codex allowance is exhausted. Other earned resets remain outside this authorization.

## Completed setup checks

The old-data proposition model completed its requested two ratings epochs: validation Spearman 0.8126011325 and 0.8216492088. The ratings control's second-epoch score was 0.821362. Native traces and the completion receipt remain on the GPU host.

At the GPU execution paths, Ruff import fixes and formatting completed; Pyrefly reported zero errors across the eight changed Python files. The following focused command passed 41 tests and 10 subtests:

```text
python -m pytest -q tests/test_proposition_pilot.py tests/test_export_proposition_epoch_scores.py tests/test_csts_proposition_pretraining.py tests/test_csts_proposition_evidence_report.py tests/test_csts_qwen_evidence.py
```

Final `ruff format --check` and `ruff check` passed for all eight files. The external transition and reset controllers passed Pyrefly with zero errors, seven focused tests, and final Ruff checks. The prose check passed for this journal and the new supervisor and pilot-test files. These checks cover setup behavior; new-model training results remain pending until the native runs complete.
