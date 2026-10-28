# Native extraction repair: exposed development progression

The checked native backends run, and the task-aware schemas recover useful evidence. Neither parsing nor a nonempty annotation list establishes complete evidence. All examples below were selected from exposed development material. They are debugging evidence, not representative accuracy estimates or model rankings.

The original generic-adapter captures, ordinary zero-shot captures and each subsequent candidate remain separate. Changes to task definitions and examples are experimental changes, not parser corrections. There is no GPT fallback, automatic role swap, inferred missing fact or successful-prefix salvage.

## Fixed family demonstration

The first candidate added one independent synthetic example for each native NER, RE and EE family, fixed across the same nine sources. It helped color extraction but did not resolve spatial qualifiers or events. KnowCoder lost the previously recovered elephant annotation. GoLLIE still omitted food. The mixed result does not support a general few-shot improvement claim.

## Condition-aware spatial and action contracts

The next candidate retained working zero-shot NER and one-example color extraction. It gave GoLLIE Food an explicit category definition and independent same-class example. Spatial constructors express the qualifier on the edge, such as `Near(subject, reference)`, rather than asking a generic location relation to preserve it implicitly. Actions use a separately declared `ActionDescription(actor, verbal_clause)` contract. This is coarse clause evidence, not resolved event roles.

GoLLIE produced nonempty source-grounded annotations on all nine sources, including sandwich/pickle, `Near(boy, water)` and the dog's full fetching clause. KnowCoder recovered four entity targets and both colors, but returned an empty spatial list and shortened the dog's clause to `fetches`. Both models returned `throws leaves over her head` for the girl and omitted `in front of a fence`; neither output establishes full clause/context coverage. Thus nine nonempty GoLLIE outputs are not nine complete semantic passes. All eighteen generations reached EOS without truncation.

The later spatial parser amendment accepts fronted cues that fall outside the two entity spans, while retaining the actual cue positions and an unvalidated-association flag. It neither generates nor repairs a relation. It leaves the eighteen generation prompts unchanged; it is distinct from the model-side task adaptation.

## Final Know-only refinement and regression

The final fixed KnowCoder candidate adds an independent illustration for every spatial predicate and a second action example contrasting a bare verb with the complete object/origin/setting phrase. Its spatial request explicitly uses a 4,096-token context: 2,511 input tokens plus 512 reserved output tokens. Other Know requests retain the 2,048 bound. GoLLIE's prompts are unchanged and its nine development captures were not regenerated.

The single nine-case run fixes `Near(boy, water)` and retains the four entity and two color outputs. It still returns only `fetches` for the dog and regresses the girl's previously recovered throwing phrase to `[]`. All nine outputs parse without truncation. The [independent delta audit](csts_know_refinement_v1_independent_review_20261028.md) verifies all indexed capture bytes and confirms that the six NER/color prompt and input/output token vectors are unchanged. This is a mixed development result, not a complete repair of action extraction. The regression is retained; there is no per-source rollback, answer selection or further exposed prompt iteration. The frozen diagnostic uses this exact final configuration.

The integrated package matches all sixteen reviewed runtime files, and 177 combined tests pass. The [integration receipt](csts_native_adapter_integration_final_20261028.json) distinguishes source hashes, earlier versions and documentation. These software checks do not establish model quality.

## Symbolic count failures

The first finite count experiment used independent mention/quantity, quantity-binding and identity stages on six exposed sources. All thirty-six calls parsed, but every binding and identity stage was empty. Extracting a number word without its binding does not deliver a count.

A separately frozen guided candidate supplied only its own validated stage-one candidates to the later stages. It improved some bindings but remained unsafe. KnowCoder linked a jersey's number five to the greyhound and produced a false lower bound of five. GoLLIE's same incorrect link conflicted with a singular article and remained unknown. Both included an untyped baby in a woman group. All twelve identity-stage outputs were empty, and each model had one rejected stage. These outputs remain failures; the arithmetic layer cannot certify the upstream semantics. General symbolic count generation remains disabled.

## Separate quote-only count evidence

A further comparator requested literal `CountEvidence` quotes without quantity interpretation, identity decisions, presence assertions or aggregation. It used its own parser and protocol and did not replace failed symbolic count results.

KnowCoder's six outputs parsed and matched source text, but it omitted the unspecified children, selected jersey-number wording instead of the greyhound mention, and included an untyped baby for the women question. Both models split the three-people/man assertion into noun phrases that lose the relational cue needed to interpret distinctness. GoLLIE also included the baby and truncated the greyhound response after repeating task text to its output cap. Its entire truncated result is rejected; the initial apparently useful quote is not salvaged.

This comparator fails evidence sufficiency. Exact quotation is a mechanical property, not a relevance or completeness judgment. Its fourteen separately frozen contrast controls remain unrun. No count, referent-resolution or downstream readout success is claimed.

## Frozen 48-case primary diagnostic

Both original attempts completed with all 48 cases retained per model. Each produced 31 actual model responses, ten explicit unsupported-route records and seven zero-call harness errors. All 62 actual responses reached EOS without truncation. The [independent operational audit](csts_native_positive_diagnostic48_operational_audit_20261028.md) verifies the source/request/capture hashes and token/text replay. These operational counts are not semantic acceptance counts.

The seven errors per model are intentional empty-input negative controls. The harness accepted string inputs at its public boundary, while its renderer and normalizer rejected empty strings. This contract mismatch blocked generation; it is a harness defect, not evidence of model weakness. Original Know error records also carry a cached error-context field from the preceding source. They still record zero calls, no bound request and no model output; that stale field is not a response to the empty input. The new producer clears this context per source and retains it only after a current-source call.

The separately reviewed mechanical repair changes only the two core passage-type guards, accepting empty/whitespace strings while retaining nonstring and invented-span rejection. Nonempty prompts remain identical. The original 96-case primary captures and their two-pass review remain immutable. A bounded recovery makes the first neural call on each of the seven previously blocked cases per model; it has a separate origin and cannot silently replace the primary failures. No completed nonempty prediction is regenerated.

Both semantic passes are complete: the original pipelines receive joint acceptance on 12/48 GoLLIE cases and 9/48 KnowCoder cases. The [final results](csts_native_final_results_20261028.md) separate these primary scores from the later mechanical recovery. All fourteen first generations on the repaired empty-input controls return literal empty lists and pass token/normalization replay; no original prediction is replaced.

The [original diagnostic archive index](csts_native_positive_diagnostic48_archives_20261028.json) binds both captures and the exact provider, protocol and inference-only job. The [public capture/replay instructions](../docs/native_positive_repair.md) and [readable frozen source](../experiments/native_positive_diagnostic48_v1/README.md) expose the experiment implementation. The suite is a designed control set, so its results do not estimate population accuracy or establish a model ranking. Fresh candidate evaluation remains blocked.

The [archive index](csts_native_development_archives_20261028.json) identifies immutable captures and zero-generation setup evidence by SHA-256. The [independent review](csts_native_development_independent_review_20261028.md) checks the ten execution archives: 274 capture/execution hash declarations, 90 explicit indexed byte lengths and 120 generations, including the rejected quote-arm truncation. These integrity counts are not semantic-pass counts. Raw generations, actual prompts, token vectors, runtime identities and original result records are retained. Model-assisted/source judgments remain separate from human adjudication. No downstream training or full-test result follows from these development checks.

Reproduce the read-only CPU audit from the repository root; it makes no model calls and writes a new temporary report directory:

```sh
python3 tools/audit_csts_native_development_20261028.py --archive-dir training_outputs --include-count-evidence
```
