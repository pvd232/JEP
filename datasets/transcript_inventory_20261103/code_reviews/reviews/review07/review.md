# Review 07 — forward matching and recording gaps

**Verdict:** Request changes for safe reuse of the historical forward merger. The existing fifteen recording-gap rows are supported by the inspected inventory and review evidence; this review establishes no change to their counts.

## Reviewed state and boundary

Published evidence snapshot: commit `620cc5eb85860ff77a837058903321876de82b15`, frozen under `inventory_work/tieout_review_20261103/base`.

The reviewed published files are `inventory.json`, `recording_gaps.json`, `completion_review.json`, `matching_audit.json`, `summary.json` and `workbook_build/assemble_outputs.py`. The earlier production scripts were inspected as separately identified local historical code, not represented as files contained in that published commit:

| Local historical script | SHA-256 |
|---|---|
| `merge_deep_results.py` | `722420947c7d7826f20ffdbd0c3400acc3ec62e5371d63b681d02553d865d82f` |
| `merge_completion_review.py` | `58e292ba901ce5302f4b2069327832b5d908b011a62ce03d75c937a88c38830a` |
| `apply_completion_summaries.py` | `d7bde7ac17aa8472bda22d0bed93587d22a2779ee96a32fcf713812b46f6cdde` |

All reviewed file hashes are in [scope_hashes.json](scope_hashes.json). Local historical scripts were copied into this review's private `source_snapshot` directory before executing the observer. No canonical, frozen or shared-cache file was modified.

## R07-01 — content verification is inferred from confidence and record ID

**Severity:** P2. **Blocks:** approval of the merger for further matching updates. **Current-data impact:** no incorrect frozen row was established.

**Location:** `inventory_work/merge_deep_results.py`, `FIELDS` and `METADATA_ONLY` at lines 7–8; `apply_deep_results` at lines 52–61 and 74–83.

**Invariant:** a high-confidence identity match must not imply a content check. Explicit verification evidence must control `content_verified`; a rejected match must not retain verification, and a previously metadata-only record must be able to acquire new verification.

The allowed update fields omit `content_verified`. The merger then sets that flag for every High record except two hardcoded IDs. A later downgrade does not clear an existing True flag. The same flag also generates the claim that the public caption panel was accessible without sign-in, although that access observation is not established by identity confidence.

The focused observer executes the actual copied merger against three isolated synthetic reports:

| Synthetic review | Expected | Actual |
|---|---|---|
| High identity confidence, explicitly metadata-only and `content_verified=False` | Verification remains False | True; labelled “Public captions checked” and caption panel accessible |
| Earlier verified candidate rejected, with Unmatched and `content_verified=False` | Verification clears | Remains True alongside “Public recording not located” |
| New affirmative caption evidence for `SDSJ-20241203` | Verification can become True | Forced False by the fixed exception set |

**Smallest credible repair:** make the explicit review verification decision authoritative, with a recorded content anchor for affirmative decisions. Clear verification when the reviewed candidate is rejected or replaced without a new content check. Remove record-ID exceptions as the source of verification truth. Preserve access/playability observations separately instead of generating them from match confidence. Existing accepted evidence can be preserved for an unchanged recording; a new High confidence value alone must not create it.

**Focused observer:** [observe_forward_verification.py](observe_forward_verification.py). It accepts `--module PATH` for verification of a repair. The three `invariant_passed` fields in [observer_results.json](observer_results.json) are False before correction; all should be True afterward. These fixtures are synthetic counterexamples, not research records.

## Frozen data and evidence findings

The actual frozen inventory has **82 High and 11 Unmatched records**. The gap register contains exactly **11 unmatched recordings, two missing continuations, and two content/coverage checks**. Its IDs, categories of gap, source dates, original links and located-recording links agree with the inventory; the completion-review audit has the same fifteen IDs and statuses. All eleven unmatched rows have empty recording links and `content_verified=False`. There are no Medium/Low candidate rows omitted from this final gap set.

The high-risk distinctions remain visible:

- `VV-064` and `VV-067` identify the private/reserved designation in their actual source openings. Their current publication status remains unconfirmed. The relevant source paragraphs contain the private/reserved and recording terms.
- `VV-065` retains the protected NRAS/XYZ labels. Identity protection is not used to infer that the complete recording is nonpublic. No identity expansion was attempted.
- `VV-019` preserves the distinction between counsel's reservation request and an established access restriction. `VV-019` and `VV-056` retain their dialogue-versus-written-continuation ambiguity.
- `VV-022` distinguishes the 22 July 2021 submission/header date from an unestablished recording day. `VV-056` preserves the 22/29 July citation conflict.
- `VV-071` retains both 12 and 20 August 2021 sessions in its composite source record. Its suspension and continuation source pointers support that distinction.
- `VV-015` and `VV-038` identify missing public-recording tails, rather than missing supplied text. The latter's appended roster is not treated as further hearing dialogue.
- The two December 2024 rows retain metadata-only matching and unverified video offsets. The saved `t=38031s` position is correctly treated as a viewing position rather than a verified source boundary.

The inspected completion-review notes explicitly state that an unsuccessful public search does not prove that a recording was never published or is reserved. No unsupported replacement recording was found in these fifteen rows. Source anchors were checked selectively for the classifications and distinctions above; this was not a new full-text or audio review.

## Fresh Live-list difference

The parent's fresh channel comparison shows no change to the 2,663 Videos IDs and one missing appearance in the new Live listing: `Pg8DvszQMME`. It occurs in the old broad channel catalog but not in the frozen supplied mapping or either scope register.

One exact [public watch-page metadata check](https://www.youtube.com/watch?v=Pg8DvszQMME), recorded at `2026-11-03T20:33:48.939199+00:00`, returned HTTP 200, official JEP channel identity and playability status `OK`. The advertised duration is 6,577 seconds; the live metadata identifies 21 October 2026. The title describes a Day 1 conditionality/responsibility/dialogic hearing, while the description is institutional boilerplate without a territorial or case identification.

Its absence from the new Live listing therefore does **not** establish deletion or unavailability. Retain the historical discovery and its current accessible status; no Casanare membership or correspondence to a supplied transcript is established by this metadata. Any inclusion requires a further bounded scope check. The sanitized receipt is [removed_live_watch_metadata.json](removed_live_watch_metadata.json). No testimony was read for this item.

## Verification and exclusions

The observer uses Python's standard library and writes only under this review directory. It verifies gap ownership separately from the synthetic merger counterexamples. A single public watch-metadata GET was made; no other network research, external communication, source editing or publication occurred.

Excluded from this review: independent listening to audio, fresh judicial-file access, replacement of protected identity labels, comprehensive new searches for all eleven missing recordings, and the separate reverse mapping/scope reviews. No new supplied transcript-to-recording match was verified here.
