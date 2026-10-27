"""Reconstruct audited C-STS project partitions from pinned source CSVs."""
from __future__ import annotations
import argparse, csv, hashlib, json
from pathlib import Path
from source_partition import HASHES, REVISION, canonical, digest, partition

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
def write(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--source',type=Path,required=True);p.add_argument('--output',type=Path,required=True);args=p.parse_args()
 here=Path(__file__).resolve().parent;manifest=read(here/'manifest.json');raw={}
 assert manifest['source']['revision']==REVISION
 for name,expected in HASHES.items():
  file=args.source/f'csts_{name}_reannotated.csv'
  if sha(file)!=expected:raise ValueError(f'Pinned source hash mismatch: {name}')
  with file.open(newline='') as f:raw[name]=list(csv.DictReader(f))
 parts,original_manifest=partition(raw['train'],raw['validation'])
 assert original_manifest['overlapping_training_rows_removed']==2532
 test=[]
 for i,r in enumerate(raw['validation']):test.append(dict(row_id=f'evaluation_{i}',sentence1=r['sentence1'],sentence2=r['sentence2'],condition=r['condition'],rating=float(r['label']),pair_id=digest(json.dumps(sorted((canonical(r['sentence1']),canonical(r['sentence2'])))))))
 sources={'training':parts['train'],'validation':parts['dev'],'test':test}
 packages={'training':read(here/'training.labels.json'),'test':read(here/'test.labels.json'),'validation':read(here.parent/'csts-validation-audit-v4-2/labels.json')}
 output={}
 for split,rows in sources.items():
  records=packages[split]['labels'];labels={r['row_id']:r for r in records};assert len(labels)==len(records)==len(rows),(split,'coverage')
  assert set(labels)=={r['row_id'] for r in rows},split
  output[split]=[]
  for r in rows:
   l=labels[r['row_id']];assert float(l['original_rating'])==r['rating'],(r['row_id'],'source label')
   usable=l.get('usable_for_split',l['rating'] is not None)
   if not usable:continue
   rating=float(l['rating']);assert 1<=rating<=5
   assert l['pair_id']==r['pair_id']
   output[split].append(dict(row_id=r['row_id'],sentence1=r['sentence1'],sentence2=r['sentence2'],condition=r['condition'],rating=rating,target=(rating-1)/4,pair_id=r['pair_id'],group_id=l['group_id']))
 caps={split:{canonical(r[k]) for r in rows for k in ('sentence1','sentence2')} for split,rows in output.items()}
 for a,b in [('training','validation'),('training','test'),('validation','test')]:assert not caps[a]&caps[b],(a,b,'caption overlap')
 for split in ('training','validation'):
  original_caps={canonical(r[k]) for r in sources[split] for k in ('sentence1','sentence2')}
  assert not original_caps&caps['test'],(split,'restored test leakage')
 args.output.mkdir(parents=True,exist_ok=True)
 names={'training':'train.json','validation':'validation.json','test':'test.json'}
 result={}
 for split,rows in output.items():
  file=args.output/names[split];write(file,rows);actual=sha(file)
  assert actual==manifest['reconstructed_sha256'][split],(split,'reconstruction hash mismatch',actual)
  result[split]=dict(rows=len(rows),sha256=actual)
 for alias,original in manifest['legacy_filename_aliases'].items():(args.output/alias).write_bytes((args.output/original).read_bytes())
 write(args.output/'reconstruction_receipt.json',dict(passed=True,revision=REVISION,partitions=result,canonical_caption_overlap=0))
 print(json.dumps(dict(passed=True,partitions=result),indent=2))
if __name__=='__main__':main()
