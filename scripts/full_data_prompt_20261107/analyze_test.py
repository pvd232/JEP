"""Report validation/test scores and paired source-group bootstrap comparisons."""
from pathlib import Path
import csv,datetime as dt,json,statistics,time
import numpy as np
from scipy.stats import rankdata,spearmanr
ROOT=Path(__file__).resolve().parents[2]
OUT=Path("/home/peter_aetherlabs_live/jep-full-data-test-launch-20261108")
DEST=ROOT/"training_outputs/full_data_prompt_20261108"
deadline=time.monotonic()+7000
while not (OUT/"test-evaluation-complete.json").exists():
 if time.monotonic()>deadline:raise TimeoutError("Test capture has not completed")
 time.sleep(15)
complete=json.loads((OUT/"test-evaluation-complete.json").read_text())
records=[m for w in complete["workers"] for m in w["metrics"]]
assert len(records)==15 and len({m["trial_id"] for m in records})==15
records.sort(key=lambda r:(r["arm"],r["seed"]))
protocol=json.loads((OUT/"payload/protocol.json").read_text())
test=json.loads((OUT/"payload/test.json").read_text())
y=np.array([r["target"] for r in test],dtype=float)
predictions=np.array([[r["prediction"] for r in json.loads((OUT/"test_predictions"/m["trial_id"]/"predictions.json").read_text())] for m in records])
for i,m in enumerate(records):
 assert abs(spearmanr(y,predictions[i]).statistic-m["test"]["spearman"])<1e-12
 assert abs(np.mean((predictions[i]-y)**2)-m["test"]["mse_0_1"])<1e-12
groups=np.array([str(r["group_id"]) for r in test])
names=sorted(set(groups));assert len(names)==1222
group_rows=[np.flatnonzero(groups==name) for name in names]
rng=np.random.default_rng(610707)
draws=10000
boot_rho=np.empty((draws,15));boot_mse=np.empty_like(boot_rho)
errors=(predictions-y)**2
for draw in range(draws):
 selected=rng.integers(0,len(names),len(names))
 ids=np.concatenate([group_rows[g] for g in selected])
 yr=rankdata(y[ids]);yr-=yr.mean()
 xr=rankdata(predictions[:,ids],axis=1);xr-=xr.mean(axis=1,keepdims=True)
 boot_rho[draw]=(xr@yr)/np.sqrt(np.sum(xr*xr,axis=1)*np.sum(yr*yr))
 boot_mse[draw]=errors[:,ids].mean(axis=1)
 if (draw+1)%1000==0:print(json.dumps({"bootstrap_draws_done":draw+1,"total":draws}),flush=True)
assert np.isfinite(boot_rho).all() and np.isfinite(boot_mse).all()
arms=["A_condition_first","B_order_only","C_case_inspired"];seeds=[7,8,9,10,11]
index={(m["arm"],m["seed"]):i for i,m in enumerate(records)}
summary=[]
for arm in arms:
 items=[m for m in records if m["arm"]==arm]
 vals=[m["validation"]["spearman"] for m in items];tests=[m["test"]["spearman"] for m in items]
 summary.append({"arm":arm,"seeds":5,"validation_mean":statistics.mean(vals),"validation_sd":statistics.stdev(vals),
                 "test_mean":statistics.mean(tests),"test_sd":statistics.stdev(tests),
                 "validation_mse_mean":statistics.mean(m["validation"]["mse_0_1"] for m in items),
                 "test_mse_mean":statistics.mean(m["test"]["mse_0_1"] for m in items)})
contrasts={}
for label,left,right in [("B-A",arms[1],arms[0]),("C-A",arms[2],arms[0]),("C-B",arms[2],arms[1])]:
 li=[index[left,s] for s in seeds];ri=[index[right,s] for s in seeds]
 paired=[records[l]["test"]["spearman"]-records[r]["test"]["spearman"] for l,r in zip(li,ri)]
 samples=(boot_rho[:,li]-boot_rho[:,ri]).mean(axis=1)
 mse_samples=(boot_mse[:,li]-boot_mse[:,ri]).mean(axis=1)
 contrasts[label]={"per_seed":dict(zip(map(str,seeds),paired)),"mean":statistics.mean(paired),
   "sample_sd":statistics.stdev(paired),"median":statistics.median(paired),"range":[min(paired),max(paired)],
   "positive_pairs":sum(d>0 for d in paired),"test_group_interval_95":np.quantile(samples,[.025,.975]).tolist(),
   "primary_two_comparison_interval_97_5":np.quantile(samples,[.0125,.9875]).tolist() if label in ["B-A","C-A"] else None,
   "mse_difference_interval_95":np.quantile(mse_samples,[.025,.975]).tolist()}
result={"status":"test_and_validation_complete","rows":{"validation":1576,"test":2430,"test_groups":1222},
 "source_commit":json.loads((OUT/"evaluation-source.json").read_text())["source_commit"],
 "checkpoint_selection":"validation_only_frozen_before_test","summary":summary,"per_trial":records,"contrasts":contrasts,
 "bootstrap":{"draws":10000,"seed":610707,"resampling":"same source groups across all 15 models in each draw",
              "interpretation":"Intervals conditional on the trained checkpoints; training-seed variation reported separately."},
 "test_status":"previously_examined_exploratory","completed_utc":dt.datetime.now(dt.timezone.utc).isoformat()}
(DEST/"test_and_validation.json").write_text(json.dumps(result,indent=2)+"\n")
fields=["arm","seed","validation_spearman","test_spearman","validation_mse_0_1","test_mse_0_1","selected_epoch","completed_epochs","training_updates","test_scoring_seconds"]
with (DEST/"test_and_validation.csv").open("w",newline="") as f:
 w=csv.DictWriter(f,fieldnames=fields);w.writeheader()
 for m in records:w.writerow({"arm":m["arm"],"seed":m["seed"],"validation_spearman":m["validation"]["spearman"],
   "test_spearman":m["test"]["spearman"],"validation_mse_0_1":m["validation"]["mse_0_1"],
   "test_mse_0_1":m["test"]["mse_0_1"],"selected_epoch":m["selected_epoch"],"completed_epochs":m["completed_epochs"],
   "training_updates":190*m["completed_epochs"],"test_scoring_seconds":m["scoring_seconds"]})
table=["| Prompt | Validation Spearman | Test Spearman |","| --- | ---: | ---: |"]
for s in summary:table.append(f'| {s["arm"]} | {s["validation_mean"]:.6f} ± {s["validation_sd"]:.6f} | {s["test_mean"]:.6f} ± {s["test_sd"]:.6f} |')
lines=["# Test and validation results","", "Mean ± sample SD across the same five paired seeds. Validation selected every checkpoint before test inference.","",*table,"",
 "Validation: 1,576 comparisons. Test: 2,430 comparisons in 1,222 source groups.","",
 "| Test contrast | Mean paired difference | Positive seed pairs | Conditional 95% group-bootstrap interval |",
 "| --- | ---: | ---: | --- |"]
for label,c in contrasts.items():lines.append(f'| {label} | {c["mean"]:+.6f} | {c["positive_pairs"]}/5 | [{c["test_group_interval_95"][0]:+.6f}, {c["test_group_interval_95"][1]:+.6f}] |')
lines+=["","Intervals use 10,000 shared source-group bootstrap draws (seed 610707), averaging paired within-seed differences. They condition on these checkpoints. The JSON also retains 97.5% intervals for the two primary contrasts. Five seed pairs provide limited information about training-population uncertainty.",
 "","This test partition was examined in earlier work. Treat the comparison as exploratory. No test scores were used to choose checkpoints or extend training.","",
 "[Per-trial scores](test_and_validation.csv) · [Full statistics](test_and_validation.json)",""]
(DEST/"test-results.md").write_text("\n".join(lines))
print(json.dumps({"test_and_validation":summary,"contrasts":contrasts}),flush=True)
