# JEP transcript inventory

This directory inventories Valentina’s Datos transcripts and their public YouTube matches as of **3 November 2026**. Open the [Excel workbook](JEP_transcript_inventory.xlsx) for the complete inventory.

## Counts and coverage

The recursive [source manifest](source_manifest.json) covers **116 files across 10 folders**: 105 transcript files, nine supporting legal PDFs and two link/index documents. The 105 transcript files resolve to **93 distinct records**, with every file assigned once. Twelve additional versions were consolidated: 11 alternate transcriptions and one set of condensed notes. The [version comparisons](version_comparisons.json) record the content evidence behind those decisions.

| Public-video match status | Records |
|---|---:|
| High — public captions checked | 80 |
| High — metadata only | 2 |
| Unmatched | 11 |
| Unresolved candidates | 0 |

**The 82 high-confidence matches include 80 checked against public captions. Two of these 80 cover partial public recordings.** Confidence establishes the identity of the matched recording; coverage notes identify missing portions. [Summary counts](summary.json) and [record evidence](inventory.json) preserve this distinction.

## Workbook and companion files

The single workbook has four tabs: **Summary**, **Transcripts**, **English summaries** and **Files**. Transcripts contains one row per distinct transcript or supplied segment, with concise evidence and clickable original Drive and YouTube links. English summaries provides a substantive account for each of the 93 records. Click an ID to move between the inventory and its summary. Seven hearing categories have distinct colors, explained by the Summary legend. Files retains links to all 116 originals, including alternate versions and supporting documents.

| Artifact | Purpose |
|---|---|
| [Excel workbook](JEP_transcript_inventory.xlsx) | Main inventory, 93 English summaries, category colors, confidence labels and original links. |
| [English summaries](english_summaries.json) | Named roles, purpose, attributed accounts and claims, responses, outcomes, source pointers and review limits for every record. |
| [Inventory CSV](inventory.csv) | The 93 transcript rows for filtering and reuse. |
| [Inventory JSON](inventory.json) | The same records, all grouped source IDs/links and verification details. |
| [Source manifest](source_manifest.json) | Recursive folder/file metadata and record assignments. |
| [Version comparisons](version_comparisons.json) | Twelve consolidation decisions and content-overlap measurements. |
| [Matching audit](matching_audit.json) | Additional review decisions and caption-anchor evidence. |
| [Summary JSON](summary.json) | Counts, categories and access notes. |

## Evidence and findings

### English-summary method

Each summary is tied to its dated source transcript. It identifies principal named people and their roles, describes the session's purpose, separates admissions, denials and allegations, and records material responses and unresolved questions. Stated positions and conduct in the hearing are described; personality traits and private motives are not inferred. A later acknowledgment is not retroactively substituted for an earlier denial.

The summaries use the readable source documents, including the eleven records without a located public video. Long transcripts were selectively reviewed across their openings, substantial accounts, relevant challenges and closing passages. Short records were reviewed in full where the individual review note says so. This is not a line-by-line audit of all source text or independent audio verification, and the summaries are not audio-validated benchmark references. Each row states its own limits.

Evidence pointers use the source spreadsheet's **Order** values, source-local timestamps, or **P0001-style** labels for nonempty paragraphs in extracted document text, paired with searchable Spanish phrases where useful. Extracted paragraph labels are navigation aids, not printed paragraph numbers in the original. Timestamps in these pointers are source-local unless explicitly identified as YouTube times. Original-document links permit checking the underlying account. Personal contact details and identification numbers are omitted; protected source aliases remain protected. Principal names may be normalized against official JEP material when the transcription is inconsistent.

### Video verification

The search covered the JEP Colombia channel’s complete available **2,663 Videos listings and 847 Live listings** as of the review date. Deeper checks resolved all 13 initial candidates and located four previously unmatched recordings. All 105 source transcript files were readable. The final public-interface check also accessed the Zamir recording that initially appeared to require sign-in. See the [summary](summary.json) and [matching audit](matching_audit.json).

Public automatic captions were compared locally with source passages. Caption anchors and reported ranges are **approximate**; independent manual audio listening and exact spoken-word boundaries remain unverified. The 3 and 4 December 2024 hearings retain **metadata-only** matches because captions are unavailable on their public pages. Principal participant lists may be incomplete. These limitations appear in the [inventory](inventory.json).

Material findings in the [record evidence](inventory.json) include:

- **Casanare:** four recognition-hearing files cover 18 September 2023 morning/afternoon, 19 September morning and 20 September morning: four sessions across three dates. The folder omits 19 September afternoon.
- **Two proceedings in one upload:** the 6 December 2019 protective-measures hearing (`VV-030`) precedes the voluntary statement (`VV-029`), with a caption boundary near **50:36**. The source’s reserved label remains documented.
- **Date and name errors:** source filenames and video metadata contain errors resolved through recorded content. Solano’s recording repeatedly gives **27 July 2020**; the filename/footer and a court citation give **29 July**, so the conflict remains visible.
- **Time references:** Angarita’s transcript begins near video **24:05**, and Paguay’s near **17:41**. Aranguren’s **5:40:49** reference cites a different recording; his own closing matches near **5:24:44–5:24:52**.
- **A composite transcript:** `VV-071` contains Rodolfo Leal Galindo's sworn declaration on **12 and 20 August 2021**. The source closes the first session at P0246, opens the continuation at P0256 and closes it at P0512. Both sessions remain in one row linked to the complete original document; neither has a located public-video match.
- **Source-quality issues:** `CAS03-20230920-AM` Order 49 contains unrelated parliamentary/mental-health discussion labelled `NO_SUSTANTIVO`; it is excluded from the English summary. The March and April 2026 sources contain inconsistent location or template headings, so the summaries identify the proceeding from the spoken opening. Such text should be reviewed against source audio before use as reference transcription.

## Remaining gaps and original sources

Public matching remains incomplete. **Eleven recordings are unlocated.** In two verified matches, the available upload omits approximately the final third of `VV-015` and final tenth of `VV-038`. Completing coverage requires the missing original public-recording URLs or continuations. Their rows explicitly flag **PARTIAL COVERAGE**.

Sources: [Datos](https://drive.google.com/drive/folders/1uP7V1HzzWd78VSk39NS-EYqKW1KAl16I), [Casanare recognition hearings](https://drive.google.com/drive/folders/1H_k2zlJ_VZbCyDBybZP9JKv5xqpjZ53h), and [versiones voluntarias transcripts](https://drive.google.com/drive/folders/15Xxxz53sCe2xQ6OJbWR_7FEX3-9Hf4uj). These outputs publish metadata, English summaries, concise evidence pointers and original links. Full source transcripts remain in Drive with their existing access settings.
