# JEP Casanare: meeting statistics

Source audit: 5 November 2026. The supplied corpus contains **93 consolidated transcript/session records**, from **105 transcript source files**, spanning August 2018–April 2026. Records include individual statements, recorded submissions, split sessions and multi-day hearings. All describe the Casanare subcase of Case 03.

| Measure | Result | Denominator |
|---|---:|---|
| Mean rendered document length | **71.5 pages** | 79 of the 79 Word/ODT records |
| Median rendered document length | **70 pages** | Same rendered documents |
| Rendered document length range | **3–164 pages** | Same rendered documents |
| Total rendered pages | **5,646** | Same rendered documents |
| Extracted text | **3,068,242 words** | All 93 records |
| Mean text length | **32,992 words** | All 93 records |
| Mean length at 500 words/page | **66.0 page equivalents** | All 93 records |
| Identifiable victim speakers | **1.57 per record** | Conservative minimum: 146 person–record incidences / 93 |
| Identifiable compareciente speakers | **2.38 per record** | Conservative minimum: 221 person–record incidences / 93 |
| Victim speakers within records with identified victim voices | **7.3 per record** | 20 records |
| Principal compareciente in individual statements/submissions | **1 per record** | 67 records |

## Counting people

The participant measures count identifiable live speakers, including people who introduce themselves. Each person counts once within a transcript and may count again in another transcript. A victim's relative speaking in their own capacity as a victim counts; lawyers acting as legal representatives have their own role and are excluded from victim counts. Five sworn-declaration records contain principal witnesses, kept separate from comparecientes.

These are **minimum speaker counts from a rapid source review**. Silent observers, unassigned voices and uncertain identities can increase actual participation. A zero records that no separate speaker in that role was identified. Audience attendance and the number of people killed or disappeared in the underlying crimes are different measures.

The review combined the participant introductions, named speaker tables, live floor announcements and personal self-identification. A row labelled VICTIMA can contain several people; a diarization ID can refer to different people after a recording restart. Repeated questions and repeated morning/afternoon introductions were merged. Family members labelled COMPARECIENTE in the December 2024 and August 2025 spreadsheets were reassigned from context. The similar Javier Abella Roa name strings on 4 December 2024 were conservatively merged; an uncertain repeated victim identity on 24 May 2024 was also merged.

## Counting pages and words

All 79 Word/ODT transcripts produced usable PDFs. Fourteen spreadsheet transcripts are measured by dialogue words.

Document page counts come from headless LibreOffice PDF rendering with the source document's layout. The report uses rendered pages because stored Word page properties were absent or inconsistent in some files. Fonts and layout engines can change pagination. Three problematic DOCX packages were XML-reserialized in temporary copies without changing their text; usable outputs, where present, are counted. The original sources were preserved.

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

- [Source-linked record counts](records.csv): one row per accepted transcript record, with rendered pages, word counts, participant minima, count evidence, original Drive link and input SHA-256.
- [Machine-readable summary](summary.json).
- [Consolidated inventory](../transcript_inventory_20261103/inventory.json) and [source manifest](../transcript_inventory_20261103/source_manifest.json), inspected at commit `13c975c6f650e03a04a329e33c2bfdd3eba2c64d`.
- [Original Catatumbo order](https://drive.google.com/file/d/18k4JNF2D_Z6gqmKTBIDgsFrJU3l7fQSz/view), printed pp. 796–809.

The corpus source text was used privately for this calculation. This directory contains the derived counts and their provenance.
