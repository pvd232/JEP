# Review 06 — timestamps and directional coverage

**Verdict: Approve the current published temporal projection. One nonblocking P2 duration-input defect is recommended for repair.** No current timestamp, date, duration or directional-gap count discrepancy was found.

Reviewed frozen commit **`620cc5eb85860ff77a837058903321876de82b15`**. Exact file hashes and supporting local-evidence hashes are recorded in [review.json](review.json). This review inspected the duration/offset/coverage projections in `workbook_build/assemble_outputs.py`, date/time and summary handling in `workbook_build/build_workbook.mjs`, the reverse review and gap records, and the resulting workbook. It did not make network requests, listen to audio, or alter shared code/data.

## Finding

### R06-01 — malformed clock components become plausible durations

**P2; nonblocking for the existing dataset.** `assemble_outputs.py:36–45`, `seconds`, accepts any two-digit minute/second component without checking its range:

| Input | Observed result | Required handling |
|---|---:|---|
| `1:99` | 159 seconds | Unknown/rejected |
| `04:60:00` | 18,000 seconds | Unknown/rejected |
| `01:00:60` | 3,660 seconds | Unknown/rejected |

The caller at lines 143–144 can select this value as the video duration; `build_workbook.mjs:152,158` then renders it as an ordinary elapsed duration. For example, `1:99` becomes `0:02:39`, concealing the malformed metadata.

**Smallest repair:** require the final seconds component to be below 60 and, for three-component inputs, the middle minutes component to be below 60. Return `None`, consistent with the existing unparseable-input behavior, or raise a specific validation error. Preserve unbounded hours and legitimate minute-based two-component durations.

[The focused observer](observe_temporal_projection.py) uses the actual converter. With `--require-fixed`, the frozen version exits 1 solely for these counterexamples; all published-data checks pass. It accepts `--assembler PATH` so the repair can be checked without changing the frozen review snapshot.

## Existing evidence checked

All **197 nonempty video duration cells**, **152 video dates**, **93 source dates**, and **87 populated video timestamp cells** reproduce their JSON values. Durations retain Excel’s `[h]:mm:ss` format, avoiding a 24-hour clock wrap. The Summary formula correctly counts **six known partial supplied-transcript records**.

| Source | Retained source/caption evidence | Result |
|---|---|---|
| VV-012 | P0004–P0005; approximately 00:24:05 opening and 09:53:58–09:54:24 close | Opening formalities omitted; approximate public offsets preserved. |
| VV-015 | P0004–P0008, P0757–P0758, P1015; public 00:21:57 and 03:55:16 | Summarized opening and missing later recording are correctly kept as two gap directions. Hearing clock 14:10 is distinguished from elapsed 03:55:16. |
| VV-016 | P0008/P0072; public 03:20:51–03:58:03 | Supplied afternoon segment is distinguished from the missing morning transcript portion. |
| VV-025 | P0011/P0684; public 00:09:53–03:13:03, with later close at 03:16:52–03:17:03 | The source’s counter is not substituted for the public offset; omitted opening and closing exchanges are supported. |
| VV-047 | P0007–P0008; public 00:17:41 opening and 05:45:04–05:45:27 close | Omitted installation is supported. |
| VV-053 | P0004–P0006; source explicitly starts transcription at 03:06, first aligned cue 03:08 | Summarized presentation is supported; cue precision is appropriately qualified. |
| VV-038 | P1411/P1495; public ends during the answer at approximately 07:09:00 | Later source text through the 18:32/18:33 hearing-clock close is a missing **recording continuation**. It is not added to the six missing supplied-source portions. |
| VV-029 / VV-030 | Shared upload around 00:49:56–00:51:26 | Distinct protective-measures and voluntary-statement segments meet near the approximate 00:50:36 caption cue. Both source links remain. |
| VV-071 | P0246/P0256/P0512 | Both 12 and 20 August 2021 remain in the source row; the clocks 16:01, 08:07 and 11:11 are explicitly not YouTube offsets. |

Two apparent duration overruns from an automatic string scan are explicitly labeled exceptions, not defects: VV-052 identifies its longer **source-local counter**, and the JEP reupload of the March 2026 hearing retains separately labeled **Radio Nacional** ranges alongside its own shorter offsets. No source/video date conflict was found among the existing links.

## Limits

The original captions and source passages support these identity and boundary checks. They do not establish exact audio word boundaries, full recording equivalence, or verbatim coverage of every introduction, recess and audiovisual insert. The code and workbook retain that qualification. The December 2024 rows remain metadata-only with unverified offsets. The four new-content-check records were reviewed for internal timing consistency and their stated limits, without new audio listening or caption export.

The count of six describes **known** supplied-source omissions supported by the review. It does not certify full transcription of every other admitted upload.

Only this review’s files were written. Frozen and production files, original transcripts and shared caches were unchanged.
