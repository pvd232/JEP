# In-task native adapter diagnostic

The original screen was interpreted too strongly. Successful published examples established basic generation, but did not validate the generic condition-to-relation mapping on our task. The original model-assisted percentages remain descriptive audits of captured outputs; the comparative native-model conclusion is suspended.

## Fixed diagnostic

Six literal positive sources and two unsupported negative sources were selected from the original 239 inputs. All inputs, variants and expected minimal anchors were sealed after the original screen and before these diagnostic generations. Both checkpoints, backends, greedy decoding and 1,024-token budget were held fixed. There was one attempt for each of 48 cells.

- A: byte-identical original generic `ConditionRelation` prompts.
- B: author-style multiline formatting with the same generic schema and guideline meaning.
- C: descriptive native classes, argument types and task mapping. These factors change jointly.

All 48 outputs were schema-valid. The empty outputs are literal decoded `[]` or `results = []`, not parser losses or truncation. Raw generations, input/output token IDs, model settings and source fixtures are retained.

| Model | A: literal positives recovered | B: literal positives recovered | C: literal positives recovered |
|---|---:|---:|---:|
| KnowCoder | 0/6 | 0/6 | 0/6 |
| GoLLIE | 0/6 | 0/6 | 4/6 |

Both models correctly abstained on both negative cases in every variant: snow color absent from the source and an unstated batter location.

GoLLIE C produced these exact minimal anchors from the actual sources:

| Source evidence | Condition | Parsed relation |
|---|---|---|
| A soccer team playing | Type of sport | `PlaysSport(participant="team", sport="soccer")` |
| A girl playing tennis | Name of sport | `PlaysSport(participant="girl", sport="tennis")` |
| A surfer on a white surfboard | Color of surfboard | `HasColor(object="surfboard", color="white")` |
| A man wearing a wetsuit | Attire of surfer | `WearsClothing(person="man", clothing="wetsuit")` |

GoLLIE still abstained on the plate containing a sandwich and pickle, and the pizza located on a table. KnowCoder remained empty throughout.

## Interpretation and correction

The unchanged GoLLIE model can recover facts that the original generic adapter missed. Formatting alone did not rescue these selected cases; the combined descriptive schema/task-mapping variant did. This demonstrates an adapter effect on these cases, without identifying one unique cause. It does not establish a 66.7% benchmark result or validate a production adapter across the full task.

KnowCoder's target failure remains unresolved. The diagnostic does not justify attributing it to the model family. The selected cases do not cover aggregate counting, full scope/multiplicity or the entire condition distribution.

Do not train on the original empty captures. A proper native baseline needs an explicit, calibrated task mapping and positive/negative controls for its supported task families, followed by a separately frozen representative evaluation. The original 219/21/22 joint acceptance counts must not be used to rule out KnowCoder or GoLLIE. The direct GPT validation baseline is unaffected.

## Evidence

[Diagnostic receipt](csts_native_adapter_diagnostic_20261028.json) · [Complete diagnostic archive](csts_native_adapter_diagnostic_20261028.tar.gz) · [Corrected original screen report](csts_extraction_screen_20261028.md)

Archive SHA-256: `69beade5a5fe13b1d9ea0e6de6e26cf12daf2405d9404a080a35696855dac619`.

Independent review verified all 118 indexed files, the reviewed seal and code, all 16 original A prompt identities, stored token-vector lengths/EOS, raw payload equality, absence of truncation, and the four literal source anchors. Token vectors were retained but were not independently re-decoded with a second tokenizer. All original 239-source runs and the original evidence archive remain unchanged.
