# Review 04 — transcript identities and versions

## Reviewed state and boundary

Frozen published dataset: `620cc5eb85860ff77a837058903321876de82b15`, copied under `inventory_work/tieout_review_20261103/base/`. Reviewed `inventory.json`, `source_manifest.json`, `version_comparisons.json`, the relevant reverse-map entries and their join in `workbook_build/assemble_outputs.py`. Historical supporting generators and matching code in `inventory_work/` were inspected by their recorded SHA-256 values; those working scripts are distinguished from the published snapshot in `review.json`.

The review covers source identity, consolidation, source-to-record ownership, preservation of all version links, and many-to-many source/video relations. It excludes fresh public discovery, territorial admission, full audio comparison and line-by-line verification of every transcript. No network requests or source/baseline modifications were made.

## Verdict

**Request changes for safe regeneration of the historical source-ID generator. Approve the existing 93-record consolidation and its many-to-many links.** The P2 finding below affects a future rebuild after an upstream filename change; it is not evidence that any existing record was assigned the wrong identity. The P3 discrepancy is limited to three small overlap statistics and does not change a consolidation or count.

## Invariants and observed results

- The manifest contains 116 distinct source file IDs across ten folders. Its 105 transcript/notes files map exactly once to 93 distinct inventory records. Nine legal PDFs and two link/index documents are separately classified.
- All twelve nonprimary source assignments have a comparison record: eleven alternate transcriptions and one condensed-notes/full-transcript pair. Every original link is retained, and the manifest's inverse assignment agrees with the inventory.
- All eleven alternate transcription pairs contain ordered exact normalized blocks of at least twelve words across all ten deciles of the alternate text (334–1,532 ordered blocks per pair). The condensed notes contain 22 such ordered blocks across deciles 1–9; their dated heading agrees with the fuller source. These observations support a shared hearing, not identical wording or full coverage equivalence.
- An independent normalized-content scan of all 105 supplied texts found no undisclosed exact duplicate. The 39 cross-record pairs exceeding the diagnostic overlap threshold all involve one of the two short procedural sessions, VV-057 or VV-058. Their different dated installations/rescheduling outcomes and the repeated judicial formalities explain why overlap alone must not merge them. No plausible missed consolidation was established.
- The 84 forward transcript/video edges exactly equal the reverse edge set, with 83 distinct linked uploads. The shared upload `eM8ZrqhZbgQ` retains distinct records VV-030 (protective measures) and VV-029 (voluntary statement), separated at approximately 50:36.
- VV-057 retains both `ztGtBj4AbQA` and `FoAy5Qfphcs`. Opening, postponement and closing evidence is recorded for the second upload. The same-session relation does not create an additional supplied transcript.
- VV-071 explicitly preserves the 12 and 20 August 2021 sessions within one composite original-document record. Its notes retain the session boundary pointers. Consequently 93 is the consolidated source-record count, not a count of distinct hearing dates or recording parts.

## Findings

### R04-01 — Filename sorting can renumber established transcript IDs

**P2; blocks reusing the historical generator for an updated source snapshot without repair. Does not block the existing inventory.**

Location: `inventory_work/build_versiones_rows.py`, module-level canonical-row generation, lines 90 and 118. The generator sorts canonical files by their mutable title and assigns `VV-{len(rows)+1:03}`. Downstream reviewed updates address those IDs directly, including the VV-057 alternate-upload update at published `workbook_build/assemble_outputs.py` lines 87–93.

Invariant: an unchanged source file/group must retain its established inventory ID when a filename is corrected or the metadata listing order changes.

Concrete reproduction: the actual generator was executed twice with every write intercepted in memory. Prefixing only the existing VV-057 source title with `AAA_`, while retaining all 75 canonical Drive IDs and source contents, changed 57 record IDs. The VV-057 source became VV-001. The old count and uniqueness checks still have 75 rows and 87 distinct source-file assignments, so those checks cannot detect semantic reassignment. Subsequent ID-addressed reviews could then attach to the wrong source.

Smallest repair: preserve an explicit existing source-file/group-to-record-ID registry derived from the accepted inventory. Resolve known groups through that registry and allocate an unused ID only for a genuinely new group. Reject conflicting existing IDs rather than choosing one by sort order. Alternatively retire this historical generator and explicitly prevent it from regenerating the accepted inventory; the currently published assembler already reads and preserves the established source IDs.

Focused observer: `observe_id_stability.py`. After the repair, a title-only change must preserve every existing source-file-to-record-ID pair, including VV-057. The current observation is in `id_stability_observations.json`.

### R04-02 — Three saved overlap statistics are not exactly reproducible from retained text

**P3; nonblocking. No effect on pair identity or rounded containment.**

Location: `version_comparisons.json`, entries for VV-008, VV-010 and VV-027. Using lowercase, accent-stripped Unicode NFD or NFKD text, `\w+` word tokens and distinct five-word spans gives:

| Record | Saved statistic | Recomputed statistic |
|---|---|---|
| VV-008 | 34,104 shared five-word spans | 34,102 |
| VV-010 | 38,244 alternate words; 15,051 shared spans | 38,245 alternate words; 15,050 shared spans |
| VV-027 | 42,353 alternate words | 42,354 |

The nine other entries reproduce exactly; all twelve rounded containment values agree. The comparison register does not retain the exact text hashes and normalization implementation used for its measurements, so the cause of the small drift cannot be assigned confidently.

Smallest repair: recompute the three statistics against the retained extraction, record the tokenization/normalization rule and source-text hashes, and update their corresponding numeric evidence strings. If an earlier extraction was intended, retain its hash and label the statistics as historical. Re-run only the pair-metric observer; no rematching or source consolidation change is justified by these differences.

## Evidence and limits

`observations.json` contains 39 data checks: 36 pass, and the three failures are exactly the small metric differences above. All 27 identity, ownership, edge and exact-duplicate checks pass. `ordered_pair_observations.json` records the distributed overlap for every consolidation. The observers emit aggregate counts, IDs and hashes, not source testimony. No full transcript or private raw payload is included in this review package.

The content scan is a diagnostic for overlooked duplication, not a proof that every possible excerpt or semantic paraphrase has been detected. Caption-derived boundaries remain approximate. Existing summaries and source links were read without modification.
