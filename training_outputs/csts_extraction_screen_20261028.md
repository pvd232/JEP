# C-STS native adapter diagnostic: comparison uncalibrated

The screen retained 239 passage/condition inputs from 120 validation comparisons across 110 connected source groups in adjudicated C-STS revision 1.1. The native runs returned empty lists on 239/239 KnowCoder inputs and 236/239 GoLLIE inputs. The model-assisted acceptance counts below describe those retained outputs. The screen did not establish that its custom condition-to-relation mapping works on in-task positive controls, so comparative conclusions about the native models are suspended. The cause could involve schema mapping, prompt serialization or model capability; this screen does not separate them.

## Captured outputs

| Arm | Retained sources | First-pass structurally valid | Empty relation lists | Recorded arm wall time |
|---|---:|---:|---:|---:|
| GPT-6.1-sol/max propositions v2 | 239 | 238 | — | — |
| KnowCoder-7B-base, author wrapper v4 | 239 | 239 | 239 | 49.81 s |
| GoLLIE-7B, compatibility backend v3 | 239 | 239 | 236 | 41.33 s |
| Preserved KnowCoder original prompt v2 | 239 | 239 | 239 | 31.38 s |

The first three arms form the sealed 717-candidate review panel. The original KnowCoder prompt run is retained separately. Empty lists pass the native output grammar; their abstention correctness requires review. GoLLIE produced three nonempty outputs. These counts describe the specific checkpoint, condition schema and inference implementation tested here.

Native execution used an NVIDIA A100-SXM4-80GB on Colab, with Python 3.13.16, PyTorch 2.14.0, Transformers 5.20.2 and CUDA 13.0. GoLLIE used the pinned tensors with a stock Llama SDPA backend, restored its author's actual rotary base of 10,000, and checked all 291 parameter tensors. Kernel rounding can differ from the original FlashAttention implementation. KnowCoder v4 restored the author's system/Input/Output wrapper, tokenizer settings and stop handling. These amendments were declared before their generation runs; earlier captures were preserved.

## Refreshed direct GPT baseline

The same original 120 GPT-6.1-sol/max responses yield **Spearman 0.886365**, **MSE 0.477583 on the 1–5 scale**, and **MSE 0.029849 on the 0–1 scale**. This is a validation sample result.

The first parser accepted 116/120 direct captures. Four captures contained a known reconnect warning followed by one completed, tool-free turn and an agreeing final response. An independently reviewed parser amendment revalidated those retained responses without new model calls. It permits only two exact reconnect-warning forms, requires one thread, one turn and one final completion, and rejects failed turns, tool use, unknown errors, duplicate answers and response disagreement. Original numeric constraints remain in force.

The same amendment accepts the one proposition capture previously marked invalid, giving 239/239 in a separate sensitivity audit. The primary 717-candidate panel retains its original 238/239 proposition validity flags. All 3,600 original run files were verified byte-unchanged before and after derivation.

## Published-example pipeline checks

After the native screen showed near-universal abstention, one published relation-extraction illustration per system was fixed and sealed before generating its control output. These were post-screen pipeline-health checks.

GoLLIE reproduced all three reference relations in its author's example. KnowCoder returned four relations: two matched the three-relation reference, two were additional, and the reference's Population(Kurush, 813) relation was missing. The additional relations have not been semantically adjudicated and are not automatically hallucinations. These single-example checks are neither calibration nor benchmark F1.

## Descriptive review of the original captured outputs

These counts audit the failed/unvalidated native adapter outputs. They are not a validated comparison of native-model capability. See the subsequent in-task diagnostic before using them for a model-choice decision.

Acceptance requires structural validity and all seven semantic criteria in both separate review passes. Each arm retains all 239 sources, including the original GPT parser failure.

| Arm | Pass A | Pass B | Accepted in both | Fraction |
|---|---:|---:|---:|---:|
| GPT propositions | 222 | 224 | 219 | 91.63% |
| KnowCoder v4 | 22 | 21 | 21 | 8.79% |
| GoLLIE v3 | 23 | 22 | 22 | 9.21% |

All 21 accepted KnowCoder outputs are abstentions. GoLLIE's accepted outputs comprise 21 abstentions and one nonempty extraction. Its other two nonempty outputs fail the review. This distinguishes appropriate abstention from useful extraction coverage.

| Native minus GPT acceptance | Difference | Paired 95% interval |
|---|---:|---:|
| KnowCoder | −82.85 percentage points | [−89.03, −76.45] |
| GoLLIE | −82.43 percentage points | [−88.28, −75.51] |

Intervals use 2,000 paired bootstrap resamples of the 110 connected source groups. They describe sampling uncertainty conditional on these model-assisted judgments. They do not quantify shared judge bias, human disagreement or a model-family ranking.

The passes disagree on at least one criterion for 214/717 candidates, while their final acceptance decisions differ for 10/717 (eight GPT, one KnowCoder, one GoLLIE). Criterion-level discrepancies remain available for adjudication. Conjunction of the two passes is a conservative acceptance rule, not an expert consensus label.

One reviewer-B batch failed with a model-capacity error before producing any response. Its original 705-judgment view and 12 missing judgments are retained. One separately declared capacity-only attempt supplied those 12 judgments; no scored answer was retried or selected. Reverse-order workers accelerated unclaimed batches with an atomic directory claim, preserving exact prompts and preventing duplicate inference. A reviewed offline collector validated complete coverage and original raw proof; it made no model calls or semantic edits.

Reviewers receive source text, condition, sealed source-only reference and raw candidate output. Arm identities are hidden; output formats remain visible. Criteria cover faithfulness, completeness, condition scope, entity binding, multiplicity, abstention and inference. The proposition generator, source-reference generator and both reviewers use the same GPT-6.1-sol/max alias in separate contexts. Human adjudication has not been performed. Agreement between these passes therefore remains model-assisted evidence.

No Qwen training or full test evaluation was performed for this screen. Published NER, relation and event benchmark F1 values concern different tasks and evaluation rules; they are not scores for this condition-extraction screen. The matched GPT JSON/Python format arms remain unexecuted.

## Evidence and reproduction

The [execution receipt](csts_extraction_screen_20261028.json) records pinned checkpoint revisions, original protocol identities, hardware, archive SHA-256 values, the parser amendment and completed review fields. The [methods](../plans/csts-extraction-comparison-methods.md) specify the comparison and review rules. The reviewed implementation passed 69 focused tests.

Author sources: [KnowCoder inference wrapper](https://github.com/ICT-GoKnow/KnowCoder/blob/b7859789fc7641e03916074088859aa592332ad3/eval/src/inference.py), [KnowCoder example](https://github.com/ICT-GoKnow/KnowCoder/blob/b7859789fc7641e03916074088859aa592332ad3/Cases.md), and [GoLLIE example](https://github.com/hitz-zentroa/GoLLIE/blob/164c611743fdc1befe71bbdf03e08c5eb4e35957/notebooks/Relation%20Extraction.ipynb). The [complete evidence archive](csts_extraction_screen_artifacts_20261028.tar.gz), [review summary](csts_extraction_fidelity_20261028.json) and [offline reproduction instructions](csts_extraction_screen_reproduce_20261028.md) retain origin implementations, inputs, raw responses, references, controls, review attempts, amendments and file hashes.

## Decision

Do not train on these captured native outputs. Suspend the comparative native conclusion until a separately sealed target-compatible positive/negative control passes through the actual task adapter. The published-example checks establish functional decoding under familiar schemas; they do not validate the C-STS mapping. Preserve all original runs as diagnostics. Any repaired adapter needs a separate protocol and fresh evaluation.

The matched GPT JSON/Python arms remain the controlled test of code-shaped representation. This native-system screen changes weights, training and interface as well as output syntax, so it does not answer that representation question. Human adjudication and a downstream similarity comparison remain separate work.

## Calibration gap found in further review

The initial review concentrated on protocol identity, capture integrity, syntax, loading and author examples. It missed a task-adapter calibration requirement. All native tasks were converted into one anonymous `ConditionRelation(subject, value)`, including unary type recognition and aggregate counting. The class guideline also carried the long policy as a JSON-escaped single-line string, unlike the multiline class-specific guidelines in the published controls. These are concrete differences to test; none has been isolated as a unique root cause of abstention. Generic `Entity` arguments alone are not a proven bug: the author's KnowCoder example also uses them.

The separately sealed [in-task diagnostic](csts_native_adapter_diagnostic_20261028.md) has now completed. With unchanged GoLLIE weights and decoding, the original and formatting-only variants recovered none of six literal positives; the descriptive task schema recovered four. Both negatives remained empty. KnowCoder remained empty in all variants. This demonstrates an adapter effect for selected GoLLIE cases and leaves KnowCoder unresolved. It is an integration diagnostic rather than a representative model benchmark.
