# Review 01 — Pagination parsing and traversal

**Verdict: Request changes** for two P2 fail-closed defects before unrestricted crawler reuse. **Neither finding demonstrates an error in the published playlist counts.**

## Reviewed state and boundary

- Commit: `620cc5eb85860ff77a837058903321876de82b15`.
- File: `pagination_fix/crawl_public_catalog.py`.
- SHA-256: `8e7ba646de4edc9ee86045201eb7405077a8d670598f245969778b2e5d8936f6`.
- Main symbols: `item_token`, `initial_list`, `continued_list`, `parse_entry`, `parse_list`, `crawl_one`, `reproduce`.
- Supporting reads: request/cache boundaries, metadata and completion functions, reduced-fixture construction, all six fixture/manifest JSON files, and selected source-accounting metadata. Exact hashes are in `review.json`.
- Baseline and shared caches remained unchanged. All observer writes are confined to this review directory; no network request was made.

The intended behavior is to follow only the positively identified primary video list, preserve every video appearance, and retain failures or ambiguous list controls as incomplete. Matching declared totals cannot substitute for a valid traversal.

## Findings

### R01-F01 · P2 · Missing target identity can be accepted as a match

**Location:** `initial_list`, lines 178–182; `continued_list`, lines 185–194. Blocks general parser approval; does not invalidate the saved dataset counts.

`initial_list` returns the modern container’s `targetId` without validating that it exists. `continued_list` uses `item.get("targetId") == target`. When both sides are missing, an unaddressed response action is admitted as the primary list.

**Reproduced failure:** A first page has one video, a continuation and no target ID. A response action also omits its target and supplies one video. With a declared total of two, the unmodified crawler reports `exhausted_reconciled`, `pagination_exhausted=true`, `count_reconciled=true`, and `target_id=null`. The action’s relationship to the primary list was never established.

**Smallest repair:** Require a nonempty string target before following a pending continuation and reject a missing/invalid target at `continued_list`. A terminal single-page list need not be rejected merely because no target is necessary.

**Focused observer:** `missing_primary_target` in `observe_pagination.py` must produce an explicit incomplete/error result and retain the pending request. All retained target-bearing pages must still replay unchanged.

**Impact boundary:** This is a synthetic malformed-input case. Every selected real playlist has a nonempty target. No wrong existing membership or count was found.

### R01-F02 · P2 · Malformed legacy controls are discarded as though terminal

**Location:** `parse_list`, lines 251–254. Blocks general parser approval; does not invalidate the saved dataset counts.

The legacy-continuation loop silently ignores supplied controls unless `nextContinuationData.continuation` is truthy. This differs from primary-list items, where an unknown control raises an error.

**Reproduced failure:** One video plus `legacy_continuations=[{"nextContinuationData": {}}]` returns an empty pending queue without error. With a declared total of one, `completion` reports `exhausted_reconciled` and `pagination_exhausted=true` despite the malformed continuation control.

**Smallest repair:** Validate every supplied legacy control. Accept the supported `nextContinuationData` shape only with a nonempty string token; raise a concise parsing error for missing tokens or unsupported controls. A reload control should not be guessed to mean another page.

**Focused observer:** `malformed_legacy_continuation` must raise, while the supported legacy token case still follows its token.

**Impact boundary:** This malformed shape was not observed in the retained selected playlist pages. The finding concerns future invalid or changed response formats.

## Mechanical evidence

The isolated standalone fixture replay passed **14/14** checks. An additional replay of **22 retained response pages across all ten selected playlists** reproduced the same ordered video IDs, source positions, appearance positions, visibility labels and final statuses. Every selected playlist’s declared count still reconciled. The code’s existing refusal of mismatched targets, request failures, repeated-token cycles and page limits was also observed directly; those paths retained incomplete status and pending request identity as appropriate.

The source hashes for all 45 frozen baseline files remained unchanged. `observations.json` records each retained-response hash and the two failing synthetic cases without publishing raw continuation tokens.

## Exclusions and residual risk

This review does not refetch public sources, establish current channel freshness, inspect video content, or assess transcript matching and scope decisions. It supports the specific repaired pagination path against the retained responses. The two synthetic failures should be repaired without treating them as evidence that the observed 898-entry and 20-entry inventories are wrong.
