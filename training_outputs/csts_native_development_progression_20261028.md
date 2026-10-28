# Native extraction repair: exposed development progression

The checked native backends run, and the task-aware schemas recover useful evidence. Neither parsing nor a nonempty annotation list establishes complete evidence. All examples below were selected from exposed development material. They are debugging evidence, not representative accuracy estimates or model rankings.

The original generic-adapter captures, ordinary zero-shot captures and each subsequent candidate remain separate. Changes to task definitions and examples are experimental changes, not parser corrections. There is no GPT fallback, automatic role swap, inferred missing fact or successful-prefix salvage.

## Fixed family demonstration

The first candidate added one independent synthetic example for each native NER, RE and EE family, fixed across the same nine sources. It helped color extraction but did not resolve spatial qualifiers or events. KnowCoder lost the previously recovered elephant annotation. GoLLIE still omitted food. The mixed result does not support a general few-shot improvement claim.

## Condition-aware spatial and action contracts

The next candidate retained working zero-shot NER and one-example color extraction. It gave GoLLIE Food an explicit category definition and independent same-class example. Spatial constructors express the qualifier on the edge, such as `Near(subject, reference)`, rather than asking a generic location relation to preserve it implicitly. Actions use a separately declared `ActionDescription(actor, verbal_clause)` contract. This is coarse clause evidence, not resolved event roles.

GoLLIE produced supported annotations on all nine sources, including sandwich/pickle, `Near(boy, water)` and the dog's full fetching clause. KnowCoder recovered four entity targets and both colors, but returned an empty spatial list and shortened the dog's clause to `fetches`. Both models returned `throws leaves over her head` for the girl and omitted `in front of a fence`; neither output establishes full clause/context coverage. Thus nine nonempty GoLLIE outputs are not nine complete semantic passes. All eighteen generations reached EOS without truncation.

The later spatial parser amendment accepts fronted cues that fall outside the two entity spans, while retaining the actual cue positions and an unvalidated-association flag. It neither generates nor repairs a relation. It leaves the eighteen generation prompts unchanged; it is distinct from the model-side task adaptation.

## Symbolic count failures

The first finite count experiment used independent mention/quantity, quantity-binding and identity stages on six exposed sources. All thirty-six calls parsed, but every binding and identity stage was empty. Extracting a number word without its binding does not deliver a count.

A separately frozen guided candidate supplied only its own validated stage-one candidates to the later stages. It improved some bindings but remained unsafe. KnowCoder linked a jersey's number five to the greyhound and produced a false lower bound of five. GoLLIE's same incorrect link conflicted with a singular article and remained unknown. Both included an untyped baby in a woman group. All twelve identity-stage outputs were empty, and each model had one rejected stage. These outputs remain failures; the arithmetic layer cannot certify the upstream semantics. General symbolic count generation remains disabled.

## Separate quote-only count evidence

A further comparator requested literal `CountEvidence` quotes without quantity interpretation, identity decisions, presence assertions or aggregation. It used its own parser and protocol and did not replace failed symbolic count results.

KnowCoder's six outputs parsed and matched source text, but it omitted the unspecified children, selected jersey-number wording instead of the greyhound mention, and included an untyped baby for the women question. Both models split the three-people/man assertion into noun phrases that lose the relational cue needed to interpret distinctness. GoLLIE also included the baby and truncated the greyhound response after repeating task text to its output cap. Its entire truncated result is rejected; the initial apparently useful quote is not salvaged.

This comparator fails evidence sufficiency. Exact quotation is a mechanical property, not a relevance or completeness judgment. Its fourteen separately frozen contrast controls remain unrun. No count, referent-resolution or downstream readout success is claimed.

The [archive index](csts_native_development_archives_20261028.json) identifies immutable captures and zero-generation setup evidence by SHA-256. Raw generations, actual prompts, token vectors, runtime identities and original result records are retained. Model-assisted/source judgments remain separate from human adjudication. No downstream training or full-test result follows from these development checks.
