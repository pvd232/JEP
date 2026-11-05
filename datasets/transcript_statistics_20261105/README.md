# JEP Casanare: meeting statistics

Revised after ten independent reviews on 5 November 2026. The supplied corpus contains **93 consolidated transcript/session records**, from **105 transcript source files**, spanning August 2018–April 2026. Records include individual statements, recorded submissions, split sessions and multi-day hearings. All describe the Casanare subcase of Case 03.

**The earlier participant averages are withdrawn.** They averaged incomplete speaker minima across document records. Six record-level counts required correction, and the speaker metric answered a different question from attendance. The [review and corrections](PARTICIPANT_AUDIT.md) document the findings.

| Measure | Result | Denominator |
|---|---:|---|
| Mean rendered document length | **71.5 pages** | 79 of the 79 Word/ODT records |
| Median rendered document length | **70 pages** | Same rendered documents |
| Rendered document length range | **3–164 pages** | Same rendered documents |
| Total rendered pages | **5,646** | Same rendered documents |
| Extracted text | **3,068,242 words** | All 93 records |
| Mean text length | **32,992 words** | All 93 records |
| Mean length at 500 words/page | **66.0 page equivalents** | All 93 records |
| Principal deponent in individual statements/submissions | **1 per record** | 67 records; procedural status is qualified separately |

## Counting people

The source reviews support **148 victim-speaker person–record occurrences** and **225 source-supported compareciente-speaker occurrences** as minima. One further principal deponent has a disputed compareciente designation and retains an unknown role count. Five sworn witnesses have a separate role; one witness's own-harm testimony has a secondary flag. These totals describe identified contributors in the supplied text.

The [person evidence ledger](participant_evidence.json) contains 379 pseudonymous person–record occurrences and representative source coordinates. Each established alias counts once within a record. Introductions count; repeated turns merge. Eleven recorded submissions retain their recording mode. Lawyers speaking as lawyers have a separate role. Zero is the observed minimum for a role lacking an identified speaking contributor in the reviewed text; whole-event attendance remains unknown.

The transcripts provide useful attendance observations with distinct scopes:

| Source record | Victims | Comparecientes | Meaning |
|---|---:|---:|---|
| 23 April 2026 observations | **47** | **22** | Secretary verifies presence at 01:02:03; later arrivals remain unknown |
| 18 September 2023 recognition, AM | **119 additional accredited attendees** | **24 personally introduced** | The victim figure is an additional group beyond speaking representatives |
| 16 July 2021 victim observations | **Approximately 60 present** | **87 requested remote listening** | The court announces remote retransmission; individual connections are unverified |
| 30 August 2018 conditionality | Complete total unknown | **11 present** | Stated roster corroborated by eleven introductions |

[Attendance observations](attendance_observations.json) retain source coordinates, planned-versus-present distinctions and announced observer groups. Whole-corpus attendance averages remain unknown because complete attendee rosters and a reconciled hearing-event denominator are unavailable. The 93 document records include AM/PM splits, multi-day material and submitted videos.

The May 2024 source supports seven named victim-speaker anchors and four further speaking personas with unresolved identity overlap. December 2024 has a possible tenth victim whose identity needs verification. Those possibilities remain outside the confirmed minima. The review checked supplied text and original files; audiovisual identity validation remains outstanding.

## Counting pages and words

All 79 Word/ODT transcripts produced usable PDFs. Fourteen spreadsheet transcripts are measured by dialogue words.

Document page counts come from headless LibreOffice PDF rendering with the source document's layout. The report uses rendered pages because stored Word page properties were absent or inconsistent in some files. Fonts and layout engines can change pagination. Three problematic DOCX packages were XML-reserialized in temporary copies with their original text preserved; usable outputs, where present, are counted. The original sources were preserved.

Word/ODT text includes document-body paragraphs and tables. Spreadsheet word counts use the dialogue column, excluding order numbers and role labels. The 500-word page equivalent is a declared length measure that covers every record. It is separate from the rendered-page measure.

## Hearing types

| Type | Records |
|---|---:|
| Statements/submissions | 67 |
| Sworn declarations | 5 |
| Recognition hearings | 4 |
| Victim observations | 4 |
| Conditionality/truth contribution | 10 |
| Late recognition | 2 |
| Protective measures | 1 |

## Harm dimensions in the shared Catatumbo order

The Catatumbo order identifies six overlapping dimensions, at printed p. 796, paragraph 1956, developed on pp. 796–809:

| Dimension | Examples |
|---|---|
| Moral harm | Grief, humiliation, damaged dignity/reputation and interrupted mourning or funeral rituals. |
| Physical, mental and emotional harm | Bodily injury, trauma and enduring psychological suffering. |
| Harm to life plans | Interrupted education, employment, relationships and family futures. |
| Property/economic harm | Lost income, assets and household providers; search, legal and funeral costs and debts. |
| Sociocultural/territorial harm | Damaged community ties and organizations, cultural practices and connections to territory. |
| Civic trust and the rule of law | Lost confidence in armed forces, justice institutions and the state's protective role. |

## Sources and calculation files

- [Source-linked record counts](records.csv): one row per accepted transcript record, with rendered pages, word counts, reviewed speaker minima, unknown attendance fields, original Drive link and input SHA-256.
- [Machine-readable summary](summary.json).
- [Ten-review manifest](review_manifest.json), [person evidence](participant_evidence.json) and [audit findings](PARTICIPANT_AUDIT.md).
- [Calculation script](calculate_statistics.py): run `python calculate_statistics.py`; add `--check-sources /path/to/corpus` to verify every original file against its frozen SHA-256.
- [Consolidated inventory](../transcript_inventory_20261103/inventory.json) and [source manifest](../transcript_inventory_20261103/source_manifest.json), inspected at commit `13c975c6f650e03a04a329e33c2bfdd3eba2c64d`.
- [Original Catatumbo order](https://drive.google.com/file/d/18k4JNF2D_Z6gqmKTBIDgsFrJU3l7fQSz/view), printed pp. 796–809.

The corpus source text was used privately for this calculation. This directory contains the derived counts and their provenance.
