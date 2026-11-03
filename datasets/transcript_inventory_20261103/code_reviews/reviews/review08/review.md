# Review 08 — workbook projection, links and acceptance gate

**Independent completed review. Verdict: request changes for three bounded workbook/gate defects; no current count or source-link correction found.**

Reviewed published commit `620cc5eb85860ff77a837058903321876de82b15` through the frozen snapshot in `tieout_review_20261103/base`. All findings below describe that snapshot, before any repair. No canonical or frozen files were changed during review. Review-only evidence and the deliberately damaged test workbook are confined to `reviews/review08/`.

## Contract and boundary

The workbook must preserve one row per supplied transcript/segment, every requested field and original document pointer, all supplied source files, and every forward/reverse recording relationship. Counts must distinguish source records, uploads and coverage gaps. Category colors, frozen headings, native hyperlinks, cached formulas and source dates must survive XLSX export. Acceptance must detect the same defects it claims to exclude.

Scope: `workbook_build/build_workbook.mjs`, `add_native_links.py`, `validate_outputs.py`, the actual XLSX ZIP/XML and corresponding JSON projections. All three source files were read in full. This review tests workbook representation and acceptance; it does not independently establish transcript/audio identity, legal conclusions or English-summary factual accuracy.

## Findings

### R08-01 — third and later links are silently lost

**P2; reusable builder defect, not observed data loss in the current workbook.** `build_workbook.mjs` lines 59–68 handles exactly one or exactly two transcript video URLs. With three URLs, neither branch runs: even the primary recording has no registered native hyperlink. Lines 166–168 retain all reverse transcript IDs as text, but write direct original-document links for only the first two.

**Counterexample:** executed the exact builder body with in-memory range/export/IO sinks. Appending `https://www.youtube.com/watch?v=TESTVIDEO03` to VV-057's existing two URLs produces zero registered video links. Giving video `eM8ZrqhZbgQ` the three source IDs VV-029, VV-030 and VV-028 preserves three IDs as text but registers only two source URLs. The actual dataset has at most two links in either direction, and all its 84 relationships survive today.

**Smallest repair:** always write the primary and second links; add third-and-later native-link columns only when required, and extend the table/style range. An explicit unsupported-cardinality rejection would also prevent silent corruption, but dynamic columns preserve the requested many-to-many map.

**Observer:** `observe_link_cardinality.mjs`; result `link_cardinality_observations.json`. A passing repair must retain every expected URL at cardinalities 0, 1, 2, 3 and above without widening the current workbook unnecessarily.

### R08-02 — a missing transcript-to-video hyperlink still passes acceptance

**P2; acceptance defect, not a missing link in the published workbook.** `validate_outputs.py` lines 30–36 compare transcript cell values, while lines 48–50 check original Drive links and the Videos tab's own YouTube links. They never compare the native video hyperlink targets attached to the transcript row, nor the reverse original-document links against every `source_links` edge.

**Counterexample:** removed only the native `<hyperlink ref="J2">` node from an isolated workbook copy. VV-028's displayed YouTube URL and all cell values stayed unchanged. The exact frozen validator returned exit code 0 and `all_passed: true`; the missing `https://www.youtube.com/watch?v=o_BvyjJigOE` link was not rejected.

**Smallest repair:** derive each transcript's expected URL list from `inventory.json` and compare it with its native video-link targets; compare each video's expected source URLs with its reverse native links. Identify records by ID, not unvalidated row assumptions. Include dynamically added link columns.

**Observer:** `observe_missing_link_gate.py`; result `missing_link_gate_observations.json`. The same one-node deletion must fail after repair. The synthetic workbook is a test input, not research output, and should not be published with the inventory.

### R08-03 — tables have no serialized filter definitions, but the gate says they do

**P2; present artifact/gate defect with no effect on research counts.** All six data sheets contain a table and frozen headings, but neither the worksheet nor its table contains an AutoFilter definition. The table-creation sites are `build_workbook.mjs` lines 49, 95, 120, 159, 185 and 205. The postprocessor does not add filter definitions. `validate_outputs.py` line 63 nevertheless labels its table-existence/freeze check “filters and frozen headings.”

**Concrete evidence:** all six `xl/tables/table*.xml` parts omit `<autoFilter>`; read-only inspection reports `table.autoFilter is None` and `worksheet.auto_filter.ref is None`. Expected table ranges are A1:N94, A1:K94, A1:I16, A1:P208, A1:J15 and A1:G117. `inspect_workbook.py` independently checks those ranges and fails exactly these six checks after passing the data/link/count checks.

**Smallest repair:** serialize a table `<autoFilter ref="…"/>` matching each table's full range, through the export API or the existing native XML postprocessor. Validate the actual serialized range, not merely the presence of a table. This review does not claim to have opened desktop Excel or tested application-specific automatic repair.

**Primary reference:** Microsoft documents AutoFilter as the SpreadsheetML collection that expresses filter settings, with `table` among its parent elements: https://learn.microsoft.com/en-us/dotnet/api/documentformat.openxml.spreadsheet.autofilter?view=openxml-3.0.1 . See also https://learn.microsoft.com/en-us/office/open-xml/spreadsheet/working-with-tables .

## Positive observations on the actual workbook

The frozen workbook contains seven sheets: Summary, Transcripts, English summaries, Recording gaps, Videos, Crawl sources and Files. The main transcript table has all 14 declared columns, including every user-requested field. There are 93 source records, 93 English-summary rows, 116 original source files, 15 recording-gap rows and 207 video rows. The reverse map admits 128 uploads; 83 link to supplied records through 84 edges. These are different units and are not interchangeable unique-hearing counts.

Independent read-only inspection compared 5,497 projected field values, 243 hearing-date values, 207 duration values, all 116 source modification times, all 93 forward link lists and all 207 reverse link lists. Source modification times agree within 1 ms of Excel serial-date rounding, and their displayed calendar dates are preserved. No source timestamp was replaced by the review date. The summary's as-of date matches the frozen 3 November 2026 build; it is not a claim that channel data were freshly retrieved then.

All 93 transcript originals, 116 Files originals and 93 summary-original links are present. All 84 transcript-to-video edges and 84 reverse source edges match JSON input. The workbook contains 725 external and 395 internal hyperlinks. All internal destinations resolve and carry the expected record ID where applicable; duplicate native hyperlink cell references were not found. Current two-link rows and the two-source video retain both direct targets.

All 22 cached formula values agree with independently counted inputs, including the 93 source records, 82 high-confidence records, 80 content-checked records, 11 unmatched source records, 128 included uploads, 83 uploads linked to source text, six partial-source uploads, four content-checked/no-source uploads, 41 metadata/no-source uploads, seven scope-unconfirmed candidates and 72 exclusions. No formula cell occurs outside Summary in the current artifact. This checks the current delivered data; it is not a general proof for arbitrary hostile future strings.

The seven category colors and the video-category aliases agree across all 816 inspected A/B cells. All six data sheets have the intended frozen panes and one table spanning their data. English summaries preserve named people/roles, purpose, claims, responses, outcomes, evidence pointers and review limits from the source JSON. Evidence remains concise data rather than embedded source documents. Formatting and native-link processing have not changed source file bytes.

## Evidence and reproduction

- `inspect_workbook.py` → `workbook_observations.json`: actual artifact projection, native links, formulas, colors, dates, tables and filter definitions. It deliberately exits 1 on the six missing filters in the frozen workbook.
- `observe_link_cardinality.mjs` → `link_cardinality_observations.json`: exact builder link-registration code, with no artifact generation.
- `observe_missing_link_gate.py` → `missing_link_gate_observations.json`: exact validator against a ZIP/XML-mutated review-only copy; no openpyxl write/save operation.
- Python and Node came from the primary runtime. Node v24.22.1. No package installation or full artifact build was required.

## Frozen hashes

| File | SHA-256 |
|---|---|
| workbook_build/build_workbook.mjs | b12a5d8b38b1e541aa8ed7321f2029b3d4db31f3e0a5987810be554eaf19cae1 |
| workbook_build/add_native_links.py | 3bc91c3e7cd0afdc3d2a34c90cf5dc5d2f011bdde4360d786c1802fb7062a5ce |
| workbook_build/validate_outputs.py | b7225b038883384433ea0b56e6a5e241d966f4f5b3dd6b136bd855240252de2f |
| JEP_transcript_inventory.xlsx | b1715e2102adabf278ea36d406f06f2147555a5906d1368015e57a570d241cee |

Frozen files retained these hashes after review. Repairs, if performed, belong to a separate rework receipt and do not alter this review verdict or its baseline evidence.
