# Qwen evidence comparison: status and live access

Snapshot checked: **2026-10-25 6:40 p.m. America/New_York (22:40 UTC)**. **Training and test evaluation are complete; all ten native stages succeeded.**

This is a timestamped snapshot, not an automatically refreshing dashboard. The command below reads current scores directly from the GPU.

| Arm | Total epochs completed | State | Best validation Spearman | Test Spearman |
|---|---:|---|---:|---|
| Ratings → ratings | 9 | Finished; stopped on validation patience | 0.782575 (total epoch 4) | **0.788505** |
| Evidence → ratings | 12 | Finished; stopped on validation patience | 0.773647 (total epoch 7) | **0.783645** |

The evidence arm's last completed validation score is 0.756276 (total epoch 12).

On the common 2,620-comparison test set, evidence → ratings scored **0.004860 lower** than ratings → ratings. Evidence did not beat the control in this seed. Paired uncertainty is being checked; this point estimate alone does not establish a reliable detrimental effect.
Both arms include two initial epochs in the total count. Validation scores select checkpoints; test scores are reported separately.

## Check the current run yourself

1. Open [the GPU in Google Cloud Console](https://console.cloud.google.com/compute/instancesDetail/zones/asia-northeast3-a/instances/jep-csts-format-20261021?project=mantra-477901) using the Columbia account with project access.
2. Click **SSH**.
3. Run the read-only command below. Rerun it whenever you want a fresh status.

```bash
sudo -u machina python3 - <<'PY'
from pathlib import Path
import datetime, json
r = Path("/home/machina/jep-csts-qwen-evidence-20261024")
s = json.loads((r / "qwen_evidence_results/initial/summary.json").read_text())
print("Checked UTC:", datetime.datetime.now(datetime.timezone.utc).isoformat())
print("Stage:", s.get("current_stage"), "| Status:", s.get("status"))
for arm in ("ratings", "evidence"):
    traces = {}
    for phase in ("pretrain", "ratings"):
        pattern = f"csts_qwen_evidence_{s['source_commit'][:8]}_{s['attempt']}_{arm}_{phase}/runs/*/*/artifacts/train/trace/trace.json"
        paths = list((r / "experiments").glob(pattern))
        if paths:
            traces[phase] = json.loads(paths[0].read_text())
    total = sum(len(t.get("epochs", [])) for t in traces.values())
    active = traces.get("ratings", traces.get("pretrain", {}))
    best = traces.get("ratings", {}).get("selected", {}).get("validation", {}).get("spearman")
    print(arm, "| total epochs completed:", total, "| status:", active.get("status", "not started"),
          "| best VALIDATION Spearman:", best, "| patience:", active.get("epochs_without_improvement"))
print("TEST scores:", s.get("live_scores") or "pending")
PY
```

From an authenticated local or Aether terminal, connect using:

```bash
gcloud compute ssh jep-csts-format-20261021 \
  --account=pvd2112@columbia.edu \
  --project=mantra-477901 \
  --zone=asia-northeast3-a \
  --tunnel-through-iap
```

Then run the same status command.

## Validation history during the rating phase

| Total epoch | Ratings → ratings | Evidence → ratings |
|---|---:|---:|
| 3 | 0.773639 | 0.741646 |
| 4 | 0.782575 | 0.768805 |
| 5 | 0.774013 | 0.761855 |
| 6 | 0.773039 | 0.772158 |
| 7 | 0.773551 | 0.773647 |
| 8 | 0.775654 | 0.773219 |
| 9 | 0.762140 | 0.764224 |
| 10 | — | 0.763423 |
| 11 | — | 0.762666 |
| 12 | — | 0.756276 |

## Source records

Training source: `cd720270a8978113be6f73af20c62ff2dde80762`. Attempt: `6b877324`.

GPU summary: `/home/machina/jep-csts-qwen-evidence-20261024/qwen_evidence_results/initial/summary.json`.

Live epoch traces are under `experiments/csts_qwen_evidence_cd720270_6b877324_*/runs/*/*/artifacts/train/trace/trace.json` inside that GPU checkout. The similarly named `training_outputs/csts_live_status.json` belongs to an older experiment and should not be used for this run.

Final report and test results will be collected into `training_outputs/csts_qwen_evidence_report.md` and `training_outputs/csts_qwen_evidence_results.json` after the comparison completes.
