# Review 05 — Reverse mapping and coverage decisions

**Verdict: Request changes.** The two P2 findings concern reusable generation code. The frozen published counts and links reconcile; neither counterexample establishes an error in the current 128/83/45 totals.

## Reviewed state and boundary

Reviewed published commit `620cc5eb85860ff77a837058903321876de82b15`: `workbook_build/assemble_outputs.py`, the reverse review, inventory, video inventory, and supporting scope/summary inputs. The working `inventory_work/reverse_audit/build_mapping_review.py` was also read in full and frozen separately. Its SHA-256 is `f409e2bc23f999f55e4363f083c116cb56af2c3f556f47aeaba827837921a0e1`; the assembler SHA-256 is `ec06e9fbe1a5afc2aee19020b70e173351013e7b0495719b4449f8b2d7dbcaed`. All inspected input hashes are in `reviewed_hashes.json` and `review.json`.

The principal invariants are preservation of every transcript–video edge, conservative treatment of unlinked uploads, and separation of source omissions, recording omissions, content checks and metadata-only decisions. Scope admission, fresh enumeration and workbook rendering belong to separate reviews.

## Findings

### R05-F1 — P2: an established forward edge can disappear from the reverse map

**Location:** `workbook_build/assemble_outputs.py`, `main`, lines 79 and 101–104.

`review_by_id` silently overwrites duplicate video IDs. The later join checks whether a returned transcript ID exists, but does not check whether all established source-to-video links were returned.

The smallest reproduced mutation removes `VV-029` from the reverse row for `eM8ZrqhZbgQ`, retaining `VV-030`. The actual assembler accepts this input and writes **83 reverse edges against 84 forward edges**. Appending a second review row for the same video, containing only `VV-030`, causes the same loss. The two source documents describe different segments of one upload, so this is a lost relation rather than legitimate deduplication.

**Repair:** reject duplicate reverse video IDs before indexing. After applying explicit forward corrections, compare the complete `(transcript ID, video ID)` edge sets and reject missing or unexplained extra edges before writing outputs.

**Observer:** `observe_reverse_join.py` runs the exact assembler against isolated copies. Its unchanged baseline preserves all 84 edges; `missing_reverse_edge` and `duplicate_reverse_id` demonstrate the defect. Both mutations should be rejected after repair. This blocks approval of the reusable assembler, while the current published edge sets remain equal.

### R05-F2 — P2: unlinked upload identity becomes a no-transcript disposition automatically

**Location:** working `inventory_work/reverse_audit/build_mapping_review.py`, the `absent` selection at line 126 and candidate construction at lines 133–151.

Every included upload without an exact existing video-ID link initially receives `No supplied transcript located for public-metadata session`. Same-person source records are appended as notes, without changing that disposition. The verified alternate `FoAy5Qfphcs` works through a later explicit exception.

The observer supplies a synthetic unlinked upload with **Marco Fabián García Céspedes and 5 July 2019**, exactly matching `VV-057` metadata. The actual builder loop finds `VV-057` among related sources, yet still assigns the no-transcript status without a content check or source anchor. Absence of an exact upload ID does not establish absence of a supplied transcript.

**Repair:** begin unlinked uploads at `Coverage unconfirmed` and promote them only from an explicit reviewed session comparison. At minimum, retain same-principal/date ambiguities generically rather than protecting only hardcoded IDs.

**Observer:** the `unlinked_candidate` case in `observe_reverse_join.py` executes the actual loop without its external I/O. The candidate should remain unresolved until its recording relationship is reviewed. This is a risk for newly admitted uploads; no exact principal/date collision was found among the current 41 metadata-based gaps.

## Current data reconciliation

| Quantity checked independently | Result |
|---|---:|
| Included uploads | 128 |
| Uploads linked to supplied transcripts | 83 |
| Unlinked uploads | 45 |
| Unlinked, content checked in frozen snapshot | 4 |
| Unlinked, metadata basis in frozen snapshot | 41 |
| Known partial supplied-source coverage | 6 |
| Forward transcript–video edges | 84 |
| Reverse transcript–video edges | 84 |
| Exact edge-set disagreement | 0 |

The shared upload `eM8ZrqhZbgQ` preserves both `VV-029` and `VV-030`. The second `VV-057` upload remains distinct. The six partial-source labels count omitted supplied text; `VV-038` instead explicitly records a missing public continuation, and `VV-015` documents gaps in both directions. The two metadata-only source matches are not labelled content checked.

All 41 metadata-based gap rows were compared against the source participant/date index. The direct same-principal supplied candidates are `w49HGaeBNRk` against `VV-017`/`VV-018`, and `eKrYlu79rGo` against `VV-041`; their dates differ. Recognition-hearing mentions of those people do not cover their earlier individual statements. `metadata_gap_audit.json` records each comparison. This is an index audit, not proof that all 41 recordings are unique hearings.

## Additional bounded content checks

The parent supplied two newly exported public caption files during the review. These observations are later than the frozen baseline and are saved separately in `priority_content_checks.json`. No canonical row was changed by this reviewer.

- **`w49HGaeBNRk`: distinct procedural installation/adjournment.** The complete 274-cue export runs to 11:09 with no truncation marker. The opening at 00:50–01:06 identifies an 08:40 continuation for Toro on **15 May 2019**. At 06:33–07:05, the proceeding is declared unable to go ahead because defense counsel is absent. The supplied records instead open on 20 February (`VV-017`, P0008) and 27 June (`VV-018`, P0005). Exact-text overlap concerns procedural introductions. **Retain a date conflict:** the closing automatic caption at 10:52–11:09 gives **14 May**, while the opening and title give 15 May. Audio has not resolved that discrepancy.
- **`eKrYlu79rGo`: distinct recorded questionnaire supplement.** The complete 999-cue export runs to 44:32. At 00:08–01:02, counsel dates the recording **15 October 2019** and explains that written questionnaire responses are supplemented on video for question 14. The closing at 44:13–44:25 gives the same date and 15:45. `VV-041` P0001 instead opens the virtual magistrate-led hearing on 27 July 2020. No exact 12-word match was found across this caption export and `VV-041`; the dated openings, different setting and recording format provide the substantive distinction.

Both checks support moving those two upload dispositions to content-checked absence relative to the supplied candidates, with the format and date limitations retained. They do not create new source transcripts or establish an audio-validated reference.

## Evidence and limits

`observations.json` records the successful baseline and three intentionally failing invariant checks. The observer exits 1 while those defects remain. Its `observer_outputs/` directory contains synthetic mutated projections and should not be published as research data.

No network calls or shared/canonical mutations occurred. No full source text is included in this report. All timestamp observations rely on automatic captions; no independent audio listening was performed. The review does not certify 45 additional unique hearings or full transcription coverage.
