# Review 09 — reproducibility and publication

**Verdict: Request changes.** Two P2 defects let command or report success outlive a failed underlying check. A P3 advisory concerns the freshness label of cached pagination proofs. None of these counterexamples establishes an incorrect count in the frozen published dataset.

Reviewed commit: `620cc5eb85860ff77a837058903321876de82b15`. Mode: independent completed code review. The scope was the crawler CLI, fixture reduction and replay, workbook assembly/report/validation, publication manifests, and execution receipts. Exact reviewed file hashes are recorded in `review.json`.

## Findings

### R09-F01 — failed proof inputs still produce an all-passed report

**P2; blocks review approval; no demonstrated current-data impact.**

Location: `workbook_build/finish_report.py`, `main`, lines 17–18 and 48. The pass counts use `len(proof['checks'])/len(proof['checks'])` and `replay['checks']/replay['checks']`. The reporter does not validate check outcomes, `all_passed`, or replay `exit_code` before updating the summary and report.

The isolated counterexample changes one actual reproduction check to failed, sets both receipts' `all_passed` to false, and sets replay `exit_code` to 1. The unmodified reporter exits 0 and generates a report still claiming 15/15 reproduction checks and 14/14 replay checks passed. The actual frozen receipts are successful, so this is a reusable reporting defect rather than evidence that the present report is false.

**Repair:** validate proof and replay receipt structure and outcomes before writing either output. Derive passed counts from individual outcomes. A failed receipt must produce an explicit failed status/nonzero exit, not an all-passed narrative. Observe both the failed-input control and the real successful inputs after repair; a missing-file exception alone is insufficient verification.

### R09-F02 — failed requested crawl returns process success

**P2; blocks review approval; no demonstrated current-data impact.**

Location: `pagination_fix/crawl_public_catalog.py`, `main`, lines 966–974. The `crawl` command prints each state but does not propagate failure or incomplete traversal to its process exit code.

The observer invokes the actual CLI branch and actual `crawl_one` with a deterministic first-request `TimeoutError`. The state correctly retains `status="error"`, `pagination_exhausted=false`, and one error, but the CLI exits 0. A caller that sequences these documented commands by exit status can proceed after an unsuccessful required source.

**Repair:** retain error receipts, aggregate every requested source result, and exit nonzero if any requested full crawl is incomplete or fails. Check transport failure, page cap, and stop-on-429 handling, while preserving normal success for exhausted collections. The intentionally two-page `probe-next` command needs its own success definition.

### R09-F03 — cached proof omits retrieval provenance

**P3 advisory; does not block review approval.**

Location: `pagination_fix/crawl_public_catalog.py`, `load_initial`, `load_next`, and `main`, lines 323–370 and 953–965. `probe-next` can reuse both saved pages, write a newly dated `live_pagination_proof.json`, and report success without indicating cache reuse or original retrieval times in that receipt.

The cache-only counterexample returned `passed=true` with zero requests and an `at` value later than both retained page-fetch times. The README does disclose cache reuse, and the current published proof is corroborated by actual fresh requests at 17:24:32 and 17:24:36 UTC on 3 November 2026, followed by its proof at 17:24:40. This advisory does not invalidate that original proof.

**Repair:** distinguish proof execution time from response retrieval time; include per-page response hash, fetch time, and cache/fresh status in the proof receipt. A cache replay remains useful evidence and does not need a gratuitous network refetch.

## Evidence that supports the current publication

- All 45 frozen publication file hashes match the baseline manifest. Both crawler hash receipts and the workbook hash/size receipt match the actual published bytes.
- All five reduced fixture hashes and their retained original-response hashes match `fixture_manifest.json`. Reduced fixtures preserve the relevant continuation structure with four synthetic token values.
- Review 01's same-hash standalone replay passed 14/14 checks. Its independent replay of 22 retained playlist pages reproduced all 1,622 ordered appearances across ten playlists. Review 02 checked the 120 retained channel response pages. These existing observations were reused rather than broadly rerun.
- The fixture replay does not claim to re-create full channel enumeration. Workbook scripts explicitly identify themselves as execution provenance with historical layout/input requirements; that disclosed lack of standalone packaging is not a blocking finding.
- The structured scan of 31 published JSON/gzip files detected no excluded raw source/player/caption payload fields or credential/signed-media URL patterns. Four retained continuation tokens are synthetic fixture values. The workbook contains no VBA, embedded objects, or external workbook-link parts. This is a bounded publication inspection, not a general sensitive-data certification.

## Verification and limits

The observer is `observe_publication.py`; its sanitized receipt is `observations.json`. Run it from the retained research workspace using the primary Python runtime. It permits explicit `--crawler` and `--reporter` overrides for focused repair verification. Its raw cached inputs stay in temporary directories that are deleted afterward. This review made no network requests and changed no frozen source, shared output, original transcript, access setting, or remote repository.

No new hearing identity, source deduplication, English summary accuracy, or live channel-freshness claim is made by this review. Those are separate review scopes. Published current evidence is consistent; reporting and CLI failure propagation require repair before unrestricted reuse.
