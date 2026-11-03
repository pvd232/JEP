import fs from 'node:fs/promises';
import path from 'node:path';
import { Workbook, SpreadsheetFile } from '@oai/artifact-tool';

const inputDir = process.argv[2] ?? '/workspace/scratch/8a7e64850a04/outputs/jep_transcripts_20261103';
const outputDir = inputDir;
const records = JSON.parse(await fs.readFile(path.join(inputDir, 'inventory.json'), 'utf8'));
const manifest = JSON.parse(await fs.readFile(path.join(inputDir, 'source_manifest.json'), 'utf8'));
const stats = JSON.parse(await fs.readFile(path.join(inputDir, 'summary.json'), 'utf8'));
const english = JSON.parse(await fs.readFile(path.join(inputDir, 'english_summaries.json'), 'utf8'));
const recordingGaps = JSON.parse(await fs.readFile(path.join(inputDir, 'recording_gaps.json'), 'utf8'));
const videoRecords = JSON.parse(await fs.readFile(path.join(inputDir, 'video_inventory.json'), 'utf8'));
const crawlSources = JSON.parse(await fs.readFile(path.join(inputDir, 'crawl_sources.json'), 'utf8'));
const englishById = new Map(english.map(r => [r.unique_id, r]));
if (englishById.size !== records.length || records.some(r => !englishById.has(r.unique_id))) throw new Error('English summary coverage differs from inventory');
await fs.mkdir(outputDir, { recursive: true });

const wb = Workbook.create();
const summary = wb.worksheets.add('Summary');
const sheet = wb.worksheets.add('Transcripts');
const synopses = wb.worksheets.add('English summaries');
const gapSheet = wb.worksheets.add('Recording gaps');
const videos = wb.worksheets.add('Videos');
const sources = wb.worksheets.add('Crawl sources');
const files = wb.worksheets.add('Files');
const navy = '#263B53', ink = '#253247', muted = '#5C6875';
const colors = {
  'Statements / submissions':'#E1EDF9',
  'Sworn declarations':'#F1E6F0',
  'Recognition hearings':'#EAE3F5',
  'Victim observations':'#E4F0E2',
  'Conditionality / truth contribution':'#FFF0D9',
  'Late recognition':'#DFF1EF',
  'Protective measures':'#E8EBEF',
};
const cellText = x => typeof x === 'string' && /^[=+@]/.test(x) ? "'" + x : x ?? '';
const nativeLinks=[];
const linkCell=(ws,cell,url,label)=>{ws.getRange(cell).values=[[label]];nativeLinks.push({sheet:ws.name,cell,url,label});};
const fields = ['unique_id','category','transcript_title','date','participants','source_folder','direct_file_link','duplicate_notes','video_title','youtube_url','timestamps','confidence','evidence','notes'];
const confidenceLabel=r=>r.confidence!=='High'?r.confidence:String(r.coverage_status??'').startsWith('Partial')?'High · partial recording':r.content_verified?'High · content checked':'High · metadata only';
const headers = ['Unique ID','Category','Transcript title','Hearing / submission date','Participants','Source folder','Original transcript','Duplicate / version notes','Video title','YouTube link(s)','Timestamps','Match confidence','Evidence','Notes'];
const end = records.length + 1;
const matrix = records.map(r=>fields.map(k=> k === 'date' && /^\d{4}-\d{2}-\d{2}$/.test(r[k]??'') ? new Date(r[k]+'T00:00:00Z') : k==='confidence'?confidenceLabel(r):cellText(r[k])));
sheet.getRange(`A1:N${end}`).values = [headers, ...matrix];
sheet.getRange(`D2:D${end}`).setNumberFormat('yyyy-mm-dd');
sheet.getRange(`A1:N${end}`).format = { font:{name:'Arial',size:10,color:ink},verticalAlignment:'top',wrapText:true };
const widths = [24,30,48,18,38,40,22,45,48,36,46,22,66,62];
widths.forEach((w,i)=>sheet.getRangeByIndexes(0,i,end,1).format.columnWidth=w);
sheet.tables.add(`A1:N${end}`,true,'TranscriptInventory').style='TableStyleLight9';
sheet.getRange('A1:N1').format = { fill:navy,font:{name:'Arial',size:10,bold:true,color:'#FFFFFF'},horizontalAlignment:'center',verticalAlignment:'center',rowHeight:34,wrapText:true };
const lookup = new Map();
records.forEach((r,i)=>{
  const row=i+2;
  lookup.set(r.unique_id,row);
  linkCell(sheet,`A${row}`,`#'English summaries'!A${row}`,r.unique_id);
  sheet.getRange(`A${row}:B${row}`).format.fill=colors[r.category]??'#EEF0F3';
  sheet.getRange(`A${row}:B${row}`).format.font.bold=true;
  if(r.direct_file_link) linkCell(sheet,`G${row}`,r.direct_file_link,'Open original transcript');
  const urls = [...String(r.youtube_url??'').matchAll(/https:\/\/[^\s;]+/g)].map(m=>m[0]);
  if(urls.length===1) linkCell(sheet,`J${row}`,urls[0],urls[0]);
  if(urls.length===2){
    const label=`Primary (click here): ${urls[0]}\nJEP reupload (click Notes): ${urls[1]}`;
    matrix[i][9]=label;
    matrix[i][13]=`Open JEP reupload (click here). ${r.notes}`;
    linkCell(sheet,`J${row}`,urls[0],label);
    linkCell(sheet,`N${row}`,urls[1],matrix[i][13]);
    sheet.getRange(`N${row}`).format.font.color='#1E5A9B';
  }
  const lines = Math.max(...matrix[i].map((v,c)=>c===6?1:String(v??'').split('\n').reduce((n,line)=>n+Math.max(1,Math.ceil(line.length/(widths[c]*1.02))),0)));
  sheet.getRange(`A${row}:N${row}`).format.rowHeight=Math.max(64,14*lines+10);
});
sheet.getRange(`G2:G${end}`).format.font.color='#1E5A9B';
sheet.getRange(`J2:J${end}`).format.font.color='#1E5A9B';
sheet.getRange(`L2:L${end}`).conditionalFormats.add('containsText',{text:'Unmatched',format:{fill:'#FCE5E5',font:{color:'#922C2C',bold:true}}});
sheet.getRange(`L2:L${end}`).conditionalFormats.add('containsText',{text:'Medium',format:{fill:'#FFF2CC',font:{color:'#7E5900',bold:true}}});
sheet.getRange(`L2:L${end}`).conditionalFormats.add('containsText',{text:'Low',format:{fill:'#FFF2CC',font:{color:'#7E5900',bold:true}}});
sheet.getRange(`L2:L${end}`).conditionalFormats.add('containsText',{text:'partial recording',format:{fill:'#FFF2CC',font:{color:'#7E5900',bold:true}}});
sheet.getRange(`L2:L${end}`).conditionalFormats.add('containsText',{text:'metadata only',format:{fill:'#FFF2CC',font:{color:'#7E5900',bold:true}}});
sheet.getRange(`L2:L${end}`).conditionalFormats.add('containsText',{text:'Restricted',format:{fill:'#FCE5E5',font:{color:'#922C2C',bold:true}}});
sheet.getRange(`H2:H${end}`).conditionalFormats.add('containsText',{text:'Possible',format:{fill:'#FFF2CC',font:{color:'#7E5900'}}});
sheet.freezePanes.freezeRows(1);
sheet.freezePanes.freezeColumns(2);
sheet.showGridLines=false;
sheet.tabColor=navy;

const sheaders=['Unique ID','Category','English title','Named people and roles','Purpose of this session','Main accounts and claims','Stated positions and responses','Outcome and open questions','Evidence pointers','Review limits','Original transcript'];
const swidths=[24,30,48,66,54,96,70,66,60,60,22];
const srows=records.map(r=>{
 const e=englishById.get(r.unique_id);
 return [r.unique_id,r.category,e.english_title,e.named_people_roles,e.purpose,e.main_accounts_claims,e.stated_positions_responses,e.outcome_open_questions,e.source_pointers.join('\n\n'),e.summary_limits,'Open original transcript'].map(cellText);
});
synopses.getRange(`A1:K${end}`).values=[sheaders,...srows];
synopses.getRange(`A1:K${end}`).format={font:{name:'Arial',size:10,color:ink},verticalAlignment:'top',wrapText:true};
swidths.forEach((w,i)=>synopses.getRangeByIndexes(0,i,end,1).format.columnWidth=w);
synopses.tables.add(`A1:K${end}`,true,'EnglishSummaries').style='TableStyleLight9';
synopses.getRange('A1:K1').format={fill:navy,font:{name:'Arial',size:10,bold:true,color:'#FFFFFF'},horizontalAlignment:'center',verticalAlignment:'center',rowHeight:34,wrapText:true};
records.forEach((r,i)=>{
 const row=i+2;
 synopses.getRange(`A${row}:B${row}`).format.fill=colors[r.category]??'#EEF0F3';
 synopses.getRange(`A${row}:B${row}`).format.font.bold=true;
 linkCell(synopses,`A${row}`,`#'Transcripts'!A${row}`,r.unique_id);
 linkCell(synopses,`K${row}`,r.direct_file_link,'Open original transcript');
 const lines=Math.max(...srows[i].map((v,c)=>String(v??'').split('\n').reduce((n,line)=>n+Math.max(1,Math.ceil(line.length/(swidths[c]*0.95))),0)));
 synopses.getRange(`A${row}:K${row}`).format.rowHeight=Math.min(409,Math.max(180,14*lines+18));
});
synopses.getRange(`A2:A${end}`).format.font.color='#1E5A9B';
synopses.getRange(`K2:K${end}`).format.font.color='#1E5A9B';
synopses.freezePanes.freezeRows(1);
synopses.freezePanes.freezeColumns(2);
synopses.showGridLines=false;
synopses.tabColor='#427E78';

const gheaders=['Record ID','Participant / hearing','Hearing / submission date','Gap / access status','Exact recording or check needed','Evidence / case-file locator','Existing public video','Original transcript','New recording link (add here)'];
const gwidths=[24,42,23,38,80,80,28,24,36];
const grows=recordingGaps.map(r=>[r.unique_id,r.participant_or_hearing,r.date,r.status,r.recording_needed,r.locator,r.existing_video_url?'Open identified video':'No verified public match','Open original transcript',''].map(cellText));
const gend=grows.length+1;
gapSheet.getRange(`A1:I${gend}`).values=[gheaders,...grows];
gapSheet.getRange(`A1:I${gend}`).format={font:{name:'Arial',size:10,color:ink},verticalAlignment:'top',wrapText:true};
gwidths.forEach((w,i)=>gapSheet.getRangeByIndexes(0,i,gend,1).format.columnWidth=w);
gapSheet.tables.add(`A1:I${gend}`,true,'RecordingGaps').style='TableStyleLight9';
gapSheet.getRange('A1:I1').format={fill:navy,font:{name:'Arial',size:10,bold:true,color:'#FFFFFF'},horizontalAlignment:'center',verticalAlignment:'center',rowHeight:44,wrapText:true};
recordingGaps.forEach((r,i)=>{
 const row=i+2;
 gapSheet.getRange(`A${row}:B${row}`).format.fill=colors[r.category]??'#EEF0F3';
 gapSheet.getRange(`A${row}`).format.font.bold=true;
 linkCell(gapSheet,`A${row}`,`#'Transcripts'!A${lookup.get(r.unique_id)}`,r.unique_id);
 linkCell(gapSheet,`F${row}`,r.evidence_url,r.locator);
 if(r.existing_video_url) linkCell(gapSheet,`G${row}`,r.existing_video_url,'Open identified video');
 linkCell(gapSheet,`H${row}`,r.original_transcript_url,'Open original transcript');
 gapSheet.getRange(`D${row}`).format.fill=r.gap_type==='Unmatched recording'?'#FCE5E5':'#FFF2CC';
 gapSheet.getRange(`D${row}`).format.font.color=r.gap_type==='Unmatched recording'?'#922C2C':'#7E5900';
 const lines=Math.max(...grows[i].map((v,c)=>String(v??'').split('\n').reduce((n,line)=>n+Math.max(1,Math.ceil(line.length/(gwidths[c]*0.95))),0)));
 gapSheet.getRange(`A${row}:I${row}`).format.rowHeight=Math.max(98,14*lines+16);
});
gapSheet.getRange(`A2:A${gend}`).format.font.color='#1E5A9B';
gapSheet.getRange(`F2:H${gend}`).format.font.color='#1E5A9B';
gapSheet.getRange(`I2:I${gend}`).format.fill='#EDF5FF';
gapSheet.freezePanes.freezeRows(1);
gapSheet.freezePanes.freezeColumns(2);
gapSheet.showGridLines=false;
gapSheet.tabColor='#C48B38';

const vheaders=['Video ID / YouTube link','Category','Scope decision','Public video title','Hearing / submission date','Participants / session','Supplied transcript coverage','Transcript ID(s)','Original transcript','Video timestamps / boundaries','Concise coverage evidence','Video duration','Publisher','Discovery sources','Scope evidence','Notes / review limits'];
const videoCategoryColors={
 'Voluntary statement or submitted segment':colors['Statements / submissions'],
 'Submitted response segment — self-read questionnaire':colors['Statements / submissions'],
 'Recognition hearing':colors['Recognition hearings'],
};
const vwidths=[25,30,23,56,22,42,49,27,26,65,85,18,25,45,66,82];
const vend=videoRecords.length+1;
const vrows=videoRecords.map(r=>[
 r.video_id,r.category,r.scope_label,r.title,/^\d{4}-\d{2}-\d{2}$/.test(r.date??'')?new Date(r.date+'T00:00:00Z'):r.date??'',r.participants,r.coverage_label,r.transcript_ids.join('\n'),r.source_links.length?'Open original '+r.transcript_ids[0]:'No supplied transcript link',r.timestamps,r.evidence,r.duration_seconds==null?'':r.duration_seconds/86400,r.publisher,r.collections.join('\n'),r.scope_evidence,r.notes
].map(cellText));
videos.getRange(`A1:P${vend}`).values=[vheaders,...vrows];
videos.getRange(`A1:P${vend}`).format={font:{name:'Arial',size:10,color:ink},verticalAlignment:'top',wrapText:true};
vwidths.forEach((w,i)=>videos.getRangeByIndexes(0,i,vend,1).format.columnWidth=w);
videos.getRange(`E2:E${vend}`).setNumberFormat('yyyy-mm-dd');
videos.getRange(`L2:L${vend}`).setNumberFormat('[h]:mm:ss');
videos.tables.add(`A1:P${vend}`,true,'VideoCoverage').style='TableStyleLight9';
videos.getRange('A1:P1').format={fill:navy,font:{name:'Arial',size:10,bold:true,color:'#FFFFFF'},horizontalAlignment:'center',verticalAlignment:'center',rowHeight:42,wrapText:true};
videoRecords.forEach((r,i)=>{
 const row=i+2;
 linkCell(videos,`A${row}`,r.url,r.video_id);
 videos.getRange(`A${row}:B${row}`).format.fill=colors[r.category]??videoCategoryColors[r.category]??'#EEF0F3';
 videos.getRange(`A${row}:B${row}`).format.font.bold=true;
 if(r.transcript_ids.length&&lookup.has(r.transcript_ids[0])) linkCell(videos,`H${row}`,`#'Transcripts'!A${lookup.get(r.transcript_ids[0])}`,r.transcript_ids.join('\n'));
 if(r.source_links.length) linkCell(videos,`I${row}`,r.source_links[0],'Open original '+r.transcript_ids[0]);
 if(r.source_links.length>1) linkCell(videos,`P${row}`,r.source_links[1],'Second original '+r.transcript_ids[1]+' (click here). '+r.notes);
 videos.getRange(`C${row}`).format.fill=r.scope_label==='Included'?'#E4F0E2':r.scope_label==='Scope unconfirmed'?'#FFF2CC':'#EEF0F3';
 if(r.coverage_label.startsWith('No supplied transcript')) videos.getRange(`G${row}`).format.fill='#FCE5E5';
 if(/Partial|unconfirmed|metadata only/i.test(r.coverage_label)) videos.getRange(`G${row}`).format.fill='#FFF2CC';
 const lines=Math.max(...vrows[i].map((v,c)=>String(v??'').split('\n').reduce((n,line)=>n+Math.max(1,Math.ceil(line.length/(vwidths[c]*0.98))),0)));
 videos.getRange(`A${row}:P${row}`).format.rowHeight=Math.min(409,Math.max(78,14*lines+12));
});
for(const col of ['A','H','I']) videos.getRange(`${col}2:${col}${vend}`).format.font.color='#1E5A9B';
videos.freezePanes.freezeRows(1); videos.freezePanes.freezeColumns(3); videos.showGridLines=false; videos.tabColor='#526E91';

const cheaders=['Source / collection','Role in this review','Declared positions','Normal-title appearances','Distinct IDs (including unavailable)','Unavailable positions','Pages checked','Pagination / accounting status','Concise evidence / limitation','Official source'];
const cwidths=[42,53,20,21,21,23,18,45,105,29];
const cend=crawlSources.length+1;
const crows=crawlSources.map(r=>[r.title,r.role,r.declared_items??'',r.visible_memberships??'',r.unique_video_ids??'',r.unavailable_positions??'',r.pages_checked??'',r.status_label,r.evidence,'Open official source'].map(cellText));
sources.getRange(`A1:J${cend}`).values=[cheaders,...crows];
sources.getRange(`A1:J${cend}`).format={font:{name:'Arial',size:10,color:ink},verticalAlignment:'top',wrapText:true};
cwidths.forEach((w,i)=>sources.getRangeByIndexes(0,i,cend,1).format.columnWidth=w);
sources.tables.add(`A1:J${cend}`,true,'CrawlSourceEvidence').style='TableStyleLight9';
sources.getRange('A1:J1').format={fill:navy,font:{name:'Arial',size:10,bold:true,color:'#FFFFFF'},horizontalAlignment:'center',verticalAlignment:'center',rowHeight:42,wrapText:true};
crawlSources.forEach((r,i)=>{
 const row=i+2; linkCell(sources,`J${row}`,r.source_url,'Open official source');
 sources.getRange(`A${row}:B${row}`).format.fill=r.supplemental?'#EEF0F3':'#E1EDF9';
 if(/gap|mismatch|failed|unconfirmed/i.test(r.status_label)) sources.getRange(`H${row}`).format.fill='#FFF2CC';
 const lines=Math.max(...crows[i].map((v,c)=>String(v??'').split('\n').reduce((n,line)=>n+Math.max(1,Math.ceil(line.length/(cwidths[c]*0.98))),0)));
 sources.getRange(`A${row}:J${row}`).format.rowHeight=Math.max(76,14*lines+12);
});
sources.getRange(`C2:G${cend}`).setNumberFormat('#,##0');
sources.getRange(`J2:J${cend}`).format.font.color='#1E5A9B';
sources.freezePanes.freezeRows(1); sources.freezePanes.freezeColumns(1); sources.showGridLines=false; sources.tabColor='#8496A8';

const fheaders=['Transcript ID','Source filename','Source folder','File type','Relationship','Original file','Modified'];
const frows=manifest.files.map(f=>[f.unique_id??'',f.title,f.source_folder,f.classification,f.relationship??'',f.url,f.modified_time?new Date(f.modified_time):'']);
const fend=frows.length+1;
files.getRange(`A1:G${fend}`).values=[fheaders,...frows];
files.getRange(`A1:G${fend}`).format={font:{name:'Arial',size:10,color:ink},wrapText:true,verticalAlignment:'top'};
[24,64,64,23,45,24,20].forEach((w,i)=>files.getRangeByIndexes(0,i,fend,1).format.columnWidth=w);
files.getRange(`G2:G${fend}`).setNumberFormat('yyyy-mm-dd');
files.tables.add(`A1:G${fend}`,true,'SourceFiles').style='TableStyleLight9';
files.getRange('A1:G1').format={fill:navy,font:{name:'Arial',size:10,bold:true,color:'#FFFFFF'},horizontalAlignment:'center',verticalAlignment:'center',rowHeight:30,wrapText:true};
manifest.files.forEach((f,i)=>{
  const n=i+2;
  linkCell(files,`F${n}`,f.url,'Open original file');
  if(f.unique_id&&lookup.has(f.unique_id)) linkCell(files,`A${n}`,`#'Transcripts'!A${lookup.get(f.unique_id)}`,f.unique_id);
  if(f.category) files.getRange(`A${n}`).format.fill=colors[f.category]??'#EEF0F3';
  const lines=Math.max(Math.ceil(f.title.length/64),Math.ceil(f.source_folder.length/64),Math.ceil((f.relationship??'').length/45),2);
  files.getRange(`A${n}:G${n}`).format.rowHeight=14*lines+10;
});
files.getRange(`A2:A${fend}`).format.font.color='#1E5A9B';
files.getRange(`F2:F${fend}`).format.font.color='#1E5A9B';
files.freezePanes.freezeRows(1);
files.freezePanes.freezeColumns(2);
files.showGridLines=false;
files.tabColor='#8496A8';

summary.getRange('A1:F64').format={font:{name:'Arial',size:11,color:ink},verticalAlignment:'center'};
summary.getRange('A1:A64').format.columnWidth=34;
summary.getRange('B1:B64').format.columnWidth=17;
summary.getRange('C1:C64').format.columnWidth=4;
summary.getRange('D1:D64').format.columnWidth=34;
summary.getRange('E1:E64').format.columnWidth=14;
summary.getRange('F1:F64').format.columnWidth=39;
summary.getRange('A2').values=[['JEP transcript inventory']];
summary.getRange('A2').format.font={name:'Arial',size:16,bold:true,color:navy};
summary.getRange('A3').values=[['Reviewed 3 November 2026']];
summary.getRange('A3').format.font.color=muted;
summary.getRange('A4:F4').format.borders={bottom:{style:'thin',color:'#A7B3C0'}};
summary.getRange('A6:B6').values=[['Inventory','Count']];
summary.getRange('D6:F6').values=[['Hearing category','Rows','Color key']];
for(const range of ['A6:B6','D6:F6']) summary.getRange(range).format={fill:navy,font:{name:'Arial',size:11,bold:true,color:'#FFFFFF'},rowHeight:26};
const metrics=[
 ['Files discovered',stats.files],['Folders inventoried',stats.folders],['Transcript files',stats.transcript_files],
 ['Unique transcripts / segments',`=COUNTA('Transcripts'!$A$2:$A$${end})`],['Additional versions / notes',stats.additional_versions],
 ['High confidence identities',`=COUNTIFS('Transcripts'!$L$2:$L$${end},"High · content checked")+COUNTIFS('Transcripts'!$L$2:$L$${end},"High · partial recording")+COUNTIFS('Transcripts'!$L$2:$L$${end},"High · metadata only")`],
 ['Of these: content checked',`=COUNTIFS('Transcripts'!$L$2:$L$${end},"High · content checked")+COUNTIFS('Transcripts'!$L$2:$L$${end},"High · partial recording")`],
 ['Uncertain candidates',`=COUNTIFS('Transcripts'!$L$2:$L$${end},"Medium (candidate)")+COUNTIFS('Transcripts'!$L$2:$L$${end},"Low (candidate)")`],
 ['Unmatched',`=COUNTIFS('Transcripts'!$L$2:$L$${end},"Unmatched")`],
 ['Supporting legal PDFs',stats.legal_pdfs],['Link / index documents',stats.link_indexes],
];
metrics.forEach(([label,val],i)=>{const r=i+7;summary.getRange(`A${r}`).values=[[label]];if(typeof val==='string'&&val.startsWith('='))summary.getRange(`B${r}`).formulas=[[val]];else summary.getRange(`B${r}`).values=[[val]];});
Object.entries(colors).forEach(([cat,color],i)=>{
 const r=i+7;
 summary.getRange(`D${r}`).values=[[cat]];
 summary.getRange(`D${r}`).format.fill=color;
 summary.getRange(`D${r}`).format.wrapText=true;
 summary.getRange(`E${r}`).formulas=[[`=COUNTIFS('Transcripts'!$B$2:$B$${end},"${cat}")`]];
 summary.getRange(`F${r}`).format.fill=color;
});
summary.getRange('A7:F17').format.rowHeight=28;
summary.getRange('B7:B17').setNumberFormat('#,##0');
summary.getRange('E7:E13').setNumberFormat('#,##0');
linkCell(summary,'A18',"#'Recording gaps'!A1",'Open recording gaps');
summary.getRange('D18').values=[['Recording / verification gaps']];
summary.getRange('E18').formulas=[[`=COUNTA('Recording gaps'!$A$2:$A$${gend})`]];
summary.getRange('E18').setNumberFormat('#,##0');
summary.getRange('A18:F18').format.rowHeight=28;
linkCell(summary,'A19',"#'Transcripts'!A1",'Open transcript table');
linkCell(summary,'D19',"#'Files'!A1",'Open all source files');
linkCell(summary,'A20',"#'English summaries'!A1",'Open English summaries');
summary.getRange('D20').values=[['English summaries included']];
summary.getRange('E20').formulas=[[`=COUNTA('English summaries'!$A$2:$A$${end})`]];
summary.getRange('E20').setNumberFormat('#,##0');
summary.getRange('A18:F20').format.font.color='#1E5A9B';
summary.getRange('A21:F21').format.borders={bottom:{style:'thin',color:'#A7B3C0'}};
const notes=[
 ['Row unit','One original transcript or separately supplied segment. Recording restarts stay together; VV-071 combines sessions on 12 and 20 Aug 2021.'],
 ['High confidence','Confidence identifies the recording. Content-checked rows use public captions; metadata-only rows have a content-verification gap.'],
 ['Flags','Amber marks partial recordings or unresolved verification. Red marks rows with no located public match. High identity confidence does not certify complete coverage.'],
 ['Timestamps','Verified YouTube ranges and anchors use approximate caption cues. Source-local times are labeled separately; exact audio word boundaries were not measured.'],
 ['Versions','Content checks grouped 12 additional versions or notes. Every original file remains linked in Files.'],
 ['Access gaps',stats.access_note],
 ['Date corrections',stats.date_note],
 ['Casanare coverage','Four 2023 files cover 18 Sep morning/afternoon, 19 Sep morning and 20 Sep morning.'],
 ['Original documents','Original transcript links open the source Drive files. Files lists all 116 originals, including alternate versions.'],
 ['Participants','Principal participants are listed. Spellings follow the transcript or the identified public video; lists are not exhaustive.'],
 ['English summaries','One substantive summary per row, with roles, attributed claims, responses, outcomes and source pointers. Long transcripts were selectively reviewed across sections; these summaries are not audio-validated reference transcripts.'],
 ['Using the summaries','Click any transcript ID to move between Transcripts and English summaries. Evidence uses source Order values or extracted paragraph labels paired with searchable Spanish phrases.'],
 ['Source-quality findings','CAS03-20230920-AM Order 49 contains unrelated text marked NO_SUSTANTIVO, excluded from its summary. Some later files retain incorrect template headings; the spoken opening determines the hearing type.'],
 ['Recording gaps','15 rows specify 11 unlocated recordings, 2 missing continuations and 2 content checks. Each gives the exact asset needed, evidence, original link and a field for a newly supplied recording link.'],
 ['Access and corrections','VV-064/VV-067 expressly describe private/reserved hearings; VV-065 protects the declarant’s identity. Current recording access needs confirmation. VV-011 is a sworn declaration.'],
];
notes.forEach(([label,value],i)=>{
  const r=i+23;
  summary.getRange(`A${r}`).values=[[label]];
  summary.getRange(`A${r}`).format.font.bold=true;
  summary.getRange(`B${r}:F${r}`).merge();
  summary.getRange(`B${r}`).values=[[value]];
  summary.getRange(`B${r}:F${r}`).format.wrapText=true;
  summary.getRange(`A${r}:F${r}`).format.rowHeight=value.length>160?44:34;
});
summary.getRange('A40:F40').merge(); summary.getRange('A40').values=[['Reverse video coverage · Case 03 / Casanare']];
summary.getRange('A40:F40').format={fill:navy,font:{name:'Arial',size:12,bold:true,color:'#FFFFFF'},rowHeight:30};
const vm=[
 ['Included public uploads',`=COUNTIFS('Videos'!$C$2:$C$${vend},"Included")`,'Distinct video IDs; repeats in playlists count once.'],
 ['Linked to supplied transcript(s)','=B41-B44-B45-B46','Included uploads less those with no source or unresolved coverage. Includes known partial supplied coverage.'],
 ['Known partial source coverage',`=COUNTIFS('Videos'!$C$2:$C$${vend},"Included",'Videos'!$G$2:$G$${vend},"Partial supplied transcript")`,'An existing supplied transcript omits an identified part of the video.'],
 ['No source · content checked',`=COUNTIFS('Videos'!$C$2:$C$${vend},"Included",'Videos'!$G$2:$G$${vend},"No supplied transcript · content checked")`,'A distinct session has a public-content check; no supplied transcript was located.'],
 ['No source · metadata basis',`=COUNTIFS('Videos'!$C$2:$C$${vend},"Included",'Videos'!$G$2:$G$${vend},"No supplied transcript · metadata basis")`,'Metadata identifies a session absent from the inventory; content remains unchecked.'],
 ['Coverage unresolved',`=COUNTIFS('Videos'!$C$2:$C$${vend},"Included",'Videos'!$G$2:$G$${vend},"Coverage unconfirmed")`,'Do not treat a possible alternate or continuation as a confirmed missing transcript.'],
 ['Scope unconfirmed in Videos',`=COUNTIFS('Videos'!$C$2:$C$${vend},"Scope unconfirmed")`,'Outside the confirmed Casanare corpus until the connection/proceeding type is established.'],
 ['Excluded candidates in Videos',`=COUNTIFS('Videos'!$C$2:$C$${vend},"Excluded")`,'Context, edited material or another case/subcase; reasons stay visible.'],
];
vm.forEach(([label,formula,note],i)=>{const r=41+i;summary.getRange(`A${r}`).values=[[label]];summary.getRange(`A${r}`).format.wrapText=true;summary.getRange(`B${r}`).formulas=[[formula]];summary.getRange(`B${r}`).setNumberFormat('#,##0');summary.getRange(`D${r}:F${r}`).merge();summary.getRange(`D${r}`).values=[[note]];summary.getRange(`D${r}:F${r}`).format.wrapText=true;summary.getRange(`A${r}:F${r}`).format.rowHeight=36;});
linkCell(summary,'A50',"#'Videos'!A1",'Open reverse video map'); linkCell(summary,'D50',"#'Crawl sources'!A1",'Open crawl sources');
summary.getRange('A50:F50').format.font.color='#1E5A9B'; summary.getRange('A50:F50').format.rowHeight=28;
const reverseNotes=[['Pagination proof',stats.reverse_audit.pagination_note],['Scope and completeness',stats.reverse_audit.completeness_note],['Broad metadata queue',stats.reverse_audit.broad_scope_note],['Direction of gaps','Recording gaps concerns source text without located recording content. Videos concerns public recordings without supplied source text. These counts overlap and must not be added.'],['Original count','The source inventory remains 93 records and 93 English summaries. Additional video uploads do not create additional source transcripts.']];
reverseNotes.forEach(([label,value],i)=>{const r=52+i;summary.getRange(`A${r}`).values=[[label]];summary.getRange(`A${r}`).format.font.bold=true;summary.getRange(`B${r}:F${r}`).merge();summary.getRange(`B${r}`).values=[[value]];summary.getRange(`B${r}:F${r}`).format.wrapText=true;summary.getRange(`A${r}:F${r}`).format.rowHeight=value.length>260?64:48;});
summary.showGridLines=false;
summary.tabColor=navy;

wb.recalculate();
const inspected=await wb.inspect({kind:'table',range:'Summary!A6:F17',include:'values,formulas',tableMaxRows:12,tableMaxCols:6,maxChars:3500});
console.log(inspected.ndjson);
const errors=await wb.inspect({kind:'match',searchTerm:'#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A|#NUM!|#NULL!|#SPILL!|#CALC!',options:{useRegex:true,maxResults:30},summary:'Final formula check'});
console.log(errors.ndjson);
for(const [name,range,file] of [['Summary','A40:F56','reverse_summary_preview.png'],['Videos','A1:G5','videos_preview.png'],['Crawl sources','A1:I5','crawl_sources_preview.png']]){
 const blob=await wb.render({sheetName:name,range,scale:1.5,format:'png'});
 await fs.writeFile(path.join('/tmp/jep-transcripts-8a7e64850a04',file),new Uint8Array(await blob.arrayBuffer()));
}
const output=await SpreadsheetFile.exportXlsx(wb);
await output.save(path.join(outputDir,'JEP_transcript_inventory.xlsx'));
await fs.writeFile('/tmp/jep-transcripts-8a7e64850a04/native_links.json',JSON.stringify(nativeLinks));
console.log(JSON.stringify({file:path.join(outputDir,'JEP_transcript_inventory.xlsx'),transcripts:records.length,source_files:manifest.files.length,english_summaries:english.length,recording_gaps:recordingGaps.length,video_rows:videoRecords.length,crawl_sources:crawlSources.length}));
