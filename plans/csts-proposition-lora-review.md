# Reconciled proposition experiment review

Independent verdict: **Approve this bounded experiment implementation for a draft PR.** The PR comparison base is `6cfe87628f6b8c5a2608be33fe5ffb54ce581721`; reconciliation preserves the actual implementation from immutable active snapshot `3c288dee32ff0e4f684406d78d7e92ed99161f64` and repairs it at the exact final file identities below. The earlier alternate runner at `8356c6b` is preserved in Git history and superseded; its duplicate inventory/runner/configuration is absent from this branch.

This review includes the complete active experiment addition, its callers and persisted inputs, and the final repairs. It is not an approval of the obsolete alternate handoff or an inference from tests alone. No remaining blocking finding was reported in the final reviewed scope. This record is supplementary review prose added after the source freeze; it changes no tested implementation, configuration, fixture or handoff bytes.

## Review ownership and boundary

- `review_proposition` independently inspected the actual canonical inventory/preparation, quality gate, raw provenance helper, capture/continuation bridge, direct source guards and their tests. It approved the final core after rereading repairs and independently running 76 tests plus 14 subtests.
- `runtime_validation` independently inspected the actual native LoRA initialization/serialization and validation controller contracts. It authored the additional real-`fit_neural` CPU regression; root independently reviewed that test and reran it. The test file's final hash is recorded below.
- `review_multiple` independently inspected dispatcher/worker source roles, native deploy/check/import/launch operations, supervisor lifetime, workspace ownership and resource locks. It approved the final operational repairs after 26 focused tests and exact hash checks.
- The `latest_test_gate` reviewer independently inspected the test/archive/sample slice and approved the retained canonical EVAL consumer plus explicit deferral. The canonical EVAL repair was authored by `iterative_codebook`, with 17 focused tests; public preparation/execution entrypoints reject access until a separately reviewed producer/protocol exists.
- Root independently reviewed the final repairs, integration boundaries, runtime-authored checkpoint fixture and handoff document. Root ran the full affected suite, all scoped Python lint and implementation type checks after source freeze.

The inspected ownership boundaries include native `TokenPairs`/`fit_neural`, standard `FitConfig` checkpoint loading, original-row prediction restoration, saved comparator artifacts, source-group partitioning, capture CLI receipts/events and existing asynchronous publication. Inherited status and audit data are preserved as historical active-pipeline evidence; they are not measurements produced by this review session.

## Findings and repairs

| Finding | Final repair and focused observer |
| --- | --- |
| Concurrent resume could start another paid request while an earlier CLI still owned it | Exclusive partition and batch locks; both are inherited by CLI children. Live and inherited-owner observers prevent duplicate requests. Interrupted recovery is explicit after owners release their locks. |
| Operator code pin and target workspace pin were conflated | Worker validates an explicit target-source role separately from immutable operator-code bytes; dispatcher accepts only allowlisted phases/modules and verified Git blobs. The historical formatting-export action retains its separate reviewed target. |
| Latest operator source was a one-off formatting exporter rather than a reusable phase entrypoint | Keep formatting export as an explicit named phase and dispatch the existing capture/native modules through a bounded parser. No active branch or running operator was changed. |
| Native preparation trusted a passing boolean and self-declared manifest | Pin exact gate bytes and all 24 supporting audit files; recompute 60 judgment identities, faithful counts and zero severe unsupported assertions. Fabricated gates and modified evidence fail. |
| Raw request/response/usage evidence was not required by native preparation | Transport `propositions_tranche8_provenance.json`; replay source-only inventory, batch schema/prompts, original command paths, source hashes, raw responses/events/usage and checked records after relocation. Missing, tampered, foreign-source and mislabeled partition evidence fails. |
| Capture locking repairs would invalidate or silently rebind an existing frozen generation source | Preserve the original audited `launch.json`; fetch the exact standalone verifier/dependencies from the target commit and record executing operational capture/verifier identities separately. Frozen prompt/schema/model/effort and original audit source remain fixed. |
| Mutable source declarations or dirty source could bypass the reviewed cohort/commit | Validate fixed original source hashes before reading preparation inputs. Direct and operational guards reject tracked and untracked changes, including an untracked import-shadow module; ignored runtime artifacts remain allowed. |
| Deployment or formatting could rewrite modules under a live native child | Exclusive mutation lease versus shared execution leases, held through the supervised child lifetime and inherited across child process boundaries. Direct operational GPU work uses the existing shared resource owner. Held-lease/source/GPU observers prevent unsafe launch or source mutation. |
| Completed LoRA fitting was falsely rejected after JSON serialization | Compare the loaded trace with `fit.model_dump(mode="json")`; saved inference checkpoints remain ordinary `FitConfig`. The actual native training-loop fixture completes and replays its selected saved checkpoint. |
| Existing Mac cache fixture used an alias path rejected by the physical-path guard | Resolve the temporary test roots; the production nonsymlink/deletion guard is unchanged. Hash, hardlink, symlink and unpublished-cache observers remain fail-closed. |
| Test consumer used noncanonical native scoring and no reviewed capture producer existed | Retain a canonical native EVAL consumer and recomputed artifact metrics. Remove generic test capture and make public test preparation/execution fail before input access. Benchmark workflow is explicitly deferred rather than claiming a complete producer. |

The actual canonical `answer_id`, first raw representative and alias audit remain unchanged. Literal evidence is checked against that representative; semantic answers are reused across its canonical aliases. Full training/validation rows, labels, source groups, conditions and original identities are retained. Abstaining sides retain their own original source text; no common unknown embedding is introduced.

Only training answer inputs reach the rating-MSE optimizer. Epoch zero and checkpoint selection use validation. The fixed selected Qwen adapter is restored as weights only, with fresh optimizer/RNG state at epoch zero. Native best/terminal checkpoints, optimizer/scheduler/dataloader resume state, transformed input hashes and traces remain the existing artifacts. The original saved Qwen predictions remain the unchanged comparator; no original-passage baseline rerun or new native control head is introduced. Existing achieved-recall cutoff tolerance and validation eligibility guards remain in force.

## Mechanical evidence

`PY` is the task-owned interpreter at `work/csts-codebook-test-env-20261026/bin/python` under the shared workspace.

Root's final affected command:

```sh
PY -m pytest -q tests/test_csts_proposition*.py tests/test_csts_tranche8_worker.py tests/test_tranche8*.py tests/test_csts_baselines.py tests/test_csts_answer_input.py tests/test_csts_early_stopping.py
```

Result: **158 tests passed, 14 subtests passed** in 6.79 seconds.

The independently repeated core command covers `test_csts_proposition_inputs.py`, `test_csts_proposition_provenance.py`, `test_csts_proposition_lora.py`, `test_tranche8_continue.py`, `test_csts_proposition_capture.py`, `test_csts_proposition_sample.py` and `test_csts_proposition_archive.py`: **76 passed, 14 subtests passed**. Operational and canonical-EVAL slices separately passed **26** and **17** tests respectively. Root independently reran the newly authored actual-trainer regression: **1 passed**.

Root ran `ruff check` over all **26 changed Python files** in the full comparison scope: passed. Pyrefly with `--preset default --python-interpreter-path "$PY" --ignore-missing-imports='*'` over all **14 changed implementation modules** reported **0 errors**, with one nonblocking annotation deprecation warning at `proposition_capture.py:257`: `@contextmanager` currently annotates `Iterator[int]`; the checker prefers `Generator[int]`. The default check exits successfully; requesting warning diagnostics separately reports that warning with a diagnostic exit status. No runtime defect was found in that annotation. `git diff --check` passed. Formatting/compile checks were repeated for their affected slices.

The actual training fixture runs `fit_neural` with a tiny CPU scorer, observes initially empty AdamW state and no old state restoration, distinguishes the selected checkpoint from terminal weights, loads the standard checkpoint and native resume state, replays selected predictions/metrics, verifies optimizer/scheduler/dataloader counters and preserves the parent bytes. Native authoring fixtures validate the canonical plan/output/environment and EVAL metric dependencies without starting workers or loading the real model.

## Exact final file identities

This manifest covers every existing final file added or changed relative to the pre-experiment comparison base, including inherited active-source additions and historical status/audit evidence. The supplementary record itself is excluded from its own manifest. Root must preserve these bytes when committing the reviewed candidate.

| File | SHA-256 |
| --- | --- |
| `csts_pilot/proposition_archive.py` | `9a230bcf535dabc3d0df3c105eb9541129217ce5afe56382dbed85e137dd1ee6` |
| `csts_pilot/proposition_capture.py` | `84e66e626bb72a6e5a6646e90ed4f19f76ff30daca95f3810432724187611c1b` |
| `csts_pilot/proposition_inputs.py` | `5fdea65ce8852e084584911150584ca2c5bc7062c80994c9ccf7f09aba260522` |
| `csts_pilot/proposition_lora.py` | `31a3aa21e4426735b63d904eae6cf8a519fa318907530f69079aef2a6c723d9c` |
| `csts_pilot/proposition_provenance.py` | `a2a1e81560acad80909fbba5ccc18a09ce34e46b5b96c847b1dc5076005251ee` |
| `csts_pilot/proposition_run.py` | `f012d46892badfd69a718c91ef2e4d231f16dc55c217c4cd84c3400bde73b550` |
| `csts_pilot/proposition_sample.py` | `7093d7ae77a5267f8d9ee5e2145e62222dc585a10db1392f59fd30643607c803` |
| `csts_pilot/proposition_test.py` | `0f0a1f70c01153af29fb2088ef7e8bc8ceefbdec4b6d5b508e42a5779444bc97` |
| `plans/csts-proposition-lora-handoff.md` | `2b29fc88c7e224ebbfacf2b072d6944a484bba9ef907ef0ea9622cdb6a05bb0f` |
| `scripts/tranche8_continue.py` | `bbbe5c46504505834f0c5ac5592b8e22dfbfe614b1cdde146d440a3e7d9cf736` |
| `scripts/tranche8_formatted_sources.py` | `c896d820b4c2e83c5c3269faa80a23f0ab0f8e84ece02b448b80b6de61585329` |
| `scripts/tranche8_native.py` | `b9f46e101c20842e7e4d6e31b3376e9d60025528b3f2bc32644c16c9812276c7` |
| `scripts/tranche8_native_supervisor.py` | `c46a9bd6478ad2ef43520a518a9cf3676d9ffcc6f7bb069d9b5f3efc1176f338` |
| `scripts/tranche8_operator.py` | `d9e7d60cbe855b0c749c70e42a36da5b47398d6d6bc24b831ce2542fe4890a2f` |
| `scripts/tranche8_worker.py` | `cf1ae9ab3b920c5f6c93a08dff8812b2301be5ddc61d2c132fe4e73d16297f89` |
| `tests/test_csts_proposition_archive.py` | `a1d37cf207532600414053396c9bbd729eaafe9121d575a930bd004e2ad7797d` |
| `tests/test_csts_proposition_capture.py` | `0a47035f247aa48e9351e0b33980d02f9e1aa1abca0f6fa1ae35500f4b356ff5` |
| `tests/test_csts_proposition_inputs.py` | `284151ce9726ece5e82c354f98d9620377ebb530e45b8f0b65b4f41e021cf393` |
| `tests/test_csts_proposition_lora.py` | `eba033b4d7114d61028a39ac193080bd0e7c81053a233726161fdc56b065cf8c` |
| `tests/test_csts_proposition_provenance.py` | `393048dedf3696c469b6ab566721f7aa7d905156632197c27d922c7cc7852448` |
| `tests/test_csts_proposition_sample.py` | `0e491168a72f445faaa7b1f8b6866ea85c296ee17fcc549d3a554a1cbcf125f1` |
| `tests/test_csts_proposition_test.py` | `9f1a4da39b4b70a900fb378169f2a899a5836e00e743043ac7895e6075bf115b` |
| `tests/test_csts_tranche8_worker.py` | `ec9155de2ee49ac22797be650eea2534e76d50db136a1c91d60f90615479e025` |
| `tests/test_tranche8_continue.py` | `3dfb10cc90f48e7494ced61270217aaae8e6cd17595de195ad469de6f4e6ff02` |
| `tests/test_tranche8_native.py` | `d23e6a8e4e1bb3c94c6b4fd5806b89fa0e6c58c76f1d90a72c84d8ba94246cd9` |
| `tests/test_tranche8_native_supervisor.py` | `8c0ad25d1e073621f352d8af75697eb65be0ce8ac773e882b071c9e56cc6aefa` |
| `tests/test_tranche8_operator.py` | `4da759dbba4192dbfeca44094943550eec39c97a965057a5b1a3f08fa9c0e1a8` |
| `training_outputs/csts_tranche8_control.json` | `02333bc4a09793c8ad54427c1ceab57dd91cee6329486a1bc5c82f47549122e1` |
| `training_outputs/csts_tranche8_operator_status.json` | `bf661afee3a54d0dfa125f8c40b0243dd9590323f090465d31942aeb1a7678fa` |
| `training_outputs/csts_tranche8_status.md` | `45f09261ce5bb172b0dcb0c0efc085829565b1bd1c48bf2755142ff5b7e56c24` |
| `training_outputs/proposition_audit/known_regressions_groups.json` | `da92271d6ccedc97a29b30a552bbb639e7e0e4f60320b5bd3528203e237683d7` |
| `training_outputs/proposition_audit/known_regressions_source_only.json` | `67c01ff51e605d957321de650f294b61b32048567cd717bc5dbd3dbca0afe3f7` |

## Exclusions and remaining gates

No new corpus generation, real Qwen tokenizer/backbone load, native worker or GPU research execution, benchmark input access/evaluation, paid resource launch or cloud promotion was performed by this review work. Tiny CPU fixture updates are verification, not experiment measurements. Inherited live status records describe the independent active pipeline.

Full-corpus semantic fidelity remains bounded by the model-assisted development screen rather than expert verification. Real complete-bank bindings, token ceilings, GPU runtime behavior, fitting outcomes and asynchronous promotion remain launch-time gates. No active capture branch, live workspace, running request or deployed pipeline was modified by reconciliation.

**Benchmark test capture/import/execution remains deferred.** A separately reviewed producer/release protocol and frozen eligible validation candidate are required. Generic test generation is rejected, and public test preparation/execution fails before opening inputs. The retained canonical EVAL consumer is not a claim that this missing release workflow has been implemented or authorized.

The final verdict approves the reviewable source and its bounded training/validation handoff. It does not authorize merging, deployment, execution or benchmark access.
