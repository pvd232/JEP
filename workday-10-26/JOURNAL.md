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

## October 27: finish both models at patience 2

The initial overnight pilot reached four full-data ratings epochs for each model and stopped on `resource_budget`. Both models improved their validation Spearman at epoch four. The user requested completion of both models through patience 2, overriding the overnight time limits and epoch ceiling.

Continue from the sealed terminal adapters, AdamW moments, random state, batch-order generator, validation history, and selected incumbent. Preserve the initial training steps and all four completed ratings epochs. The explicit `train_until_patience` setting disables fitting time and epoch limits for constant-rate neural training. The native execution timeout is also disabled for GPU stages in this completion run. A completed training stage must report `validation_patience`.

Use a separate GPU checkout and result directory, leaving the original pilot's source and measurement artifacts intact. Reuse earlier test predictions when the selected model bytes and test cohort remain identical; compute new predictions for a changed selected checkpoint. Continue publishing at the same score-table path and retain the four-epoch report alongside it. Apply the existing validation-only trigger for missing proposition generation after both models finish.

The completion change passed Pyrefly with zero errors and 80 focused tests across the baseline trainer, Qwen evidence trainer, proposition LoRA wrapper, pilot decisions, epoch exporter, and comparison report. Final Ruff format and lint checks passed for all nine changed Python files at the GPU execution paths. The tests verify continuation beyond the old time and epoch limits, restoration of a previously stale validation check, preservation of optimizer state and next batch order, and publication of the live continuation trace.


## October 27: approved four-epoch first-phase follow-up

After the current two-initial-epoch comparison finishes both models at patience 2 and publishes its final report, automatically run the approved follow-up. Continue both saved first-phase checkpoints from epoch two through epoch four. Restore terminal adapters, AdamW moments, the batch generator and random state. Preserve the original two epochs and their artifacts.

Keep the same frozen 2,135 covered training comparisons and proposition bank. Give each model 268 total first-phase optimizer updates: the control learns ratings, and the proposition model writes propositions. Then start a fresh optimizer for each full-data ratings phase on all 6,051 comparisons, with validation patience 2 and disabled time and epoch limits. Preserve seed 7, learning rate, model initialization, batches and all split hashes. The initial four epochs constitute a matched fixed exposure; the full-data ratings phases continue through patience.

Run the follow-up in its own GPU checkout. The persistent queue waits for the preceding run's successfully published final report, requires `validation_patience` for both models, and acquires the shared GPU lease only when training starts. Archive the completed two-initial-epoch table beside the live table. Continue publishing each completed epoch at the same public path after 30-second checks. Keep validation-only checkpoint selection and the existing positive-result generation trigger.

Publish conditional generation coverage in separate `generation_progress.json` and `generation_progress.md` files so generation updates preserve the active training table. Serialize generation ownership and reuse every completed raw batch. Both comparison monitors can trigger this same reusable queue.

At the actual follow-up GPU paths, Pyrefly reported zero errors; 47 focused tests and 10 subtests passed. The continuation test checks both objectives with a real tiny Qwen/PEFT model, proving that two saved epochs followed by two resumed epochs produce identical trainable weights, AdamW moments, random state, batch orders, losses and validation predictions to four uninterrupted epochs. It also checks rejection of a changed learning rate and byte preservation of the original artifacts. A later publication-test addition passed all seven pilot tests, including archival of the completed table and preservation of generation progress. Final Ruff format and lint checks passed after each change. Frozen input hashes and the four-epoch settings passed preflight. The external controllers passed zero-error Pyrefly, 10 tests, and final Ruff checks.

The first continuation test exposed a tuple/list comparison across JSON serialization. Comparing the current configuration in JSON mode fixed that check; all subsequent checks above passed. The full-data experiment measurements remain pending.


## October 27: user reduced patience to one

Keep the completed ratings control and its best epoch-four checkpoint. Continue the proposition model from its sealed epoch-four adapters, optimizer and random state with patience 1. Both models in the queued four-initial-epoch comparison use patience 1. The first non-improving validation check ends ratings training; preserve each model's best checkpoint. Time and epoch limits remain disabled, and publishing continues at the same score-table path.

The unfinished proposition continuation was stopped before completing a new epoch. This interruption was unnecessary: a watcher could have stopped it after a completed validation decline. Preserve that interrupted attempt and restart from the last sealed epoch-four state. Reuse the completed six-epoch ratings-control record, whose selected checkpoint remains epoch four, and reuse existing test predictions whenever selected checkpoint bytes match.

The revised source passed zero-error Pyrefly, 93 focused tests and 10 subtests, then final Ruff format and lint checks at the actual proposition execution paths. The added continuation test changes patience from 2 to 1, stops on its first new decline, preserves all earlier epochs and the best checkpoint byte-for-byte, and leaves parent artifacts unchanged. The epoch-report test checks distinct patience values for the completed control and current proposition model. The queued settings declare patience 1 for both models. The generation controllers continue to require both models' completed validation-patience stops before a positive validation result can trigger generation.


The resumed proposition worker remained active while native score publication hit a 60-second Git fetch timeout. Prefetching with the source HEAD as the negotiation tip and disabling automatic maintenance completed in four seconds. The publisher now uses those fetch options and can attach to an already-running training PID. Replacing the publication owner leaves the model worker and its optimizer state running. The completed study summary determines success after an attached process exits. This repair passed zero-error Pyrefly, eight pilot tests, and final Ruff checks at the queued GPU checkout. The public table was refreshed during the repair with the current proposition patience 1 and preserved control history.


Detached native Git fetches continued to time out, so a connected publication bridge now exports the native reporter's proposed files and pushes them through the working connection. It acknowledges the native publication marker only after the destination commit succeeds. Both experiment monitors and the queued follow-up continue to use that confirmed marker. The bridge checks both current and queued comparisons every 30 seconds and exits after both final reports are published. Its three focused tests verify that exporting bytes leaves publication unacknowledged, a failed push cannot acknowledge success, and a successful push acknowledges the exact commit. Pyrefly and final Ruff checks passed locally; the native exporter also passed Pyrefly and final Ruff checks at its operator path. The first bridge publication was confirmed at `6a2541295959c0b16f7c3763bc4214274f09b703`. The proposition worker remained unchanged throughout this publication repair.
