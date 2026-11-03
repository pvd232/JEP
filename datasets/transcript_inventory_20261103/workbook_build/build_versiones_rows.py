"""Build draft source rows while preserving accepted Drive-file identities.

The accepted registry freezes source-file/group IDs across filename changes.
New groups receive unused draft IDs; accepted additions belong in that registry
before a later source snapshot is built. This script does not accept or rewrite
the registry automatically.
"""
import json,re,unicodedata,hashlib
from pathlib import Path


def read_record_id_registry(path):
    """Load the accepted file-to-record map and reject ambiguous ownership."""
    registry = json.loads(path.read_text())
    if registry.get('schema_version') != 1 or not isinstance(registry.get('records'), list):
        raise ValueError('Unsupported accepted record-ID registry')
    by_source = {}
    record_ids = set()
    for record in registry['records']:
        uid = record.get('unique_id')
        source_ids = record.get('source_file_ids')
        if not isinstance(uid, str) or not uid or uid in record_ids:
            raise ValueError('Missing or repeated accepted record ID: ' + str(uid))
        if not isinstance(source_ids, list) or not source_ids:
            raise ValueError('Accepted record has no source-file IDs: ' + uid)
        record_ids.add(uid)
        for fid in source_ids:
            if not isinstance(fid, str) or not fid or fid in by_source:
                raise ValueError('Missing or multiply assigned accepted source ID: ' + str(fid))
            by_source[fid] = uid
    return by_source, record_ids


def resolve_record_ids(files, comparisons, accepted_by_source, reserved_ids):
    """Assign one stable ID per source group, rejecting merges or splits of IDs.

    Any accepted member identifies the group, so changing the preferred source
    or adding a new alternate does not create a new record. Filename sorting
    affects presentation only. New-group allocation sorts immutable Drive IDs.
    """
    by_file = {}
    for item in files:
        fid = item['id']
        if fid in by_file:
            raise ValueError('Repeated source-file ID in metadata: ' + fid)
        by_file[fid] = item
    variants = {}
    for pair in comparisons:
        canonical_id, variant_id = pair['canonical_id'], pair['variant_id']
        if canonical_id not in by_file or variant_id not in by_file:
            raise ValueError('Version comparison references an absent source file')
        if canonical_id == variant_id or variant_id in variants:
            raise ValueError('Source variant is self-referential or assigned twice: ' + variant_id)
        variants[variant_id] = canonical_id
    canonical = [item for item in files if item['id'] not in variants]
    groups = {item['id']: [item['id']] for item in canonical}
    for variant_id, canonical_id in variants.items():
        if canonical_id not in groups:
            raise ValueError('Version groups cannot contain a canonical/variant chain')
        groups[canonical_id].append(variant_id)

    assigned = {}
    active_record_ids = {}
    new_groups = []
    for canonical_id, source_ids in groups.items():
        known_ids = {accepted_by_source[fid] for fid in source_ids if fid in accepted_by_source}
        if len(known_ids) > 1:
            raise ValueError('Source group mixes established record IDs: ' + ', '.join(sorted(known_ids)))
        if not known_ids:
            new_groups.append(canonical_id)
            continue
        uid = next(iter(known_ids))
        if uid in active_record_ids:
            raise ValueError('Established record ID appears in more than one source group: ' + uid)
        assigned[canonical_id] = uid
        active_record_ids[uid] = canonical_id

    # Reserve IDs even when their source files are absent from this snapshot.
    used_ids = set(reserved_ids) | set(active_record_ids)
    numbers = [int(match[1]) for uid in used_ids if (match := re.fullmatch(r'VV-(\d+)', uid))]
    next_number = max(numbers, default=0) + 1
    for canonical_id in sorted(new_groups):
        uid = f'VV-{next_number:03}'
        while uid in used_ids:
            next_number += 1
            uid = f'VV-{next_number:03}'
        assigned[canonical_id] = uid
        used_ids.add(uid)
        next_number += 1
    return canonical, assigned


P=Path(__file__).resolve().parent
meta=json.loads((P/'versiones_metadata.json').read_text())['files']
byid={f['id']:f for f in meta}
docs=json.loads((P/'versiones_text_private.json').read_text())
names=json.loads((P/'versiones_names_full.json').read_text())
names['13EK-a2CpGibQ5FjmPFxYIGE8D2RXowJT']='Manuel Guillermo Torres Ramírez'
pairs=json.loads((P/'versiones_version_pairs.json').read_text())
accepted_by_source, reserved_record_ids = read_record_id_registry(P/'tieout_review_20261103/accepted_record_ids.json')
canonical, record_ids = resolve_record_ids(meta, pairs, accepted_by_source, reserved_record_ids)
public={}
def walk(obj):
    if isinstance(obj,dict):
        yield obj
        for v in obj.values():yield from walk(v)
    elif isinstance(obj,list):
        for v in obj:yield from walk(v)
for f in list(P.glob('*catalog*.json'))+[P/'youtube_search_latest.json']:
    try:data=json.loads(f.read_text())
    except:continue
    for v in walk(data):
        vid=v.get('id') or v.get('video_id');title=v.get('title');author=v.get('by') or v.get('channel') or v.get('author')
        if isinstance(vid,str) and re.fullmatch(r'[A-Za-z0-9_-]{11}',vid) and isinstance(title,str) and author=='JEP Colombia':
            public[vid]={**public.get(vid,{}),**v,'catalog_source':f.name}
for f in (P/'public_video_cache').glob('*.json'):
    if f.name.endswith(('.player.json','.captions.json','.transcript.json')):continue
    try:v=json.loads(f.read_text())
    except:continue
    if v.get('author')=='JEP Colombia' and v.get('title'):public[v['video_id']]={**public.get(v['video_id'],{}),**v,'id':v['video_id']}

def norm(s):return ''.join(c for c in unicodedata.normalize('NFD',s.lower()) if not unicodedata.combining(c))
def date_from_filename(s):
    m=re.search(r'(?<!\d)(\d{1,2})_?(\d{2})_?(\d{4})(?!\d)',s)
    if m:return f'{m[3]}-{int(m[2]):02}-{int(m[1]):02}'
    return ''
date_overrides={'1ZCaNDr-ZXYdlBYBg5c3spFCwDIuByoDH':'2020-09-15','1DVSSFSwWRxlxxevpA9dxvOAM3IQbGft3':'2021-03-19','1JTQYDtd_rZ-SMuFVPUwXZMjXL1rS5tZm':'2020-07-27','1mItfHk3W54vx0FITbtkm93YwtH2pwo4q':'2021-02-26','18rzshw-ncns3VACI_xkkEAQHEtfLudbM':'2021-02-11','1wXJeoXNE0lboCSGRlpCDbtLiHfU1cP3M':'2020-09-30','11cO1ywUtlEHJsNgY7OXgLkeXJXyw6jnK':'2021-10-28'}
notes={
 '1ZCaNDr-ZXYdlBYBg5c3spFCwDIuByoDH':'Filename says 15 Oct 2021; header and opening state 15 Sep 2020. Public surname spelling may be Vaquero/Baquero.',
 '1DVSSFSwWRxlxxevpA9dxvOAM3IQbGft3':'Filename says 19 Feb 2021; header and opening state 19 Mar 2021.',
 '1JTQYDtd_rZ-SMuFVPUwXZMjXL1rS5tZm':'Opening states Monday 27 Jul 2020; filename and footer say 29 Jul 2020. Date conflict retained.',
 '1GdPPPTf1vjCvmvdz8VjFUaH-uePylhEX':'Separate protective-measures hearing; opening says voluntary statement follows. Closing labels this hearing private/reserved. Do not substitute the same-day public voluntary-statement video.',
 '1Y5qnU1nMOdAwXnyo1L2o1wFgVNjO2Mnb':'Heading labels a reserved hearing; second part only. First part is not supplied in this subtree.',
 '11cO1ywUtlEHJsNgY7OXgLkeXJXyw6jnK':'Sworn declaration involving protected minor XYZ. Retain source initials and protected label; no private testimony or identity expanded.',
 '1PN1Snb8AnIUiJtuykAqEc3KMGBbhvcrc':'Procedural installation/adjournment; closing reschedules continuation for 26 Jul 2019.',
 '1oVJANsQw20rg4kj1ornOHgvS7A2se3KX':'Procedural adjournment after counsel travel/weather issue; closing reschedules continuation for 30 Sep 2019.',
 '1tqF3vwbOVtv8_Um2pa50W15tniiYs60x':'Header says total audio 3/3, 05:49:45; transcript begins after formal installation. Recording boundaries require alignment.',
 '1_usjFoRvI8pSkTvBzKvpXKAF2tCPEmkW':'Complementary recorded submission; opening formalities omitted. Date absent from filename and extracted text.',
 '1Ss4qPHRnP26LuE0jb7raabat7VhdVs6v':'Sworn declaration, not a voluntary statement; local markers include invalid 00:08:64 (transcription timestamp error).',
 '11K1Ss57NMu93TYbCCm6YGXjMOGpNaRV6':'Sworn declaration; kept separate from voluntary statements.',
 '138-yUT_gJ7h8SYpaehxzk8h16UUrTCNm':'Sworn declaration with multiple source-video parts; time counters restart.',
 '1j-6mhB2S2x79LKsqorHEc78FA0RtDn3n':'Source identifies Sala de Definición de Situaciones Jurídicas; type differs from SRVR voluntary statements.',
 '1DnF_xlCndyksTEJmUB2FJrdXQgs5CKK7':'Source identifies Sala de Definición de Situaciones Jurídicas; type differs from SRVR voluntary statements.',
 '1cehr39R0sTduj4brl_Z2yW91kOBasmaA':'ODT text extracted locally; document identifies several source-video parts. Local counters are not YouTube offsets.',
 '1kKD2dUYz-USwnur2KTonUq3LFygfJZ4b':'Transcript spells Helbert/Herbert; public JEP video uses Gélver Pérez García. Name variant retained.',
 '1b1X0zzlTEZYzUx4hEdzPmBY4C7HE5FS1':'Transcript spells Helbert/Herbert; public JEP video uses Gélver Pérez García. Name variant retained.',
}
manual_video={
 '1f1Qt70iSbwOs57NcBken15lNg9td5SWV':['UzDjEgD4TEI'],
 '17sB2S1nRbSX7GDan43p1-ZraYiYl2ui0':['YVr6Kg_bLWI'],
 '15j_EE9zVj-tNdJqdGHrapM5UnzJCXbvL':['o_BvyjJigOE'],
 '1kKD2dUYz-USwnur2KTonUq3LFygfJZ4b':['zH62fXoKMX8'],
 '1b1X0zzlTEZYzUx4hEdzPmBY4C7HE5FS1':['eM8ZrqhZbgQ'],
 '1LJWWz_20fL0kQEq4eod0-_q6WoPGgSOf':['OwRzkECLUwE'],
 '1Q4Dv_g3c8mu457JeZ26uTStsGCGeicIs':['nWPgiw7qyZo'],
 '1_usjFoRvI8pSkTvBzKvpXKAF2tCPEmkW':['p2CITFhwOz4'],
 '1NviirtyULTCpTaiu3uKRCkv2LYkjLVtq':['GAs_0KxedWg'],
 '1Rdc7ibmcQTQe1YviFkpQjo7SNyIOAGSw':['QenmEm4OdvI'],
 '1IDfQ5w0x9ixuYNU8Sgd2wrFEVR_LWqVB':['JIEzFbO15mw'],
 '1ySIFbficSs-_ElQ-xLwtgqEiyWzGbu4V':['mJX7VBllEQw'],
 '1kec9P5SdbfJy4XxximR5_L6awtJMDCBO':['natlD9Yr6Oo'],
}
never_match={'1GdPPPTf1vjCvmvdz8VjFUaH-uePylhEX','1Y5qnU1nMOdAwXnyo1L2o1wFgVNjO2Mnb','11cO1ywUtlEHJsNgY7OXgLkeXJXyw6jnK'}
known_words={'jep','caso','subcaso','casanare','version','voluntaria','de','la','el','y','apellido','final','no','confirmado'}
def words(s):return set(re.findall(r'[a-z]+',norm(s)))-known_words
def videotitle_dates(title):
    vals=[]
    for y,m,d in re.findall(r'(20\d\d)[.\-/]?(\d\d)[.\-/]?(\d\d)',title):vals.append(y+'-'+m+'-'+d)
    for d,m,y in re.findall(r'(\d\d)/(\d\d)/(20\d\d)',title):vals.append(y+'-'+m+'-'+d)
    return vals
def candidates(name,date):
    out=[]; ns=words(name)
    for vid,v in public.items():
        nt=words(v['title']); overlap=len(ns&nt); ratio=overlap/max(1,len(ns)); ds=videotitle_dates(v['title']); date_ok=date in ds
        if overlap>=2 and (ratio>=.6 or date_ok):out.append((ratio+int(date_ok),date_ok,vid,v))
    return sorted(out,key=lambda a:(a[0],a[1]),reverse=True)

rows=[]
for f in sorted(canonical,key=lambda x:x['title'].casefold()):
    fid=f['id'];t=docs[fid]['text'];name=names.get(fid,'Unresolved');date=date_overrides.get(fid,date_from_filename(f['title']));pp=[x for x in pairs if x['canonical_id']==fid]
    links=[f['url']]+[byid[x['variant_id']]['url'] for x in pp]
    duplicate='No duplicate established.'
    if pp:
        x=pp[0]; duplicate=f"Same hearing, {x['relation']}: {x['variant_file']} ({byid[x['variant_id']]['url']}). Same participant/date; {x['shared_fivegrams']:,} shared normalized five-word spans. Text differs; all source files retained."
    source_title=f['title']
    # Keep reserved/protected records as bibliographic pointers only.
    matches=[]
    if fid not in never_match:
        cc=candidates(name,date)
        if fid in manual_video:matches=[public[v] if v in public else {'id':v,'title':'Public JEP candidate; metadata readback pending','by':'JEP Colombia'} for v in manual_video[fid]]
        elif cc and cc[0][1]:matches=[cc[0][3]]
    confidence='Unmatched';evidence=f'Doc: heading/opening or closing identifies {name}; {date or "date unresolved"}. No public session match established in reviewed JEP catalog.'
    if matches:
        v=matches[0];vd=videotitle_dates(v.get('title',''));exact=date in vd
        confidence='High (metadata)' if exact and fid not in {'1kKD2dUYz-USwnur2KTonUq3LFygfJZ4b','1b1X0zzlTEZYzUx4hEdzPmBY4C7HE5FS1','1JTQYDtd_rZ-SMuFVPUwXZMjXL1rS5tZm','1ZCaNDr-ZXYdlBYBg5c3spFCwDIuByoDH'} else 'Medium / verify'
        evidence=f'Doc heading/opening/closing: {name}, {date or "date not stated"}. Official JEP title'+('/description' if v.get('description') else '')+': same participant'+(' and hearing date.' if exact else '; date/name discrepancy needs verification.')
    if fid in never_match:
        confidence='Unmatched — reserved/protected';evidence='Source heading/opening/closing labels reserved/protected material; no public-video equivalence asserted.'
    # Local transcript clocks are kept separate from YouTube offsets.
    times=re.findall(r'(?<!\d)(\d{1,2}:\d{2}:\d{2})(?!\d)',t)
    valid=[x for x in times if all(int(z)<60 for z in x.split(':')[1:])]
    local='Not established; no verified YouTube offsets.'
    if valid:local=f'Transcript local markers include {valid[0]}–{valid[-1]}; counters may restart. YouTube alignment unverified.'
    elif fid=='1_usjFoRvI8pSkTvBzKvpXKAF2tCPEmkW':local='Transcript starts at source minute 03:06; YouTube offset unverified.'
    elif fid=='1vBhsy4fx5pCa8cN3lgkl1J7sduZA4Kw3':local='Transcript starts at source minute 16:39; YouTube offset unverified.'
    elif fid=='1w_141oY2AwUeVRpPbDeCi42PQMHYastO':local='First source marker 00:11:56; YouTube alignment unverified.'
    row={'source_id':fid,'unique_id':record_ids[fid],'title':source_title,'transcript_title':source_title,'date':date or 'Unknown','participants':name,'source_folder':'Datos/Diligencias Judiciales/Versiones Voluntarias/Transcripciones Equipo JEP'+('/Transcripciones anteriores' if '/Transcripciones anteriores' in f['folder'] else ''),'source_folder_url':'https://drive.google.com/drive/folders/'+('1RqAo3RWxqeiXxP5NO1SbxVTLvHKMyuL0' if '/Transcripciones anteriores' in f['folder'] else '15Xxxz53sCe2xQ6OJbWR_7FEX3-9Hf4uj'),'direct_file_link':f['url'],'source_file_ids':[fid]+[x['variant_id'] for x in pp],'all_file_links':links,'duplicate_notes':duplicate,'video_title':'\n'.join(v['title'] for v in matches),'youtube_url':'\n'.join('https://www.youtube.com/watch?v='+v.get('id',v.get('video_id','')) for v in matches),'timestamps':local,'confidence':confidence,'evidence':evidence,'notes':notes.get(fid,''),'video_candidates':matches,'normalized_text_sha256':hashlib.sha256(re.sub(r'\s+',' ',norm(t)).strip().encode()).hexdigest(),'content_characters':len(t)}
    rows.append(row)
(P/'versiones_rows_draft.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2))
(P/'versiones_public_catalog_merged.json').write_text(json.dumps(list(public.values()),ensure_ascii=False,indent=2))
print('rows',len(rows),'public_videos',len(public),'matched',sum(bool(r['youtube_url']) for r in rows))
for r in rows:print(json.dumps({k:r[k] for k in ('unique_id','title','date','participants','youtube_url','confidence')},ensure_ascii=False))
