# Tranche 6 — independent MOA review

**Final verdict: Approve the reviewed bounded experiment for execution.** No unresolved P0–P2 source, mathematical, or experimental-design finding remains. The source files match the passed final validation receipt. This review records zero new attention-model benchmark inference or fitting; those are the prospective experiment.

## Method and snapshot

The review follows the user's Multi-Agent Orchestration workflow and code-review skill already identified in the [Tranche 5 review](csts-tranche-5-review.md). Two independent agents reviewed separate boundaries: `/root/moa_review` reviewed the complete core, mathematical/experimental contract, tests, and relevant controller operations; `/root/moa_review/runtime_review` reviewed the complete native controller, runtime/provenance contracts, queue behavior, and relevant core/helper operations. Their outputs are separate. The exact model identifier is not exposed by the collaboration interface; both agents inherited the session configuration. This is an actual multi-agent workflow, with no claim of a separate installed MOA executable or multi-model panel.

| File | SHA-256 |
|---|---|
| `csts_pilot/evidence_attention.py` | `9c3fa6288d7e2a725a9647f0577651f8bff15ab59d843be67515ec67c096d349` |
| `csts_pilot/evidence_attention_run.py` | `178904501da47710602ceb43095fddc5146f21933078bba15d2ba7fbb359f7a8` |
| `tests/test_csts_evidence_attention.py` | `95afd5192cd2ad805935ca79c6fa2e0539e094beea1cc66c33f71d4e0a3d01aa` |
| `configs/csts-evidence-attention.json` | `d7230f45dd6dcc26d2f70ff8a420cb4894ab5bd3717400141149a5d16bb68ca5` |
| `plans/csts-tranche-6-evidence-attention.md` | `abd0e7ce51905d6dd32b8ce2a80340bc0deff14579c772b87f168a27e36f73af` |

All five hashes were independently recomputed against [the final implementation receipt](csts-tranche-6-verification.json). Relevant existing source helpers include prompt/token/EOD construction, teacher-cache validation, common fitting-row exclusion, early stopping, archived-prediction identity checks, rating metrics, recall cutoffs, paired group bootstrap, and native artifact/publication interfaces. The [independent runtime report](csts-tranche-6-runtime-review.md) records its operational review.

## Exact experiment reviewed

This follow-up trains two copies of the same small attention architecture on cached states from the selected frozen ratings-only Qwen + LoRA parent. One minimizes rating MSE; the other adds the predeclared coefficient **0.1** times span cross-entropy. The encoder and adapters receive zero updates. No native baseline is rescored or refitted. Seed 7, fitting rows, head initialization, comparison permutations, dropout policy, optimizer settings, and checkpoint rule are shared.

A query comes from the mean of condition-prefix token states. Nonaffine LayerNorm with epsilon 1e-5 precedes the bias-free query/key maps. Their scaled dot product produces passage-only attention weights. The weighted raw passage states then pass through the bias-free output projection, LeakyReLU 0.01, dropout 0.15, and unit normalization. Prefix/separator/special/EOD/padding positions receive no pooling weight. All head calculations preserve float32 under an enclosing worker autocast context; double heads retain float64 for gradient observers.

Condition-prefix positions precede the passage in the causal model. Earlier passage positions contain their causal prefixes; the original pretrained retrieval readout was the final EOD state. The plan expressly treats the utility of this new aggregation as an experimental question. This is a newly defined architecture inspired by evidence localization, and its source description preserves IPED's actual candidate/block-query and evidence-feature roles.

The teacher cache is fixed by SHA-256. The target mapper requires one unique exact literal occurrence of an accepted answer. Its distribution is uniform over positive-overlap passage-token positions. Repeated, canonical-only, absent, or empty alignments abstain from evidence supervision and remain in the rating cohort. Teacher targets are training-only; validation/test caches reject teacher bindings and contain zero target mass. The accepted cache remains teacher-checked evidence, without an independent expert-validation claim.

## Mathematical findings and observers

The rating objective averages over the actual comparison batch. Span CE averages over aligned passage occurrences, each with unit target mass. A batch with no targets receives a differentiable finite zero span term. Masked log probabilities are set to zero before their target product, preventing zero-times-negative-infinity NaNs. CE directly supervises query/key weights; the rating objective also trains the output projection. Both objectives differentiate through the pooling probabilities used for cosine prediction.

The epoch's `training_objective` is the comparison-count-weighted mean of the batch objectives. Its reported `span_cross_entropy` separately weights accepted passage occurrences. This distinction matters when the accepted-evidence count differs across batches. The implementation and plan agree on the optimization objective.

The coordinator independently checked the complete small attention system with NumPy float64, fixed inverted-dropout masks, unequal passage lengths, and one unlabelled passage. Central finite differences checked every query/key/output matrix coordinate under span weights 0 and 0.1. Softmax Jacobian and nonaffine LayerNorm observers supplemented those checks. **Eight checks passed**, with maximum error **1.724151377224814e-10**, below tolerance **1e-7**. The [independent receipt](csts-evidence-attention-moa-math-checks.json) records the checks. These formulas were evaluated independently of the production implementation.

The production tests inspect exact prompt IDs and local offsets, Unicode/literal whitespace, ambiguity abstention, passage masks, masked CE and no-label batches, actual query/key/value gradient paths, a finite-difference condition derivative, outer-autocast parity, semantic cache joins, teacher lineage, held-out target prohibition, and restored prediction identities. Two actual tiny CPU fits retain unlabelled rating rows and demonstrate matched initialization/order/cohort and the combined objective. They then reload selected weights and call the actual native selection stage, preserving deliberately independent archived native scores.

## Findings and disposition

| Priority | Concrete concern | Resolution |
|---|---|---|
| P1 | An independently launched follow-up could overlap the active Tranche 5 GPU worker. | The controller takes the same original-workspace GPU flock used by the active job, then requires a terminal predecessor before stage execution. The runtime reviewer inspected the real existing lock ownership. |
| P1 | A queued controller could execute a changed source/configuration after waiting for the GPU. | The queue records committed source and settings hashes; after acquiring the shared lock it checks them again and rejects tracked source changes. |
| P2 | A cache with the right shapes/model/cohort could omit the teacher provenance or alias passage occurrences. | Training caches require the pinned teacher SHA; held-out caches require no teacher binding. Exact two-occurrence-per-row coverage, semantic joins, and full occurrence coverage are validated. Counterexamples are tested. |
| P2 | Canonical substring acceptance cannot identify which repeated literal span the teacher intended. | Only a unique literal match produces targets. Other accepted answers abstain with recorded coverage loss while preserving every rating row. |
| P2 | The initial architectural prose omitted the implemented normalization/activation, and described IPED query roles imprecisely. | The final plan defines nonaffine LayerNorm, output activation/dropout, and causal state limits, and correctly distinguishes the new readout from IPED's published module. |
| P2 | Training CE could be presented as evidence of held-out grounding. | The supplied plan makes no held-out span-quality claim. Held-out teacher targets remain prohibited. Any later grounding diagnostic needs a separately defined post-selection analysis. |

No finding is being waived because tests pass. Invalid masks, cache lineage, selected predictions, or vector directions fail explicitly; no comparison rows are dropped.

## Validation and overnight decision

The final owner-runtime gate used `/home/machina/jep-format-env/bin/python`:

- **37 tests passed in 10.05 seconds**.
- Ruff checks/formatting passed for the three Python files.
- Pyrefly basic checks returned **zero errors in the two production modules**.
- Preflight verified configured cohorts, parent, teacher cache, and archived native identity with **no attention inference or training**.
- The plan's **62 math expressions** parsed without errors and use no single-dollar delimiters.

Selection uses validation only: at least +0.005 Spearman over the archived native comparator, condition-ordering decline at most 0.01, and FPR increase at most 0.01 at the validation-derived recall cutoff. An ineligible result stops before candidate test extraction. Test thresholds remain frozen; transfer additionally guards recall. Existing-test outcomes do not choose the evidence coefficient or architecture. The difference between the two validation heads is reported even when neither qualifies. A gain over native from the evidence head alone does not isolate evidence supervision's contribution; the matched rating head supplies that comparison.

The controller directly reuses the predecessor's sealed deterministic bank and verifies contents/SHA, so both tranches retain the same fitting cohort. It permits at most 4,800 GPU seconds for training/validation extraction, 1,800 aggregate head-fitting seconds, and 600 GPU seconds for conditional test extraction: **120 GPU minutes total**, with **30 CPU analysis minutes**. Every GPU stage is additionally bounded by **2026-10-26 12:30 UTC**. Explicit execution, exclusive attempt preservation, canonical native EVAL inputs, independent metric-worker dependencies, progress broadcasts, and asynchronous publication follow the reviewed native contracts. Automatic recovery remains outside this runner.

The archived LLM result has separately been verified as **0.8029168452132416 test Spearman** on the same 2,620 rows/1,241 groups; [the provenance receipt](csts-llm-comparator-provenance.md) binds its exact source artifacts. It supplies descriptive test context and no validation target. A later candidate-minus-LLM paired analysis can use the frozen saved predictions without changing selection or running a baseline.

Real token extraction, measured resource use, full native stage materialization, benchmark attention fitting, selected test scoring, and durable publication remain runtime observations. This approval authorizes the bounded, prospectively specified screen under the user's overnight instruction; it asserts no successful experimental outcome.
