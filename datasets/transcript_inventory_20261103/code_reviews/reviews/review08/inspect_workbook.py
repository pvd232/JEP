"""Read-only comparison of the frozen workbook with its published input tables."""
from pathlib import Path
from zipfile import ZipFile
from datetime import datetime, timezone
from collections import Counter
import hashlib
import json
import re
import xml.etree.ElementTree as ET
import openpyxl

HERE = Path(__file__).resolve().parent
BASE = HERE.parents[1] / 'base'


def main():
    load = lambda name: json.loads((BASE / name).read_text())
    inv, videos, english, gaps, crawl, manifest = [load(n) for n in ['inventory.json', 'video_inventory.json', 'english_summaries.json', 'recording_gaps.json', 'crawl_sources.json', 'source_manifest.json']]
    book = openpyxl.load_workbook(BASE / 'JEP_transcript_inventory.xlsx', data_only=False)
    values = openpyxl.load_workbook(BASE / 'JEP_transcript_inventory.xlsx', data_only=True)
    problems = []
    comparisons = Counter()
    def equal(label, actual, expected):
        comparisons[label.split(':')[0]] += 1
        if actual != expected:
            problems.append({'check': label, 'actual': str(actual)[:200], 'expected': str(expected)[:200]})
    def value(sheet, row, col, expected):
        actual = book[sheet].cell(row, col).value
        equal('Cell projection:' + sheet + ':' + book[sheet].cell(row, col).coordinate, actual if actual is not None else '', expected if expected is not None else '')
    def external(sheet, row, col, target):
        cell = book[sheet].cell(row, col)
        equal('External link:' + sheet + ':' + cell.coordinate, cell.hyperlink.target if cell.hyperlink else None, target)
    def date(sheet, row, col, text):
        actual = book[sheet].cell(row, col).value
        if re.fullmatch(r'\d{4}-\d{2}-\d{2}', text or ''):
            equal('Date:' + sheet + ':' + str(row), actual.date().isoformat() if isinstance(actual, datetime) else str(actual), text)
        else:
            value(sheet, row, col, text)
    equal('Sheet set', book.sheetnames, ['Summary', 'Transcripts', 'English summaries', 'Recording gaps', 'Videos', 'Crawl sources', 'Files'])
    source_rows = {r['unique_id']: i for i, r in enumerate(inv, 2)}
    english_by_id = {r['unique_id']: r for r in english}
    forward_links = []
    for i, r in enumerate(inv, 2):
        for col, key in [(1,'unique_id'),(2,'category'),(3,'transcript_title'),(5,'participants'),(6,'source_folder'),(8,'duplicate_notes'),(9,'video_title'),(11,'timestamps'),(13,'evidence')]:
            value('Transcripts', i, col, r[key])
        date('Transcripts',i,4,r['date'])
        external('Transcripts',i,7,r['direct_file_link'])
        expected = re.findall(r'https://[^\s;]+',r.get('youtube_url') or '')
        actual = [book['Transcripts'].cell(i,c).hyperlink.target for c in (10,14) if book['Transcripts'].cell(i,c).hyperlink]
        equal('Transcript video links:' + r['unique_id'], actual, expected)
        confidence = r['confidence'] if r['confidence'] != 'High' else ('High · partial recording' if str(r.get('coverage_status','')).startswith('Partial') else 'High · content checked' if r.get('content_verified') else 'High · metadata only')
        value('Transcripts',i,12,confidence)
        value('Transcripts',i,14,('Open JEP reupload (click here). ' if len(expected)==2 else '')+r['notes'])
        forward_links.extend(expected)
        e = english_by_id[r['unique_id']]
        expected_summary = [r['unique_id'],r['category'],e['english_title'],e['named_people_roles'],e['purpose'],e['main_accounts_claims'],e['stated_positions_responses'],e['outcome_open_questions'],'\n\n'.join(e['source_pointers']),e['summary_limits']]
        for col,text in enumerate(expected_summary,1): value('English summaries',i,col,text)
        external('English summaries',i,11,r['direct_file_link'])
    reverse_links = []
    for i,r in enumerate(videos,2):
        expected = [r['video_id'],r['category'],r['scope_label'],r['title'],None,r['participants'],r['coverage_label'],'\n'.join(r['transcript_ids']),None,r['timestamps'],r['evidence'],None,r['publisher'],'\n'.join(r['collections']),r['scope_evidence']]
        for col,text in enumerate(expected,1):
            if col not in (5,9,12): value('Videos',i,col,text)
        date('Videos',i,5,r.get('date'))
        external('Videos',i,1,r['url'])
        actual = [book['Videos'].cell(i,c).hyperlink.target for c in (9,16) if book['Videos'].cell(i,c).hyperlink]
        equal('Video source links:' + r['video_id'],actual,r['source_links'])
        value('Videos',i,16,('Second original '+r['transcript_ids'][1]+' (click here). ' if len(r['source_links'])>1 else '')+r['notes'])
        duration=book['Videos'].cell(i,12).value
        equal('Video duration:'+r['video_id'],duration.total_seconds() if duration is not None else None,r['duration_seconds'])
        reverse_links.extend(actual)
    for i,r in enumerate(manifest['files'],2):
        for col,key in [(1,'unique_id'),(2,'title'),(3,'source_folder'),(4,'classification'),(5,'relationship')]: value('Files',i,col,r.get(key,''))
        external('Files',i,6,r['url'])
        modified=book['Files'].cell(i,7).value
        expected_modified=datetime.fromisoformat(r['modified_time'].replace('Z','+00:00')).replace(tzinfo=None) if r.get('modified_time') else None
        equal('Source modified date within 1ms:'+str(i),abs((modified-expected_modified).total_seconds())<=0.001 if modified and expected_modified else modified==expected_modified,True)
    for i,r in enumerate(gaps,2):
        for col,key in [(1,'unique_id'),(2,'participant_or_hearing'),(3,'date'),(4,'status'),(5,'recording_needed'),(6,'locator')]: value('Recording gaps',i,col,r[key])
        external('Recording gaps',i,6,r['evidence_url']);external('Recording gaps',i,8,r['original_transcript_url'])
        if r['existing_video_url']: external('Recording gaps',i,7,r['existing_video_url'])
    for i,r in enumerate(crawl,2):
        expected=[r['title'],r['role'],r.get('declared_items') or '',r.get('visible_memberships') or '',r.get('unique_video_ids') or '',r.get('unavailable_positions') if r.get('unavailable_positions') is not None else '',r.get('pages_checked') or '',r['status_label'],r['evidence']]
        for col,text in enumerate(expected,1): value('Crawl sources',i,col,text)
        external('Crawl sources',i,10,r['source_url'])
    colors={'Statements / submissions':'E1EDF9','Sworn declarations':'F1E6F0','Recognition hearings':'EAE3F5','Victim observations':'E4F0E2','Conditionality / truth contribution':'FFF0D9','Late recognition':'DFF1EF','Protective measures':'E8EBEF','Voluntary statement or submitted segment':'E1EDF9','Submitted response segment — self-read questionnaire':'E1EDF9','Recognition hearing':'EAE3F5'}
    for sheet,rows in [('Transcripts',inv),('English summaries',inv),('Recording gaps',gaps),('Videos',videos)]:
        for i,r in enumerate(rows,2):
            expected = colors.get(r.get('category'),'EEF0F3')
            for col in (1,2): equal('Category color:' + sheet + ':' + str(i),book[sheet].cell(i,col).fill.fgColor.rgb[-6:],expected)
    internal_count = external_count = 0
    for sheet in book:
        for row in sheet:
            for cell in row:
                if cell.hyperlink and cell.hyperlink.location:
                    internal_count += 1
                    target = re.fullmatch(r"'([^']+)'!([A-Z]+\d+)",cell.hyperlink.location)
                    equal('Internal destination parsed:' + sheet.title + ':' + cell.coordinate, bool(target), True)
                    if target:
                        name, coord = target.groups()
                        equal('Internal destination exists:' + sheet.title + ':' + cell.coordinate, name in book.sheetnames and book[name][coord].value is not None, True)
                        if sheet.title != 'Summary': equal('Internal record identity:' + sheet.title + ':' + cell.coordinate,book[name][coord].value,str(cell.value).split('\n')[0])
                if cell.hyperlink and cell.hyperlink.target: external_count += 1
                if sheet.title != 'Summary': equal('No data formula:' + sheet.title + ':' + cell.coordinate,cell.data_type == 'f',False)
    included = [r for r in videos if r['scope_label']=='Included']
    expected_summary={'B10':len(inv),'B12':sum(r['confidence']=='High' for r in inv),'B13':sum(r['confidence']=='High' and r.get('content_verified',False) for r in inv),'B14':sum(r['confidence'] in ['Medium (candidate)','Low (candidate)'] for r in inv),'B15':sum(r['confidence']=='Unmatched' for r in inv),'E18':len(gaps),'E20':len(english),'B41':len(included),'B42':sum(bool(r['transcript_ids']) for r in included),'B43':sum(r['coverage_label']=='Partial supplied transcript' for r in included),'B44':sum(r['coverage_label']=='No supplied transcript · content checked' for r in included),'B45':sum(r['coverage_label']=='No supplied transcript · metadata basis' for r in included),'B46':sum(r['coverage_label']=='Coverage unconfirmed' for r in included),'B47':sum(r['scope_label']=='Scope unconfirmed' for r in videos),'B48':sum(r['scope_label']=='Excluded' for r in videos)}
    for i,category in enumerate(list(colors)[:7],7): expected_summary['E'+str(i)] = sum(r['category']==category for r in inv)
    for cell,n in expected_summary.items(): equal('Cached summary:' + cell,values['Summary'][cell].value,n)
    for sheet,freeze in [('Transcripts','C2'),('English summaries','C2'),('Recording gaps','C2'),('Videos','D2'),('Crawl sources','B2'),('Files','C2')]:
        s = book[sheet];equal('Freeze:' + sheet,s.freeze_panes,freeze)
        equal('Table:' + sheet,len(s.tables),1)
        t = s.tables[next(iter(s.tables))];equal('Full filter:' + sheet,t.autoFilter.ref if t.autoFilter is not None else None,t.ref)
    ns = '{http://schemas.openxmlformats.org/spreadsheetml/2006/main}'
    with ZipFile(BASE/'JEP_transcript_inventory.xlsx') as z:
        for name in z.namelist():
            if re.fullmatch(r'xl/worksheets/sheet\d+\.xml',name):
                nodes=ET.fromstring(z.read(name)).findall(ns+'hyperlinks/'+ns+'hyperlink')
                equal('Unique native link cells:' + name,len(nodes),len({n.get('ref') for n in nodes}))
    hashes={name:hashlib.sha256((BASE/name).read_bytes()).hexdigest() for name in ['workbook_build/build_workbook.mjs','workbook_build/add_native_links.py','workbook_build/validate_outputs.py','JEP_transcript_inventory.xlsx']}
    report={'reviewed_commit':'620cc5eb85860ff77a837058903321876de82b15','hashes':hashes,'all_observed_current_data_checks_passed':not problems,'comparison_counts':dict(comparisons),'problems':problems,'source_records':len(inv),'source_files':len(manifest['files']),'summaries':len(english),'native_external_hyperlinks':external_count,'native_internal_hyperlinks':internal_count,'transcript_video_edges':len(forward_links),'reverse_source_edges':len(reverse_links),'cached_formula_cells_checked':len(expected_summary),'max_transcript_urls':max(len(re.findall(r'https://[^\s;]+',r.get('youtube_url')or'')) for r in inv),'max_video_source_links':max(len(r['source_links']) for r in videos),'worksheet_shapes':{s.title:[s.max_row,s.max_column] for s in book}}
    (HERE/'workbook_observations.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))
    return 1 if problems else 0


if __name__=='__main__':
    raise SystemExit(main())
