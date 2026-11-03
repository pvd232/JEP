"""Integrate retained fresh channel receipts without fetching or losing history.

Rebuild only crawl_manifest.json, memberships.json and catalog.json from the
frozen review baseline and immutable Videos/Live states. --check recomputes the
same bytes and checks the existing outputs instead of replacing them.
"""
from __future__ import annotations

import argparse
import collections
import copy
import gzip
import hashlib
import json
from pathlib import Path


WORK=Path(__file__).resolve().parent
ROOT=WORK.parents[1]
REVIEW=ROOT/'inventory_work/tieout_review_20261103'
BASE=REVIEW/'base'
FRESH=REVIEW/'fresh_discovery'
CHANNEL_ID='UCay5mclHBbWQTQ8fhoNCWow'
CHANNEL_NAME='JEP Colombia'
SURFACES={'videos':('deep_channel_videos','Videos'),'streams':('deep_channel_streams','Live')}
HISTORICAL='historical_not_in_latest_listing'
CURRENT='current_selected_snapshot'


def require(condition,message):
    if not condition:
        raise ValueError(message)


def digest(value):
    return hashlib.sha256(value if isinstance(value,bytes) else value.encode()).hexdigest()


def load(path):
    return json.loads(path.read_text())


def encoded(value):
    return (json.dumps(value,ensure_ascii=False,indent=2)+'\n').encode()


def relative(path):
    return str(path.resolve().relative_to(ROOT))


def fresh_fingerprint():
    files={relative(p):digest(p.read_bytes()) for surface in SURFACES for p in sorted((FRESH/surface).rglob('*')) if p.is_file()}
    return {'files':len(files),'sha256_of_file_hashes':digest(json.dumps(files,sort_keys=True))}


def fresh_surface(surface,previous,baseline_members,baseline_info):
    """Verify retained receipts, normalize owner identity and retain lost IDs."""
    key,tab_title=SURFACES[surface]
    directory=FRESH/surface
    state_path=directory/'state.json'
    state=load(state_path)
    state_sha=digest(state_path.read_bytes())
    require(state['collection_id']==previous['collection_id']==CHANNEL_ID+':'+surface,'Channel collection identity differs: '+surface)
    require(state['source_url']=='https://www.youtube.com/@jepcolombia/'+surface,'Unexpected channel source URL: '+surface)
    require(state['selected_tab_title']==tab_title,'Wrong selected channel tab: '+surface)
    require(state['pagination_exhausted'] and not state['errors'] and not state['pending_token_sha256'],'Fresh channel is not exhausted cleanly: '+surface)
    require([p['page_index'] for p in state['pages']]==list(range(len(state['pages']))),'Noncontiguous fresh page chain: '+surface)
    first=load(directory/'page_000.json')
    identity=first['metadata']['channelMetadataRenderer']
    require(identity.get('externalId')==CHANNEL_ID and identity.get('title')==CHANNEL_NAME,'First-page channel identity is unverified: '+surface)
    require(identity.get('channelUrl')=='https://www.youtube.com/channel/'+CHANNEL_ID,'First-page canonical channel URL differs: '+surface)
    pages=[]
    for page in state['pages']:
        index=page['page_index']
        response_path=directory/f'page_{index:03}.json'
        receipt_path=directory/f'page_{index:03}.meta.json'
        receipt=load(receipt_path)
        require(receipt==page['request'],'State/request receipt mismatch: '+str(receipt_path))
        require(receipt.get('http_status')==200 and receipt.get('fetched_at'),'Missing successful timestamped response: '+str(receipt_path))
        if index:
            require(receipt.get('method')=='POST' and receipt.get('request_token_sha256'),'Missing continuation request evidence: '+str(receipt_path))
            require(receipt.get('parsed_response_sha256')==digest(json.dumps(load(response_path),sort_keys=True)),'Parsed response checksum mismatch: '+str(response_path))
        observed=copy.deepcopy(page)
        observed['response_path']=relative(response_path)
        observed['response_json_file_sha256']=digest(response_path.read_bytes())
        observed['request_receipt_path']=relative(receipt_path)
        observed['request_receipt_file_sha256']=digest(receipt_path.read_bytes())
        pages.append(observed)
    rows=copy.deepcopy(state['memberships'])
    require(len(rows)==state['returned_memberships']==sum(p['items'] for p in pages),'Fresh page/member count mismatch: '+surface)
    require(len({r['video_id'] for r in rows})==state['unique_video_ids'],'Fresh unique-ID count mismatch: '+surface)
    require([r['position'] for r in rows]==list(range(1,len(rows)+1)),'Fresh positions are not contiguous: '+surface)
    require(collections.Counter(r['page_index'] for r in rows)==collections.Counter({p['page_index']:p['items'] for p in pages}),'Fresh membership page counts differ: '+surface)
    normalization={'rows':len(rows),'channel_ids_replaced':0,'channel_names_replaced':0}
    for row in rows:
        require(row['collection_id']==state['collection_id'],'Membership assigned to another channel surface')
        require(row.get('channel_id') in (None,CHANNEL_ID),'Conflicting explicit membership owner: '+row['video_id'])
        normalization['channel_ids_replaced']+=row.get('channel_id')!=CHANNEL_ID
        normalization['channel_names_replaced']+=row.get('channel_name')!=CHANNEL_NAME
        row.update(collection_key=key,channel_id=CHANNEL_ID,channel_name=CHANNEL_NAME,
                   channel_identity_basis='selected_channel_surface_metadata',is_current=True,
                   membership_status=CURRENT,listing_observed_at=pages[row['page_index']]['request']['fetched_at'],
                   selected_snapshot_state_sha256=state_sha)
    current_ids={r['video_id'] for r in rows}
    previous_ids={r['video_id'] for r in baseline_members}
    history=[]
    for original in baseline_members:
        if original['video_id'] not in current_ids:
            row=copy.deepcopy(original)
            row.update(is_current=False,membership_status=HISTORICAL,
                       latest_snapshot_finished_at=state['finished_at'],
                       latest_snapshot_state_sha256=state_sha,
                       historical_evidence={**baseline_info,'original_fetch_time':previous.get('provenance',{}).get('original_fetch_time'),
                           'note':'Retains the prior listed appearance and its original position. Not returned by the latest exhausted channel surface; no deletion or playability conclusion.'})
            history.append(row)
    collection={k:copy.deepcopy(v) for k,v in state.items() if k!='memberships'}
    collection.update(collection_key=key,pages=pages,pages_checked=len(pages),
                      retained_memberships=len(rows)+len(history),historical_memberships=len(history),
                      historical_video_ids=sorted(previous_ids-current_ids),
                      fresh_state_collection_key=state['collection_key'],
                      previous_selected_snapshot=copy.deepcopy(previous),
                      provenance={'state_path':relative(state_path),'state_sha256':state_sha,
                          'original_fetch_time':pages[0]['request']['fetched_at'],
                          'last_response_fetched_at':pages[-1]['request']['fetched_at'],
                          'finished_at':state['finished_at'],'basis':'Fresh exhausted selected channel surface; retained per-page request receipts and parsed-cache hashes.'})
    identity_basis={'collection_id':collection['collection_id'],'collection_key':key,
                    'channel_id':CHANNEL_ID,'channel_name':CHANNEL_NAME,'selected_tab_title':tab_title,
                    'source_url':state['source_url'],'json_pointer':'metadata.channelMetadataRenderer',
                    'response_path':pages[0]['response_path'],'response_json_file_sha256':pages[0]['response_json_file_sha256'],
                    'request_response_sha256':pages[0]['request']['sha256'],'fetched_at':pages[0]['request']['fetched_at'],
                    'normalization':normalization}
    change={'change':'replace_reused_channel_surface_with_fresh_receipt_chain','collection_id':collection['collection_id'],
            'collection_key':key,'previous_returned_memberships':len(baseline_members),
            'current_returned_memberships':len(rows),'historical_memberships_retained':len(history),
            'added_video_ids':sorted(current_ids-previous_ids),'not_in_latest_listing_video_ids':sorted(previous_ids-current_ids),
            'pages_checked':len(pages),'fresh_state_path':relative(state_path),'fresh_state_sha256':state_sha,
            'fresh_first_fetched_at':pages[0]['request']['fetched_at'],'fresh_finished_at':state['finished_at'],
            'baseline':baseline_info}
    return collection,rows+history,identity_basis,change


def assemble():
    inputs={name:BASE/name for name in ['crawl_manifest.json','public_memberships.json.gz','public_catalog.json.gz']}
    hashes={name:digest(path.read_bytes()) for name,path in inputs.items()}
    frozen_index=load(REVIEW/'baseline_hashes.json')
    require(all(hashes[name]==frozen_index['files'][name] for name in hashes),'Frozen integration inputs differ from the review baseline')
    original_manifest=load(inputs['crawl_manifest.json'])
    original_members=json.loads(gzip.decompress(inputs['public_memberships.json.gz'].read_bytes()))
    original_catalog=json.loads(gzip.decompress(inputs['public_catalog.json.gz'].read_bytes()))
    baseline_info={'commit':frozen_index['commit'],'memberships_path':relative(inputs['public_memberships.json.gz']),
                   'memberships_sha256':hashes['public_memberships.json.gz'],'manifest_sha256':hashes['crawl_manifest.json']}
    groups=collections.defaultdict(list)
    for row in original_members:groups[row['collection_id']].append(row)
    original_by_key={c['collection_key']:c for c in original_manifest['collections']}
    replacements={};member_replacements={};identity_bases=[];changes=[]
    for surface,(key,_) in SURFACES.items():
        previous=original_by_key[key]
        collection,rows,basis,change=fresh_surface(surface,previous,groups[previous['collection_id']],baseline_info)
        replacements[key]=collection;member_replacements[previous['collection_id']]=rows
        identity_bases.append(basis);changes.append(change)
    manifest=copy.deepcopy(original_manifest)
    manifest['collections']=[replacements.get(c['collection_key'],copy.deepcopy(c)) for c in original_manifest['collections']]
    members=[]
    for collection in original_manifest['collections']:
        members.extend(member_replacements.get(collection['collection_id'],copy.deepcopy(groups[collection['collection_id']])))
    require(len(members)==sum(len(rows) for rows in groups.values())+sum(len(c['added_video_ids']) for c in changes),'Retained membership accounting changed unexpectedly')
    current=[m for m in members if m.get('is_current',True)]
    historical=[m for m in members if not m.get('is_current',True)]
    current_ids={m['video_id'] for m in current};all_ids={m['video_id'] for m in members}
    historical_only=sorted(all_ids-current_ids)

    catalog=copy.deepcopy(original_catalog)
    nodes={r['video_id']:r for r in catalog}
    all_groups=collections.defaultdict(list)
    for row in members:all_groups[row['video_id']].append(row)
    fresh_rows=[m for m in current if m['collection_id'] in member_replacements]
    affected={m['video_id'] for m in members if m['collection_id'] in member_replacements}
    fresh_by_id=collections.defaultdict(list)
    for row in fresh_rows:
        fresh_by_id[row['video_id']].append(row)
        if row['video_id'] not in nodes:
            node={'video_id':row['video_id'],'url':row['url'],'title':row['title'],'observed_titles':[],
                  'channel_id':CHANNEL_ID,'channel_name':CHANNEL_NAME,'duration_text':None,'description':None,
                  'listing_visibility':[],'scope_status':'Not classified; collection membership alone does not establish substantive Casanare scope',
                  'collection_ids':[],'source_urls':[],'metadata_provenance':[]}
            catalog.append(node);nodes[row['video_id']]=node
        node=nodes[row['video_id']]
        node.update(channel_id=CHANNEL_ID,channel_name=CHANNEL_NAME,channel_identity_basis='selected_channel_surface_metadata')
        for key,value in [('observed_titles',row['title']),('collection_ids',row['collection_id']),('source_urls',row['source_url']),('listing_visibility',row['visibility'])]:
            if value not in node[key]:node[key].append(value)
        if not node.get('duration_text') and row.get('duration_text'):node['duration_text']=row['duration_text']
    for vid in affected:
        node=nodes[vid];observations=all_groups[vid]
        active=[m for m in observations if m.get('is_current',True)]
        past=[m for m in observations if not m.get('is_current',True)]
        node.update(is_current=bool(active),membership_status=CURRENT if active else HISTORICAL,
                    current_membership_count=len(active),historical_membership_count=len(past),
                    current_collection_ids=list(dict.fromkeys(m['collection_id'] for m in active)),
                    historical_collection_ids=list(dict.fromkeys(m['collection_id'] for m in past)),
                    latest_channel_listing_observations=[{'collection_id':m['collection_id'],'collection_key':m['collection_key'],
                        'page_index':m['page_index'],'position':m['position'],'fetched_at':m['listing_observed_at'],
                        'state_sha256':m['selected_snapshot_state_sha256']} for m in fresh_by_id[vid]])
        if past:node['historical_listing_evidence']=[{'collection_id':m['collection_id'],'page_index':m['page_index'],
                   'position':m['position'],'membership_status':HISTORICAL,'latest_snapshot_finished_at':m['latest_snapshot_finished_at'],
                   'latest_snapshot_state_sha256':m['latest_snapshot_state_sha256'],'baseline':m['historical_evidence']} for m in past]
    require(set(nodes)==all_ids,'Catalog IDs differ from all retained membership IDs')

    manifest.update(schema_version='1.3',baseline_generated_at=original_manifest['generated_at'],
                    generated_at=max(c['fresh_finished_at'] for c in changes),
                    generated_at_basis='Latest retained fresh-snapshot completion time; deterministic local integration, not a new network fetch.',
                    membership_count=len(members),current_membership_count=len(current),historical_membership_count=len(historical),
                    unique_video_ids=len(all_ids),current_unique_video_ids=len(current_ids),
                    historical_only_unique_video_ids=len(historical_only),historical_only_video_ids=historical_only,
                    channel_refresh_pages=sum(c['pages_checked'] for c in changes),
                    source_changes=changes,channel_identity_normalization={'rule':'Use the verified owner of each selected channel surface. lockupViewModel metadata text may contain view counts and recency; it is not an owner name.',
                        'basis':identity_bases},
                    integration_inputs={'baseline_commit':frozen_index['commit'],'baseline_sha256':hashes,
                        'catalog_merge_rule':'Preserve baseline titles, watch metadata and evidence; append fresh observed titles, fill missing listing durations, normalize fresh channel owners and annotate current/historical membership.'})
    manifest['snapshot_selection_rule']+=' Videos and Live now use the timestamped fresh exhausted receipt chains. Earlier appearances absent from those chains are retained under the same collection ID with is_current=false; no additional collection is created.'
    manifest['count_definitions'].update({
        'membership_count':'All retained membership rows, including explicitly historical appearances; current_membership_count + historical_membership_count.',
        'current_membership_count':'Membership rows in the selected snapshot for each collection. is_current defaults to true on unchanged baseline playlist/Shorts/web rows; per-source timestamps govern recency.',
        'historical_membership_count':'Retained prior appearances with is_current=false and membership_status=historical_not_in_latest_listing. Not added to selected collection returned_memberships.',
        'unique_video_ids':'At collection level: distinct IDs in its selected snapshot. At manifest level: distinct IDs across all retained current and historical memberships.',
        'current_unique_video_ids':'Distinct IDs with at least one is_current=true (or unchanged legacy) membership in a selected source snapshot.',
        'historical_only_unique_video_ids':'Retained discovery IDs without any current selected-snapshot membership. Not a deletion, availability or scope determination.',
        'retained_memberships':'For refreshed channel collections: selected returned_memberships plus retained historical_memberships.',
        'membership_status':'current_selected_snapshot or historical_not_in_latest_listing on refreshed channel rows/nodes; unchanged legacy rows imply current for their selected baseline snapshot.',
    })
    channel_ids=set(member_replacements)
    checks={
        'same_collection_ids_and_keys':[(c['collection_id'],c['collection_key']) for c in manifest['collections']]==[(c['collection_id'],c['collection_key']) for c in original_manifest['collections']],
        'ten_playlist_snapshots_unchanged':[c for c in manifest['collections'] if c['collection_type']=='playlist']==[c for c in original_manifest['collections'] if c['collection_type']=='playlist'] and sum(c['collection_type']=='playlist' for c in manifest['collections'])==10,
        'alternate_snapshot_views_unchanged':manifest['alternate_snapshot_views']==original_manifest['alternate_snapshot_views'],
        'shorts_web_and_other_nonchannel_collections_unchanged':[c for c in manifest['collections'] if c['collection_id'] not in channel_ids]==[c for c in original_manifest['collections'] if c['collection_id'] not in channel_ids],
        'all_nonchannel_membership_rows_unchanged':[m for m in members if m['collection_id'] not in channel_ids]==[m for m in original_members if m['collection_id'] not in channel_ids],
        'unavailable_placeholder_records_unchanged':manifest['unavailable_placeholders']==original_manifest['unavailable_placeholders'],
        'unaffected_catalog_nodes_unchanged':[n for n in catalog if n['video_id'] not in affected]==[n for n in original_catalog if n['video_id'] not in affected],
        'baseline_watch_metadata_and_provenance_preserved':all(all(n.get(k)==nodes[n['video_id']].get(k) for k in ['title','description','length_seconds','upload_date','publish_date','live','playability','playability_reason','captions_available','metadata_provenance','scope_status']) for n in original_catalog),
        'fresh_memberships_have_verified_owner':all(m['channel_id']==CHANNEL_ID and m['channel_name']==CHANNEL_NAME for m in fresh_rows),
        'fresh_catalog_nodes_have_verified_owner':all(nodes[m['video_id']]['channel_id']==CHANNEL_ID and nodes[m['video_id']]['channel_name']==CHANNEL_NAME for m in fresh_rows),
        'historical_rows_preserve_original_fields':all(all(m.get(k)==old.get(k) for k in old) for m in historical for old in groups[m['collection_id']] if old['video_id']==m['video_id'] and old['position']==m['position']),
        'current_plus_historical_equals_retained':len(current)+len(historical)==len(members),
        'current_plus_historical_only_ids_equals_catalog':len(current_ids)+len(historical_only)==len(catalog),
        'collection_selected_counts_reconcile':all(sum(m.get('is_current',True) for m in members if m['collection_id']==c['collection_id'])==c['returned_memberships'] for c in manifest['collections']),
    }
    require(all(checks.values()),'Integration reconciliation failed: '+repr([k for k,v in checks.items() if not v]))
    outputs={'crawl_manifest.json':manifest,'memberships.json':members,'catalog.json':catalog}
    receipt={'integration_script':relative(Path(__file__)),'script_sha256':digest(Path(__file__).read_bytes()),
             'baseline_commit':frozen_index['commit'],'checks':checks,'counts':{k:manifest[k] for k in ['membership_count','current_membership_count','historical_membership_count','unique_video_ids','current_unique_video_ids','historical_only_unique_video_ids','historical_only_video_ids','channel_refresh_pages']},
             'channel_sources':[{k:c[k] for k in ['collection_key','current_returned_memberships','historical_memberships_retained','pages_checked','fresh_first_fetched_at','fresh_finished_at','added_video_ids','not_in_latest_listing_video_ids']} for c in changes],
             'channel_identity_normalization':manifest['channel_identity_normalization'],
             'preserved_alternate_snapshots':len(manifest['alternate_snapshot_views']),
             'preserved_nonchannel_memberships':sum(m['collection_id'] not in channel_ids for m in original_members),
             'input_sha256':hashes,'output_sha256':{name:digest(encoded(value)) for name,value in outputs.items()},
             'no_network_fetch_performed':True,'scope_or_transcript_decisions_modified':False}
    return outputs,receipt


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check',action='store_true',help='Recompute deterministically and verify the three existing outputs without rewriting them.')
    args=parser.parse_args()
    immutable_before=fresh_fingerprint()
    outputs,receipt=assemble()
    if args.check:
        for name,value in outputs.items():require((WORK/name).read_bytes()==encoded(value),'Output differs from deterministic integration: '+name)
    else:
        for name,value in outputs.items():
            temporary=WORK/(name+'.channel-integration.tmp')
            temporary.write_bytes(encoded(value))
            temporary.replace(WORK/name)
    immutable_after=fresh_fingerprint()
    require(immutable_before==immutable_after,'Fresh caches changed during integration')
    frozen_index=load(REVIEW/'baseline_hashes.json')['files']
    frozen_ok=all(digest((BASE/name).read_bytes())==expected for name,expected in frozen_index.items())
    require(frozen_ok,'Frozen review baseline changed')
    receipt.update(mode='check_existing_outputs' if args.check else 'write_three_outputs',
                   fresh_cache_integrity={'before':immutable_before,'after':immutable_after,'unchanged':True},
                   all_frozen_hashes_match_manifest=frozen_ok,all_passed=True,
                   output_files=[relative(WORK/name) for name in outputs])
    target=REVIEW/'fresh_channel_integration_receipt.json'
    target.write_bytes(encoded(receipt))
    print(json.dumps({'receipt':str(target),'mode':receipt['mode'],'counts':receipt['counts'],'all_passed':True},indent=2))


if __name__=='__main__':main()
