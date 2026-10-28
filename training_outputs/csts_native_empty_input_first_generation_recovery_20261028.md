# Empty-input first-generation recovery

Both models made their first neural call on the seven intentional empty-input controls that the original harness rejected. **All fourteen returned literal empty annotation lists, ended at EOS, and passed normalization and CPU token replay.** There were no truncations, fallback calls or repeats of the previously generated sources.

| Separate recovery origin | KnowCoder-IE | GoLLIE |
| --- | ---: | ---: |
| Previously zero-call sources | 7 | 7 |
| First actual generations | 7 | 7 |
| Literal empty annotation lists | 7 | 7 |
| Operational and replay checks passed | 7 | 7 |

The repair permits empty/whitespace strings through the renderer and normalizer while retaining type and source-span checks. The producer also clears cached error context per source and retains it only after a current-source call. Nonempty prompts, demonstrations, schemas, decoding options and token budgets are unchanged.

The [receipt and artifact index](csts_native_empty_input_first_generation_recovery_20261028.json) binds the executed capsule, both raw capture archives, original zero-call selection and preservation audit. Rehashing confirms that all 292 original indexed capture artifacts and the original inference job remain unchanged. The original 12/48 GoLLIE and 9/48 KnowCoder primary results are not replaced or recomputed.

The [executed capsule](csts_native_empty_input_recovery_capsule_20261028.tar.gz) retains its exact driver, source-only inputs, protocol and support manifest. Restore its declared layout and use its included driver instructions with the pinned historical native environment; the [general reproduction guide](../docs/native_positive_repair.md) describes those runtime identities. The raw archives retain original prompts, token vectors, payloads and per-source replay checks.

This establishes the mechanical empty-input recovery. No new formal seven-criterion sensitivity score, human adjudication, count capability, downstream readout or fresh-evaluation qualification is claimed. The broader extraction-quality failures remain.
