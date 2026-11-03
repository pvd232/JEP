"""Apply the ten-review tieout decisions without changing supplied source identities.

All conclusions below are bounded research decisions, not keyword admissions.
Retained caption exports are local evidence; only paraphrased anchors are published.
"""
from __future__ import annotations

import collections
import hashlib
import json
import re
from pathlib import Path

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[1]
REVIEW = ROOT / 'inventory_work/tieout_review_20261103'
OUT = ROOT / 'outputs/jep_transcripts_20261103'


def read(path):
    return json.loads(Path(path).read_text())


def write(path, value):
    Path(path).write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n')


MEMORIAL = 'https://www.jep.gov.co/Sala-de-Prensa/Paginas/la-jep-cumplio-su-compromiso-con-las-victimas-de-casanare-verifico-la-instalacion-de-19-placas-del-camino-de-la-memoria.aspx'
DABEIBA = 'https://www.jep.gov.co/Sala-de-Prensa/Paginas/jep-realizara-en-dabeiba-el-27-de-junio-la-audiencia-publica-de-reconocimiento-por-falsos-positivos.aspx'
HUILA = 'https://www.jep.gov.co/Sala-de-Prensa/Paginas/jep-imputa-por-crimenes-de-guerra-y-de-lesa-humanidad-a-35-integrantes-del-ejercito-nacional-en-huila-entre-ellos-a-jaime-l.aspx'

# Content checks resolve public identity/format, not full audio equivalence.
# Date conflicts remain explicit and are never silently corrected from ASR.
CHECKS = [
    ('KpZNfys5EgQ', '00:00:51–00:01:10', 'Opening identifies Jaime Alberto Rivera Mahecha, 6 December 2018 at 13:14, and Auto 76.', '2018-12-06', 'Opening date and participant agree with official title.', 'Voluntary statement', 'KpZNfys5EgQ.txt'),
    ('4-L2pa3TLSQ', '00:00:55–00:01:44; 05:58:28–05:58:43', 'Opening and closing identify Jaime Alberto Rivera Mahecha on 25 February 2019. The opening explicitly resumes the statement begun on 6 December 2018; these are connected sessions on different dates, not established duplicate uploads.', '2019-02-25', 'Opening and closing date agree with title; the earlier statement date is explicitly distinguished.', 'Voluntary-statement continuation', '4-L2pa3TLSQ_anchors.json'),
    ('1M2x7H2vH74', '00:00:35–00:00:55', 'Opening identifies Gustavo Enrique Soto Bracamonte and 7 December 2018 at 08:34, under Auto 061.', '2018-12-07', 'Opening date and participant agree with official title.', 'Voluntary statement', '1M2x7H2vH74_dom.json'),
    ('xHM6s1lT4M0', '00:00:08–00:00:49', 'Opening identifies Gustavo Soto and explicitly resumes his 7 December 2018 statement.', '2019-03-01', '1 March 2019 comes from the title; the checked opening dates the earlier statement, not this continuation.', 'Voluntary-statement continuation', 'xHM6s1lT4M0.txt'),
    ('w49HGaeBNRk', '00:00:50–00:01:06; 00:06:33–00:07:05; 00:10:52–00:11:09', 'Toro procedural installation: opening gives 15 May 2019 at 08:40; missing defense counsel prevents continuation and the proceeding is adjourned. Supplied VV-017 and VV-018 open on 20 February and 27 June 2019.', '2019-05-15', 'Title and opening give 15 May; closing automatic captions render 14 May. Conflict retained; no full testimony occurs.', 'Procedural installation / adjournment', 'w49HGaeBNRk.txt'),
    ('Z7O6PZdr4qw', '00:01:07–00:01:28', 'Opening identifies Jaime Alexander Romero Vargas, 21 June 2019 and Auto 075 of 28 May.', '2019-06-21', 'Spoken date and participant agree with title; garbled automatic-caption clock is not adopted.', 'Voluntary statement', 'Z7O6PZdr4qw.txt'),
    ('5GR24Fuq30c', '00:01:08–00:01:31; 02:47:30–02:47:56', 'Opening identifies Jholman Farley Cuevas Arenas on 16 September 2019 at 08:37; closing repeats that date and names the participant.', '2019-09-16', 'Opening and closing date agree with title.', 'Voluntary statement', '5GR24Fuq30c_anchors.json'),
    ('eKrYlu79rGo', '00:00:08–00:01:02; 00:44:13–00:44:25', 'Solano recorded questionnaire supplement: counsel explains that question 14 is answered by video alongside written answers; closing gives 15 October 2019 at 15:45. Supplied VV-041 opens on 27 July 2020.', '2019-10-15', 'Dated closing confirms title; distinct format and supplied-source opening exclude VV-041 equivalence.', 'Recorded questionnaire response', 'eKrYlu79rGo.txt'),
    ('VSpKiFEOBSg', '00:00:47–00:01:20', 'Opening identifies Orlando Rivas Tovar, 28 November 2019 at 12:04 in Yopal, and Auto 231 of 6 November.', '2019-11-28', 'Opening date, participant and Yopal location agree with official metadata.', 'Voluntary statement', 'VSpKiFEOBSg.txt'),
    ('xuxtUERYNxk', '00:00:30–00:01:05; 00:02:32–00:03:24; 00:10:55–00:11:58', 'Wilson Rodríguez proceeding on 2 December 2019: the participant was not transported to the hearing, so the court records preparations and closes at 09:38. This is not a completed voluntary statement.', '2019-12-02', 'Opening and closing agree on 2 December 2019.', 'Procedural installation / adjournment', 'xuxtUERYNxk.txt'),
    ('uIHoKm5tM-o', '00:00:48–00:01:33; 06:11:22–06:11:55', 'Opening identifies Henry William Torres Escalante, 11 December 2019 at 09:13, including consideration of his pactum veritatis; closing schedules continuation on 18 December.', '2019-12-11', 'Opening date and participant agree with title.', 'Voluntary statement', 'uIHoKm5tM-o_anchors.json'),
    ('YbtWpt_e_FA', '00:00:44–00:01:10', 'Opening identifies General Carlos Ovidio Saavedra Sáenz, 14 January 2020, and Auto 227 of 8 November 2019.', '2020-01-14', 'Opening date and participant agree with title; the full hearing is not audio-certified.', 'Voluntary statement', 'YbtWpt_e_FA.txt'),
    ('U2k8Iaa-bd4', '00:00:28–00:01:04', 'Opening identifies Wilson Rodríguez and 3 February, under Auto 230 of 6 November. The title gives 2020, while the automatic captions render 2019.', '2020-02-03', 'Year remains title-based with an explicit 2019/2020 caption conflict. Identity is checked; exact spoken year is not certified.', 'Voluntary statement', 'U2k8Iaa-bd4.txt'),
]


def main():
    scope = read(BASE/'scope_decisions_initial.json')
    broad = read(BASE/'broad_metadata_scope.json')
    reverse = read(BASE/'reverse_mapping_review.json')
    controls = read(BASE/'root_content_checks.json')
    inventory = read(OUT/'inventory.json')
    smap = {x['video_id']: x for x in scope['records']}
    bmap = {x['video_id']: x for x in broad['records']}
    rmap = {x['video_id']: x for x in reverse['videos']}
    cmap = {x['video_id']: x for x in controls['checks']}
    before_ids = [(x['unique_id'], x.get('source_file_ids')) for x in inventory]
    changes = []
    details = read(REVIEW/'scope_watch_details.json')
    queue = read(REVIEW/'reviews/review03/scope_risk_candidates.json')['records']
    assert len(queue) == 74 and set(details) == {x['video_id'] for x in queue}
    for old in queue:
        vid = old['video_id']; md = details[vid]
        if md.get('error') or md.get('channel_id') != 'UCay5mclHBbWQTQ8fhoNCWow':
            raise ValueError('Scope metadata is not a verified official upload: '+vid)
        if vid == 'BHfnWY4b_mI':
            reason = 'Opening 00:00:33–00:00:47 identifies the 9 September 2024 Araque Leal extension; 00:10:50–00:10:57 identifies Batallón 27 Magdalena. JEP’s official Huila notice identifies this participant and unit in that subcase. Territorial exclusion uses these combined pointers, not the participant name alone.'
            support = HUILA; group = 'explicit_other_region'; region = 'Huila'
        elif vid == 'hCAmw349Fjw':
            reason = 'Public opening 00:01:17–00:02:10 identifies 20 October 2020, Carlos Eduardo Chiquito, joint Cases 03 and 04, and the Urabá territorial municipalities. The title’s 03–03 label is inconsistent; the explicit opening resolves the territorial boundary.'
            support = 'https://www.youtube.com/watch?v='+vid+'&t=77s'; group = 'explicit_other_case_region'; region = 'Urabá / Dabeiba'
        elif vid == 'Lv387B0laD0':
            reason = 'Official video description explicitly identifies Prada’s intervention at the recognition hearing in Dabeiba, Antioquia. It is a hearing intervention outside Casanare, not generic contextual material.'
            support = DABEIBA; group = 'explicit_other_region'; region = 'Dabeiba'
        else:
            text = md['title']+' '+md.get('description','')
            if not re.search(r'(?:caso\s*0?4|(?:casos?|c)\s*0?3\s*[-–y/]\s*0?4)',text,re.I):
                raise ValueError('Expected explicit Case04 marker missing: '+vid)
            reason = 'Official title/description explicitly identifies Case 04 or joint Cases 03–04. JEP’s territorial definition places this proceeding group in Urabá/Dabeiba, outside Casanare; no evidence supports the former generic non-hearing label.'
            support = DABEIBA; group = 'explicit_other_case_region'; region = 'Urabá / Dabeiba'
        for records in [bmap, smap]:
            if vid not in records: continue
            row = records[vid]
            row.update(scope_decision='excluded', category='Other territorial proceeding', scope_group=group, evidence=reason, evidence_url='https://www.youtube.com/watch?v='+vid, supporting_scope_url=support, scope_confidence='High', notes='Scope-boundary check only; no substantive analysis of outside-scope testimony.', metadata_review_complete=True, exclusion_territory=region)
            row.pop('uncertainty_group',None); row.pop('unresolved_reason',None)
        changes.append({'video_id':vid,'change':'Corrected unsupported exclusion rationale','decision':'excluded','evidence':reason,'public_url':'https://www.youtube.com/watch?v='+vid,'supporting_url':support,'metadata_response_sha256':md['provenance'].get('sha256')})
    for vid in ['Psa0P7IaEBo','XXsg70ZuTyE','OZxGzpJemqM']:
        if vid == 'OZxGzpJemqM':
            reason = 'Public title identifies victim messages; bounded captions 00:00–00:01:38 contain short appeals for truth, memory and return of the disappeared, with no identifiable hearing installation or complete statement. Classified as a derivative victim-message clip under the existing primary-hearing boundary.'
            support = 'https://www.youtube.com/watch?v='+vid
        else:
            reason = 'Official title/description and JEP’s 20 October 2026 notice identify the memorial-plaque delivery (5 July 2025) and completion act (16 October 2026). These restorative public events are contextual material under the existing judicial-hearing/statement scope.'
            support = MEMORIAL
        for records in [smap,bmap]:
            if vid in records:
                row=records[vid]; row.update(scope_decision='excluded',category='Derivative / context material',scope_group='non_hearing_or_context',scope_confidence='High',evidence=reason,supporting_scope_url=support,notes='Related Casanare material retained for provenance; no missing-transcript conclusion is made.');row.pop('unresolved_reason',None);row.pop('uncertainty_group',None)
        changes.append({'video_id':vid,'change':'Resolved recording-format boundary','decision':'excluded','evidence':reason,'public_url':'https://www.youtube.com/watch?v='+vid,'supporting_url':support})
    # Preserve the one historical Live discovery and explicitly resolve its scope.
    historical = read(REVIEW/'reviews/review07/removed_live_watch_metadata.json')
    old_catalog=read(REVIEW/'base/video_inventory.json')
    hvid='Pg8DvszQMME'
    hreason='Public opening 00:11:13–00:12:25 identifies Neiva, the Huila subcase and 21 October 2026. The upload remains playable but is absent from the refreshed Live listing; it is an outside-scope Huila hearing, not a deleted-video inference.'
    if hvid not in smap:
        smap[hvid]=dict(video_id=hvid,title='Audiencia de aporte de verdad y seguimiento al régimen de condicionalidad — Huila',scope_decision='excluded',category='Other territorial proceeding',date='2026-10-21',participants='',evidence=hreason,notes='Historical Live-list membership retained separately from the fresh listing. Bounded procedural opening only.',evidence_url='https://www.youtube.com/watch?v='+hvid,publisher='JEP Colombia',date_basis='Date and Huila subcase stated in public opening.',duration_metadata='6577',current_inventory_ids=[],exact_video_id_currently_linked=False,reverse_mapping_status='outside_confirmed_hearing_mapping',discovery_collections=['Historical official channel Live listing'],scope_confidence='High',scope_group='explicit_other_region')
    changes.append({'video_id':hvid,'change':'Historical catalog difference resolved','decision':'excluded','evidence':hreason,'public_url':'https://www.youtube.com/watch?v='+hvid})
    # Do not force a territorial conclusion for the national-phase hearing.
    national=smap['UN7yvo0no14']
    national.update(evidence='Official description and opening 00:51:39–00:53:29 identify national-phase observations, especially Third-Division statements, installed in Cali on 22 July 2026 under Auto 24 of 15 May 2026. A direct Casanare segment is not established.',notes='Bounded procedural opening checked; remains outside the confirmed Casanare corpus. A national title and participant overlap alone are insufficient for admission.',date_basis='Day/month in opening and year in Auto/title; territorial inclusion remains unresolved.')
    if national['video_id'] in bmap:
        bmap[national['video_id']].update({k:national[k] for k in ['evidence','notes','date_basis']})
    content_receipts=[]
    for vid, offsets, finding, date, date_basis, kind, filename in CHECKS:
        path=REVIEW/'captions'/filename
        if not path.exists(): raise FileNotFoundError(path)
        row=rmap[vid]
        if row.get('transcript_ids'): raise ValueError('Cannot label linked source absent: '+vid)
        row.update(coverage_status='No supplied transcript located; public identity content checked',public_session_date=date,date_basis=date_basis,recording_kind=kind,basis='Bounded public caption anchors plus reviewed 93-record supplied-session index',coverage_gap='No supplied source for this public recording located in the 93-record inventory.',video_offsets=[{'offsets':offsets,'verification':finding}])
        row['review_limits']=['Only the specified caption anchors were used for this conclusion; automatic captions can contain errors. No full-audio equivalence or unique-hearing count is certified.',date_basis,'Compared against the supplied 93-record inventory, not all JEP or Drive holdings.']
        row['evidence']=[{'claim':finding,'public_url':row['url'],'pointer':offsets},{'claim':'Reviewed supplied-session index contains no corresponding source; same-person candidate checks are retained when applicable.','source':'review05/metadata_gap_audit.json'}]
        if vid in ['w49HGaeBNRk','eKrYlu79rGo']:
            row['evidence'].append({'claim':'Source opening dates and ordered content comparison distinguish the existing same-person supplied record(s).','source':'review05/priority_content_checks.json'})
        smap[vid]['date_basis']=date_basis
        smap[vid]['notes']='Public identity content checked against the supplied-session index; no supplied source located. '+date_basis
        if kind in ['Procedural installation / adjournment','Recorded questionnaire response']:
            smap[vid]['category']=kind
        if vid in bmap:
            bmap[vid]['date_basis']=date_basis
            bmap[vid]['notes']=smap[vid]['notes']
        check=dict(video_id=vid,url=row['url'],finding=finding,confidence='Bounded public-content identity check; see date limitations',duration_text=smap[vid].get('duration_text',''),anchors=[{'new_video_range':offsets,'evidence':finding}],review_limits=' '.join(row['review_limits']),date_basis=date_basis,recording_kind=kind,local_caption_sha256=hashlib.sha256(path.read_bytes()).hexdigest())
        cmap[vid]=check;content_receipts.append(check)
    for first,later,reason in [
        ('KpZNfys5EgQ','4-L2pa3TLSQ','The later opening explicitly resumes the 6 December 2018 statement on 25 February 2019; distinct dated recording segments, not alternate copies.'),
        ('1M2x7H2vH74','xHM6s1lT4M0','The later opening explicitly resumes the 7 December 2018 statement. Its current 1 March 2019 date remains title-based; not an established alternate copy.')]:
        for vid,other in [(first,later),(later,first)]:
            rmap[vid]['related_video_ids']=sorted(set(rmap[vid].get('related_video_ids',[])+[other]))
            rmap[vid]['duplicate_relation']=reason
    # Synchronize corrected measurement prose, without regenerating record IDs.
    for row in inventory:
        if row['unique_id']=='VV-008':row['duplicate_notes']=row['duplicate_notes'].replace('34,104','34,102')
        if row['unique_id']=='VV-010':row['duplicate_notes']=row['duplicate_notes'].replace('15,051','15,050')
    assert before_ids==[(x['unique_id'],x.get('source_file_ids')) for x in inventory]
    scope['records']=sorted(smap.values(),key=lambda x:x['video_id']);scope['counts']=dict(collections.Counter(x['scope_decision'] for x in scope['records']))
    scope['uncertain_groups']=dict(collections.Counter(x.get('uncertainty_group','unclassified') for x in scope['records'] if x['scope_decision']=='scope_unconfirmed'))
    scope['status']='Ten-review tieout applied; unresolved scope stays outside confirmed corpus'
    broad['counts']=dict(collections.Counter(x['scope_decision'] for x in broad['records']))
    broad['scope_group_counts']=dict(collections.Counter(x.get('scope_group','unclassified') for x in broad['records']))
    broad['residual_generic_video_ids']=[x['video_id'] for x in broad['records'] if x['scope_decision']=='scope_unconfirmed']
    broad['metadata_review_status']='All 74 challenged exclusion reasons rechecked against official metadata or bounded territorial openings; exclusions retained with specific evidence.'
    reverse['counts']=dict(collections.Counter(x['coverage_status'] for x in reverse['videos']))
    controls['checks']=list(cmap.values())
    controls['method']='Bounded public caption/description checks with explicit dates, source-index comparison and retained uncertainty; no complete audio certification.'
    for name,value in [('scope_decisions_initial',scope),('broad_metadata_scope',broad),('reverse_mapping_review',reverse),('root_content_checks',controls)]:write(BASE/(name+'.json'),value)
    write(OUT/'inventory.json',inventory)
    # The reviewed measurements are the source of truth for the historical generator.
    write(ROOT/'inventory_work/versiones_version_pairs.json',read(OUT/'version_comparisons.json'))
    receipt={'review_date':'2026-11-03','source_record_count':len(inventory),'source_id_and_assignment_preservation':True,'corrected_exclusion_rationales':74,'scope_changes':changes,'new_public_identity_checks':content_receipts,'main_scope_counts':scope['counts'],'broad_scope_counts':broad['counts'],'remaining_main_scope_ids':[x['video_id'] for x in scope['records'] if x['scope_decision']=='scope_unconfirmed'],'scope_limit':'Case03–Casanare only. Territorial openings outside scope were used solely to establish exclusion, not to analyze testimony.'}
    write(REVIEW/'tieout_data_decisions.json',receipt)
    print(json.dumps({k:receipt[k] for k in ['source_record_count','corrected_exclusion_rationales','main_scope_counts','broad_scope_counts','remaining_main_scope_ids']},indent=2))


if __name__=='__main__':main()
