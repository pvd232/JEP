# Tranche 5: independent runtime and provenance review

Reviewer: `/root/moa_review/runtime_review`, independent of implementation ownership and the numerical/statistical reviewer. Review date: 2026-10-26. Workflow: the user's Multi-Agent Orchestration instructions in `/Users/machina/Developer/ChatGPT/moa/introduction-to-multi-agent-orchestration.md`, together with `/Users/machina/.agents/skills/code-review/SKILL.md` and its literature reference.

**Verdict: no open blocking runtime/provenance findings in the reviewed four-arm delivery.** The supplied runner trains the four alternative heads and consumes the existing sealed native predictions as its sole comparator. The review establishes the bounded implementation contract below. Real Qwen extraction, native stage materialization, head fitting on the benchmark, and final test execution remain unperformed in this delivery.

## Reviewed snapshot

All six deliverables were read, including their relevant callers and helpers. The implementation was reviewed through successive repairs; the hashes identify the latest reviewed contents. A later source change requires a bounded rereview and manifest refresh.

| File | SHA-256 |
|---|---|
| `csts_pilot/matched_baselines.py` | `9a89e28bea4f9dff98b8b760931c12babb94c794b27d80cab7175db425f0669a` |
| `csts_pilot/matched_baselines_run.py` | `1e71195a4cc0c034a7bc592112534f5483be02b1af8590ac5ce1dfc47607c65c` |
| `configs/csts-tranche-5.json` | `c492c508e7fb63a199b3e927461d954d4d939fecb2d578dbaa6e245f4153f07c` |
| `tests/test_csts_matched_baselines.py` | `2f9f52eeb5af224ebe75ea28269a3aa29985cea7e19cab9b87c4554976e0ede9` |
| `plans/csts-tranche-5-matched-baselines.md` | `5582db5136accc41002cfd772f8405e4a3b935efd44eb05419981d5b744ba387` |
| `plans/csts-tranche-5-derivations.md` | `a7b58e0e3417ce09a20bce7d613acd66f335037c1c73396b04bfcdbd9584c492` |

Relevant dependency behavior inspected: `convergence_run.check_inputs` and `artifact_path`; the original `qwen_evidence_run` producer bindings for validation/test predictions; conditional-reference metric/bootstrap helpers; pinned encoder/readout helpers; existing loader/publication and native BUILD/TRAIN/EVAL conventions. The numerical/statistical reviewer owns the independent algebra, gradient, eligibility, cutoff, and uncertainty verdict.

## Runtime and provenance conclusions

- Default invocation displays settings. `--preflight` validates declared inputs, schemas, parent checkpoint bytes, and archived validation prediction identities without inference or fitting. `--execute` acquires an exclusive study lock before entering execution.
- Runtime configuration lists exactly `same_passage`, `population`, `projection`, and `case`. The TRAIN loop uses that four-arm list. Baseline reproduction and native-head fitting stages are absent. Raw native contextual states remain required inputs to three alternative constructions.
- The archived validation predictions and selected checkpoint come from the same recorded original training run. The selected checkpoint is SHA-256 checked before execution. Archived validation rows must match the complete declared cohort in identity, contents, order, and multiplicity before inference. Archived prediction hashes are recorded in validation selection and test capture/report receipts; native stored-input references retain their producer identities.
- Native stages bind the exact source commit, declared environment/lockfile, configurations, parent model, bank, cohorts, and predecessor artifacts. Every stored binding has its own materialization path. Final CPU EVAL receives canonical stored test, model, and full-cohort index inputs; its stateless metric declares artifact dependencies and a numerical comparator.
- Bank construction is deterministic and uses training passages from distinct source groups. The same bank groups are excluded from every alternative head's fitting rows. Train/validation group and canonical-caption overlap fail closed. The selected LoRA checkpoint's earlier exposure to the original training groups is explicitly documented.
- Extraction freezes the encoder and adapters in evaluation mode; reference and passage states are cached with input/model/bank identities. Initial and terminal adapter tensor digests must agree. Cache validation checks finite shapes, row coverage, semantic key/index alignment, and configured lineage before fitting or prediction. The new heads receive cached tensors only.
- Selection reloads all four selected head checkpoints and reproduces their captured validation predictions on CPU. It verifies arm names, feature/checkpoint identities, common initialization, and common fitting cohort. It freezes thresholds and the candidate before candidate test extraction/scoring. Input identity checks read the split files earlier, and this existing test set was already examined historically. Test metrics do not enter candidate selection. An ineligible validation result ends the experiment before test extraction.
- Test capture uses the frozen candidate plus the archived native predictions and verifies complete test row identities. CPU EVAL verifies snapshot hashes, model/selection/bank/cohort bindings, the frozen selected arm, all cohort indices, and the exact two-system snapshot before computing metrics.
- Extraction progress, epoch scores, completed-arm scores, stage transitions, and failures are flushed to stdout and the tranche-5 JSONL sidecar. Controller records preserve source/settings identity, native run references, the in-flight stage, resource accounting, selection, and errors. Native local sealing precedes asynchronous publication.
- A repeated attempt name raises an error. Automatic artifact reuse and resume are explicitly outside this runner. External timeouts and invalid features preserve a failed attempt for manual reconciliation; successful terminal training state contains the head, optimizer, RNG, generator, cohort IDs, epoch, and update count.

## Findings and disposition

| Finding | Original consequence | Disposition |
|---|---|---|
| P1: tranche-4 emitter imported by tranche-5 controller | Scores printed without reaching the requested tranche-5 sidecar. | Repaired: local emitter reads `CSTS_TRANCHE5_EVENTS`, rejects nonfinite JSON, prints with flush, and appends to that sidecar. Focused test supplied. |
| P1: implicit execution from the default CLI | A settings inspection could launch extraction and fitting. | Repaired: explicit mutually exclusive modes; default is configuration-only. |
| P1: cache validation checked counts without matching row semantics | A valid permutation could attach another passage's feature to a row. | Repaired: exact `(condition, passage)` checks for both sides of every row before fit/selection/test capture. Concrete swapped-index observer supplied. |
| P1: incomplete checkpoint/cache/arm lineage checks | A checkpoint could be bound under the wrong arm or cache identity. | Repaired: checkpoint configuration and cache metadata are checked against arm/model/bank/cohort/cache bindings. |
| P1: selection expected trace fields absent from fit output | Selection would raise after completed fitting. | Repaired: final trace contains common fitting-ID hash and `training_rows`, matching the selection reader. Toy fit/selection coverage supplied. |
| P2: archived validation cohort checked only after all head fits | A stale archive could consume the full fitting budget before failing. | Repaired: complete archived validation identity check runs before preflight return and before any inference. |
| P2: completed-head score emission delayed until all-head selection | The user could not see a completed arm immediately. | Repaired: controller emits each sealed head's selected epoch, coefficient, validation metrics, and producer reference before starting the next arm. |
| P2: prose promised automatic recovery and additional diagnostic caches | Readers could rely on unsupported artifact reuse, token/mask caches, geometry, or bank-member stability. | Repaired by narrowing the explicit delivery contract and deferring those extensions. |
| Prior native reproduction gate and native-head control requirements | Earlier review requested reproduction before fitting under the initial five-arm design. | Retired following the user's revised four-arm scope. Existing native predictions are reused directly; the plan describes comparison of complete candidate pipelines with the existing baseline. |

## Verification and limits

Independently executed in the local review environment: parsed all three Python deliverables; parsed the frozen JSON; verified its exact four-arm list; confirmed baseline rescoring/reproduction entrypoints are absent from the runner; confirmed the cheap archive check precedes preflight return. Source inspection covered the full stage DAG, artifact bindings, execution modes, error preservation, and changed contract text.

The implementation owner's mechanical test, Ruff, and Pyrefly receipts are recorded by the coordinating MOA reviewer. Those receipts are separate from this reviewer's independently executed checks. The toy head-fit/selection test exercises actual stage functions with small cached features and archived comparator scores independent of those features. It supplies offline coverage of selected-weight/prediction and common-cohort contracts.

No GPU experiment, benchmark head fit, baseline scoring, or benchmark test scoring was launched by this reviewer. Actual native materialization and environment execution, real tokenizer/EOD/ceiling coverage, measured memory/throughput, and frozen-encoder digest observations remain execution checks. Preflight explicitly states this scope. A candidate gain measures its complete corrected-head pipeline relative to the existing native comparator; the revised design contains no newly fitted native head that could isolate the contribution of head capacity.

## Final source rereview

The final delta was reviewed after formatting and the precision repair. `CorrectedHead.forward` explicitly disables an enclosing worker autocast context while retaining the cache/head tensor dtype, so the production float32 head contract and float64 gradient observers both remain supported. Four parameterized CPU-bfloat16 outer-context regressions cover all fitted arms, compare the forward values exactly, and check finite float32 weight gradients. The remaining final changes record archived prediction hashes, include the MSE point difference, qualify floating-point sigmoid endpoints, accept the released continuous rating range, and identify the reviewed execution branch. These changes introduce no open runtime/provenance blocker.

Independently rechecked the final receipt's seven source/document hashes against the actual files and parsed all four Python files in that manifest. Repeated the four-arm configuration, absent-baseline-entrypoint, and early-archive-identity checks. All passed. The six-file manifest above now matches `csts-tranche-5-verification.json` exactly.

The owner-runtime receipt reports 43 focused tests passed in 8.56 seconds, Ruff check/format passed for four files, Pyrefly basic checking passed with zero errors for the two production modules, 24 mathematical checks passed, and input/archive preflight passed with zero benchmark inference or fitting. The preflight archived validation-prediction SHA-256 is `f82e66b853940ac44b316fb1325e12c6d4d09b1ac7f86c67b76a7177611d6bd0`. This review accepts the final bounded delivery; execution observations remain excluded as stated above.
