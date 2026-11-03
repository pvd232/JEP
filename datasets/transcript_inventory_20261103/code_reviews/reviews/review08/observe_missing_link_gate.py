"""Show whether the actual acceptance gate rejects a missing video hyperlink.

Only a review-owned copy is changed, using an OOXML edit. openpyxl is read-only.
"""
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
import argparse
import contextlib
import hashlib
import importlib.util
import io
import json
import re
import xml.etree.ElementTree as ET
import openpyxl

HERE = Path(__file__).resolve().parent
BASE = HERE.parents[1] / 'base'
WORKSPACE = BASE.parents[2]
MAIN = 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--validator', type=Path, default=BASE / 'workbook_build/validate_outputs.py')
    parser.add_argument('--require-fixed', action='store_true')
    args = parser.parse_args()
    owned = HERE / 'case_omitted_video_hyperlink'
    owned.mkdir(exist_ok=True)
    for filename in ['inventory.json', 'video_inventory.json', 'summary.json', 'crawl_manifest.json', 'public_memberships.json.gz']:
        dest = owned / filename
        if not dest.exists():
            dest.symlink_to(BASE / filename)
    inv = json.loads((BASE / 'inventory.json').read_text())
    index = next(i for i, row in enumerate(inv, 2) if re.search(r'https://', row.get('youtube_url', '')))
    cell = f'J{index}'
    original = BASE / 'JEP_transcript_inventory.xlsx'
    before_hash = hashlib.sha256(original.read_bytes()).hexdigest()
    with ZipFile(original) as z:
        contents = {name: z.read(name) for name in z.namelist()}
    # The pinned workbook's second sheet is Transcripts; verify before editing.
    book = openpyxl.load_workbook(original, data_only=False)
    assert book.sheetnames[1] == 'Transcripts'
    expected_url = book['Transcripts'][cell].hyperlink.target
    sheet_path = 'xl/worksheets/sheet2.xml'
    root = ET.fromstring(contents[sheet_path])
    hyperlinks = root.find(f'{{{MAIN}}}hyperlinks')
    removed = [node for node in hyperlinks if node.get('ref') == cell]
    assert len(removed) == 1
    hyperlinks.remove(removed[0])
    contents[sheet_path] = ET.tostring(root, encoding='utf-8', xml_declaration=True)
    changed = owned / original.name
    with ZipFile(changed, 'w', ZIP_DEFLATED) as z:
        for name, data in contents.items():
            z.writestr(name, data)
    changed_book = openpyxl.load_workbook(changed, data_only=False)
    assert changed_book['Transcripts'][cell].value == book['Transcripts'][cell].value
    assert changed_book['Transcripts'][cell].hyperlink is None
    spec = importlib.util.spec_from_file_location('review08_validator', args.validator)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.ROOT = WORKSPACE
    module.OUT = owned
    exit_code = 0
    captured = io.StringIO()
    try:
        with contextlib.redirect_stdout(captured):
            module.main()
    except SystemExit as exc:
        exit_code = exc.code
    gate = json.loads((owned / 'workbook_validation.json').read_text())
    report = {
        'validator': str(args.validator),
        'validator_sha256': hashlib.sha256(args.validator.read_bytes()).hexdigest(),
        'frozen_workbook_sha256': before_hash,
        'synthetic_copy': str(changed),
        'mutation': {'sheet': 'Transcripts', 'cell': cell, 'record_id': inv[index - 2]['unique_id'], 'removed_native_link': expected_url, 'displayed_cell_value_preserved': True},
        'gate_exit_code': exit_code,
        'gate_all_passed': gate['all_passed'],
        'failed_gate_checks': [c['check'] for c in gate['checks'] if not c['passed']],
        'missing_video_hyperlink_rejected': not gate['all_passed'] or exit_code != 0,
        'frozen_workbook_unchanged': hashlib.sha256(original.read_bytes()).hexdigest() == before_hash,
    }
    (HERE / 'missing_link_gate_observations.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))
    if args.require_fixed and not report['missing_video_hyperlink_rejected']:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
