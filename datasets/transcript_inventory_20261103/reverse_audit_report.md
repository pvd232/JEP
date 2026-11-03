# Pagination correction and Casanare reverse audit

Reviewed **3 November 2026**. Scope remains **JEP Case 03, Subcase Casanare**, including directly connected Casanare proceedings in the supplied Datos collection. Other cases and territorial subcases are discovery metadata only and are excluded from the confirmed corpus.

## Pagination failure reproduced and corrected

The old parser returned zero continuation tokens after the first 100 entries of the broad Case 03 playlist even though its header declared 898. The saved response contains a primary video-list continuation in `continuationItemViewModel.continuationCommand.innertubeCommand.continuationCommand.token`. The old implementation recognized only `continuationItemRenderer.continuationEndpoint.continuationCommand.token`.

The corrected parser recognizes both structures, follows the primary list’s target, and ignores the outer-section continuation. The request body remains the ordinary public browse body containing `context` and `continuation`. This is a public-interface response-parser correction, not a change to the documented YouTube Data API’s `nextPageToken` format.

The [live next-page proof](live_pagination_proof.json) records 100 new video IDs at positions 101–200. Full traversal reached a terminal page after nine pages. The default view returned 895 normal-title entries; its last page reported hidden unavailable material. Following the ordinary public **Show unavailable videos** action exposed three additional blank-title IDs. The selected snapshot therefore accounts for **898 of 898 positions:895 normal-title entries and 3 unavailable placeholders**. It does not establish that all 898 recordings are playable.

The [reproduction report](pagination_reproduction.json) passed 15/15 checks against the retained responses. A standalone replay using sanitized fixtures passed 14/14 checks without the original research caches. Checks cover the missed continuation, exclusion of the outer token, legacy compatibility, hidden positions, repeated playlist memberships, request-failure/cycle/page-limit states, and terminal channel snapshots. Exact commands and fixture provenance are in [pagination_fix](pagination_fix/README.md). Opaque continuation tokens and raw watch/player payloads are not published.

## Source accounting

| Source | Normal-title appearances | Unavailable positions | Distinct IDs | Declared total | Pagination/accounting |
|---|---:|---:|---:|---:|---|
| JEP Colombia / videos | 2663 | — | 2663 | — | reused terminal snapshot |
| JEP Colombia / streams | 847 | — | 847 | — | reused terminal snapshot |
| JEP Colombia / Shorts | 64 | — | 64 | — | exhausted count unknown |
| Caso 03 de la JEP / Falsos positivos | 895 | 3 | 898 | 898 | exhausted with unavailable |
| Subcaso Casanare | 19 | 1 | 20 | 20 | exhausted with unavailable |
| Audiencias & Diligencias / JEP / HD | 42 | 2 | 43 | 44 | exhausted with unavailable |
| Régimen de Condicionalidad | 4 | 0 | 4 | 4 | exhausted reconciled |
| Camino de la Memoria - Casanare | 24 | 0 | 24 | 24 | exhausted reconciled |
| Caso 03 / Subcaso Antioquia | 18 | 0 | 18 | 18 | exhausted reconciled |
| Caso 03 / Subcaso Costa Caribe/ La Popa | 248 | 0 | 248 | 248 | exhausted reconciled |
| Caso 03 de la JEP / Subcaso Norte de Santander | 10 | 0 | 10 | 10 | exhausted reconciled |
| Caso 03 / Subcaso Huila | 186 | 0 | 186 | 186 | exhausted reconciled |
| Caso 03 / Subcaso Meta | 169 | 1 | 170 | 170 | exhausted with unavailable |
| Official JEP Case 03 page — Casanare-labelled hearing cards | 7 | — | 5 | — | observed cards extracted |

The [crawl manifest](crawl_manifest.json) records each source, response-page evidence, terminal state and count reconciliation. The [full discovery catalog](public_catalog.json.gz) contains 3,606 distinct IDs; the [membership table](public_memberships.json.gz) retains 5,203 appearances across collections. These are discovery quantities, **not Casanare hearing counts**, and collection totals must not be added to estimate unique videos.

The retained channel Videos and Live catalogs contain 2,663 and 847 IDs respectively. Their terminal response structures were rechecked, but the earlier collector did not record original fetch times; they were not refetched in this pass. The Shorts surface was enumerated in this pass. A surface without a declared total can reach a verified terminal page but cannot be numerically reconciled to an undisclosed count. The official JEP page extraction is restricted to active Casanare-labelled cards; mismatched thumbnail/text-link destinations remain visible in provenance.

Five regional playlists were read only to identify other-subcase membership. Official descriptions were checked for the remaining generic titles; no outside-case captions or testimony were analyzed. The [broad Case 03 register](broad_metadata_scope.json) assigns all 898 IDs: **96 included, 789 excluded and 13 scope unconfirmed**. Unresolved geography remains outside the confirmed Casanare corpus. Main-workbook scope decisions are in [scope_decisions.json](scope_decisions.json).

## Reverse map and supplied-source counts

| Quantity | Count | Interpretation |
|---|---:|---|
| Source files |116|Every original retains its Drive link.|
| Consolidated supplied transcript records |93|Unchanged; includes separately supplied segments and one composite source.|
| English summaries |93|Preserved with their source pointers and review limits.|
| Included public video IDs |128|Uploads, not a certified number of unique hearings.|
| Video IDs linked to supplied transcript records |83|Includes alternate uploads and partial supplied coverage.|
| Known partial supplied-source coverage |6|Subset of linked uploads; includes omitted openings and one missing morning portion.|
| No supplied-source mapping, content checked |4|A distinct session/recording or recorded response was checked against supplied candidates.|
| No supplied-source mapping, metadata basis |41|Identity/date metadata supports the candidate; further content checks could reveal errors or alternate uploads.|
| Source records with a high-confidence recording identity |82|80 public-caption checked, 2 metadata-only.|
| Source records without a located recording |11|Unresolved forward-map gaps.|

The **45 video IDs without a supplied-source mapping are not a certified count of that many additional unique transcripts or hearings**. The [Videos table](video_inventory.json) gives each upload’s status, date basis, concise evidence and links. The [detailed reverse review](reverse_mapping_review.json) retains source anchors and the limitations behind every decision.

### Findings that change the map

- `FoAy5Qfphcs` and `ztGtBj4AbQA` are two uploads of Marco Fabián García Céspedes’s 5 July 2019 procedural session. Opening, defense postponement and closing anchors match `VV-057`; both video IDs are preserved and no new transcript row is created.
- `cGyu3lTjqso` is the **19 September 2023 afternoon** recognition session: the captioned resumption identifies 16:02 and the close 20:09. The supplied same-day transcript ends at the morning lunch adjournment.
- `cSKgOHGfLQw` is the **20 September 2023 afternoon** recognition session, ending at 17:45. Its dated afternoon resumption and participant sequence differ from the supplied morning segment.
- `uTjViv5Vtpc` is a short recorded questionnaire response attributed to Edwin Leonardo Toro Ramírez. Ordered comparison distinguishes it from supplied `VV-017`, `VV-018` and same-date Montaño `VV-025`. The title supplies 21 October 2019; no spoken date was observed, and the upload ends during the account. The description’s hearing-format wording is not adopted as a verified fact.
- The previously checked Faiber Amaya continuation `s6x7MjB24E8` belongs to 28 August 2020, distinct from the supplied 29 April 2019 source.

New bounded caption checks are recorded in [new_content_checks.json](new_content_checks.json). Cue timestamps are approximate; these checks establish identity or session distinction, not full audio equivalence. The original 93 summaries have not been replaced with summaries of newly discovered videos.

## Residual gaps and completeness claim

The source-tree inventory is complete for the supplied folders. The defined public-source pass has been executed and every admitted upload has a coverage decision. **Fully verified matching remains incomplete.**

The source-side gap register remains 11 unlocated recordings, 2 missing public continuations and 2 metadata-only content checks. Those counts must not be added to the reverse video/source gap count: the direction differs and some records overlap. In particular `VV-015` lacks a later public recording portion while its supplied text also summarizes an opening; `VV-038` extends beyond its located upload without proving a reverse transcript gap.

There are 5 distinct unavailable IDs exposed across the audited playlists: `6S-j34I6qYs`, `KnwzIgiijTA`, `UoQwxCMYJGQ`, `n1HYbvijKKI`, `o6q9K9GMm4E`. The Casanare playlist’s unavailable member is retained with an access/scope-unconfirmed status. A blank title and unavailable content cannot establish its hearing identity, even when its video ID is known. The main Videos table contains 7 scope-unconfirmed candidates; the broad metadata register separately retains unresolved territorial membership. These are explicit unresolved decisions, not silently excluded material.

The public-source evidence cannot prove the absence of private, deleted, unlisted or never-published recordings. JEP or an authorized custodian can clarify the unavailable IDs, unresolved source-recording locators and recording access. The already-public videos without supplied transcripts are a separate source-expansion question; their availability does not require locating new public recordings through JEP.

No message or request was sent to JEP or anyone else. Original source files and their access settings were preserved. The workbook and evidence files are the reviewable outputs.
