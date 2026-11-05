"""Recalculate corpus statistics from reviewed counts and a person evidence ledger."""
import argparse
import collections
import csv
import hashlib
import json
import statistics
from pathlib import Path


def number(value, field, nullable=False):
    """Read a nonnegative integer while preserving an explicitly unknown value."""
    if value in ('', None):
        if nullable:
            return None
        raise ValueError(f'{field}: required count is missing')
    if isinstance(value, bool) or str(value) != str(int(value)) or int(value) < 0:
        raise ValueError(f'{field}: expected a nonnegative integer')
    return int(value)


def validate(records, evidence, manifest, corpus=None):
    """Require reviewed record coverage, unique people and matching source versions."""
    ids=[row['record_id'] for row in records]
    expected=set(manifest['expected_record_ids'])
    reviewer_ids={r['reviewer_id'] for r in manifest['reviewers']}
    if len(reviewer_ids) != manifest['reviewer_count'] or any(r['status']!='completed' for r in manifest['reviewers']):
        raise ValueError('Reviewer completion manifest is inconsistent')
    if len(set(ids)) != len(ids) or set(ids) != expected:
        raise ValueError('Record coverage differs from the reviewed source snapshot')
    if set(evidence['record_reviewers']) != expected:
        raise ValueError('Every record requires an explicit source review')
    by_id={row['record_id']:row for row in records}
    if any(row['participation_mode'] not in ('recorded_submission','hearing_transcript') for row in records):
        raise ValueError('Record participation mode is unknown')
    counts=collections.defaultdict(collections.Counter)
    seen=set()
    disputed=set()
    allowed_roles={'victim','compareciente','witness','principal_deponent'}
    for person in evidence['people']:
        uid=person['record_id']
        key=(uid,person['person_id'])
        if uid not in by_id or key in seen:
            raise ValueError('Person occurrence is duplicated or belongs to an unknown record')
        seen.add(key)
        if person['source_sha256'] != by_id[uid]['source_sha256']:
            raise ValueError(f'{uid}: person evidence uses another source version')
        if not person['source_anchors'] or not any(person['source_anchors']):
            raise ValueError(f'{uid}: counted person requires a source coordinate')
        roles=person['roles']
        if person['role_status'] not in ('supported','disputed_compareciente'):
            raise ValueError(f'{uid}: person role status is unresolved')
        if not roles or len(set(roles)) != len(roles) or not set(roles) <= allowed_roles:
            raise ValueError(f'{uid}: invalid or repeated role')
        if not isinstance(person['counted'],bool) or not isinstance(person['self_reported_harm'],bool):
            raise ValueError(f'{uid}: person inclusion flags must be boolean')
        allowed_modes={'recorded_submission'} if by_id[uid]['participation_mode']=='recorded_submission' else {'live','hearing_transcript'}
        if person['mode'] not in allowed_modes:
            raise ValueError(f'{uid}: person and record recording modes disagree')
        if person['role_status']=='disputed_compareciente':
            if 'compareciente' in roles:
                raise ValueError(f'{uid}: disputed role was counted as established')
            disputed.add(uid)
        if person['counted']:
            counts[uid].update(roles)
            if person['self_reported_harm']:
                if 'witness' not in roles:
                    raise ValueError(f'{uid}: secondary witness harm flag has no witness role')
                counts[uid]['self_reported_harm_witness']+=1
    for row in records:
        uid=row['record_id']
        if row['participant_review_status'] != 'reviewed_minimum':
            raise ValueError(f'{uid}: participant review is missing')
        if row['reviewer_id'] != evidence['record_reviewers'][uid] or row['reviewer_id'] not in reviewer_ids:
            raise ValueError(f'{uid}: reviewer identity mismatch')
        for field,role in [('victim_speakers_min','victim'),('principal_deponents_min','principal_deponent'),('witness_deponents','witness')]:
            if number(row[field],field) != counts[uid][role]:
                raise ValueError(f'{uid}: {field} differs from person evidence')
        comp=number(row['compareciente_speakers_min'],'compareciente_speakers_min',True)
        if uid in disputed:
            if comp is not None or row['compareciente_role_status'] != 'source_disputed':
                raise ValueError(f'{uid}: disputed role must remain unknown')
        elif comp is None or comp != counts[uid]['compareciente']:
            raise ValueError(f'{uid}: compareciente count lacks matching evidence')
        for field in ['rendered_pages','text_words','self_reported_harm_witness']:
            number(row[field],field,field=='rendered_pages')
        if number(row['self_reported_harm_witness'],'self_reported_harm_witness') != counts[uid]['self_reported_harm_witness']:
            raise ValueError(f'{uid}: secondary harm flag differs from person evidence')
        if row['attendance_victims'] not in ('',None) or row['attendance_comparecientes'] not in ('',None) or row['attendance_status'] != 'unknown_whole_event':
            raise ValueError(f'{uid}: whole-event attendance is unestablished in this snapshot')
        if corpus is not None:
            source=Path(corpus)/(uid+'.'+row['format'])
            if hashlib.sha256(source.read_bytes()).hexdigest() != row['source_sha256']:
                raise ValueError(f'{uid}: source bytes changed after review')
    return counts,disputed


def describe(values):
    """Summarize a measured numeric cohort with its actual denominator."""
    return {'n':len(values),'total':sum(values),'mean':statistics.mean(values),'median':statistics.median(values),'min':min(values),'max':max(values),'sample_sd':statistics.stdev(values) if len(values)>1 else None}


def calculate(records,evidence,manifest,prior,corpus=None):
    """Retain length measures and report attendance as unknown when rosters are incomplete."""
    counts,disputed=validate(records,evidence,manifest,corpus)
    pages=[number(r['rendered_pages'],'rendered_pages') for r in records if r['rendered_pages']]
    words=[number(r['text_words'],'text_words') for r in records]
    result={key:value for key,value in prior.items() if key not in {'identified_victim_speakers_min','identified_compareciente_speakers_min','records_with_identified_victim_speakers','victim_speakers_mean_in_records_with_victim_speakers','participant_count_scope','participant_count_status','participant_audit'}}
    result.update(rendered_document_pages=describe(pages),text_words=describe(words),all_records_page_equivalent_500_words_mean=statistics.mean(words)/500)
    result['participant_audit']={
        'review_status':'ten_reviews_completed; headline_attendance_means_withdrawn',
        'reviewer_count':manifest['reviewer_count'],
        'source_records_reviewed':len(records),
        'mean_victim_attendance':None,
        'mean_compareciente_attendance':None,
        'attendance_mean_reason':'Incomplete attendee rosters; document records include submitted videos, split sessions and multi-day material. Separate attendance observations retain their original scope.',
        'confirmed_recorded_speaker_incidences_min':{'victim':sum(c['victim'] for c in counts.values()),'compareciente':sum(c['compareciente'] for c in counts.values()),'sworn_witness':sum(c['witness'] for c in counts.values())},
        'disputed_compareciente_role_records':sorted(disputed),
        'witnesses_reporting_own_harm_separately':sum(number(r['self_reported_harm_witness'],'self_reported_harm_witness') for r in records),
        'recorded_submission_records':[r['record_id'] for r in records if r['participation_mode']=='recorded_submission'],
        'count_scope':'Distinct source-supported person occurrences within supplied records. Introductions count; established aliases merge repeated turns. Primary recorded submissions and live hearing contributions retain their mode. Prerecorded inserts within hearings and unresolved identities are excluded.',
        'confirmed_correction_records':list(manifest['confirmed_corrections']),
        'superseded_values':{'victim_speaker_mean':1.5698924731182795,'compareciente_speaker_mean':2.3763440860215055,'positive_record_victim_mean':7.3,'status':'superseded; not attendance statistics'}
    }
    return result


def main():
    """Rebuild the published summary and optionally verify all original source bytes."""
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--directory',type=Path,default=Path(__file__).resolve().parent)
    parser.add_argument('--check-sources',type=Path)
    args=parser.parse_args()
    directory=args.directory
    manifest=json.loads((directory/'review_manifest.json').read_text())
    for name,expected in manifest['input_sha256'].items():
        if hashlib.sha256((directory/name).read_bytes()).hexdigest()!=expected:
            raise ValueError(f'{name}: reviewed input snapshot changed')
    with (directory/'records.csv').open() as handle:
        records=list(csv.DictReader(handle))
    evidence=json.loads((directory/'participant_evidence.json').read_text())
    prior=json.loads((directory/'summary.json').read_text())
    result=calculate(records,evidence,manifest,prior,args.check_sources)
    target=directory/'summary.json'
    pending=target.with_suffix('.json.pending')
    pending.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    pending.replace(target)
    print(json.dumps({'records':len(records),'reviewers':manifest['reviewer_count'],'recorded_speaker_minima':result['participant_audit']['confirmed_recorded_speaker_incidences_min'],'attendance_means':None,'source_bytes_verified':args.check_sources is not None}))


if __name__=='__main__':
    main()
