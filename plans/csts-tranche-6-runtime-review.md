# Tranche 6: independent runtime and provenance review

Reviewer: `/root/moa_review/runtime_review`. Date: 2026-10-26. Independent of the attention-core/controller authors and numerical/statistical reviewer. Workflow follows the user's Multi-Agent Orchestration primer and code-review skill used for Tranche 5.

**Final runtime verdict: no open blocking finding in the reviewed two-arm implementation.** Owner-environment mechanical checks passed and the final formatted-source hashes were independently verified. This review launched no follow-up inference, fitting, baseline scoring, or GPU job.

## Reviewed snapshot

The core, controller, settings, tests, and both relevant plans were read in full, including the inherited Tranche 5 source/bank/cache/metric helpers. The five final delivery hashes below match `csts-tranche-6-verification.json`. The overnight handoff was also inspected as execution context.

| File | SHA-256 |
|---|---|
| `csts_pilot/evidence_attention.py` | `9c3fa6288d7e2a725a9647f0577651f8bff15ab59d843be67515ec67c096d349` |
| `csts_pilot/evidence_attention_run.py` | `178904501da47710602ceb43095fddc5146f21933078bba15d2ba7fbb359f7a8` |
| `configs/csts-evidence-attention.json` | `d7230f45dd6dcc26d2f70ff8a420cb4894ab5bd3717400141149a5d16bb68ca5` |
| `tests/test_csts_evidence_attention.py` | `95afd5192cd2ad805935ca79c6fa2e0539e094beea1cc66c33f71d4e0a3d01aa` |
| `plans/csts-tranche-6-evidence-attention.md` | `abd0e7ce51905d6dd32b8ce2a80340bc0deff14579c772b87f168a27e36f73af` |

## Verified runtime contract

- The only new TRAIN arms are `attention_ratings` and `attention_evidence`. They use the same frozen selected Qwen checkpoint, pinned tokenizer/revision, full comparison cohorts, bank-excluded fitting rows, initialization, permutations, dropout policy, and optimization settings. Archived native predictions supply the comparator; no baseline-inference or newly trained native-head path is present.
- A complete archived validation prediction identity check precedes follow-up inference. Model, prepared data, teacher cache, bank, feature caches, selected heads, and output snapshots carry hash/configuration bindings. The pinned teacher cache produces targets only in the training token cache. Validation/test extraction rejects teacher input and teacher lineage, stores zero target mass, and prediction requires no teacher target.
- Token caches preserve input IDs, character offsets, condition/passage indices, packed token boundaries, exact semantic row joins, and exactly two passage occurrences per comparison. Caches must have complete finite features and a declared split/teacher identity. The frozen encoder is in evaluation mode with gradients disabled; initial and terminal adapter digests must agree. The head retains float32 under worker autocast and supports the double-precision numerical observers.
- Every native stored artifact receives a distinct binding/materialization path. BUILD extracts frozen tokens and freezes validation selection; TRAIN fits the two small heads; canonical stored model/test/full-cohort indices feed CPU EVAL and its separately declared stateless metric worker. The selected validation head is independently restored on CPU and must reproduce captured validation scores before thresholds/candidate are frozen.
- A missing eligible validation candidate stops test extraction. The candidate/test capture and independent evaluation reuse archived native test scores, require exact row identity and snapshot bindings, and retain validation-derived classification thresholds.
- The controller directly reuses the predecessor's sealed Tranche 5 bank record. It requires a terminal predecessor, the selected parent identity, the deterministic seed-7/16-group bank contents, and equality with the predecessor's bank SHA. It records the predecessor summary hash and reused producer reference. It performs zero new bank-selection/native-baseline model passes.
- Default invocation displays configuration; preflight performs identity/schema checks without inference. Execution requires the predecessor summary and uses a separate exclusive attention-study lock. Existing queue/attempt files fail closed and remain available for reconciliation. Automatic stage reuse/resume is outside this runner.
- Before waiting, the queue records committed source and settings identities. It requires a clean tracked tree and compares those identities again after obtaining the shared GPU lock. The owner launch must use the final independently reviewed and mechanically checked source snapshot. Changes to source/settings while queued stop execution.
- The follow-up acquires the original parent workspace's `.viper/overnight_gpu.lock` internally and holds it through execution. The active Tranche 5 external wrapper holds that same path. The follow-up command must use its internal lock directly; adding an outer wrapper around that same lock would deadlock.
- Resource categories are cumulative across stages: 4,800 seconds for training/validation token extraction, 1,800 seconds total for the two heads with 900-second individual ceilings, and 600 seconds for conditional test extraction. Their total is 7,200 seconds, or 120 GPU minutes. CPU analysis has a separate cumulative 1,800-second limit. Every stage timeout uses its remaining category allowance; failures preserve the in-flight stage and native diagnostics.
- Every GPU-stage allowance is additionally capped by the remaining time before `2026-10-26T12:30:00Z`. An exhausted overnight window raises before a GPU stage starts. This prevents a queued follow-up from starting new GPU work after the stop time and limits work already started to that remaining window.
- Token-extraction progress, epoch metrics, selected completed-arm metrics, selection/test results, stage transitions, resource counters, failures, and publication references are flushed through the attention event sidecar/controller summary. Native local sealing precedes independent cloud publication.

## Live serialization observation

Read-only process/descriptor checks were made on `jep-csts-format-20261021` using the existing account and owner environment. At inspection, PID 54341 was the external `flock` wrapper for the active Tranche 5 controller. Its descriptor 3 pointed to `/home/machina/jep-csts-qwen-evidence-20261024/.viper/overnight_gpu.lock`; `lslocks` independently reported PID 54341 owning that file lock. Child controller PID 54342 had parent 54341, descriptor 3 for the same overnight GPU lock, and descriptor 4 for its own `matched_baselines.lock`. NVIDIA reported a single compute process, PID 54661, using 14,884 MiB. A second read-only check verified that PID 54661 ran `python -m viper._workers.stages`, with parent 54342 and grandparent 54341. This verifies the actual native worker/controller/wrapper relationship and the lock path used by the reviewed follow-up serializer.

## Findings and repairs

| Finding | Consequence | Disposition |
|---|---|---|
| Initial follow-up draft used an independent study lock only. | It could overlap the active Tranche 5 GPU workload. | Repaired with the shared original-workspace blocking GPU lock; independently matched to the active wrapper's actual descriptor/lock. |
| Initial queue had no post-wait source/settings check. | A queued process could run after its reviewed checkout/settings changed. | Repaired with initial identity capture, clean tracked-tree requirement, and identity comparison after shared-lock acquisition. |
| Initial draft resealed a bank without comparing predecessor identity. | A follow-up cohort difference could go unnoticed. | Repaired by directly consuming the predecessor's sealed bank and checking deterministic contents plus SHA before extraction. |
| Initial draft lacked the overnight stop time. | A long queue could start new GPU work after the declared deadline. | Repaired by pinning the deadline in settings and capping every GPU-stage timeout before native execution. |
| Initial cache validation omitted explicit teacher lineage and exact occurrence count. | Training/held-out target identity or occurrence reuse could escape shape checks. | Repaired with split-dependent teacher SHA checks and exactly `2 * comparison_count` occurrences plus complete semantic index coverage. |

## Executed checks and execution limits

Independently parsed all three Python deliverables and the JSON settings locally, reviewed the complete new DAG and changed helper paths, checked the resource arithmetic, and inspected the live shared-lock owner/descriptor relationship. The coordinating reviewer records the numerical/gradient observers and owner-environment test/lint/type-check receipts separately.

Actual follow-up native stage materialization, real tokenizer offset coverage, literal-span alignment counts, measured token-cache memory/throughput, frozen adapter digest observations, benchmark fitting, and final test metrics remain execution evidence. Preflight performs no model inference.

## Final source and owner-gate rereview

Reviewed the final formatted source through normalized Python syntax trees and the document/configuration diffs. The final semantic delta removes an unused import, orders imports, and uses the standard `datetime.UTC` singleton in the deadline calculation. These preserve the inspected runtime behavior. Recomputed every final receipt hash against the actual file and parsed all three Python deliverables; all five hashes matched and syntax checks passed.

The owner-runtime receipt reports 37 focused tests passed in 10.05 seconds, Ruff passed for three files, Pyrefly basic checking passed with zero errors for the two production modules, and preflight passed with zero attention inference or fitting. The coordinating reviewer independently checked eight mathematical observers. These receipts are attributed to their respective owners; this runtime reviewer independently checked source, bindings, hashes, resource arithmetic, and the live predecessor serialization above. The final bounded implementation is ready for the user-authorized queued launch under the reviewed source/settings identity.
