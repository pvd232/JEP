# Ordinary native extraction development gate, 2026-10-28 UTC

Both pinned checkpoints now run in checked native backends, but the zero-shot task-aware candidate still fails substantive ordinary-task checks. These nine selected exposed positive sources are development cases, not a benchmark sample. No locked/fresh candidate calls or model ranking are authorized by this result.

| Source-backed target | KnowCoder-IE | GoLLIE7B |
| --- | --- | --- |
| Elephant type | Animal(elephant) | Animal(elephant) |
| Sandwich and pickle types | Food(sandwich), Food(pickle) | empty |
| Train type | Vehicle(train) | Vehicle(train) |
| Helmet presence | Helmet(blue helmets) | Helmet(blue helmets) |
| Brown dog color | Color(brown,dog): reversed arguments | empty |
| White surfboard color | empty | HasColor(surfboard,white) |
| Boy near the water | empty | Location(boy,water): loses near |
| Dog fetching a stick from dead leaves | empty | empty |
| Girl throwing leaves over her head | empty | empty |

The two independent KnowCoder companion replays retain Wears(man,wetsuit) and Sport(tennis). Every output reaches EOS without truncation. Both models emitted five nonempty lists on the nine targets, but nonempty is not equivalent to correct evidence. The reversed animal-color relation is Python-valid and its strings occur in the source; it still has the wrong binding. GoLLIE's location output omits a condition-relevant spatial qualifier. Both event tasks remain empty. Correct object spans with harmless boundary differences, such as surfboard versus white surfboard, are not automatically counted as semantic failures.

## Parser-envelope correction, no inference rerun

The original nine KnowCoder result records all reported malformed syntax because vLLM's API text starts with a space before results. The strict parser called ast.parse on that unstripped envelope. The two companion parsers already stripped it and succeeded.

The envelope fix uses payload.strip() in direct and per-stage parsing before the same AST allowlist and source/binding checks. It strips only external whitespace, preserves quoted spans, and still rejects blank output, additional statements and arbitrary code. Three regressions bring the integrated targeted suite to149 passing tests. Original raw generations and result records remain unchanged. The derived reparse sidecar records all18 target cases and their exact original hashes:9/9 parse and ground for each model, with five answered and four empty predictions. This parser recovery is reported separately from any few-shot effect; it does not fix reversed bindings or missing facts.

KnowCoder's27 indexed files and GoLLIE's22 indexed files match their stored hashes and byte sizes. The execution archives retain raw token vectors, actual inputs, original classifications, runtime/checkpoint proofs and source seals. The accompanying reparse sidecar binds the amended normalizer's complete helper identity. No hidden fact repair, role swap, GPT fallback or repeated generation was used.

## Next declared development candidate

One separately frozen candidate adds exactly one independent synthetic demonstration for each native NER, RE and EE task family, fixed across targets. It preserves the nine target schemas and uses a separately named prompt profile; it is not a prompt grid or a target-answer demonstration. Its outputs must be checked against these failures before any progression to negative/uncertainty, count-stage or locked/fresh quality gates. All old candidate versions remain reproducible.
