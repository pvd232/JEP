"""Merge reviewed content checks into the metadata-first inventory."""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
FIELDS = {'confidence','date','participants','youtube_url','video_title','timestamps','evidence','notes','match_basis','duplicate_notes','coverage_status','content_verified','playability'}

def canonical_confidence(value):
    if str(value).startswith('High'):
        return 'High'
    if str(value).startswith('Medium'):
        return 'Medium (candidate)'
    if str(value).startswith('Low'):
        return 'Low (candidate)'
    return 'Unmatched'

def apply_deep_results(rows):
    """Apply explicit review facts without inferring content checks from confidence."""
    by_id = {row['unique_id']:row for row in rows}
    audit = []
    reports = [
        'deep_versiones_content_root.json',
        'deep_versiones_content_repo.json',
        'deep_root_content.json',
        'deep_candidates_identity.json',
        'deep_candidates_dates.json',
        'deep_unmatched.json',
    ]
    for name in reports:
        path = ROOT/name
        if not path.exists():
            continue
        report = json.loads(path.read_text())
        records = report.get('rows',report.get('records',[]))
        if isinstance(records,dict):
            records = list(records.values())
        for check in records:
            uid = check['unique_id']
            if uid not in by_id:
                raise ValueError(f'Unknown reviewed record: {uid}')
            update = dict(check.get('proposed_fields',check.get('proposed_update',{})))
            if name == 'deep_candidates_dates.json':
                for source, target in [('recommended_confidence','confidence'),('suggested_evidence','evidence'),('suggested_notes','notes'),('suggested_timestamps','timestamps')]:
                    if check.get(source):
                        update[target] = check[source]
                if update.get('confidence','').startswith('High'):
                    update['match_basis'] = 'Source compared with public automatic captions, including dated opening and closing where available. Caption times are approximate.'
            if not update:
                continue
            row = by_id[uid]
            previous_video = row.get('youtube_url','')
            for key,value in update.items():
                if key in FIELDS and value is not None:
                    row[key] = canonical_confidence(value) if key == 'confidence' else value
            extra = update.get('notes_append','').strip()
            if extra and extra not in row['notes']:
                # Detailed overlap statistics belong in the audit, not a workbook cell.
                extra = re.sub(r'\s*\([\d,]+ ordered blocks across all ten source deciles\)', '', extra)
                row['notes'] = (row['notes'].rstrip()+' '+extra).strip()
            verification = update.get('content_verified',check.get('content_verified'))
            if row['confidence']!='High':
                row['content_verified'] = False
            elif isinstance(verification,bool):
                row['content_verified'] = verification
            elif row.get('youtube_url','') != previous_video:
                row['content_verified'] = False
            else:
                row.setdefault('content_verified',False)
            comparison = check.get('caption_comparison',{})
            audit.append({
                'unique_id':uid,
                'review':name,
                'status':check.get('review_status',check.get('status','Reviewed')),
                'public_video':row.get('youtube_url',''),
                'evidence':row.get('evidence',''),
                'timestamps':row.get('timestamps',''),
                'ordered_content_blocks':comparison.get('matching_blocks_in_monotonic_order'),
                'content_anchors':comparison.get('short_content_check_pointers',check.get('verified_anchors',check.get('verified_video_anchors',[]))),
                'limits':check.get('limits',check.get('remaining_blockers',[])),
            })
    for row in rows:
        row.setdefault('content_verified',False)
        if row['confidence']=='High':
            row['verification_level'] = 'Public captions checked' if row['content_verified'] else 'Metadata only'
        elif row['confidence']=='Unmatched':
            row['verification_level'] = 'Public recording not located'
        else:
            row['verification_level'] = 'Candidate not verified'
        if row['unique_id']=='VV-030':
            row['duplicate_notes']='Separate protective-measures segment before VV-029 in the same public upload. The two transcripts are distinct.'
        if row['unique_id']=='VV-029':
            row['duplicate_notes']='Separate voluntary-statement segment after VV-030 in the same public upload. The two transcripts are distinct.'
    return audit
