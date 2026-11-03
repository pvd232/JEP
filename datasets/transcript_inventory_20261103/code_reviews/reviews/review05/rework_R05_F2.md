# Review 05 — R05-F2 repair receipt

**Verdict:** R05-F2 is closed for the isolated absence-admission boundary. This is a repair follow-up to Review 05, not an additional independent review. Root owns integration and the separate R05-F1 edge-preservation fix.

## Change

The mapping builder now assigns an unlinked upload **Coverage unconfirmed** unless a reviewed disposition in `accepted_reverse_dispositions.json` is bound to the same source-session index, exact video ID, title hash and parsed participant/date. An exact principal/date collision with supplied metadata stays unresolved. A changed source-session index fails closed before outputs can be written. A final check also prevents a later status override from bypassing the accepted ledger.

The ledger retains the accepted **45** upload dispositions against **93** supplied records: **41** metadata-based and **4** content-based. These remain upload counts, not a certified number of additional unique hearings. Existing content refinements and transcript-to-video links are unchanged.

The deterministic source identity includes record ID, source-file IDs, title, date, participants and document type. Sorting changes, video URL edits and coverage notes do not change identity. The current index SHA-256 is `84ea4abd30c448bce30be72bcc75a81b65bf2e1c88082b7987a002ecc0ae2f27`.

## Focused observation

Ran the actual repaired pure functions plus isolated candidate and final-validation loops against frozen fixtures. The top-level builder was neither imported nor executed. The observer wrote only its own receipt. No canonical research output was regenerated.

```bash
"$CODEX_PRIMARY_RUNTIME_PYTHON" inventory_work/tieout_review_20261103/reviews/review05/observe_disposition_repair.py
```

Exit status: **0**.

| Observation | Result |
| --- | --- |
| All 45 accepted baseline dispositions survive both admission and final validation | Pass |
| A new unreviewed upload remains unresolved | Pass |
| An exact principal/date collision remains unresolved even with a metadata ledger entry | Pass |
| A changed source-session index fails closed | Pass |
| Ordering, video URLs and coverage-note changes do not redefine the source-session index | Pass |
| Duplicate accepted video IDs cannot overwrite a disposition | Pass |
| A later override cannot bypass accepted-disposition admission | Pass |

The baseline test establishes preservation of all 45 accepted absence IDs through admission and validation. The four existing content refinements were inspected in the patch context and are unchanged; this observer does not claim an end-to-end canonical build.

## Reproduction identity

Accepted published commit: `620cc5eb85860ff77a837058903321876de82b15`.

| Artifact | SHA-256 |
| --- | --- |
| `builder_before` | `f409e2bc23f999f55e4363f083c116cb56af2c3f556f47aeaba827837921a0e1` |
| `builder_after` | `c268c8fad85bb5c7a8b3fc9d20529aae786f471ce94f5eaaf6d11bb834ba1776` |
| `accepted_disposition_ledger` | `2381d6747c2f2171d8ccb050fd5dc1a604b789eefc8ea8dbc2829e84d5ee7e2b` |
| `observer` | `d033c3cee54b026a0276414629d622d1e5ac2ce8c1883593133344707f24f743` |
| `observer_results` | `70939569cb45123490892cf470415cb365f903fc95af70af31ddd5ec4833a835` |
| `accepted_inventory` | `e261e1b82e9fe41b62aba96277ab54b5f377839a0fc428797dae8d005756b404` |
| `accepted_reverse_mapping_review` | `6c8db273082b2c641f799e98996e92650472c9bb451d0ffaab61200ea631af55` |
| `accepted_scope_decisions` | `b49bb97967d26c9421b51dc2d3aac6363da7ea4ae5b8c98fa18b98f37f5e5766` |
| `original_review` | `8b0cd0eb9edfafdc44acd0014f7dc1a16460f5de235efa8566784f89a6af4cab` |
| `all_41_metadata_comparisons` | `2f81da80dd477c313abb682241ee7b6224842e1ab8ec627bc852ab34f2545d1e` |

Exact paths, helper line locations, check details and scope limits are recorded in `rework_R05_F2.json`. `disposition_repair_observations.json` contains the machine-readable focused results. The historical failing-counterexample observer and original review remain intact.

## Integration boundary

Production changes are limited to `inventory_work/reverse_audit/build_mapping_review.py` and `inventory_work/reverse_audit/accepted_reverse_dispositions.json`. New review files are under `reviews/review05/`. Root retains control over canonical records, the workbook assembler and publication. The accepted ledger preserves the frozen review; new caption evidence and any revised statuses require root reconciliation. No raw captions or private source text are included in this receipt.
