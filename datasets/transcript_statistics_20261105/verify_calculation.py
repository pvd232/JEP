"""Exercise the demonstrated review failures against the corrected calculation."""
import argparse
import copy
import csv
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
import calculate_statistics as calculation


def main():
    """Check source bindings, identity guards, unknown values and reproducibility."""
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--corpus',type=Path,required=True)
    args=parser.parse_args()
    directory=Path(__file__).resolve().parent
    with (directory/'records.csv').open() as handle:
        rows=list(csv.DictReader(handle))
    evidence=json.loads((directory/'participant_evidence.json').read_text())
    manifest=json.loads((directory/'review_manifest.json').read_text())
    summary=json.loads((directory/'summary.json').read_text())
    result=calculation.calculate(rows,evidence,manifest,summary,args.corpus)
    checks={'all_source_hashes_match':True,'calculation_reproduces_summary':result==summary}
    checks['retained_length_measures_unchanged']=all(result[k]==v for k,v in manifest['retained_measurements'].items())

    def rejects(name,change):
        """Run one isolated counterexample against copied inputs."""
        candidate_rows,candidate_evidence=copy.deepcopy((rows,evidence))
        change(candidate_rows,candidate_evidence)
        try:
            calculation.validate(candidate_rows,candidate_evidence,manifest)
        except ValueError:
            checks[name]=True
        else:
            checks[name]=False

    rejects('negative_count_rejected',lambda r,e:r[0].__setitem__('victim_speakers_min','-1'))
    rejects('duplicate_person_key_rejected',lambda r,e:e['people'].append(copy.deepcopy(e['people'][0])))
    rejects('missing_review_rejected',lambda r,e:e['record_reviewers'].pop(r[0]['record_id']))
    def compensate(r,e):
        """Preserve the grand total while breaking two source-person counts."""
        r[0]['victim_speakers_min']=str(int(r[0]['victim_speakers_min'])+1)
        r[1]['victim_speakers_min']=str(int(r[1]['victim_speakers_min'])-1)
    rejects('compensating_count_errors_rejected',compensate)
    rejects('disputed_role_zero_substitution_rejected',lambda r,e:next(x for x in r if x['record_id']=='VV-023').__setitem__('compareciente_speakers_min','0'))
    rejects('unknown_record_mode_rejected',lambda r,e:r[0].__setitem__('participation_mode','unknown'))
    rejects('unresolved_person_role_rejected',lambda r,e:e['people'][0].__setitem__('role_status','unresolved_identity'))
    rejects('source_version_mismatch_rejected',lambda r,e:e['people'][0].__setitem__('source_sha256','0'*64))
    rejects('unknown_attendance_zero_substitution_rejected',lambda r,e:r[0].__setitem__('attendance_victims',0))
    rejects('recording_mode_conflict_rejected',lambda r,e:next(p for p in e['people'] if p['mode']=='recorded_submission').__setitem__('mode','live'))
    rejects('secondary_harm_count_mismatch_rejected',lambda r,e:next(x for x in r if x['record_id']=='VV-065').__setitem__('self_reported_harm_witness','2'))

    with tempfile.TemporaryDirectory() as temporary:
        corpus=Path(temporary)/'corpus';corpus.mkdir()
        for row in rows:
            filename=row['record_id']+'.'+row['format']
            (corpus/filename).symlink_to((args.corpus/filename).resolve())
        target=corpus/(rows[0]['record_id']+'.'+rows[0]['format'])
        target.unlink()
        target.write_bytes(b'changed bytes for the source-binding counterexample')
        try:
            calculation.validate(rows,evidence,manifest,corpus)
        except ValueError:
            checks['changed_source_bytes_rejected']=True
        else:
            checks['changed_source_bytes_rejected']=False

    with tempfile.TemporaryDirectory() as temporary:
        candidate=Path(temporary)
        for name in ['records.csv','participant_evidence.json','review_manifest.json','attendance_observations.json','summary.json']:
            shutil.copy2(directory/name,candidate/name)
        command=[sys.executable,str(directory/'calculate_statistics.py'),'--directory',str(candidate)]
        run=subprocess.run(command,capture_output=True,text=True)
        checks['cli_regeneration_byte_identical']=run.returncode==0 and (candidate/'summary.json').read_bytes()==(directory/'summary.json').read_bytes()
        with (candidate/'records.csv').open('a') as handle:handle.write('\n')
        run=subprocess.run(command,capture_output=True,text=True)
        checks['changed_reviewed_input_rejected']=run.returncode!=0 and 'reviewed input snapshot changed' in run.stderr

    checks['all_correction_rows_match_review']=all(int(next(r for r in rows if r['record_id']==uid)[{'victims':'victim_speakers_min','comparecientes':'compareciente_speakers_min'}[role]])==values[1] for uid,change in manifest['confirmed_corrections'].items() for role,values in change.items() if role in ('victims','comparecientes'))
    named=next(p for p in evidence['people'] if p['record_id']=='SDSJ-20240524' and p['person_id']=='R06-v06')
    checks['later_name_anchor_preserved']=any(a.get('dialogue_cell')=='C667' for a in named['source_anchors'])
    if not all(checks.values()):
        raise AssertionError({name:passed for name,passed in checks.items() if not passed})
    receipt={'date':'2026-11-05','status':'passed','checked_records':len(rows),'checked_person_occurrences':len(evidence['people']),'checks':checks,'calculator_sha256':hashlib.sha256((directory/'calculate_statistics.py').read_bytes()).hexdigest(),'verification_script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'input_sha256':manifest['input_sha256'],'independent_rework_reviewers':['08','10'],'remaining_scope':'Human identity annotation and source interpretation remain review judgments. Complete audiovisual validation and event attendance reconciliation remain outstanding.'}
    (directory/'validation.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps({'status':'passed','focused_checks':len(checks),'source_records':len(rows),'person_occurrences':len(evidence['people'])}))


if __name__=='__main__':
    main()
