# Task-aware scope and staged-count proposal v5

This candidate leaves the approved ordinary-v3 canary archive and all original runs unchanged. It adds explicit condition-only contracts for the 21 previously unsupported exposed-screen conditions. These contracts cover all 93 screen conditions, but model fidelity and production approval remain pending. Count generation remains off outside the separately reviewed finite stage canary.

| Contract | Native stages | Limitation to inspect in development |
| --- | --- | --- |
| Travel mode; bathroom items; background/environment/place | Typed NER | Category scope and actual foreground/background binding |
| Bathroom design; ground substance; food context; train/track | Meaningful RE | Correct subject/value and source qualifiers |
| Human-use items | Category NER, explicit-use RE | Per-reading facet statuses separate category evidence from actual use |
| Person/rider descriptions | Subject NER, separate clothing/action/riding tasks | No completeness claim from a subject mention |
| Sport | Category NER, participant RE | Category evidence does not require an invented participant; Go participation retains PlaysSport(participant,sport) |
| Purpose/attention/hobby | Observed context task, separate explicit-goal/state RE | Context survives; unstated goal/state remains not specified |
| Sweetness/food amount | Food NER, separate explicit property/amount RE | No taste from food type; no total across unlike units |
| Counts | Mentions/quantity phrases, quantity bindings, identity | Separate source/scope/coreference/completeness validation required |

GoLLIE preserves HasColor(object,color), WearsClothing(person,clothing), and the participation-only PlaysSport(participant,sport) anchor. KnowCoder preserves the author system and real multiline NER/RE object-instantiation instruction, flat requested leaf classes, generic Entity relation arguments and only needed bases. New task descriptions and the event format remain empirical proposals; this is not an author benchmark reproduction or a syntax-only ablation.

Normalization preserves all exact source candidates, bindings, multiplicity, uncertainty and edge polarity. Denying color does not deny the subject's existence. Lexical man→male and pants→clothing retain source spans; a man substring inside woman cannot establish male. Source occurrence and schema validity never certify semantic support. Spatial qualifier loss is not repaired: near water and water remain different argument evidence and need review. No deterministic span expansion or hidden GPT fallback is applied. Candidate grounding ambiguity is labeled as unresolved model binding, not intrinsic source ambiguity. Exports retain unvalidated-semantic and unapproved-route flags; parse-valid alone cannot authorize training.

`normalize_stages` validates each stage separately before a literal union. It requires every declared stage and never fills a missing one. Count identity joins reuse scoped NER mentions rather than manufacture positive copies of uncertain groups. Conditional aggregation rejects contradictory identity/containment/disjointness and unsupported cardinal-expression tails. Unknown is not zero; unspecified plurals remain inexact; explicit negated cardinality is not absence. These conditional CPU rules are reviewed separately in count-v3 (receipt 00ccb68e37e8a1f94d47d705cfa6039da5680eee1f23449bbb64350bbc829485). They do not prove arbitrary English parsing or model counting ability.

Six exposed count cases propose separate three-stage anchors for three-plus-one, repeated subset, unspecified plural, jersey-number exclusion, unmentioned wheels and women excluding an untyped baby. The packet has 18 prompts/model, no model calls and no exact scene-total assertions. Its references need independent source review. Implicit singular articles are read from group mentions; quantity-link gold uses only explicit numeric words, not whole noun phrases. The scope packet contains 42 exposed sources for the 21 new contracts. No locked gold, ratings or fresh responses were inspected for these proposals.

Inventory covers 239 exposed sources/93 conditions/110 groups and 1,576 validation rows/771 conditions. Full validation still has explicit unsupported conditions. A future reserve excludes all 110 exposed groups and checks caption overlap: 1,246 rows/570 groups/639 conditions. Freshness is relative to this extraction screen, not historically untouched project validation.

All Python helpers are byte-bound by implementation_identity and each request binds plan, profile, stage and exact prompt. Outer integration must seal every imported helper, model/tokenizer/runtime and capture artifact, retaining old arm versions. Runtime descriptors distinguish KnowCoder BASE and IE at separate checkpoint revisions; no loader/precision replacement is implicit. The reusable CLI normalizes/exports through the same common graph and retains failure rows, but explicitly leaves external model-execution verification to the frozen runner.

77 tests pass. Offline actual-tokenizer accounting checks 353 KnowCoder stage prompts over the screen: 242 ordinary and 111 disabled count-stage prompts; maximum 475 input plus 512 reserved output tokens is below 2,048. No truncation or model calls. GoLLIE still requires its pinned runtime tokenizer check before model execution.

Independent review approved this frozen scope-v5 implementation and its six source-only count references for finite exposed development checks. Production, negative/uncertainty and fresh model gates remain pending.
