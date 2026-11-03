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
    allowed_changes=True
    for i in range(1,before.max_row+1):
        for j in range(1,before.max_column+1):
            if before.cell(i,j).value!=after.cell(i,j).value:
                uid=before.cell(i,1).value;col=openpyxl.utils.get_column_letter(j)
                changed.append([uid,col])
                permitted=uid=='VV-057' and col in ['H','J','K','M','N']
                corrections={'VV-008':('34,104','34,102'),'VV-010':('15,051','15,050')}
                if uid in corrections and col=='H':
                    old_count,new_count=corrections[uid]
                    permitted=after.cell(i,j).value==str(before.cell(i,j).value).replace(old_count,new_count)
                allowed_changes=allowed_changes and permitted
    check('Only intended VV-057 link fields and exact reviewed duplicate-metric corrections changed',allowed_changes,True)
    check('Transcript records preserved',after.max_row-1,93)
    inv=json.loads((OUT/'inventory.json').read_text())
    video=json.loads((OUT/'video_inventory.json').read_text())
    stats=json.loads((OUT/'summary.json').read_text())
    check('All transcript IDs unique',len({r['unique_id'] for r in inv}),93)
    check('All video IDs unique',len({r['video_id'] for r in video}),len(video))
    transcript_rows={after.cell(i,1).value:i for i in range(2,after.max_row+1)}
    video_sheet=book['Videos']
    video_rows={video_sheet.cell(i,1).value:i for i in range(2,video_sheet.max_row+1)}
    check('Workbook transcript IDs equal inventory order',[after.cell(i,1).value for i in range(2,after.max_row+1)],[r['unique_id'] for r in inv])
    check('Workbook video IDs equal inventory order',[video_sheet.cell(i,1).value for i in range(2,video_sheet.max_row+1)],[r['video_id'] for r in video])
    included=[r for r in video if r['scope_label']=='Included']
    check('Included video decisions',len(included),stats['reverse_audit']['included_video_ids'])
    known={r['unique_id'] for r in inv}
    check('Every reverse transcript link resolves',all(i in known for r in video for i in r['transcript_ids']),True)
    check('All included videos have coverage status',all(bool(r['coverage_label']) for r in included),True)
    check('Each source row retains an original Drive hyperlink',all(after.cell(i,7).hyperlink and after.cell(i,7).hyperlink.target==inv[i-2]['direct_file_link'] for i in range(2,95)),True)
    check('All116 originals remain linked',sum(bool(book['Files'].cell(i,6).hyperlink) for i in range(2,118)),116)
    check('All video rows have exact YouTube hyperlinks',all(book['Videos'].cell(i,1).hyperlink and book['Videos'].cell(i,1).hyperlink.target==r['url'] for i,r in enumerate(video,2)),True)
    def native_targets(sheet,row,columns):
        return [sheet.cell(row,col).hyperlink.target for col in columns
                if sheet.cell(row,col).hyperlink and sheet.cell(row,col).hyperlink.target]
    for r in inv:
        row=transcript_rows.get(r['unique_id'])
        expected=re.findall(r'https://[^\s;]+',str(r.get('youtube_url') or ''))
        actual=native_targets(after,row,[10,14,*range(15,after.max_column+1)]) if row is not None else None
        check('Exact transcript video edges '+r['unique_id'],actual,expected)
    originals={r['unique_id']:r['direct_file_link'] for r in inv}
    for r in video:
        row=video_rows.get(r['video_id'])
        actual=native_targets(video_sheet,row,[9,16,*range(17,video_sheet.max_column+1)]) if row is not None else None
        check('Exact video source edges '+r['video_id'],actual,r['source_links'])
        check('Video source URLs correspond to transcript IDs '+r['video_id'],r['source_links'],[originals.get(i) for i in r['transcript_ids']])
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
    for name,freeze in {'Transcripts':'C2','English summaries':'C2','Recording gaps':'C2','Videos':'D2','Crawl sources':'B2','Files':'C2'}.items():
        sheet=book[name]
        expected_range=f'A1:{openpyxl.utils.get_column_letter(sheet.max_column)}{sheet.max_row}'
        check('Frozen headings '+name,sheet.freeze_panes,freeze)
        check('One full table '+name,[table.ref for table in sheet.tables.values()],[expected_range])
        check('Explicit table filter '+name,[table.autoFilter.ref if table.autoFilter is not None else None for table in sheet.tables.values()],[expected_range])
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
