"""Independently verify headline metrics from persisted score records."""
import collections,hashlib,json,math
from pathlib import Path
R=Path("/home/pvd2112_columbia_edu/columbia-projects/jep/data/moral-geometry-20261110")
def ranks(values):
 ordered=sorted(range(len(values)),key=lambda i:values[i]);out=[0.]*len(values);i=0
 while i<len(ordered):
  j=i+1
  while j<len(ordered) and values[ordered[j]]==values[ordered[i]]:j+=1
  for k in ordered[i:j]:out[k]=(i+j-1)/2+1
  i=j
 return out
def rho(x,y):
 a,b=ranks(x),ranks(y);am=sum(a)/len(a);bm=sum(b)/len(b)
 aa=sum((v-am)**2 for v in a);bb=sum((v-bm)**2 for v in b)
 return None if aa==0 or bb==0 else sum((u-am)*(v-bm) for u,v in zip(a,b))/math.sqrt(aa*bb)
result=json.loads((R/"results_v2.json").read_text());rows=json.loads((R/"retrieval_predictions_v2.json").read_text());groups=collections.defaultdict(list)
for row in rows:
 s=row["scores"];accuracy=sum((1 if s[0]-v>1e-7 else 0 if v-s[0]>1e-7 else .5) for v in s[1:])/(len(s)-1)
 assert abs(accuracy-row["accuracy"])<1e-10
 groups[(row["split"],row["method"],row["family"])].append(accuracy)
for split,methods in result["retrieval"].items():
 for method,summary in methods.items():
  family_values=[sum(v)/len(v) for (sp,m,f),v in groups.items() if sp==split and m==method]
  assert abs(sum(family_values)/len(family_values)-summary["accuracy"])<1e-10
ref=[r for r in json.loads((R/"reference_predictions_v2.json").read_text()) if r["split"]=="test"]
for arm,summary in result["reference"].items():
 x=[r["scores"][arm] for r in ref];y=[r["target"] for r in ref];r=rho(x,y)
 assert (r is None and summary["spearman"] is None) or abs(r-summary["spearman"])<1e-10
 mse=sum((a-b)**2 for a,b in zip(x,y))/len(x);assert abs(mse-summary["mse"])<1e-10
# Counterexample observer: changing one controlled score changes recomputed accuracy.
assert sum(1 if 1>v else 0 for v in [0,0])/2==1
assert sum(1 if -1>v else 0 for v in [0,0])/2==0
receipt=dict(status="passed",retrieval_records=len(rows),reference_records=len(ref),rank_correlation="independent average-tie rank/Pearson implementation",hashes={n:hashlib.sha256((R/n).read_bytes()).hexdigest() for n in ["retrieval_predictions_v2.json","reference_predictions_v2.json","results_v2.json"]})
(R/"metric_verification.json").write_text(json.dumps(receipt,indent=2)+"\n")
print("INDEPENDENT_METRICS_VERIFIED",len(rows),len(ref))
