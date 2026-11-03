# Ten independent reviews — findings, repairs and research gaps

**Exactly ten independent reviews identified 20 findings: 2 P1, 16 P2 and 2 P3.** All remedies have code/data evidence at their stated review boundary. The final workbook has been rebuilt, visually reviewed and accepted; all six native table filters and exact source/video hyperlinks pass. Repository publication is identified by the accompanying commit.

Three findings affected existing outputs: unsupported exclusion rationales for 74 candidates, small comparison-metric discrepancies in three rows, and missing filter definitions in all six Excel data tables. The other 17 concern guards, regeneration or provenance; none established a wrong existing transcript consolidation or a lost current match. Original review verdicts remain frozen against commit `620cc5eb85860ff77a837058903321876de82b15`; later fixes have separate receipts. This aggregation is not an eleventh review.

## Exactly ten review scopes

| Review and scope | Finding IDs / priority / impact | Fix and verification |
|---|---|---|
| [R01 — Primary-list pagination parsing and traversal](reviews/review01/review.md) | R01-F01, R01-F02 · P2 · guards | Missing targets and malformed legacy tokens now reject. Valid controls and retained playlist traversal remain supported. [Evidence](root_crawler_rework.json). |
| [R02 — Crawl completeness and retained-cache accounting](reviews/review02/review.md) | R02-01 · P1; R02-02 · P2 · guards | Check every retained page and primary continuation; keep missing declared sources visible. All 120 historical responses replay; missing-page and disguised-branch controls reject. [Evidence](root_crawler_rework.json). |
| [R03 — Casanare scope decisions and register projection](reviews/review03/review.md) | R03-F1 · P1 · actual rationale defect; R03-F2 · P2 · guard | All 74 challenged rationales now have specific public/territorial pointers and remain excluded. Contradictory main/broad decisions or omitted broad admissions reject. [Evidence](tieout_data_decisions.json) / [additional receipt](root_assembler_rework.json). |
| [R04 — Transcript identity, duplicates, versions and many-to-many links](reviews/review04/review.md) | R04-01 · P2 · guard; R04-02 · P3 · actual metric drift | Stable Drive-ID registry: title rename changes zero IDs, versus 57 before. All 93 IDs / 105 assignments preserved. Shared spans become 34,102 (VV-008) and 15,050 (VV-010); VV-010/VV-027 variant word counts each rise by one. All twelve pairs reproduce; 26 checks pass. [Evidence](reviews/review04/rework.json) / [additional receipt](reviews/review04/rework_observations.json). |
| [R05 — Reverse mapping and no-source coverage decisions](reviews/review05/review.md) | R05-F1, R05-F2 · P2 · guards | Exact bilateral edge validation protects the shared upload. New unlinked uploads stay coverage-unconfirmed until admitted by a source-bound review ledger. Seven admission checks preserve all 45 accepted baseline dispositions. [Evidence](root_assembler_rework.json) / [additional receipt](reviews/review05/rework_R05_F2.json). |
| [R06 — Timestamps, dates, durations and directional coverage](reviews/review06/review.md) | R06-01 · P2 · guard | Reject malformed duration components; three invalid and six valid controls pass. Existing dates, offsets and distinct gap directions were supported. [Evidence](root_assembler_rework.json). |
| [R07 — Forward-match verification, recording gaps and protected labels](reviews/review07/review.md) | R07-01 · P2 · guard | Explicit evidence governs content verification; confidence does not create it. All three merger counterexamples pass; fifteen recording-gap rows retain correct ownership. [Evidence](reviews/review07/rework_observer.json). |
| [R08 — Workbook projection, hyperlinks, filters and acceptance](reviews/review08/review.md) | R08-01, R08-02 · P2 · guards; R08-03 · P2 · actual filter defect | Dynamic native links pass cardinalities 0/1/2/3/15. Missing forward/reverse links and filters reject. Postprocessor writes all six filters; final workbook acceptance passed. [Evidence](reviews/review08/rework.json). |
| [R09 — Reproducibility, failure reporting and publication provenance](reviews/review09/review.md) | R09-F01, R09-F02 · P2; R09-F03 · P3 · guards/provenance | Failed proof receipts cannot produce success reports; failed/incomplete crawls exit nonzero. Cached proofs carry original fetch times/hashes. Nine report controls and crawler controls pass. [Evidence](reviews/review09/rework.json) / [additional receipt](root_crawler_rework.json). |
| [R10 — Fresh channel traversal, cache binding and surface provenance](reviews/review10/review.md) | R10-01, R10-02 · P2 · guards | Bind parsed first-page cache to its HTML and verify the requested channel surface. Both mismatches reject; seven controls and full 118-page fresh replay pass. [Evidence](reviews/review10/rework.json) / [additional receipt](reviews/review10/rework_replay.json). |

## Reconciled research counts

| Unit | Current count |
|---|---:|
| Original source files / transcript-or-notes files | 116 / 105 |
| Consolidated source records / retained alternate versions | 93 / 12 |
| High-confidence source matches / content-checked source matches | 82 / 80 |
| Admitted uploads / uploads linked to supplied sources / source–video edges | 128 / 83 / 84 |
| Uploads without a located supplied transcript | 45: **17** bounded content-identity checks; **28** metadata-based |
| Main scope register | 208: 128 included, 76 excluded, 4 unconfirmed |
| Broad Case 03 register | 898: 96 included, 789 excluded, 13 unconfirmed |

Root added **13 bounded public identity checks**; the underlying 45-upload set did not change. These checks establish participants, dated openings or recording format at named anchors. They do not certify 45 additional unique hearings or complete audio equivalence. The 93 source records remain unchanged; VV-071 is a composite two-date document, and VV-029/VV-030 share one upload with distinct segments. [Data decision receipt](tieout_data_decisions.json).

## Fresh discovery and repair checks

**Fresh channel discovery is 118 pages: 89 Videos pages with 2,663 IDs, and 29 Live pages with 846 IDs**, fetched on 3 November 2026. Both traversals reached terminal pages; YouTube supplied no independent declared channel total. The older 847 Live IDs are historical evidence, not the fresh count. The single absent current appearance, `Pg8DvszQMME`, remains playable; its bounded opening identifies Huila, so it remains historical discovery and is excluded from the Casanare corpus. [Fresh comparison](fresh_channel_comparison.json) / [118-page replay](reviews/review10/rework.json).

Root’s [crawler repair verification](root_crawler_rework.json) passes **11 focused cases** and the separate **120-page historical replay**. Its [assembler verification](root_assembler_rework.json) passes **10 assembly cases plus nine duration cases**, preserving all 84 accepted edges while rejecting inconsistent inputs before writes. These are follow-up checks, not extra independent reviews.

Fresh discovery integration: [the completed check-mode receipt](fresh_channel_integration_receipt.json) passes all preservation and repeatability checks. It retains **5,203 appearances = 5,202 current + one historical**, and **3,606 discovery IDs = 3,605 current + one historical-only**. All ten playlist snapshots and other non-channel memberships remain unchanged; discovery counts do not enlarge the Casanare corpus.

## Remaining research gaps

- **11 supplied source records** still have no located public recording; **two** require missing recording continuations; **two** source matches remain metadata-only. These are the fifteen source-side gap rows.
- **Six known supplied-transcript omissions** describe the opposite coverage direction. They overlap with other gap categories and must not be added to produce a total missing-hearing count.
- **45 admitted uploads** have no supplied transcript located, with 17 bounded content-identity checks and 28 metadata-based decisions. Full-audio coverage and upload-to-unique-hearing equivalence remain uncertified.
- **Four main candidates and thirteen broad-register entries** remain scope-unconfirmed (one ID overlaps). They stay outside the admitted corpus. Four unavailable IDs across those registers lack usable recording identity, including the Casanare playlist placeholder.

These are explicit evidence/access uncertainties, not unresolved code defects. Caption date conflicts and approximate timestamp limits remain visible. The workbook review verified projection of the 93 English summaries; it did not independently fact-check every summary claim. Final workbook rebuild, native-link/filter postprocessing and acceptance have passed. See the [workbook acceptance](../workbook_validation.json) and [release reconciliation](../catalog_validation.json); publication is recorded by the repository commit.

Full frozen review/source hashes, repair-receipt hashes, current data hashes, exact finding IDs and stage limits are recorded in [ten_review_summary.json](ten_review_summary.json). No source document or canonical research data was modified by this aggregation.
