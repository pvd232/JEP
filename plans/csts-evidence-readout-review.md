# Revised evidence-readout implementation review

Review scope: author self-review of the new full-width readout, symmetric comparator, writing-retention audit, native stages/controller, fixtures, pinned configuration, interventions and methods. This is not an independent external review, and it does not establish scientific efficacy.

## Design changes prompted by the full-bank results

Use the final full-bank proposition checkpoint rather than the earlier ratings parent and all 11,909 captured training identities rather than the 2,496-input pilot. Replace the three-arm proposal with B/C readouts followed by frozen-readout D/E comparison fitting. Recompute both final parent references on C-STS version 1.1. Audit writing before/after the final ratings phase using the same 121 existing writing-validation references and fixed 32-generation sample.

The methods distinguish the exact cosine contrast C−B, the fixed-representation comparison contrasts D−B/E−C, and E−D's inclusion of separately fitted comparison weights. The new comparator starts at cosine and preserves all 4,096 coordinates. This is a limited symmetric coordinate comparator, not a test of all possible semantic comparison functions.

## Correctness review and resolved findings

| Finding | Resolution |
|---|---|
| Updating readouts while fitting D/E would confound the comparison question | Select B/C first, clear old gradients, freeze parameters, detach vectors and verify unchanged readout hashes/no new gradients after comparison fitting. |
| A fresh randomly initialized comparator could destroy a useful score before training | Zero-initialize a symmetric residual so epoch zero equals cosine exactly; retain epoch zero for validation selection. |
| A learned comparison could introduce order-dependent sentence scoring | Use only absolute coordinate differences and coordinate products, alongside cosine; verify swap invariance before and after an optimizer update. |
| Historical breakthrough scores used 2,430 test rows while the approved revision has 2,431 | Re-extract A/R on current pinned inputs and keep historical scores as motivation only. |
| Earlier partial-capture fidelity could be mistaken for final-model factual accuracy | Add pre/post retention CE and deterministic generated probes. Explicitly distinguish exact reference agreement from factual correctness and existing validation from fresh evaluation. |
| Legacy parameter restoration only operates on parameters marked trainable | Temporarily identify the saved LoRA parameters for restoration, then disable all gradients before retention inference; compare adapter bytes before/after. |
| Missing teacher records or ambiguous quotations could become false negatives | Bind canonical training identities; apply evidence loss only to aligned answered or explicit not-specified records, with all rating rows retained. |
| Null softmax near one can cause unstable content normalization | Pool with a separate source-only softmax. Null never gates scoring or row inclusion. |
| Null-only evidence gradients could distort the shared-gradient diagnostic | Measure loss alignment on query/key weights only; diagnostic gradients do not enter optimizer updates. |
| Multiple native cache/model inputs could share a materialization path | Use a unique stored-source binding per cache and seed model. |
| Native EVAL requires stored canonical test/split inputs, an eval ID and objective | Publish test and holdout first, bind canonical model/test plus stored holdout, and declare a stateless C−B report metric with explicit artifact dependency. |
| Native validation metrics may describe terminal rather than selected weights | Replay selected four-cell predictions and publish an explicit final reporting step after both fitting phases. |
| Colour and appearance could be counted as separate corroborating signals | Export family membership IDs and describe overlap explicitly. Same-pair diagnostics group by exact unordered sentence text rather than broad source group. |
| Repeated or uncertain attempts could silently rerun a favorable subset | Preserve native records, selected/terminal states and failures; reject automatic replay of ambiguous attempts and source/input substitutions. |

## Verification

| Check | Result |
|---|---|
| New readout/comparator/retention tests plus inherited attention and preparation suites | 62 tests passed; 10 subtests passed |
| Ruff lint and formatting, all six new Python files | Passed |
| Pyrefly with the actual Python 3.13 environment, four production modules and native driver | Zero errors |
| Pinned full-bank/checkpoint/tokenizer preflight | Passed: all 11,909 canonical records; all three checkpoints rank 32, width 4,096, 288 adapter tensors |
| Literal quotation alignment before backbone inference | 12,102 sentence occurrences: 11,267 answered, 806 explicit null, 28 ambiguous-status skips and one repeated-quotation skip; no rating rows removed |
| Native CPU transport, complete three-seed four-cell fitting and final EVAL | Running; final receipt will be recorded here |

Numerical checks cover differentiable readout gradients and exact padding exclusion; finite source normalization at near-unit null probability; teacher-status and quotation handling; selected-checkpoint replay and independent snapshots; identical trajectories when evidence targets are absent; comparator symmetry and exact cosine initialization; fixed readout hashes through comparator fitting; all five paired bootstrap contrasts and overlapping family membership; exact-pair condition diagnostics with half-credit ties; and restoring two adapters while freezing every parameter. Queue fixtures reject source changes and wait for an occupied GPU lease without starting computation.

The CPU native fixture uses random 5D states and does not load Qwen or use the GPU. The preflight loads tokenizer/checkpoint metadata and verifies source alignment, but does not run the backbone. These checks are implementation evidence, not empirical support for the working hypothesis.

## Limits and execution status

Three head seeds condition on one backbone seed and one teacher policy. The benchmark has already informed project decisions. Bootstrap intervals omit selection and project-wide search uncertainty. Attention agreement is not causal faithfulness, null probability is uncalibrated/length-sensitive, family subsets overlap, and six synthetic cases do not establish generality. The same validation set is used in two fitting phases. The restricted comparator cannot rule out richer cross-coordinate or token-level comparison on a negative result.

No revised scientific training, real-Qwen retention audit or GPU inference has run for this PR. CPU fixtures do not answer the scientific questions. The L4 queue implementation is included for the reviewed source; this PR leaves scientific execution unstarted so the complete design can be reviewed.
