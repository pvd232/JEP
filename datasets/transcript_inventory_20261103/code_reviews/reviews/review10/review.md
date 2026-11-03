# Review 10 — Fresh channel traversal and provenance

**Verdict: Request changes to the candidate code. The retained fresh data passes this scoped offline audit.** Two P2 cache/identity defects are reproducible; neither was present in the actual saved responses. This receipt was frozen before the separately authorized repair.

## Reviewed state and invariants

Published baseline: `620cc5eb85860ff77a837058903321876de82b15`. The new candidate `inventory_work/reverse_audit/refresh_channel_catalogs.py` was reviewed at SHA-256 `0cabb13c3c085059d30ce2e0656154737b717f26938ba2cea095066f089c8999`. Its then-current `crawl_public_catalog.py` dependency was frozen at `12e5a7b9daa3067ddd714a8b56c15ee753e4025a659a285051bc263c6845acaa`; this includes the parent's initial target and legacy-control repairs. Exact paths and hashes are recorded in [review.json](review.json).

The review requires a checksum-bound first page, the requested official channel surface, continuous primary-list pagination, honest incomplete states, preserved historical discovery, and separate upload/session/transcript counts. The saved response replay reconstructs all membership fields and ordering, compares each request receipt with its sidecar, verifies every predecessor token fingerprint and normalized continuation checksum, and checks terminal state and retrieval-time provenance. Network access is blocked in the observer.

## Findings

### R10-01 — P2: the parsed first-page cache is not bound to its HTML

**Location:** `refresh_channel_catalogs.py`, `refresh`, lines 54–59.

The cached branch verifies `initial.html` against its raw receipt but consumes `page_000.json` independently. Removing the continuation only from that parsed JSON leaves the original HTML and its checksum intact. The actual function then reports `exhausted_count_unknown`, one video, no errors and `pagination_exhausted=true`.

**Repair:** re-extract `ytInitialData` from the checksum-verified retained HTML and reject a different parsed cache before selecting the primary list. The R10-01 observer must report an explicit mismatch, while both actual first-page JSONs must continue to agree with their HTML. No current-data mismatch was observed.

### R10-02 — P2: the selected tab is not checked against the requested surface

**Location:** `refresh_channel_catalogs.py`, `refresh`, lines 70–79.

The selected tab must have a primary grid and the response must identify the official channel, but the selected endpoint is never compared with the requested `videos` or `streams` URL. A fully consistent official Videos response supplied for a streams request completes as `channel_streams` with a selected title of Videos.

**Repair:** compare the observed selected-tab endpoint with the requested surface and official channel path before consuming the grid. Preserve its endpoint alongside its title. R10-02 must become an explicit surface mismatch. The actual snapshots select `/@jepcolombia/videos` and `/@jepcolombia/streams` correctly.

## Retained data reconciliation

| Surface | Saved pages checked | Distinct upload IDs | Newly appearing IDs | IDs absent versus prior catalog |
|---|---:|---:|---:|---|
| Videos | 89 | 2,663 | 0 | None |
| Live | 29 | 846 | 0 | `Pg8DvszQMME` |

All **118** page checks pass. Every membership, its order and page index, every receipt chain, the official channel ID, the primary target, and the final empty continuation agree with the saved states. Both statuses are honestly `exhausted_count_unknown`: YouTube did not supply a declared total for these channel surfaces, so traversal exhaustion is established without claiming an independently reconciled total.

Videos first fetched at `2026-11-03T20:19:11.924638+00:00` and finished at `20:26:51.601385+00:00`; its script start is later than the previously saved first-page seed and is not substituted for the original fetch time. Live first fetched at `20:26:51.644307+00:00` and finished at `20:28:54.535610+00:00`. Request timestamps are ordered and precede completion.

The historical Live catalog has 847 IDs. The sole difference, `Pg8DvszQMME`, was still accessible and playable in Review07's separate public-watch metadata check at `2026-11-03T20:33:48.939199+00:00`. Its absence from the current channel listing does not establish deletion, unavailability or a particular privacy setting. Retain its historical discovery and unresolved scope; do not silently subtract it from the research provenance. The fresh metadata alone does not establish its territorial scope.

Seven focused controls pass: a valid terminal page, request failure with its pending token retained, page limit with its pending token retained, wrong request-token receipt, changed continuation checksum, wrong response target, and a repeated continuation cycle. The two counterexamples and per-page hashes are in [observations.json](observations.json); the replay is [observe_fresh_integrity.py](observe_fresh_integrity.py).

## Integration observations

I inspected the frozen assembler's joins and the bounded findings from Reviews03/05. Their requirements remain necessary before publication: reject divergent broad/main scope decisions or omitted broad inclusions; reject duplicate reverse IDs; preserve the complete corrected forward/reverse edge set; and keep newly unlinked uploads coverage-unconfirmed until reviewed. These are the existing R03-F2, R05-F1 and R05-F2 findings, not three additional findings in this review. The parent owns those repairs and the fresh-snapshot integration.

Use the fresh traversal in current source accounting while retaining historical membership and unavailable-item provenance. Both channel grids are discovery sources, not a declaration that the entire channel belongs to the scoped Casanare corpus.

## Evidence limits and repair boundary

The first-page raw HTML is retained and checked byte-for-byte. Continuation JSON is retained in formatted form, so its normalized parsed-response checksum can be verified; the original HTTP-body checksum cannot independently be recomputed from those formatted bytes. Token fingerprints and the reviewed request builder establish the recorded context chain, not a packet capture. This review does not add hearing-content checks, new transcript matches or geographic determinations.

No network call, shared-cache mutation or source-document change occurred during this review. The parent authorized repairs only in `refresh_channel_catalogs.py` after this receipt. Subsequent exact hashes, counterexample outcomes, replay results and immutable-response checks will be recorded separately in `rework.json`.
