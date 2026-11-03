"""Local-only review assembly; no canonical inventory or source mutations."""
from __future__ import annotations

import collections
import hashlib
import json
import pathlib
import re
import unicodedata

ROOT = pathlib.Path('/workspace/scratch/8a7e64850a04')
WORK = ROOT / 'inventory_work'
OUT = WORK / 'reverse_audit'
INV_PATH = ROOT / 'outputs/jep_transcripts_20261103/inventory.json'
INV = json.loads(INV_PATH.read_text())
BY_UID = {r['unique_id']: r for r in INV}
CAT = json.loads((WORK / 'deep_official_channel_complete.json').read_text())
CAT_BY_ID = {r['id']: r for r in CAT}
URL_RE = re.compile(r'(?:youtu\.be/|youtube\.com/(?:watch\?v=|live/))([\w-]{11})')


def norm(s):
    return ''.join(c for c in unicodedata.normalize('NFD', s.lower()) if not unicodedata.combining(c))


def url(vid):
    return f'https://www.youtube.com/watch?v={vid}'


def source_anchor(uid, anchor, note):
    return {'transcript_id': uid, 'source_url': BY_UID[uid]['direct_file_link'], 'anchor': anchor, 'supports': note}


def record_source_reference(r):
    source = json.loads((WORK / 'summary_sources' / f"{r['unique_id']}.json").read_text())
    segs = source['segments']
    return source_anchor(r['unique_id'], f"{segs[0]['anchor']}–{segs[-1]['anchor']}", 'Canonical supplied transcript; content/offset evidence is reused from the completed forward review.')


def cache(vid):
    f = WORK / 'public_video_cache' / f'{vid}.json'
    if f.exists():
        return json.loads(f.read_text())
    f = OUT / 'video_details.json'
    if f.exists():
        data = json.loads(f.read_text())
        if isinstance(data, dict):
            return data.get(vid, {})
        if isinstance(data, list):
            return next((x for x in data if x.get('video_id') == vid), {})
    return {}


def public_date(title):
    m = re.search(r'\b((?:19|20)\d{2})[./-]?(\d{2})[./-]?(\d{2})\b', title)
    if m:
        return '-'.join(m.groups())
    m = re.search(r'(\d{2})/(\d{2})/((?:19|20)\d{2})', title)
    return '-'.join(m.groups()[::-1]) if m else ''


def public_participant(title):
    if 'Saavedra' in title:
        return 'Carlos Ovidio Saavedra Sáenz'
    parts = [s.strip() for s in title.split('|')]
    if len(parts) >= 4 and not title.startswith('Audiencia'):
        return parts[-1] if 'Erwin Eduardo' in parts[-1] else parts[1]
    return ''


PARTIAL_SOURCE = {
    'VV-012': ('Partial supplied transcript; opening formalities omitted', 'Before approximately 00:24:05, opening formalities are not transcribed.', [('P0004–P0005', 'Source begins after procedural explanation, at the general questionnaire.')]),
    'VV-015': ('Partial supplied transcript; opening formalities summarized', 'Before approximately 00:21:57, opening formalities are summarized. The supplied source also continues beyond this public upload; that is a separate forward recording gap.', [('P0004–P0008', 'Opening presentations and procedural explanation are summarized, then dialogue starts.'), ('P0757–P0758', '14:10 resumption is at public 03:55:16; upload ends during the next answer.')]),
    'VV-016': ('Partial supplied transcript; morning portion absent', 'Only the afternoon continuation at 03:20:51–03:58:03 is supplied. The preceding morning portion of the upload has no supplied transcript in the 93-record inventory.', [('P0008', 'Afternoon resumption at 13:58 on 6 Nov 2020.'), ('P0072', 'Closing at 14:35 on the same date.')]),
    'VV-025': ('Partial supplied transcript; opening and closing exchanges omitted', 'Verified source interval approximately 00:09:53–03:13:03; initial formalities and later final exchanges/adjournment are absent from this source.', [('P0011', 'First supplied dialogue after introductory source metadata.'), ('P0684', 'Last supplied dialogue; no complete hearing adjournment.')]),
    'VV-047': ('Partial supplied transcript; opening formalities omitted', 'Formal installation before approximately 00:17:41 is omitted; later dialogue and closing match.', [('P0007–P0008', 'Source starts when general questions begin.')]),
    'VV-053': ('Partial supplied transcript; opening presentation summarized', 'Presentation before approximately 00:03:06 is summarized/omitted; supplied substantive recording follows.', [('P0004–P0006', 'Source labels counsel presentation and states transcription begins at 03:06.')]),
}

rows = []
grouped = collections.defaultdict(list)
for r in INV:
    for vid in URL_RE.findall(r.get('youtube_url', '')):
        grouped[vid].append(r)

for vid, linked in grouped.items():
    md = cache(vid)
    status = 'Supplied transcript located; content match established'
    limits = ['Reuses the completed forward review. Caption anchors are approximate, not a word-for-word audio certification. Unchecked introductions, recesses and repeated audiovisual inserts are not presumed verbatim transcribed.']
    gap = ''
    anchors = [record_source_reference(r) for r in linked]
    if any(not r.get('content_verified') for r in linked):
        status = 'Supplied transcript linked by metadata; content/coverage unverified'
        limits = ['The existing source/video identity is metadata-supported; public captions or playable-media content checks remain unavailable. Do not count as verified full-video transcription coverage.']
    for r in linked:
        uid = r['unique_id']
        if uid in PARTIAL_SOURCE:
            status, gap, aa = PARTIAL_SOURCE[uid]
            anchors = [source_anchor(uid, a, note) for a, note in aa]
        if uid == 'VV-038':
            gap = 'No reverse transcript gap established for this located upload. The source continues beyond its 07:09:00 end; missing public continuation is a forward recording gap.'
            anchors = [source_anchor(uid, 'P1411', 'Last public caption match at 07:08:04; upload ends during this answer.'), source_anchor(uid, 'P1412–P1495', 'Additional supplied text after the located upload, through hearing close.')]
    duplicate = 'No alternate-upload equivalence inferred.'
    related = []
    if vid == 'eM8ZrqhZbgQ':
        status = 'Supplied by two distinct transcript segments; content match established'
        duplicate = 'VV-030 protective-measures segment precedes VV-029 voluntary statement within this same upload; these are not duplicate transcripts.'
        anchors = [source_anchor('VV-030', 'P0001 onward', 'Protective-measures segment documented in completed forward review.'), source_anchor('VV-029', 'P0001 onward', 'Voluntary-statement segment documented in completed forward review.')]
    if vid in {'GJ8DgTuRFws', 'f6dkdTyATco'}:
        other = 'f6dkdTyATco' if vid == 'GJ8DgTuRFws' else 'GJ8DgTuRFws'
        related = [other]
        duplicate = 'Verified same 19 Mar 2026 hearing. JEP upload GJ8DgTuRFws removes long recesses present in Radio Nacional upload f6dkdTyATco; one supplied transcript covers all four source parts.'
    rows.append({
        'video_id': vid, 'url': url(vid), 'title': md.get('title') or CAT_BY_ID.get(vid, {}).get('title') or linked[0].get('video_title', ''),
        'transcript_ids': [r['unique_id'] for r in linked], 'coverage_status': status,
        'evidence': [{'transcript_id': r['unique_id'], 'claim': r['evidence'], 'source_url': r['direct_file_link'], 'public_url': url(vid)} for r in linked],
        'source_anchors': anchors,
        'video_offsets': [{'transcript_id': r['unique_id'], 'offsets': r['timestamps'], 'verification': r.get('verification_level', '')} for r in linked],
        'duplicate_relation': duplicate, 'related_video_ids': related,
        'coverage_gap': gap, 'review_limits': limits,
        'source_dates': sorted(set(r['date'] for r in linked)),
        'basis': 'Existing forward content review' if all(r.get('content_verified') for r in linked) else 'Existing forward metadata mapping',
    })

scope = json.loads((OUT / 'scope_decisions_initial.json').read_text())
absent = [r for r in scope['records'] if r['scope_decision'] == 'included' and not r['exact_video_id_currently_linked'] and r['video_id'] not in grouped]
for r in absent:
    vid = r['video_id']
    md = cache(vid)
    title = md.get('title') or r['title']
    who = public_participant(title)
    date = public_date(title)
    rr = {
        'video_id': vid, 'url': url(vid), 'title': title, 'transcript_ids': [],
        'coverage_status': 'No supplied transcript located for public-metadata session',
        'public_session_date': date, 'date_basis': 'Date in official public title; hearing content not checked in this reverse pass.',
        'public_participant': who,
        'evidence': [{'claim': f'Official Casanare title identifies {who or "this hearing"}' + (f' on {date}.' if date else '.'), 'public_url': url(vid), 'pointer': 'Official public title; channel catalog.'},
                     {'claim': 'Compared with all 93 supplied records and their established session identities. No corresponding transcript record found; mentions of this person in other hearings do not constitute a transcript of this session.', 'source': 'outputs/jep_transcripts_20261103/inventory.json'}],
        'source_anchors': [], 'video_offsets': [], 'duplicate_relation': 'No duplicate or alternate-upload relationship established.', 'related_video_ids': [],
        'coverage_gap': 'No supplied source session located.',
        'review_limits': ['Absence decision is against the supplied 93-record inventory, not all possible Drive holdings or all JEP records. Public name/date metadata supports the candidate session; this upload has not received a new content check.'],
        'basis': 'Public title plus complete supplied-session index comparison',
    }
    if who:
        words = set(norm(who).split())
        near = [x for x in INV if x['unique_id'].startswith('VV-') and len(words & set(norm(x['participants']).split())) >= 3 and 'Protected' not in x['participants']]
        if near:
            rr['related_transcript_ids'] = [x['unique_id'] for x in near]
            rr['related_video_ids'] = sorted({v for x in near for v in URL_RE.findall(x.get('youtube_url', ''))})
            rr['evidence'].append({'claim': 'Same-person supplied sessions have dates: ' + '; '.join(f"{x['unique_id']} {x['date']}" for x in near) + '. Their presence alone does not establish coverage of this upload.', 'source': 'Supplied source openings and completed forward content checks.'})
    rows.append(rr)

by = {r['video_id']: r for r in rows}
for vid in ['FoAy5Qfphcs']:
    r = by[vid]
    r.update(coverage_status='Coverage unconfirmed; possible same-session alternate upload', related_transcript_ids=['VV-057','VV-059','VV-058','VV-060'], related_video_ids=['ztGtBj4AbQA','uzg0kvYZudo','-ZfNT5R72fI','Tr3kzy06EHo'], coverage_gap='Do not count as a missing transcript or duplicate until content is compared.', duplicate_relation='Title gives the same participant and 5 Jul 2019 date as supplied VV-057/current ztGtBj4AbQA. Similar title alone is insufficient to merge.')
    r['source_anchors'] = [source_anchor('VV-057', 'P0003/P0006', 'Source dates installation 5 Jul 2019 and names Marco Fabián García Céspedes.'), source_anchor('VV-057', 'P0048', 'Procedural continuation scheduled for 26 Jul 2019.')]
    r['review_limits'] = ['A short opening/body/closing comparison against ztGtBj4AbQA and VV-057 is needed. Neither duplicate status nor an additional missing session is inferred from title alone.']

for vid, uid, opening, closing in [('cGyu3lTjqso', 'CAS03-20230919-AM', 'Orders2–3', 'Order205'), ('cSKgOHGfLQw', 'CAS03-20230920-AM', 'Order1', 'Order107')]:
    r = by[vid]
    r.update(coverage_status='Coverage unconfirmed; same-day recognition upload', related_transcript_ids=[uid], related_video_ids=URL_RE.findall(BY_UID[uid]['youtube_url']), coverage_gap='Candidate missing afternoon/continuation, pending public-content check.', duplicate_relation='Same calendar date as a supplied morning record. A separate upload does not by itself prove a distinct afternoon session.')
    r['source_anchors'] = [source_anchor(uid, opening, 'Supplied morning installation.'), source_anchor(uid, closing, 'Supplied source ends at lunch adjournment.')]
    r['evidence'].append({'claim': BY_UID[uid]['evidence'], 'source_url': BY_UID[uid]['direct_file_link']})
    r['review_limits'] = ['Need this upload opening/closing or equivalent content comparison to determine whether it is an afternoon segment or alternate morning upload.']

for vid, uids, anchors in [
    ('w49HGaeBNRk', ['VV-017', 'VV-018'], [('VV-017', 'P0008', 'Supplied 20 Feb 2019 installation.'), ('VV-018', 'P0005', 'Supplied 27 Jun 2019 continuation installation.')]),
    ('uTjViv5Vtpc', ['VV-017', 'VV-018'], [('VV-017', 'P0008', 'Supplied 20 Feb 2019 installation.'), ('VV-018', 'P0005', 'Supplied 27 Jun 2019 continuation installation.')]),
    ('eKrYlu79rGo', ['VV-041'], [('VV-041', 'P0001', 'Supplied opening explicitly gives 27 Jul 2020; source filename 29 Jul is a retained conflict.')]),
]:
    r = by[vid]
    r['related_transcript_ids'] = uids
    r['source_anchors'] = [source_anchor(*a) for a in anchors]
    r['review_limits'].append('A same-person source exists for another date. Because public metadata elsewhere contains date errors, an opening-content check is needed before treating the session distinction as content verified.')

r = by['s6x7MjB24E8']
r.update(coverage_status='No supplied transcript located; distinct session content verified', public_session_date='2020-08-28', date_basis='Public captions explicitly state28 Aug 2020 at opening and closing.', related_transcript_ids=['VV-020'], basis='Public caption comparison from previous investigation plus supplied-session index')
r['source_anchors'] = [source_anchor('VV-020', 'P0004/P0009/P0010', 'Supplied Amaya hearing is 29 Apr 2019, a different session.')]
r['video_offsets'] = [{'offsets':'00:00:08;05:43:19–05:43:34','verification':'Dated opening and closing establish 28 Aug 2020.'}]
r['evidence'].append({'claim':'Existing public-caption check at 00:08 and05:43:28 establishes28 Aug 2020, whereas the only supplied Amaya source repeatedly states 29 Apr 2019.', 'public_url':url('s6x7MjB24E8'), 'source_url':BY_UID['VV-020']['direct_file_link'], 'pointer':'inventory_work/deep_unmatched.json, VV-020 candidate_rejection.'})
r['review_limits'] = ['This is an existing bounded caption check, not a new complete audio review. No supplied28 Aug 2020 transcript found among 93 records.']

AUTO = 'https://www.coljuristas.org/observatorio_jep/documentos/sala_de_reconocimiento/Auto_SRVR-SUB-D-055_14-julio-2022.pdf'
for vid, page, footnote, claim in [
    ('QefPfduOZ2Y',32,178,'Auto 055 independently cites Henry William Torres Escalante 10 Sep 2021, supporting the title year.'),
    ('KpZNfys5EgQ',55,349,'Auto 055 independently cites Jaime Alberto Rivera Mahecha 6 Dec 2018. An inconsistent annex date should not override both this citation and the public title.'),
    ('qTkUcVlA098',196,1307,'Auto 055 independently cites Gustavo Alberto Parada Cuellar 19 May 2022. An inconsistent annex date should not override both this citation and the public title.'),
    ('eKrYlu79rGo',190,1261,'Auto 055 independently identifies Solano’s written voluntary statement of 15 Oct 2019; video may be its recorded supplement, distinct from the supplied July 2020 hearing.'),
]:
    by[vid]['evidence'].append({'claim':claim,'public_url':f'{AUTO}#page={page}','pointer':f'Auto SRVR-SUB-D-055, 14 Jul 2022, PDF p.{page}, footnote {footnote}.'})


# Bounded root browser checks can resolve alternates without merging video IDs.
forward_corrections = []
root_check_path = OUT / 'root_content_checks.json'
if root_check_path.exists():
    root_checks = json.loads(root_check_path.read_text())
    for check in root_checks.get('checks', []):
        if check.get('video_id') != 'FoAy5Qfphcs':
            continue
        r = by['FoAy5Qfphcs']
        r.update(
            transcript_ids=['VV-057'],
            coverage_status='Supplied transcript located; same-session alternate upload verified',
            duplicate_relation='Content-verified same procedural session as ztGtBj4AbQA, with separate video IDs retained. Not a claim of byte identity or every-frame equivalence.',
            related_video_ids=['ztGtBj4AbQA'],
            related_transcript_ids=['VV-057'],
            coverage_gap='',
            basis='Bounded public caption opening, middle and closing comparison by root reviewer',
            review_limits=[check['review_limits']],
            video_offsets=[{'transcript_id':'VV-057','offsets':a['new_video_range'],'comparison_to_existing_upload':a['existing_video_range'],'verification':a['evidence']} for a in check['anchors']],
            evidence=[{'claim':check['finding'],'source_url':BY_UID['VV-057']['direct_file_link'],'public_url':url('FoAy5Qfphcs'),'pointer':'root_content_checks.json; three ordered caption anchors.'}],
            source_anchors=[source_anchor('VV-057','P0006','Installation at 09:33 on 5 July 2019.'),source_anchor('VV-057','P0042','Defense request to suspend.'),source_anchor('VV-057','P0048','Continuation scheduled for 26 July 2019.')],
        )
        by['ztGtBj4AbQA']['related_video_ids'] = ['FoAy5Qfphcs']
        by['ztGtBj4AbQA']['duplicate_relation'] = r['duplicate_relation']
        forward_corrections.append({'unique_id':'VV-057','action':'Add verified alternate public upload; retain established URL','add_youtube_url':url('FoAy5Qfphcs'),'evidence':'Same 5 July 2019 procedural hearing verified at opening 00:00:08–00:00:54, suspension request 00:17:48–00:18:04, and closing 00:30:58–00:31:41. Separate upload identity, not byte duplication.'})

nav_path = OUT / 'legal_date_navigation_private.json'
if nav_path.exists():
    # Each candidate below was manually checked against its local public-PDF
    # navigation window; only bibliographic pointers leave the scratch cache.
    legal = json.loads(nav_path.read_text())
    for item in legal['candidates']:
        r = by[item['video_id']]
        m = item['matches'][0]
        if item['video_id'] == 's6x7MjB24E8':
            m['footnote'] = '1060'
        pointer = f"Auto SRVR-SUB-D-055, 14 July 2022, PDF p. {m['pdf_page']}"
        if m.get('footnote'):
            pointer += f", footnote {m['footnote']}"
        pointer += f"; citation to {m['matching_name']}, {m['matching_date']}."
        r['evidence'].append({'claim':'The public decision independently cites this named participant and hearing date. This corroborates session metadata, not the content of this specific upload.','public_url':f"{AUTO}#page={m['pdf_page']}",'pointer':pointer})
        r['independent_date_corroboration'] = True
        if r['coverage_status'] == 'No supplied transcript located for public-metadata session':
            r['date_basis'] = 'Official public-title date independently corroborated by the cited Auto 055 bibliography; this specific upload has not received a content check.'

# Parent's bounded public-caption check, delivered with explicit anchors.
r = by['cGyu3lTjqso']
r.update(
    coverage_status='No supplied transcript located; distinct afternoon session content verified',
    public_session_date='2023-09-19',
    date_basis='Public caption at 00:29:11 explicitly resumes at 16:02 on Tuesday 19 September 2023 in Yopal; dated closing agrees.',
    duplicate_relation='Afternoon continuation of the same hearing day, distinct from the supplied morning upload fHVMPnXbj88. Not a duplicate of the morning transcript.',
    coverage_gap='No supplied 19 September 2023 afternoon transcript found. Supplied CAS03-20230919-AM ends at the 14:27 lunch adjournment.',
    basis='Public caption installation and closing, official afternoon description, and supplied morning-source closing comparison',
    video_offsets=[
        {'offsets':'00:29:11','verification':'16:02, Tuesday 19 September 2023, Yopal; afternoon resumption.'},
        {'offsets':'00:32:06; 00:34:13','verification':'Marcolino Puerto Jiménez is introduced and speaks.'},
        {'offsets':'04:36:34–04:37:04','verification':'Closing at 20:09 on 19 September 2023.'},
    ],
    review_limits=['Bounded public automatic-caption check, not exhaustive audio review. First available caption 00:28:50 is not a certified recording start. Player/catalog duration differs by one second.'],
)
r['evidence'].append({'claim':'Public opening and closing establish a distinct afternoon session: 16:02 resumption and 20:09 closing, 19 September 2023. Source Order 205 instead ends the morning at 14:27 for lunch.','public_url':url('cGyu3lTjqso'),'source_url':BY_UID['CAS03-20230919-AM']['direct_file_link'],'pointer':'Parent public-transcript-panel check; 00:29:11 and 04:36:34–04:37:04.'})

r = by['cSKgOHGfLQw']
r.update(
    coverage_status='No supplied transcript located; distinct afternoon session content verified',
    public_session_date='2023-09-20',
    date_basis='Public captions explicitly identify the afternoon of Wednesday 20 September 2023, with a dated closing.',
    duplicate_relation='Afternoon continuation of the same hearing day, distinct from supplied morning upload i1WWWhIL7_Y. Not a duplicate of the morning transcript.',
    coverage_gap='No supplied 20 September 2023 afternoon transcript found. Supplied CAS03-20230920-AM ends at the 13:21 lunch adjournment and announces a 14:35 return.',
    basis='Public caption resumption and closing plus supplied morning-source closing comparison',
    video_offsets=[
        {'offsets':'00:05:47–00:06:36','verification':'Explicit afternoon resumption on Wednesday 20 September 2023.'},
        {'offsets':'00:07:00–00:07:20','verification':'Gildardo Antonio Jiménez Castrillón is called.'},
        {'offsets':'02:49:44–02:50:08','verification':'Closing at 17:45 on Wednesday 20 September 2023.'},
    ],
    review_limits=['Bounded public automatic-caption check, not exhaustive audio review. The opening wall-clock caption is garbled and has not been normalized to an inferred time.'],
)
r['evidence'].append({'claim':'Public captions establish the distinct afternoon session on 20 September 2023; closing states 17:45. Source Order 107 instead ends the morning at 13:21 and announces a 14:35 return.','public_url':url('cSKgOHGfLQw'),'source_url':BY_UID['CAS03-20230920-AM']['direct_file_link'],'pointer':'Parent public-transcript-panel check; 00:05:47–00:06:36 and 02:49:44–02:50:08.'})

r = by['uTjViv5Vtpc']
r.update(
    coverage_status='No supplied transcript located; distinct recorded response content checked',
    date_basis='21 October 2019 is the official public-title/description label only. No spoken session or recording date observed in the full public caption export.',
    recording_type='Short recorded questionnaire response',
    duplicate_relation='Distinct questionnaire-response recording, not an alternate of supplied Toro hearings VV-017/VV-018 or the same-date Montaño hearing VV-025.',
    related_transcript_ids=['VV-017','VV-018','VV-025'],
    related_video_ids=['Dlfn1RekIeA','VB-J8_VU7dk','kzsidY3b75k'],
    coverage_gap='No supplied transcript of this recorded questionnaire response located among the 93 records.',
    basis='Complete 11-minute public caption export compared locally with both supplied Toro texts, with manual structural checks and same-date Montaño control',
    video_offsets=[
        {'offsets':'00:00:08–00:00:30','verification':'Self-introduction and explicit response to a JEP questionnaire; first question concerns Batallón de Artillería 4.'},
        {'offsets':'00:03:32–00:04:40','verification':'Compact question/answer on selection for precision-rifle training; different wording and structure from supplied course account.'},
        {'offsets':'00:08:26–00:11:27','verification':'Final questionnaire item and route account; upload then cuts to music at 11:29 without a completed formal adjournment.'},
    ],
    source_anchors=[
        source_anchor('VV-017','P0008','Supplied dated formal installation: 20 February 2019.'),
        source_anchor('VV-018','P0005/P0042','Supplied dated formal installation: 27 June 2019; course account has different wording.'),
        source_anchor('VV-018','P0381–P0405','Supplied Sprint-vehicle passages concern a different route and do not reproduce the public final sequence.'),
        source_anchor('VV-025','P0004–P0011','Same-date source identifies Giovanni Montaño; not this Toro questionnaire recording.'),
    ],
    review_limits=[
        'Public automatic captions contain name-recognition errors. Recording identity/format is supported by official title, self-introduction and content; precise recording date remains unverified.',
        'Zero long exact-text matches alone is not proof of distinction. The result is combined with manually checked questionnaire structure, distinctive route details and different supplied openings.',
        'The official description calls this a presided virtual hearing; the recording itself presents a self-read questionnaire response. The description formula is not treated as proof of hearing format.',
        'The final account cuts to music; no complete formal closing is present. Full source audio was not independently listened to.',
    ],
)
r['evidence'].append({'claim':'Full public export has 254 caption cues and 1,620 normalized words. It has zero unique exact 12-word matches against supplied VV-017, VV-018 and VV-025. Manual review confirms a different self-read questionnaire sequence; repeated general topics are not treated as identical transcript content.','public_url':url('uTjViv5Vtpc'),'pointer':'toro_questionnaire_alignment.json; public 00:08–00:30,03:32–04:40,08:26–11:27.'})

for r in rows:
    md = cache(r['video_id'])
    if md:
        r['metadata_check'] = {k: md.get(k) for k in ['title','author','channel_name','channel_id','length_seconds','publish_date','upload_date','playability'] if md.get(k) is not None}
    r['review_confidence'] = (
        'Content-verified session identity; supplied-source coverage limited as stated'
        if 'content verified' in r['coverage_status'] or 'content checked' in r['coverage_status'] or (r['transcript_ids'] and all(BY_UID[u].get('content_verified') for u in r['transcript_ids']))
        else 'Metadata-supported; recording content or coverage remains unverified'
    )

result = {
    'as_of':'2026-11-03',
    'status':'Local mapping complete for the current included hearing set; final scope reconciliation pending.',
    'inventory_record_count':len(INV),
    'inventory_sha256':hashlib.sha256(INV_PATH.read_bytes()).hexdigest(),
    'scope_source':'inventory_work/reverse_audit/scope_decisions_initial.json',
    'scope_unconfirmed_video_ids':[r['video_id'] for r in scope['records'] if r['scope_decision'] == 'scope_unconfirmed'],
    'unit':'One public video ID. Session grouping and transcript coverage are separate questions.',
    'method':[
        'Start with complete cached official channel 3510-item metadata catalog. Select explicit Casanare hearing titles absent from current primary links; scope decisions and live playlist additions are provided by sibling reviewers.',
        'Compare each candidate against all 93 supplied records, established participant/session dates, source openings where same-person or same-day ambiguity exists, and documented public date corrections.',
        'Reuse completed forward caption-content evidence for existing video IDs. Do not treat a source extending past an upload as an upload lacking a transcript. Track source excerpts separately.',
        'Different video IDs and similar titles are not evidence of duplication. Retain unresolved alternatives until public content or equivalent independent evidence establishes relation.',
        'A local cross-check for supplied principal names in other catalog hearing titles found only two additional Barrero uploads explicitly labelled Meta in October 2024; a same-person match does not establish Casanare scope or source coverage.',
        'No source files changed; no recordings or private testimony transmitted to public search. This review performs local comparisons only.',
    ],
    'counts':dict(collections.Counter(r['coverage_status'] for r in rows)),
    'videos':rows,
    'priority_content_checks': [],
    'forward_mapping_corrections':forward_corrections,
    'limits':[
        'The no-supplied-source count is a count of public video IDs, not a certified count of additional unique hearings or transcripts. Metadata-only cases may still include undiscovered reuploads or mislabeled session dates.',
        'Metadata-supported missing-source candidates are not represented as new content-verified hearing identities. Final inclusion depends on separate scope review and freshly enumerated playlist additions.',
    ],
}
(OUT / 'reverse_mapping_review.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'videos':len(rows),'counts':result['counts'],'priority_content_checks':result['priority_content_checks']},ensure_ascii=False,indent=2))
