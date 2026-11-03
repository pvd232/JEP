"""Write the concise execution report from the reviewed output tables."""
from pathlib import Path
import collections
import json

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'outputs/jep_transcripts_20261103'


def passed_check_counts(report, label):
    """Require successful boolean outcomes before allowing a pass narrative."""
    if not isinstance(report, dict):
        raise SystemExit(f'{label}: expected a validation report object')
    checks=report.get('checks')
    if not isinstance(checks, list) or not checks:
        raise SystemExit(f'{label}: a nonempty check list is required')
    if any(not isinstance(check, dict) or type(check.get('passed')) is not bool for check in checks):
        raise SystemExit(f'{label}: every check must have a boolean passed result')
    passed=sum(check['passed'] is True for check in checks)
    if report.get('all_passed') is not True or passed != len(checks):
        raise SystemExit(f'{label}: validation failed ({passed}/{len(checks)} checks passed)')
    return passed,len(checks)


def main():
    read=lambda name:json.loads((OUT/name).read_text())
    stats=read('summary.json'); counts=stats['reverse_audit']
    broad=read('broad_metadata_scope.json'); bc=broad['counts']
    scope=read('scope_decisions.json')
    crawl=read('crawl_manifest.json')
    sources=read('crawl_sources.json')
    proof=read('pagination_reproduction.json')
    replay=read('standalone_replay_result.json')
    replay_report=read('standalone_replay.json')
    proof_passed,proof_total=passed_check_counts(proof,'Pagination reproduction')
    replay_passed,replay_total=passed_check_counts(replay_report,'Standalone replay')
    if not isinstance(replay, dict) or replay.get('all_passed') is not True:
        raise SystemExit('Standalone replay receipt: all_passed must be true')
    if type(replay.get('exit_code')) is not int or replay['exit_code'] != 0:
        raise SystemExit('Standalone replay receipt: successful exit_code 0 is required')
    if type(replay.get('checks')) is not int or replay['checks'] != replay_total:
        raise SystemExit('Standalone replay receipt: check count disagrees with its full report')
    v=read('video_inventory.json')
    btotal=sum(bc.values())
    stats['reverse_audit']['pagination_note']='Failure reproduced at 100/898. The live fix returned 100 new IDs at positions 101–200. Nine pages plus the normal unavailable-item view reconcile all 898 positions: 895 normal-title entries and 3 unavailable placeholders.'
    stats['reverse_audit']['broad_scope_note']=f"Broad Case 03: {bc.get('included',0)} included, {bc.get('excluded',0)} excluded and {bc.get('scope_unconfirmed',0)} scope unconfirmed across {btotal} IDs. Generic or unavailable items without established Casanare membership stay outside the confirmed corpus. See the complete scope register."
    stats['reverse_audit']['completeness_note']='The declared public-source pass is executed and all admitted videos have coverage decisions. Videos and Live were freshly traversed on 3 November 2026 across 118 pages, with retrieval receipts. All ten playlists reconcile. Unavailable items and four unresolved main-register scope decisions remain explicit.'
    stats['reverse_audit']['source_count']=len(sources)
    stats['reverse_audit']['discovery_video_id_union']=crawl['unique_video_ids']
    stats['reverse_audit']['discovery_memberships']=crawl['membership_count']
    stats['reverse_audit']['current_discovery_memberships']=crawl.get('current_membership_count',crawl['membership_count'])
    stats['reverse_audit']['historical_discovery_memberships']=crawl.get('historical_membership_count',0)
    stats['reverse_audit']['independent_code_reviews']=10
    stats['reverse_audit']['session_count_certified']=False
    stats['reverse_audit']['session_count_note']='Distinct uploads are counted separately from source documents. Different upload IDs are grouped only where content establishes equivalence; a definitive number of additional unique hearings is not claimed.'
    (OUT/'summary.json').write_text(json.dumps(stats,ensure_ascii=False,indent=2)+'\n')
    table=['| Source | Normal-title appearances | Unavailable positions | Distinct IDs | Declared total | Pagination/accounting |','|---|---:|---:|---:|---:|---|']
    val=lambda n:'—' if n is None else str(n)
    for s in sources:
        table.append('| '+s['title'].replace('|','/')+' | '+val(s['visible_memberships'])+' | '+val(s['unavailable_positions'])+' | '+val(s['unique_video_ids'])+' | '+val(s['declared_items'])+' | '+s['status_label']+' |')
    unknown=[r for r in v if r['scope_label']=='Scope unconfirmed']
    unavailable_ids=sorted({i for c in crawl['collections'] for i in c.get('hidden_only_video_ids',[])})
    text=f'''# Pagination correction and Casanare reverse audit

Reviewed **3 November2026**. Scope remains **JEP Case03, Subcase Casanare**, including directly connected Casanare proceedings in the supplied Datos collection. Other cases and territorial subcases are excluded from the confirmed corpus. Outside-scope procedural openings were checked only where needed to resolve a territorial boundary; no substantive testimony analysis was added.

## Ten independent code reviews and tieout

Ten independent subagent reviews covered pagination, completeness, scope, duplicate/source identity, reverse joins, timestamps, forward gaps, workbook integrity, reproducibility and fresh-channel integrity. The [review register](code_reviews/ten_review_summary.md) preserves the findings and after-repair evidence. Repairs reject malformed or misdirected continuation controls, missing intermediate pages, contradictory scope decisions, lost source/video links, unsupported absence defaults and failed validation reports. Stable source IDs now depend on Drive-file identities rather than filename sorting. The workbook has explicit native table filters and validated clickable links in both directions.

No supplied record was added or merged in this pass: **93 records, 116 source files and 93 English summaries remain**. Four tiny measurement corrections across three duplicate-comparison rows were synchronized; consolidation decisions are unchanged. All **74 challenged exclusion rationales** were replaced with specific official case/territorial evidence. Three previously uncertain contextual items were resolved as outside the hearing/statement corpus: two memorial events and one short victim-message clip. The [tieout decisions](tieout_data_decisions.json) preserve concise evidence and explicit limits.

## Pagination failure reproduced and corrected

The old parser returned zero continuation tokens after the first100 entries of the broad Case03 playlist even though its header declared898. The saved response contains a primary video-list continuation in `continuationItemViewModel.continuationCommand.innertubeCommand.continuationCommand.token`. The old implementation recognized only `continuationItemRenderer.continuationEndpoint.continuationCommand.token`.

The corrected parser recognizes both structures, follows the primary list’s target, and ignores the outer-section continuation. The request body remains the ordinary public browse body containing `context` and `continuation`. This is a public-interface response-parser correction, not a change to the documented YouTube Data API’s `nextPageToken` format.

The [live next-page proof](live_pagination_proof.json) records100 new video IDs at positions101–200. Full traversal reached a terminal page after nine pages. The default view returned895 normal-title entries; its last page reported hidden unavailable material. Following the ordinary public **Show unavailable videos** action exposed three additional blank-title IDs. The selected snapshot therefore accounts for **898 of898 positions:895 normal-title entries and3 unavailable placeholders**. It does not establish that all898 recordings are playable.

The [reproduction report](pagination_reproduction.json) passed {proof_passed}/{proof_total} checks against the retained responses. A standalone replay using sanitized fixtures passed {replay_passed}/{replay_total} checks without the original research caches. Checks cover the missed continuation, exclusion of the outer token, legacy compatibility, hidden positions, repeated playlist memberships, request-failure/cycle/page-limit states, and terminal channel snapshots. Exact commands and fixture provenance are in [pagination_fix](pagination_fix/README.md). Opaque continuation tokens and raw watch/player payloads are not published.

## Source accounting

{chr(10).join(table)}

The [crawl manifest](crawl_manifest.json) records each source, response-page evidence, terminal state and count reconciliation. The [full discovery catalog](public_catalog.json.gz) retains {crawl['unique_video_ids']:,} distinct IDs; the [membership table](public_memberships.json.gz) retains {crawl['membership_count']:,} appearances across collections, including {crawl.get('historical_membership_count',0)} explicitly historical appearance(s) absent from the latest listing. These are discovery quantities, **not Casanare hearing counts**, and collection totals must not be added to estimate unique videos.

The freshly traversed channel Videos and Live catalogs contain **2,663 and 846 IDs**, across **89 and 29 pages** respectively. Retrieval receipts cover 3 November 2026, 20:19–20:29 UTC; both primary lists reached terminal pages. The earlier Live listing contained one additional ID, `Pg8DvszQMME`. It remains playable, and its opening at 00:11:13–00:12:25 identifies Neiva and the Huila subcase on 21 October 2026. Its historical listing evidence is retained, and it is excluded from Casanare. Absence from a refreshed listing does not imply deletion or privacy status.

The fresh snapshot's 118 pages were independently replayed; the repaired traversal rejects a mismatched first-page cache or selected channel surface. The older 120-response chain also replays, including one verified non-video About response per channel. Its original unknown retrieval times remain a historical limitation, but no longer describe the selected current channel catalogs. Shorts and ten playlists were also enumerated in this investigation. A surface without a declared total can reach a verified terminal page but cannot be numerically reconciled to an undisclosed count. The official JEP page extraction is restricted to active Casanare-labelled cards; mismatched thumbnail/text-link destinations remain visible in provenance.

Five regional playlists were read to identify other-subcase membership. Official descriptions and a small number of procedural openings resolved the challenged territorial exclusions; substantive review remains in Casanare. The [broad Case03 register](broad_metadata_scope.json) assigns all {btotal} IDs: **{bc.get('included',0)} included, {bc.get('excluded',0)} excluded and {bc.get('scope_unconfirmed',0)} scope unconfirmed**. This register overlaps the main workbook and its counts must not be added to the main-register counts. Unresolved geography remains outside the confirmed Casanare corpus. Main-workbook scope decisions are in [scope_decisions.json](scope_decisions.json).

## Reverse map and supplied-source counts

| Quantity | Count | Interpretation |
|---|---:|---|
| Source files |116|Every original retains its Drive link.|
| Consolidated supplied transcript records |93|Unchanged; includes separately supplied segments and one composite source.|
| English summaries |93|Preserved with their source pointers and review limits.|
| Included public video IDs |{counts['included_video_ids']}|Uploads, not a certified number of unique hearings.|
| Video IDs linked to supplied transcript records |{counts['video_ids_with_supplied_transcript']}|Includes alternate uploads and partial supplied coverage.|
| Known partial supplied-source coverage |{counts['known_partial_supplied_coverage_video_ids']}|Subset of linked uploads; includes omitted openings and one missing morning portion.|
| No supplied-source mapping, content checked |{counts['no_supplied_transcript_content_checked']}|Public identity/format checked against the supplied index; date conflicts remain explicit.|
| No supplied-source mapping, metadata basis |{counts['no_supplied_transcript_metadata_basis']}|Identity/date metadata supports the candidate; further content checks could reveal errors or alternate uploads.|
| Source records with a high-confidence recording identity |82|80 public-caption checked,2 metadata-only.|
| Source records without a located recording |11|Unresolved forward-map gaps.|

The **{counts['no_supplied_transcript_content_checked']+counts['no_supplied_transcript_metadata_basis']} video IDs without a supplied-source mapping are not a certified count of that many additional unique transcripts or hearings**. The [Videos table](video_inventory.json) gives each upload’s status, date basis, concise evidence and links. The [detailed reverse review](reverse_mapping_review.json) retains source anchors and the limitations behind every decision.

### Findings that change the map

- `FoAy5Qfphcs` and `ztGtBj4AbQA` are two uploads of Marco Fabián García Céspedes’s5 July2019 procedural session. Opening, defense postponement and closing anchors match `VV-057`; both video IDs are preserved and no new transcript row is created.
- `cGyu3lTjqso` is the **19 September2023 afternoon** recognition session: the captioned resumption identifies16:02 and the close20:09. The supplied same-day transcript ends at the morning lunch adjournment.
- `cSKgOHGfLQw` is the **20 September2023 afternoon** recognition session, ending at17:45. Its dated afternoon resumption and participant sequence differ from the supplied morning segment.
- `uTjViv5Vtpc` is a short recorded questionnaire response attributed to Edwin Leonardo Toro Ramírez. Ordered comparison distinguishes it from supplied `VV-017`, `VV-018` and same-date Montaño `VV-025`. The title supplies21 October2019; no spoken date was observed, and the upload ends during the account. The description’s hearing-format wording is not adopted as a verified fact.
- The previously checked Faiber Amaya continuation `s6x7MjB24E8` belongs to28 August2020, distinct from the supplied29 April2019 source.
- `w49HGaeBNRk` is a Toro procedural installation and adjournment because defense counsel was absent. Its opening/title give 15 May 2019 while the closing automatic captions give 14 May; the discrepancy remains visible. Neither supplied Toro transcript covers this proceeding.
- `xuxtUERYNxk` records preparations on 2 December 2019 after Wilson Rodríguez was not transported to the hearing. It is not a completed voluntary statement. `eKrYlu79rGo` is a dated Solano questionnaire supplement, distinct from supplied `VV-041`.
- Further bounded opening checks identify Rivera, Soto, Romero, Cuevas, Torres and Saavedra recordings against the supplied-session index. Soto's continuation date remains title-based. For Rodríguez upload `U2k8Iaa-bd4`, the title gives 3 February 2020 while the opening captions render 2019; the year is explicitly unverified. These observations strengthen identity/format decisions without turning uploads into certified unique hearings.

New bounded caption checks are recorded in [new_content_checks.json](new_content_checks.json). Cue timestamps are approximate; these checks establish identity or session distinction, not full audio equivalence. The original93 summaries have not been replaced with summaries of newly discovered videos.

## Residual gaps and completeness claim

The source-tree inventory is complete for the supplied folders. The defined public-source pass has been executed and every admitted upload has a coverage decision. **Fully verified matching remains incomplete.**

The source-side gap register remains11 unlocated recordings,2 missing public continuations and2 metadata-only content checks. Those counts must not be added to the reverse video/source gap count: the direction differs and some records overlap. In particular `VV-015` lacks a later public recording portion while its supplied text also summarizes an opening; `VV-038` extends beyond its located upload without proving a reverse transcript gap.

There are {len(unavailable_ids)} distinct unavailable IDs exposed across the audited playlists: {', '.join('`'+x+'`' for x in unavailable_ids)}. The Casanare playlist’s unavailable member is retained with an access/scope-unconfirmed status. A blank title and unavailable content cannot establish its hearing identity, even when its video ID is known. The main Videos table contains {len(unknown)} scope-unconfirmed candidates; the broad metadata register separately retains unresolved territorial membership. These are explicit unresolved decisions, not silently excluded material.

The public-source evidence cannot prove the absence of private, deleted, unlisted or never-published recordings. JEP or an authorized custodian can clarify the unavailable IDs, unresolved source-recording locators and recording access. The already-public videos without supplied transcripts are a separate source-expansion question; their availability does not require locating new public recordings through JEP.

No message or request was sent to JEP or anyone else. Original source files and their access settings were preserved. The workbook and evidence files are the reviewable outputs.
'''
    # Editorial spacing only; identifiers and stored data are unaffected.
    fixes={'November2026':'November 2026','Case03':'Case 03','first100':'first 100','declared898':'declared 898','records100':'records 100','positions101':'positions 101','returned895':'returned 895','of898':'of 898','entries and3':'entries and 3','895 normal':'895 normal','all898':'all 898','passed12':'passed 12','contain2663':'contain 2,663','and847':'and 847','2 metadata':'2 metadata','80 public':'80 public','Céspedes’s5':'Céspedes’s 5','July2019':'July 2019','September2023':'September 2023','identifies16':'identifies 16','close20':'close 20','at17':'at 17','supplies21':'supplies 21','October2019':'October 2019','to28':'to 28','August2020':'August 2020','supplied29':'supplied 29','April2019':'April 2019','original93':'original 93','remains11':'remains 11',',2 ':', 2 ','|116|':'|116|'}
    fixes['and2 ']='and 2 '
    for a,b in fixes.items(): text=text.replace(a,b)
    (OUT/'reverse_audit_report.md').write_text(text)
    print(json.dumps({'report':'reverse_audit_report.md','sources':len(sources),'broad_scope_counts':bc,'main_scope_unconfirmed':len(unknown),'unavailable_ids':unavailable_ids},indent=2))


if __name__=='__main__':main()
