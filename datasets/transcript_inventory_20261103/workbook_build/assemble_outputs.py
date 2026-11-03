"""Assemble reviewed metadata for the existing single workbook; preserve sources."""
from __future__ import annotations

import collections
import csv
import gzip
import hashlib
import json
import re
import shutil
from pathlib import Path

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[1]
OUT = ROOT / 'outputs/jep_transcripts_20261103'


def read(path):
    return json.loads(Path(path).read_text())


def write(name, data):
    (OUT/name).write_text(json.dumps(data, ensure_ascii=False, indent=2)+'\n')


def safe_paths(value):
    if isinstance(value, dict):
        return {k:safe_paths(v) for k,v in value.items()}
    if isinstance(value, list):
        return [safe_paths(v) for v in value]
    if isinstance(value, str):
        return value.replace(str(ROOT)+'/', '')
    return value


def seconds(value):
    if value is None or value == '':
        return None
    if str(value).isdigit():
        return int(value)
    if re.fullmatch(r'\d+(?::\d{2}){1,2}', str(value)):
        total=0
        for n in str(value).split(':'):
            total=total*60+int(n)
        return total
    return None


def coverage_label(record):
    status=record.get('coverage_status','')
    if status.startswith('Partial supplied transcript'):
        return 'Partial supplied transcript'
    if 'metadata; content/coverage unverified' in status:
        return 'Supplied transcript linked · metadata only'
    if status.startswith('No supplied transcript'):
        if 'content verified' in status or 'content checked' in status:
            return 'No supplied transcript · content checked'
        return 'No supplied transcript · metadata basis'
    if status.startswith('Coverage unconfirmed'):
        return 'Coverage unconfirmed'
    if record.get('transcript_ids'):
        if 'alternate' in status.lower() or (record.get('related_video_ids') and 'alternate' in record.get('duplicate_relation','').lower() and not record.get('duplicate_relation','').lower().startswith('no ')):
            return 'Supplied transcript linked · alternate upload'
        return 'Supplied transcript linked · content checked'
    return status or 'Coverage unconfirmed'


def main():
    scope=read(BASE/'scope_decisions_initial.json')
    reverse=read(BASE/'reverse_mapping_review.json')
    crawl=read(BASE/'crawl_manifest.json')
    catalog=read(BASE/'catalog.json')
    memberships=read(BASE/'memberships.json')
    broad=read(BASE/'broad_metadata_scope.json')
    controls=read(BASE/'root_content_checks.json')
    current=read(OUT/'inventory.json')
    stats=read(OUT/'summary.json')
    current_by_id={r['unique_id']:r for r in current}
    review_by_id={r['video_id']:r for r in reverse['videos']}
    catalog_by_id={r['video_id']:r for r in catalog}
    extra_by_id={r['video_id']:r for r in controls['checks']}
    coll_by_id={r['collection_id']:r for r in crawl['collections'] if r.get('collection_id')}
    member_by_id=collections.defaultdict(list)
    for m in memberships:
        member_by_id[m['video_id']].append(m)

    # The supplied source row is unchanged in identity; add the verified second upload.
    r=current_by_id['VV-057']
    r['youtube_url']='https://www.youtube.com/watch?v=ztGtBj4AbQA ; https://www.youtube.com/watch?v=FoAy5Qfphcs'
    r['duplicate_notes']='No duplicate source document established. Public uploads ztGtBj4AbQA and FoAy5Qfphcs cover the same procedural session; both IDs retained.'
    r['timestamps']='Primary ztGtBj4AbQA: 00:00:08, 00:17:49, 00:31:27. Alternate FoAy5Qfphcs: 00:00:08–00:00:54, 00:17:48–00:18:04, 00:30:58–00:31:41. Approximate public-caption anchors.'
    r['evidence']='Both uploads: 5 July 2019 installation at 09:33, defense postponement request, and 10:03 suspension until 26 July 2019 at 13:30. Opening, middle and closing captions agree with supplied P0006–P0048.'
    r['notes']='Procedural installation/adjournment. A second upload was verified in the reverse audit; same-session equivalence is established, not byte or every-frame identity.'

    video_rows=[]
    for s in scope['records']:
        vid=s['video_id']; review=review_by_id.get(vid,{})
        if s['scope_decision']=='included' and not review:
            raise ValueError('Included video lacks reverse coverage review: '+vid)
        node=catalog_by_id.get(vid,{})
        ids=review.get('transcript_ids',[])
        if any(i not in current_by_id for i in ids):
            raise ValueError('Unknown source ID for '+vid)
        links=[current_by_id[i]['direct_file_link'] for i in ids]
        title=s['title'] or node.get('title','')
        extra=extra_by_id.get(vid)
        claim_parts=[]
        for e in review.get('evidence',[]):
            if e.get('pointer'):
                claim_parts.append(e['pointer'])
            elif e.get('claim'):
                claim_parts.append(e['claim'])
        if extra:
            claim_parts=[extra['finding']]+[a['evidence'] for a in extra['anchors']]
        evidence=' '.join(dict.fromkeys(claim_parts))
        if review.get('coverage_gap') and review['coverage_gap'] not in evidence:
            evidence+=' '+review['coverage_gap']
        if s['scope_decision']!='included':
            evidence='Scope decision only; no transcript-absence conclusion is made.'
        offsets=[]
        for x in review.get('video_offsets',[]):
            if isinstance(x,dict):
                offsets.append((x.get('transcript_id','')+': '+x.get('offsets',x.get('range',''))).strip(': '))
            else:
                offsets.append(str(x))
        if extra:
            offsets=[a['new_video_range'] for a in extra['anchors']]
        collection_labels=[]
        for m in member_by_id[vid]:
            coll=coll_by_id.get(m.get('collection_id'),{})
            label=coll.get('title',m.get('collection_key','Collection'))
            pos=m.get('position')
            collection_labels.append(label+(f' · position {pos}' if pos else ''))
        if not collection_labels:
            collection_labels=s.get('discovery_collections',[])
        limits=review.get('review_limits',[])
        notes=[]
        if s.get('notes'): notes.append(s['notes'])
        if s.get('date_basis'): notes.append(s['date_basis'])
        notes.extend(limits)
        if review.get('related_video_ids'): notes.append('Related uploads: '+', '.join(review['related_video_ids'])+'. '+review.get('duplicate_relation',''))
        meta=review.get('metadata_check',{})
        duration=seconds(meta.get('length_seconds')) or seconds(node.get('duration_text')) or seconds(s.get('duration_metadata'))
        if extra: duration=seconds(extra.get('duration_text')) or duration
        label=coverage_label(review) if s['scope_decision']=='included' else ('Scope unconfirmed · outside confirmed corpus' if s['scope_decision']=='scope_unconfirmed' else 'Excluded · outside corpus')
        video_rows.append(dict(video_id=vid,url='https://www.youtube.com/watch?v='+vid,category=s['category'],scope_label={'included':'Included','excluded':'Excluded','scope_unconfirmed':'Scope unconfirmed'}[s['scope_decision']],title=title,date=s.get('date'),participants=s.get('participants',''),coverage_label=label,transcript_ids=ids,source_links=links,timestamps='\n'.join(offsets),evidence=evidence.strip(),duration_seconds=duration,publisher=s.get('publisher') or node.get('channel_name',''),collections=list(dict.fromkeys(collection_labels)),scope_evidence=s.get('evidence',''),notes=' '.join(dict.fromkeys(notes))))

    # Keep the reader's first view in-scope, chronological, then show the boundary decisions.
    video_rows.sort(key=lambda r:({'Included':0,'Scope unconfirmed':1,'Excluded':2}[r['scope_label']],r.get('date') or '9999',r['title'],r['video_id']))
    assert len({r['video_id'] for r in video_rows})==len(video_rows)
    included=[r for r in video_rows if r['scope_label']=='Included']
    counts=collections_module_count(video_rows,included)
    source_rows=[]
    for c in crawl['collections']:
        unavailable=c.get('hidden_unavailable_count')
        if c.get('unavailable_placeholder_memberships'):
            unavailable=c['unavailable_placeholder_memberships']
        if c.get('unavailable_placeholder_count') is not None:
            unavailable=c['unavailable_placeholder_count']
        pages=len(c.get('pages',[])) or c.get('pages_checked')
        if c['collection_key']=='deep_channel_videos': pages=90
        if c['collection_key']=='deep_channel_streams': pages=30
        if c.get('collection_type')=='official_web_page_section': pages=1
        evidence=[]
        if c.get('pagination_exhausted'): evidence.append('Primary-list pagination reached a terminal page.')
        if c.get('count_reconciled') is True: evidence.append('Listed positions reconcile to the declared total.')
        evidence.extend(x.rstrip('.')+'.' for x in c.get('notices',[]))
        if c.get('duplicate_memberships'): evidence.append(str(c['duplicate_memberships'])+' repeated appearance(s); video IDs retained once in the video map.')
        if c.get('hidden_only_video_ids'): evidence.append('Unavailable IDs exposed by the public list: '+', '.join(c['hidden_only_video_ids'])+'. Titles/content not exposed.')
        if c.get('unaccounted_declared_items'): evidence.append(str(c['unaccounted_declared_items'])+' declared positions remain unexplained.')
        if c.get('errors'): evidence.append('Errors: '+str(c['errors']))
        if c.get('status')=='reused_terminal_snapshot': evidence.append('Reuses earlier channel snapshot; original fetch time was not recorded. Terminal page checked with both continuation formats; not refetched.')
        if c.get('status')!='reused_terminal_snapshot' and c.get('provenance',{}).get('original_fetch_time'): evidence.append(c['provenance']['original_fetch_time'])
        source_rows.append(dict(title=c.get('title',c['collection_key']),role=c.get('scope','Metadata discovery'),declared_items=c.get('declared_items'),visible_memberships=c.get('normal_title_memberships',c.get('visible_memberships')),unique_video_ids=c.get('unique_video_ids'),unavailable_positions=unavailable,pages_checked=pages,status_label=c.get('status','Unknown').replace('_',' '),evidence=' '.join(dict.fromkeys(evidence)),source_url=c['source_url'],supplemental=c.get('supplemental',False) or c['collection_key'].startswith('region_')))

    if crawl.get('web_sources'):
        for web in crawl['web_sources']:
            source_rows.append(dict(title=web.get('title','Official Case03 page — Casanare section'),role='Casanare page links/embeds only',declared_items=None,visible_memberships=web.get('video_count'),unique_video_ids=web.get('video_count'),unavailable_positions=None,pages_checked=1,status_label=web.get('status','reviewed'),evidence=web.get('note',web.get('evidence','Relevant section extracted; unrelated navigation excluded.')),source_url=web.get('source_url',web.get('url','https://www.jep.gov.co/macrocasos/caso03.html')),supplemental=False))

    stats['reverse_audit']=dict(counts)
    stats['reverse_audit']['review_date']='2026-11-03'
    stats['reverse_audit']['broad_metadata_scope_counts']=broad.get('counts',{})
    stats['reverse_audit']['pagination_note']='Original parser stopped at100/898. Corrected primary-list parser fetched100 new IDs at positions101–200, then exhausted nine pages. See Crawl sources and the saved live reproduction for final unavailable-position accounting.'
    stats['reverse_audit']['completeness_note']='Every admitted video has a coverage decision. Declared-source pagination, hidden positions and unresolved geographic metadata are reported explicitly. This is a public-source audit, not proof that no private, unlisted or unpublished recordings exist.'
    stats['reverse_audit']['broad_scope_note']='Full broad Case03 membership decisions are saved in broad_metadata_scope.json. Generic proceedings without established Casanare membership remain outside the confirmed corpus; the residual count is reported there and in the accompanying report.'
    stats['reverse_audit']['new_verified_alternate_upload']='FoAy5Qfphcs → VV-057; existing transcript count unchanged.'
    stats['reverse_audit']['transcript_video_edges']=sum(len(re.findall(r'(?:v=|youtu.be/)([A-Za-z0-9_-]{11})',r.get('youtube_url',''))) for r in current)
    stats['reverse_audit']['existing_source_inventory_count_preserved']=len(current)
    write('inventory.json',current)
    with (OUT/'inventory.csv').open('w',newline='',encoding='utf-8-sig') as f:
        keys=['unique_id','category','transcript_title','date','participants','source_folder','direct_file_link','duplicate_notes','video_title','youtube_url','timestamps','confidence','evidence','notes']
        writer=csv.DictWriter(f,fieldnames=keys,extrasaction='ignore');writer.writeheader();writer.writerows(current)
    write('video_inventory.json',video_rows)
    write('crawl_sources.json',source_rows)
    write('summary.json',stats)
    for name in ['pagination_reproduction.json','live_pagination_proof.json','standalone_replay_result.json','crawl_manifest.json','scope_decisions_initial.json','broad_metadata_scope.json','reverse_mapping_review.json','root_content_checks.json']:
        write(name.replace('scope_decisions_initial','scope_decisions').replace('root_content_checks','new_content_checks'),safe_paths(read(BASE/name)))
    # Full discovery metadata is compressed; no source transcripts, watch payloads, tokens or media.
    for name in ['catalog','memberships']:
        payload=json.dumps(safe_paths(read(BASE/(name+'.json'))),ensure_ascii=False,separators=(',',':')).encode()
        (OUT/('public_'+name+'.json.gz')).write_bytes(gzip.compress(payload,mtime=0))
    print(json.dumps({'videos':len(video_rows),'counts':counts,'source_rows':len(source_rows),'broad_counts':broad.get('counts',{})},ensure_ascii=False,indent=2))


def collections_module_count(rows,included):
    return {
        'candidate_rows':len(rows),
        'included_video_ids':len(included),
        'video_ids_with_supplied_transcript':sum(bool(r['transcript_ids']) for r in included),
        'known_partial_supplied_coverage_video_ids':sum(r['coverage_label'].startswith('Partial') for r in included),
        'no_supplied_transcript_content_checked':sum(r['coverage_label']=='No supplied transcript · content checked' for r in included),
        'no_supplied_transcript_metadata_basis':sum(r['coverage_label']=='No supplied transcript · metadata basis' for r in included),
        'coverage_unconfirmed_video_ids':sum(r['coverage_label'].startswith('Coverage unconfirmed') for r in included),
        'scope_unconfirmed_candidates':sum(r['scope_label']=='Scope unconfirmed' for r in rows),
        'excluded_candidates':sum(r['scope_label']=='Excluded' for r in rows),
    }


if __name__=='__main__':
    main()
