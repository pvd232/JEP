"""Read-only acceptance checks for the updated inventory and source links."""
from pathlib import Path
import collections
import hashlib
import json
import re
import openpyxl

BASE=Path(__file__).resolve().parent
ROOT=BASE.parents[1]
OUT=ROOT/'outputs/jep_transcripts_20261103'


def main():
    old=openpyxl.load_workbook(ROOT/'upload/JEP_transcript_inventory.xlsx',data_only=False)
    book=openpyxl.load_workbook(OUT/'JEP_transcript_inventory.xlsx',data_only=False)
    values=openpyxl.load_workbook(OUT/'JEP_transcript_inventory.xlsx',data_only=True)
    checks=[]
    def check(label,actual,expected):
        checks.append({'check':label,'passed':actual==expected,'actual':actual,'expected':expected})
    check('Worksheet set',book.sheetnames,['Summary','Transcripts','English summaries','Recording gaps','Videos','Crawl sources','Files'])
    for name in ['English summaries','Recording gaps','Files']:
        a=old[name];b=book[name]
        same=all(a.cell(i,j).value==b.cell(i,j).value for i in range(1,a.max_row+1) for j in range(1,a.max_column+1))
        check(name+' content preserved',same,True)
        def link_value(cell):
            return (cell.hyperlink.target,cell.hyperlink.location) if cell.hyperlink else None
        links_equal=all(link_value(a.cell(i,j))==link_value(b.cell(i,j)) for i in range(1,a.max_row+1) for j in range(1,a.max_column+1))
        check(name+' original link targets preserved',links_equal,True)
    before=old['Transcripts'];after=book['Transcripts']
    changed=[]
    for i in range(1,before.max_row+1):
        for j in range(1,before.max_column+1):
            if before.cell(i,j).value!=after.cell(i,j).value:
                changed.append([before.cell(i,1).value,openpyxl.utils.get_column_letter(j)])
    check('Only intended VV-057 transcript fields changed',all(r=='VV-057' and c in ['H','J','K','M','N'] for r,c in changed),True)
    check('Transcript records preserved',after.max_row-1,93)
    inv=json.loads((OUT/'inventory.json').read_text())
    video=json.loads((OUT/'video_inventory.json').read_text())
    stats=json.loads((OUT/'summary.json').read_text())
    check('All transcript IDs unique',len({r['unique_id'] for r in inv}),93)
    check('All video IDs unique',len({r['video_id'] for r in video}),len(video))
    included=[r for r in video if r['scope_label']=='Included']
    check('Included video decisions',len(included),stats['reverse_audit']['included_video_ids'])
    known={r['unique_id'] for r in inv}
    check('Every reverse transcript link resolves',all(i in known for r in video for i in r['transcript_ids']),True)
    check('All included videos have coverage status',all(bool(r['coverage_label']) for r in included),True)
    check('Each source row retains an original Drive hyperlink',all(after.cell(i,7).hyperlink and after.cell(i,7).hyperlink.target==inv[i-2]['direct_file_link'] for i in range(2,95)),True)
    check('All116 originals remain linked',sum(bool(book['Files'].cell(i,6).hyperlink) for i in range(2,118)),116)
    check('All video rows have exact YouTube hyperlinks',all(book['Videos'].cell(i,1).hyperlink and book['Videos'].cell(i,1).hyperlink.target==r['url'] for i,r in enumerate(video,2)),True)
    formula_errors=[]
    for sheet in values:
        for row in sheet:
            for c in row:
                if c.data_type=='e': formula_errors.append([sheet.title,c.coordinate,c.value])
    check('Cached formula errors',formula_errors,[])
    check('Source-record summary recalculation',values['Summary']['B10'].value,93)
    check('Video-count summary recalculation',values['Summary']['B41'].value,len(included))
    check('Mapped-upload summary recalculation',values['Summary']['B42'].value,sum(bool(r['transcript_ids']) for r in included))
    check('Known partial-source summary recalculation',values['Summary']['B43'].value,stats['reverse_audit']['known_partial_supplied_coverage_video_ids'])
    check('Unmatched content-checked upload summary',values['Summary']['B44'].value,stats['reverse_audit']['no_supplied_transcript_content_checked'])
    check('Unmatched metadata-based upload summary',values['Summary']['B45'].value,stats['reverse_audit']['no_supplied_transcript_metadata_basis'])
    check('Every new table has filters and frozen headings',all(book[n].freeze_panes is not None and len(book[n].tables)>0 for n in ['Videos','Crawl sources']),True)
    # Independent manifest membership accounting, including unavailable positions.
    crawl=json.loads((OUT/'crawl_manifest.json').read_text())
    import gzip
    members=json.loads(gzip.decompress((OUT/'public_memberships.json.gz').read_bytes()))
    counts=collections.Counter(m['collection_id'] for m in members)
    for c in crawl['collections']:
        if c['collection_type']=='playlist':
            check(c['collection_key']+' returned-position count',counts[c['collection_id']],c.get('returned_memberships',c.get('visible_memberships')))
            check(c['collection_key']+' no pending requests',c.get('pending_token_sha256',[]),[])
            check(c['collection_key']+' no request/parse errors',c.get('errors',[]),[])
            check(c['collection_key']+' declared total reconciled',c.get('count_reconciled'),True)
    payload=(OUT/'JEP_transcript_inventory.xlsx').read_bytes()
    report={'as_of':'2026-11-03','all_passed':all(c['passed'] for c in checks),'checks':checks,'changed_transcript_fields':changed,'workbook_sha256':hashlib.sha256(payload).hexdigest(),'workbook_bytes':len(payload),'formula_cells':sum(c.data_type=='f' for s in book for row in s for c in row),'external_hyperlinks':sum(bool(c.hyperlink and c.hyperlink.target) for s in book for row in s for c in row),'internal_hyperlinks':sum(bool(c.hyperlink and c.hyperlink.location) for s in book for row in s for c in row)}
    (OUT/'workbook_validation.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k!='checks'},indent=2))
    for c in checks:
        if not c['passed']: print(json.dumps(c))
    if not report['all_passed']: raise SystemExit(1)


if __name__=='__main__':main()
