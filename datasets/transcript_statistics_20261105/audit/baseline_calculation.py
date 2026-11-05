"""Build source-linked JEP corpus statistics from extracted records and reviewed counts."""
from pathlib import Path
import json,csv,hashlib,statistics,collections,subprocess,io
import fitz

BASE=Path(__file__).resolve().parent
OUT=BASE/'publication'/'transcript_statistics_20261105';OUT.mkdir(parents=True,exist_ok=True)
sources=json.loads((BASE/'extracted_private.json').read_text())
review=json.loads((BASE/'participant_review.json').read_text())
overrides=review['records']
assert len(sources)==93 and len({r['unique_id'] for r in sources})==93
rows=[]
for r in sources:
 uid=r['unique_id'];pdf=None
 for d in ['rendered_repaired','rendered_retry','rendered']:
  p=BASE/d/(uid+'.pdf')
  if p.exists():
   try:
    with fitz.open(p) as doc:
     if len(doc)>0 and sum(len(page.get_text()) for page in doc)>100:pdf=p;break
   except Exception:pass
 pages=len(fitz.open(pdf)) if pdf else None
 if r['extension']=='xlsx':
  word_count=0
  for sheet in r['sheets']:
   h=sheet['rows'][0];di=[i for i,v in enumerate(h) if v.lower().startswith(('diál','dial'))][0]
   word_count+=sum(len(row[di].split()) for row in sheet['rows'][1:])
 else:word_count=r['extracted_words']
 default_comp=1 if r['category'] in ['Statements / submissions','Protective measures'] else 0
 pcount=overrides.get(uid,{'victims':0,'comparecientes':default_comp})
 evidence=pcount.get('evidence','One principal deponent in the source/inventory; sworn witnesses kept separate from comparecientes. No separately identified victim speaking floor counted in the rapid review.')
 rows.append({'record_id':uid,'category':r['category'],'date':r['date'],'format':r['extension'],'rendered_pages':pages,'text_words':word_count,'pages_at_500_words':round(word_count/500,3),'victim_speakers_min':pcount['victims'],'compareciente_speakers_min':pcount['comparecientes'],'witness_deponents':int(r['category']=='Sworn declarations'),'source_url':r['direct_file_link'],'source_sha256':hashlib.sha256(Path(r['path']).read_bytes()).hexdigest(),'participant_count_evidence':evidence})
pages=[r['rendered_pages'] for r in rows if r['rendered_pages'] is not None]
word_counts=[r['text_words'] for r in rows]
victims=[r['victim_speakers_min'] for r in rows];comps=[r['compareciente_speakers_min'] for r in rows]
def desc(values):
 return {'n':len(values),'total':sum(values),'mean':statistics.mean(values),'median':statistics.median(values),'min':min(values),'max':max(values),'sample_sd':statistics.stdev(values)}
summary={'as_of':'2026-11-05','inventory_commit':'13c975c6f650e03a04a329e33c2bfdd3eba2c64d','consolidated_transcript_records':len(rows),'source_transcript_files_before_consolidation':105,'format_counts':dict(collections.Counter(r['format'] for r in rows)),'hearing_category_counts':dict(collections.Counter(r['category'] for r in rows)),'rendered_document_pages':desc(pages),'page_count_exclusions':[{'record_id':r['record_id'],'reason':'Spreadsheet dialogue has no stable transcript pagination' if r['format']=='xlsx' else 'PDF rendering failed'} for r in rows if r['rendered_pages'] is None],'text_words':desc(word_counts),'all_records_page_equivalent_500_words_mean':statistics.mean(word_counts)/500,'identified_victim_speakers_min':desc(victims),'identified_compareciente_speakers_min':desc(comps),'records_with_identified_victim_speakers':sum(v>0 for v in victims),'victim_speakers_mean_in_records_with_victim_speakers':statistics.mean(v for v in victims if v>0),'participant_count_scope':review['metric'],'participant_count_status':'Rapid source audit; conservative minimum counts. Generic role tags and diarization identifiers were corrected at named/announced floors; unresolved identities are merged or omitted. These are recorded speakers, not total audience attendance or underlying-crime victim totals.','soffice_version':subprocess.run(['soffice','--version'],capture_output=True,text=True).stdout.strip()}
assert sum(summary['format_counts'].values())==93
assert sum(summary['hearing_category_counts'].values())==93
assert sum(victims)==146 and sum(comps)==221
(OUT/'summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
with (OUT/'records.csv').open('w',newline='') as f:
 writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
missing_docs=[r['record_id'] for r in rows if r['format']!='xlsx' and r['rendered_pages'] is None]
coverage=f"{len(pages)} of the 79 Word/ODT records"
paragraph=(f"Fourteen spreadsheet transcripts are measured by dialogue words. {len(missing_docs)} document(s) did not produce a usable PDF: {', '.join(missing_docs)}. Their text and participant counts remain included." if missing_docs else "All 79 Word/ODT transcripts produced usable PDFs. Fourteen spreadsheet transcripts are measured by dialogue words.")
readme=f'''# JEP Casanare: meeting statistics

Source audit: 5 November 2026. The supplied corpus contains **93 consolidated transcript/session records**, from **105 transcript source files**, spanning August 2018–April 2026. Records include individual statements, recorded submissions, split sessions and multi-day hearings. All describe the Casanare subcase of Case 03.

| Measure | Result | Denominator |
|---|---:|---|
| Mean rendered document length | **{statistics.mean(pages):.1f} pages** | {coverage} |
| Median rendered document length | **{statistics.median(pages):g} pages** | Same rendered documents |
| Rendered document length range | **{min(pages)}–{max(pages)} pages** | Same rendered documents |
| Total rendered pages | **{sum(pages):,}** | Same rendered documents |
| Extracted text | **{sum(word_counts):,} words** | All 93 records |
| Mean text length | **{statistics.mean(word_counts):,.0f} words** | All 93 records |
| Mean length at 500 words/page | **{statistics.mean(word_counts)/500:.1f} page equivalents** | All 93 records |
| Identifiable victim speakers | **{sum(victims)/93:.2f} per record** | Conservative minimum: {sum(victims)} person–record incidences / 93 |
| Identifiable compareciente speakers | **{sum(comps)/93:.2f} per record** | Conservative minimum: {sum(comps)} person–record incidences / 93 |
| Victim speakers within records with identified victim voices | **{statistics.mean(v for v in victims if v>0):.1f} per record** | {sum(v>0 for v in victims)} records |
| Principal compareciente in individual statements/submissions | **1 per record** | 67 records |

## Counting people

The participant measures count identifiable live speakers, including people who introduce themselves. Each person counts once within a transcript and may count again in another transcript. A victim's relative speaking in their own capacity as a victim counts; lawyers acting as legal representatives have their own role and are excluded from victim counts. Five sworn-declaration records contain principal witnesses, kept separate from comparecientes.

These are **minimum speaker counts from a rapid source review**. Silent observers, unassigned voices and uncertain identities can increase actual participation. A zero records that no separate speaker in that role was identified. Audience attendance and the number of people killed or disappeared in the underlying crimes are different measures.

The review combined the participant introductions, named speaker tables, live floor announcements and personal self-identification. A row labelled VICTIMA can contain several people; a diarization ID can refer to different people after a recording restart. Repeated questions and repeated morning/afternoon introductions were merged. Family members labelled COMPARECIENTE in the December 2024 and August 2025 spreadsheets were reassigned from context. The similar Javier Abella Roa name strings on 4 December 2024 were conservatively merged; an uncertain repeated victim identity on 24 May 2024 was also merged.

## Counting pages and words

{paragraph}

Document page counts come from headless LibreOffice PDF rendering with the source document's layout. The report uses rendered pages because stored Word page properties were absent or inconsistent in some files. Fonts and layout engines can change pagination. Three problematic DOCX packages were XML-reserialized in temporary copies without changing their text; usable outputs, where present, are counted. The original sources were preserved.

Word/ODT text includes document-body paragraphs and tables. Spreadsheet word counts use the dialogue column, excluding order numbers and role labels. The 500-word page equivalent is a declared length measure that covers every record. It is separate from the rendered-page measure.

## Hearing types

| Type | Records |
|---|---:|
| Statements/submissions | 67 |
| Sworn declarations | 5 |
| Recognition hearings | 4 |
| Victim observations | 4 |
| Conditionality/truth contribution | 10 |
| Late recognition | 2 |
| Protective measures | 1 |

## Harm dimensions in the shared Catatumbo order

The Catatumbo order identifies six overlapping dimensions, at printed p. 796, paragraph 1956, developed on pp. 796–809:

| Dimension | Examples |
|---|---|
| Moral harm | Grief, humiliation, damaged dignity/reputation and interrupted mourning or funeral rituals. |
| Physical, mental and emotional harm | Bodily injury, trauma and enduring psychological suffering. |
| Harm to life plans | Interrupted education, employment, relationships and family futures. |
| Property/economic harm | Lost income, assets and household providers; search, legal and funeral costs and debts. |
| Sociocultural/territorial harm | Damaged community ties and organizations, cultural practices and connections to territory. |
| Civic trust and the rule of law | Lost confidence in armed forces, justice institutions and the state's protective role. |

## Sources and calculation files

- [Source-linked record counts](records.csv): one row per accepted transcript record, with rendered pages, word counts, participant minima, count evidence, original Drive link and input SHA-256.
- [Machine-readable summary](summary.json).
- [Consolidated inventory](../transcript_inventory_20261103/inventory.json) and [source manifest](../transcript_inventory_20261103/source_manifest.json), inspected at commit `13c975c6f650e03a04a329e33c2bfdd3eba2c64d`.
- [Original Catatumbo order](https://drive.google.com/file/d/18k4JNF2D_Z6gqmKTBIDgsFrJU3l7fQSz/view), printed pp. 796–809.

The corpus source text was used privately for this calculation. This directory contains the derived counts and their provenance.
'''
(OUT/'README.md').write_text(readme)
print(json.dumps({k:summary[k] for k in ['rendered_document_pages','text_words','identified_victim_speakers_min','identified_compareciente_speakers_min','records_with_identified_victim_speakers','page_count_exclusions']},ensure_ascii=False))
