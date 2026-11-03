# Review 03 — Scope decisions and projection

**Reviewed state:** published commit `620cc5eb85860ff77a837058903321876de82b15`, frozen under `inventory_work/tieout_review_20261103/base`.

**Verdict: Request changes.** One current evidence/classification defect blocks the claim of a completed scope audit. A second, reproducible consistency gap affects subsequent updates. No confirmed admission of an outside territorial case was found.

## Scope and invariants

Reviewed the scope and broad metadata registers, their projected Videos data, `assemble_outputs.py`, and the crawler's `export_all`/`web_seed` paths and HTML/link helpers. The boundary is Case 03–Casanare and directly related proceedings already within the supplied corpus. A person name or broad Case 03 membership cannot establish inclusion. An exclusion also needs affirmative territory or recording-format evidence. The broad and main scope registers must agree before publication.

The inspection was offline. It made no network requests, reviewed no other-case testimony, changed no canonical files and published nothing. Exact file hashes are in [review.json](review.json).

## R03-F1 — Unsupported non-hearing exclusions suppress 74 candidates

**P1; blocks approval of the completed-scope claim.**

`broad_metadata_scope.json` assigns 74 of its 114 `non_hearing_or_context` rows the same evidence sentence asserting that their titles identify contextual, explanatory, commemorative or announcement material. Their titles instead identify dated named people or units, often in multi-hour recordings. All 74 lack a catalog description and checked regional-playlist membership. These rows therefore never enter the published set of 13 broader scope uncertainties.

Concrete examples:

| Video ID | Published title or subject | Listing duration | JSON record begins |
|---|---|---:|---:|
| `BHfnWY4b_mI` | `20240909 · Félix Juan Carlos Araque Leal` | 1:59:07 | line 3915 |
| `WGhhJLrHEeo` | Yair Rodríguez, Richard Barroso and Manuel Echavarría, 27 Aug 2021 | 9:15:22 | line 11312 |
| `K_IXrokQqnM` | Case 03, Jaime Coral Trujillo, BCG79, 25 Feb 2020 | 3:42:35 | line 7302 |
| `Lv387B0laD0` | Recognition of truth by Efraín Prada, former BCG79 commander | 48:48 | line 7854 |

Duration alone does not prove a primary hearing. It also cannot supply the missing affirmative evidence that these are contextual material. The bare name/date title for `BHfnWY4b_mI`, for example, does not support the published non-hearing rationale at all.

The same issue covers many dated Case 03–04 recordings concerning BCG79, BCG26 and BRIM11, and three long `Invitación Caso04` recordings. They may be properly excluded for another case or territory, but that is a separate conclusion requiring its own evidence. The assembler copies this register at lines 196–197 and reports its totals at line 182; it does not supply or validate that missing basis.

**Repair:** perform bounded public-description or territorial-membership checks for the [74 exact IDs](scope_risk_candidates.json). Retain an exclusion where affirmative metadata supports it and state that reason; otherwise use `scope_unconfirmed`. None should be admitted to Casanare just because this review challenged its exclusion. Replace the catch-all non-hearing rationale with specific evidence.

**Observer:** every listed row must gain a concrete supporting pointer or remain explicitly unresolved. The four examples above must not retain their current format classification solely from their recorded titles. This finding does not establish that the positively admitted count of 128 is wrong; it means the broader exclusion and residual-review claims are not yet supported.

## R03-F2 — Scope files can contradict each other without stopping assembly

**P2; no current-data mismatch observed.**

At `assemble_outputs.py:74`, the broad register is loaded. At line 96, the output loop iterates only the main scope register. At line 182, broad counts are copied independently. No check requires broad inclusions to reach the main map or requires overlapping decisions to agree.

The [offline observer](observe_scope_join.py) runs the actual assembler with isolated outputs and clearly marked synthetic input changes:

- Promoting broad-only `j7YryvmCbBw` and adding a reverse review succeeds, reports 97 broad inclusions, but leaves the admitted Videos view at 128 with no row for that ID.
- Changing `O25PKSrxRuA` to excluded only in the broad register succeeds while Videos still marks it Included.

The original inputs are consistent; these synthetic fixtures are **not research reclassifications**. They demonstrate that a legitimate later scope correction can be silently omitted or contradicted during this tie-out work.

**Repair:** before any output writes, require broad included IDs to be included in the main scope, require shared scope decisions to agree, and require a reverse review for every admitted ID. Raise a targeted consistency error on violation.

**Observer:** the two inconsistent fixtures must be rejected while the unchanged baseline inputs pass. [Observed results](scope_join_observer.json) record the current failure.

## Checks that passed

The 207 main rows agree with the Videos projection: 128 included, 72 excluded and seven uncertain. All 96 included broad-playlist IDs appear in the main register. All overlapping scope decisions agree. No main, broad or video IDs are duplicated. Every existing transcript-to-video link is admitted. All recorded regional memberships agree with actual membership rows; none of the 128 admitted IDs appears in the five other-region playlists.

All discovery entries mentioning Casanare, Yopal, Brigada XVI/16, Sixteenth Brigade or Torres Escalante in their available titles/descriptions have a main disposition. The five unique official web-card video IDs are represented, and inconsistent card-heading dates remain separate provenance rather than overriding checked video identity. These checks support the existing positive inclusions but do not fix the unsupported broad exclusions above.

## Residual limits

No new geographic or recording-format facts were established from external sources here. The parent is separately resolving the two memorial events using newly obtained official event descriptions; excluding those public memorial-implementation events under the fixed hearing/statement boundary is reasonable if that evidence remains attached.

No production repair was made. The parent owns corrected data, implementation, focused verification and publication.
