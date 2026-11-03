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

The single workbook has seven tabs: **Summary**, **Transcripts**, **English summaries**, **Recording gaps**, **Videos**, **Crawl sources** and **Files**. Transcripts contains one row per distinct transcript or supplied segment, with concise evidence and clickable original Drive and YouTube links. English summaries provides a substantive account for each of the 93 records. Click an ID to move between the inventory and its summary. Seven hearing categories have distinct colors, explained by the Summary legend. Recording gaps identifies the exact material or verification needed for 15 records, with original links, case-file locators and a blank column for newly supplied recording links. Videos adds the reverse recording-to-source map and explicit scope decisions. Crawl sources records collection counts, pagination and unavailable-item accounting. Files retains links to all 116 originals, including alternate versions and supporting documents.

| Artifact | Purpose |
|---|---|
| [Excel workbook](JEP_transcript_inventory.xlsx) | Main inventory, 93 English summaries, category colors, confidence labels and original links. |
| [English summaries](english_summaries.json) | Named roles, purpose, attributed accounts and claims, responses, outcomes, source pointers and review limits for every record. |
| [Inventory CSV](inventory.csv) | The 93 transcript rows for filtering and reuse. |
| [Inventory JSON](inventory.json) | The same records, all grouped source IDs/links and verification details. |
| [Source manifest](source_manifest.json) | Recursive folder/file metadata and record assignments. |
| [Version comparisons](version_comparisons.json) | Twelve consolidation decisions and content-overlap measurements. |
| [Matching audit](matching_audit.json) | Additional review decisions and caption-anchor evidence. |
| [Recording gaps](recording_gaps.json) | Eleven unlocated recording records, two missing continuations and two content/coverage checks, with precise retrieval requirements. |
| [Completion review](completion_review.json) | Further search coverage, access evidence, corrected classifications and public judicial locators. |
| [Recording request draft](recording_request.md) | Spanish request naming the required sessions, parts and verification points. Prepared for review; not sent. |
| [Video coverage method](video_coverage_method.md) | Fixed Casanare scope, source pagination and the implemented two-way video/transcript audit. |
| [Pagination and reverse-audit report](reverse_audit_report.md) | Reproduced failure, live correction, final source accounting, reverse-map counts and residual limitations. |
| [Video inventory](video_inventory.json) | One row per reviewed video ID, with scope, source coverage, concise evidence and links. |
| [Reverse mapping review](reverse_mapping_review.json) | Detailed evidence for every admitted recording, known partial coverage and verified alternate uploads. |
| [Scope decisions](scope_decisions.json) | Casanare candidate inclusion/exclusion decisions; unresolved formats remain outside the confirmed corpus. |
| [Broad metadata scope register](broad_metadata_scope.json) | Every broad Case 03 playlist ID accounted for without admitting other territorial subcases. |
| [Crawl manifest](crawl_manifest.json) | Sources, successful pages, terminal states, unavailable positions and request accounting. |
| [Pagination implementation](pagination_fix/README.md) | Corrected crawler, sanitized replay fixtures and exact reproduction commands. |
| [Crawl readiness review](crawl_readiness_review.json) | Retained channel terminal-page checks, a missed Case 03 playlist continuation, and the Casanare playlist's hidden unavailable item. |
| [Summary JSON](summary.json) | Counts, categories and access notes. |

## Ten-review tieout

Ten independent subagent code reviews found 20 issues. The [review register](code_reviews/ten_review_summary.md) distinguishes existing-output corrections from guards for future runs and records reproduced failures and repair checks. The 93 record identities and all source-file assignments remain unchanged. Corrected duplicate measurements do not change consolidation decisions; native filters and exact clickable links were repaired and validated. All 74 challenged exclusion rationales now have specific case/territorial evidence.

The reverse map retains **128 included uploads: 83 linked to supplied records and 45 without supplied-source mappings**. Of those 45, **17 have bounded public-content identity/format checks and 28 remain metadata-based**. Two checked uploads are procedural installations/adjournments, and two are recorded questionnaire responses. Different dates and continuations are retained explicitly; 45 uploads is not a certified count of 45 additional unique hearings. **Four main-register candidates remain scope unconfirmed**, including the unavailable Casanare playlist item; the overlapping broad Case 03 register retains 13 unresolved IDs. See [tieout decisions](tieout_data_decisions.json) and the [updated reverse audit](reverse_audit_report.md).

## Evidence and findings

### English-summary method

Each summary is tied to its dated source transcript. It identifies principal named people and their roles, describes the session's purpose, separates admissions, denials and allegations, and records material responses and unresolved questions. Stated positions and conduct in the hearing are described; personality traits and private motives are not inferred. A later acknowledgment is not retroactively substituted for an earlier denial.

The summaries use the readable source documents, including the eleven records without a located public video. Long transcripts were selectively reviewed across their openings, substantial accounts, relevant challenges and closing passages. Short records were reviewed in full where the individual review note says so. This is not a line-by-line audit of all source text or independent audio verification, and the summaries are not audio-validated benchmark references. Each row states its own limits.

Evidence pointers use the source spreadsheet's **Order** values, source-local timestamps, or **P0001-style** labels for nonempty paragraphs in extracted document text, paired with searchable Spanish phrases where useful. Extracted paragraph labels are navigation aids, not printed paragraph numbers in the original. Timestamps in these pointers are source-local unless explicitly identified as YouTube times. Original-document links permit checking the underlying account. Personal contact details and identification numbers are omitted; protected source aliases remain protected. Principal names may be normalized against official JEP material when the transcription is inconsistent.

### Video verification

The final review freshly traversed JEP Colombia’s **2,663 Videos listings and 846 Live listings** across **118 pages**, with dated request receipts on 3 November 2026. One earlier Live listing is absent from the fresh list but remains playable; its procedural opening identifies Huila, so its historical discovery is retained outside Casanare. The older snapshots remain historical evidence, with their unknown original fetch times stated explicitly. Deeper checks resolved all 13 initial candidates and located four previously unmatched recordings. All 105 source transcript files were readable. The final public-interface check also accessed the Zamir recording that initially appeared to require sign-in. See the [summary](summary.json), [matching audit](matching_audit.json) and [source-accounting limits](reverse_audit_report.md).

Those channel listings were used to find matches for the supplied transcripts; they are not a count of Casanare hearings. The subsequent [reverse audit](reverse_audit_report.md) corrects the broad-playlist pagination defect, accounts for collection membership and compares each admitted video with the supplied inventory. Its coverage claim is bounded by the declared public sources and recorded scope/access uncertainties. Public Casanare videos can lack a supplied transcript even when the recording itself is readily available. A video-ID count is not a certified hearing or transcript count.

Public automatic captions were compared locally with source passages. Caption anchors and reported ranges are **approximate**; independent manual audio listening and exact spoken-word boundaries remain unverified. The 3 and 4 December 2024 hearings retain **metadata-only** matches because captions are unavailable on their public pages. Principal participant lists may be incomplete. These limitations appear in the [inventory](inventory.json).

Material findings in the [record evidence](inventory.json) include:

- **Casanare:** four recognition-hearing files cover 18 September 2023 morning/afternoon, 19 September morning and 20 September morning. Public-caption checks establish separate afternoon recordings on both 19 and 20 September, with no corresponding supplied transcripts located; see Videos and the [new content checks](new_content_checks.json).
- **Two proceedings in one upload:** the 6 December 2019 protective-measures hearing (`VV-030`) precedes the voluntary statement (`VV-029`), with a caption boundary near **50:36**. The source’s reserved label remains documented.
- **Date and name errors:** source filenames and video metadata contain errors resolved through recorded content. Solano’s recording repeatedly gives **27 July 2020**; the filename/footer and a court citation give **29 July**, so the conflict remains visible.
- **Time references:** Angarita’s transcript begins near video **24:05**, and Paguay’s near **17:41**. Aranguren’s **5:40:49** reference cites a different recording; his own closing matches near **5:24:44–5:24:52**.
- **A composite transcript:** `VV-071` contains Rodolfo Leal Galindo's sworn declaration on **12 and 20 August 2021**. The source closes the first session at P0246, opens the continuation at P0256 and closes it at P0512. Both sessions remain in one row linked to the complete original document; neither has a located public-video match.
- **Classification and submission date:** `VV-011` is Clovis Duque's **sworn declaration**, established by its opening and oath despite the template heading. `VV-022` is Sarmiento Valbuena's recorded extension **submitted on 22 July 2021**; its actual recording day is unverified. These corrections appear in the inventory and English summaries.
- **Written-continuation labels:** the Auto 055 annex uses this terminology for Pereira (`VV-056`) and Puentes (`VV-019`), whose source transcripts contain dialogue. Each follows an earlier written statement. The medium and publication history require clarification; the label does not establish that no recording exists. Pereira's source says **22 July 2020**, while one Auto 055 footnote says **29 July** and quotes matching content. Both dates were searched.
- **Access and protected identity:** the openings of `VV-064` and `VV-067` expressly describe private, reserved hearings and audio/video recording. Their later publication status remains unconfirmed. The [Auto 055 annex](https://es.scribd.com/document/649822528/Anexo-Auto-SRVR-SUB-D-055-14-julio-2022), Table 5, p. 21, entry 6 and footnote 5, records identity protection for the `VV-065` declarant. NRAS/XYZ remain unexpanded labels for that declarant; the identity-protection order does not establish that the entire recording is nonpublic.
- **Source-quality issues:** `CAS03-20230920-AM` Order 49 contains unrelated parliamentary/mental-health discussion labelled `NO_SUSTANTIVO`; it is excluded from the English summary. The March and April 2026 sources contain inconsistent location or template headings, so the summaries identify the proceeding from the spoken opening. Such text should be reviewed against source audio before use as reference transcription.

## Remaining gaps and original sources

Public matching remains incomplete. **Eleven transcript records have no located public recording.** In two verified matches, the available upload omits approximately the final third of `VV-015` and final tenth of `VV-038`. Their rows explicitly flag **PARTIAL COVERAGE**. The earlier recording-retrieval review supplied precise missing-asset locators and corrected metadata. The subsequent reverse audit verified one alternate upload for an already matched source and identified additional public recordings without a supplied-source mapping; it did not resolve these eleven recording-side gaps.

The recording-side dependencies are recorded individually in **Recording gaps**. The separate **Videos** tab identifies supplied-source gaps; these two directions must not be added together. The reverse pass also verified a second upload of the 5 July 2019 Marco Fabián García Céspedes procedural session, linking it to existing record `VV-057`; it does not create a new transcript row.

The recording-side dependencies include:

- **VV-015:** continuation after the public upload ends around **03:56:20**, during source P0758, through P1076, including the later **15:48 hearing-clock restart**. The supplied source has no formal close.
- **VV-038:** final segment after the public upload ends around **07:09**, from the remainder of P1411 through the **18:32/18:33 hearing-clock close** at P1495. P1496–P1528 is an appended participant roster.
- **Sworn declarations:** the published evidence index places Duque, Mojica, Leal, NRAS/XYZ and Páez in **Cuaderno territorial de la Br16**, with entry numbers recorded in the gap rows. Leal also has a **Cuaderno General Décimo Sexta Brigada** reference; the two names have not been established to identify the same volume. No individual recording filenames or public playback links were supplied by that index.
- **3/4 December 2024:** identified uploads need usable captions or playable recording content to verify the opening and source-ending offsets. For 4 December, the saved `t=38031s` position is not a verified transcript boundary.

The [Spanish request draft](recording_request.md) asks the source owner or recording custodian for these exact assets and their access status. It has **not been sent**. For case-file copies and access, the [JEP's published instructions](https://www.jep.gov.co/ServicioAlCiudadano/Paginas/preguntas.aspx), questions 41–42, direct requests to the relevant Secretaría Judicial and specify access by the person concerned, their representative or someone expressly authorized. Public or redacted recording links can be supplied where available. A missing search result does not prove permanent nonpublication.

Sources: [Datos](https://drive.google.com/drive/folders/1uP7V1HzzWd78VSk39NS-EYqKW1KAl16I), [Casanare recognition hearings](https://drive.google.com/drive/folders/1H_k2zlJ_VZbCyDBybZP9JKv5xqpjZ53h), and [versiones voluntarias transcripts](https://drive.google.com/drive/folders/15Xxxz53sCe2xQ6OJbWR_7FEX3-9Hf4uj). These outputs publish metadata, English summaries, concise evidence pointers and original links. Full source transcripts remain in Drive with their existing access settings.
