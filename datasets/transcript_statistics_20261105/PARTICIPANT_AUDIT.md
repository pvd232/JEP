# Participant-count review

**Verdict: revise the speaker counts and withdraw the attendance averages.** Six source reviewers covered all 93 supplied records. Four further reviewers checked the calculation, definitions, identity decisions and proposed corrections. A second source reviewer checked the numeric corrections independently. The reviewed publication is commit `6a1e900fdd00d59cfdae292283c8c756e2c97963`.

## Confirmed corrections

These are distinct identified speakers within each supplied record. They are minimum counts.

| Record | Role | Earlier count | Supported count | Source control |
|---|---|---:|---:|---|
| 19 September 2023 recognition | Compareciente | 6 | **8** | Two continuing floors at the opening precede six later principals |
| 23 April 2026 observations | Compareciente | 3 | **4** | Additional live floor at 08:41:20 |
| 24 April 2026 observations | Compareciente | 1 | **2** | Separate live floors at 03:43:20 and 03:55:02 |
| 24 May 2024 conditionality | Victim | 6 | **7** | Seven ordinarily distinct named anchors; four further personas have unresolved aliases |
| 3 December 2024 conditionality | Victim | 8 | **9** | Additional introduction at dialogue order 12, worksheet row 13 |
| 13 August 2025 truth contribution | Compareciente | 21 | **22** | A rollcall introduction was incorrectly labelled as defense counsel |

The May review initially identified eleven context personas. Independent cross-checking reduced the supported minimum to seven. A new identity requires a distinguishing personal anchor; a changed case or family relationship supplies context. Assigning the speaker a named parent's identity requires evidence beyond that relationship.

The corrected ledger records **148 victim-speaker occurrences**, **225 source-supported compareciente occurrences**, **five sworn-witness occurrences** and **one principal deponent with disputed compareciente status**. An occurrence is one person within one transcript record. These totals are observed minima, with recording mode preserved.

## Why the earlier averages were misleading

1. **Speaking and attendance were conflated in the meeting answer.** On 23 April 2026, the secretary verifies 47 victims and 22 comparecientes present at rollcall. The corrected speaker counts for that record are six and four. Individual statement sources also announce victim groups listening silently.
2. **The denominator was document records.** An AM and PM split counts twice, a record containing several dates counts once, and eleven submitted videos were included under a live-speaker label. A trial or complete hearing requires a separate event reconciliation.
3. **The code imported manual totals.** Seventy-three records received category defaults. Twenty aggregate overrides supplied every positive victim count. The repair adds a person identity ledger and recording-mode validation.
4. **The checks froze the old answer.** The assertion requiring totals of 146 and 221 accepted compensating errors and rejected genuine corrections. Executable counterexamples also accepted a negative count and changed source bytes while retaining old extraction and decisions.

The revised calculation requires explicit review coverage for every record, counts person aliases, checks nonnegative integers and role consistency, retains a disputed role as unknown, and verifies frozen source hashes when original files are supplied. The original calculation and manual inputs are retained under [audit](audit/) as superseded evidence.

## Unresolved boundaries

- **May 2024:** seven named anchors; four further contextual personas may repeat established people. A complete distinct-person count remains unknown.
- **December 2024:** nine identified victim speakers; adjacent similar personal introductions may establish a tenth after audio review.
- **VV-023:** one principal deponent is certain; the header and proceeding statements conflict about compareciente status. The corresponding role count is null.
- **Protected sworn witness:** own-harm testimony is retained as a secondary flag. Primary witness role and victim accreditation are separate matters.
- **Attendance:** snapshot counts, expected observers and requested remote listeners retain their source qualifiers. Complete event attendance remains unknown.

## Ten reviewers

| Reviewer | Scope |
|---|---|
| 01 | VV-001–025: 25 source records |
| 02 | VV-026–050: 25 source records |
| 03 | VV-051–075: 25 source records |
| 04 | Four recognition records and the 2018 conditionality record |
| 05 | Four victim-observation and two late-recognition records |
| 06 | Seven 2024–2025 conditionality records |
| 07 | Measurement definitions, population and denominator |
| 08 | Code, input provenance and executable counterexamples |
| 09 | Identity, disputed roles and recording modes |
| 10 | Independent adversarial check of proposed source corrections |

The [manifest](review_manifest.json) records the ten completed tasks, review hashes and source scopes. [Person evidence](participant_evidence.json) provides pseudonymous aliases and worksheet/paragraph coordinates; [attendance observations](attendance_observations.json) retain the court's stated counts. Text and raw source files were checked. Complete audio validation remains outstanding.

Page and word measures retain their original measurement scope. The focused repair checks are recorded in [validation](validation.json).
