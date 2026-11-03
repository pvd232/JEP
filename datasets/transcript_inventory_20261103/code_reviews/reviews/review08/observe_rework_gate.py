"""Focused postprocessor/gate counterexamples; mutate only review-only ZIP copies."""
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
import contextlib
import hashlib
import importlib.util
import io
import json
import os
import shutil
import subprocess
import xml.etree.ElementTree as ET

import openpyxl

ROOT=Path('/workspace/scratch/8a7e64850a04')
BASE=ROOT/'inventory_work/tieout_review_20261103/base'
HERE=Path(__file__).resolve().parent
CASES=HERE/'rework_cases'
POST=Path('/tmp/jep-transcripts-8a7e64850a04/add_native_links.py')
VALIDATOR=ROOT/'inventory_work/reverse_audit/validate_outputs.py'
NS='{http://schemas.openxmlformats.org/spreadsheetml/2006/main}'


def entries(path):
    with ZipFile(path) as z:
        return {name:z.read(name) for name in z.namelist()}


def mutate(path,part,node_ref=None,filter_node=False):
    data=entries(path)
    root=ET.fromstring(data[part])
    parent=root if filter_node else root.find(NS+'hyperlinks')
    node=root.find(NS+'autoFilter') if filter_node else next(x for x in parent if x.get('ref')==node_ref)
    parent.remove(node)
    data[part]=ET.tostring(root,encoding='utf-8',xml_declaration=True)
    with ZipFile(path,'w',ZIP_DEFLATED) as z:
        for name,body in data.items(): z.writestr(name,body)


def run_gate(case):
    spec=importlib.util.spec_from_file_location('review08_fixed_validator',VALIDATOR)
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.ROOT=ROOT
    module.OUT=case
    code=0
    with contextlib.redirect_stdout(io.StringIO()):
        try:
            module.main()
        except SystemExit as exc:
            code=int(exc.code or 0)
    report=json.loads((case/'workbook_validation.json').read_text())
    return {'exit_code':code,'all_passed':report['all_passed'],'failed_checks':[c['check'] for c in report['checks'] if not c['passed']]}


def main():
    CASES.mkdir(exist_ok=True)
    empty_links=CASES/'empty_links.json'
    empty_links.write_text('[]\n')
    valid=CASES/'valid'
    valid.mkdir(exist_ok=True)
    target=valid/'JEP_transcript_inventory.xlsx'
    shutil.copyfile(BASE/'JEP_transcript_inventory.xlsx',target)
    result=subprocess.run([os.environ['CODEX_PRIMARY_RUNTIME_PYTHON'],str(POST),str(target),str(empty_links)],check=True,text=True,capture_output=True)
    before,after=entries(BASE/'JEP_transcript_inventory.xlsx'),entries(target)
    changed=[name for name in before if before[name]!=after[name]]
    book=openpyxl.load_workbook(target,data_only=False)
    filter_ranges={sheet.title:[table.autoFilter.ref if table.autoFilter is not None else None for table in sheet.tables.values()] for sheet in book if sheet.tables}
    all_filters=all(table.autoFilter is not None and table.autoFilter.ref==table.ref for sheet in book for table in sheet.tables.values())
    video=json.loads((BASE/'video_inventory.json').read_text())
    reverse_row=next(i for i,r in enumerate(video,2) if r['video_id']=='eM8ZrqhZbgQ')
    observations={}
    for name in ['valid','missing_forward','missing_reverse','missing_filter']:
        case=CASES/name
        case.mkdir(exist_ok=True)
        for source in [BASE/name for name in ['inventory.json','video_inventory.json','summary.json','crawl_manifest.json','public_memberships.json.gz']]:
            link=case/source.name
            if not link.exists(): link.symlink_to(source)
        # The validator owns this output; it must never point at frozen inputs.
        report_path=case/'workbook_validation.json'
        if report_path.is_symlink(): report_path.unlink()
        casefile=case/'JEP_transcript_inventory.xlsx'
        if name!='valid': shutil.copyfile(target,casefile)
        if name=='missing_forward': mutate(casefile,'xl/worksheets/sheet2.xml','J2')
        if name=='missing_reverse': mutate(casefile,'xl/worksheets/sheet5.xml',f'I{reverse_row}')
        if name=='missing_filter': mutate(casefile,'xl/tables/table1.xml',filter_node=True)
        observations[name]=run_gate(case)
    checks={
        'postprocessor_added_six_filters':json.loads(result.stdout)['table_filters']==6 and all_filters,
        'only_table_xml_parts_changed':len(changed)==6 and all(p.startswith('xl/tables/') for p in changed),
        'intact_copy_passes':observations['valid']['all_passed'] and observations['valid']['exit_code']==0,
        'missing_forward_link_rejected_for_correct_reason':observations['missing_forward']['failed_checks']==['Exact transcript video edges VV-028'],
        'missing_reverse_link_rejected_for_correct_reason':observations['missing_reverse']['failed_checks']==['Exact video source edges eM8ZrqhZbgQ'],
        'missing_filter_rejected_for_correct_reason':observations['missing_filter']['failed_checks']==['Explicit table filter Transcripts'],
    }
    report={'postprocessor_sha256':hashlib.sha256(POST.read_bytes()).hexdigest(),'validator_sha256':hashlib.sha256(VALIDATOR.read_bytes()).hexdigest(),'checks':checks,'all_passed':all(checks.values()),'filter_ranges':filter_ranges,'changed_zip_parts':changed,'cases':observations,'method':'Review-only copies of frozen XLSX; native helper with empty links adds filters; actual fixed validator; no artifact build or openpyxl save'}
    (HERE/'rework_gate_observations.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))
    return 0 if report['all_passed'] else 1


if __name__=='__main__': raise SystemExit(main())
