"""Publish read-only GPU experiment snapshots to the existing GitHub result page."""

import argparse
import base64
import datetime as dt
import hashlib
import json
from pathlib import Path
import subprocess
import time

BRANCH = "experiment/csts-matched-baselines-20261026"
ENDPOINT = "repos/pvd232/JEP/contents/training_outputs/csts_overnight_status.md"
GPU_QUERY = r'''
import json
from pathlib import Path
roots = [Path('/home/machina/jep-csts-matched-baselines-20261026'),
         Path('/home/machina/jep-csts-evidence-attention-20261026')]
result = []
for root in roots:
 for dirname in ('matched_baseline_results', 'evidence_attention_results'):
  parent = root / dirname
  if not parent.exists(): continue
  for path in sorted(parent.glob('*/summary.json')):
   try:
    summary = json.loads(path.read_text())
    event_path = path.parent / 'events.jsonl'
    events = []
    if event_path.exists():
     for line in event_path.read_text().splitlines():
      try: events.append(json.loads(line))
      except json.JSONDecodeError: pass
    completed = [e for e in events if e.get('event','').endswith('head_complete') or e.get('event') in ('validation_result','validation_selection','test_result','study_complete','study_failed')]
    latest = {}
    for event in events:
     name = event.get('event','')
     if 'epoch' in name or 'progress' in name:
      latest[(name,str(event.get('arm','')),str(event.get('kind','')))] = event
    result.append({'root':str(root),'attempt':path.parent.name,'summary_path':str(path),
      'mtime':path.stat().st_mtime,'summary':summary,'completed':completed,
      'latest':list(latest.values()),'last_event':events[-1] if events else None})
   except (OSError,ValueError) as exc:
    result.append({'summary_path':str(path),'error':str(exc)})
print(json.dumps(result,allow_nan=False))
'''


def shell_quote(value):
    return "'" + value.replace("'", "'\\''") + "'"


def snapshot():
    remote = "sudo -n -u machina /home/machina/jep-format-env/bin/python -c " + shell_quote(GPU_QUERY)
    command = ["/Users/machina/google-cloud-sdk/bin/gcloud", "compute", "ssh",
        "jep-csts-format-20261021", "--account=pvd2112@columbia.edu",
        "--project=mantra-477901", "--zone=asia-northeast3-a", "--tunnel-through-iap",
        "--quiet", "--ssh-flag=-oBatchMode=yes", "--ssh-flag=-oConnectTimeout=15",
        "--command=" + remote]
    response = subprocess.run(command, capture_output=True, text=True, check=True, timeout=55)
    return json.loads(response.stdout)


def number(value):
    return "—" if value is None else f"{float(value):.6f}"


def render(records):
    now = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    lines = ["# JEP overnight experiments — live status", "", f"Published: **{now}**.", "",
        "| Comparator | Validation Spearman | Existing-test Spearman |",
        "|---|---:|---:|", "| Saved Qwen + LoRA | 0.782575 | 0.788505 |",
        "| Archived LLM pair judge | — | 0.802917 |", "",
        "Existing baseline predictions are reused. Scores below identify validation or test explicitly.", ""]
    if not records:
        lines += ["Deployment and preflight underway. No new score yet.", ""]
    for record in sorted(records, key=lambda x: x.get("mtime",0), reverse=True):
        if "error" in record:
            lines += [f"Snapshot unavailable: `{record['summary_path']}` — {record['error']}", ""]
            continue
        summary = record["summary"]
        lines += [f"## {record['attempt']}", "", f"Status: **{summary.get('status','unknown')}**.", "",
            f"Controller: `{record['summary_path']}`", "",
            f"Source: `{summary.get('source_commit','unrecorded')}`.", ""]
        stage = summary.get("in_flight")
        if stage: lines += [f"Current native stage: `{stage}`.", ""]
        if summary.get("error"): lines += [f"Failure: `{summary['error']}`. Attempt preserved.", ""]
        completed = {e.get("arm"):e for e in record["completed"] if e.get("event","").endswith("head_complete")}
        epochs = {e.get("arm"):e for e in record["latest"] if "epoch" in e.get("event","")}
        if completed or epochs:
            lines += ["| Arm | Validation Spearman | Validation MSE | Epoch | State |", "|---|---:|---:|---:|---|"]
            for arm in dict.fromkeys([*completed,*epochs]):
                e = completed.get(arm,epochs.get(arm,{}))
                metrics = e.get("validation",{})
                lines.append(f"| {arm} | {number(metrics.get('spearman'))} | {number(metrics.get('mse_0_1',metrics.get('mse')))} | {e.get('selected_epoch',e.get('epoch','—'))} | {'selected checkpoint' if arm in completed else 'latest epoch'} |")
            lines.append("")
        for e in record["completed"]:
            if e.get("event") == "validation_selection":
                lines += ["Frozen validation decision:", "", "```json", json.dumps(e,indent=2), "```", ""]
            if e.get("event") == "test_result":
                lines += [f"Existing-test **{e.get('arm')}**: Spearman **{number(e.get('spearman'))}**, MSE **{number(e.get('mse_0_1',e.get('mse')))}**.", ""]
        progress = [e for e in record["latest"] if "progress" in e.get("event","")]
        for e in progress[-3:]:
            lines += [f"Extraction `{e.get('split','')}/{e.get('kind','')}`: **{e.get('done','?')}/{e.get('total','?')}** occurrences; {float(e.get('seconds',0)):.0f} seconds elapsed.", ""]
        if summary.get("stop_reason"): lines += [f"Stop reason: `{summary['stop_reason']}`.", ""]
    lines += ["## Experiment records", "", "[Overnight plan](../plans/csts-overnight-20261026.md) · [Four correction heads](../plans/csts-tranche-5-matched-baselines.md) · [IPED source review](../plans/csts-iped-research-20261026.md)", "",
        "Scores are published independently of asynchronous VIPER cloud promotion. The hourly autonomous checks reconcile failures and continue reviewed, eligible work within the overnight budget.", ""]
    return "\n".join(lines)


def github_publish(markdown):
    gh = "/opt/homebrew/bin/gh"
    response = subprocess.run([gh,"api",ENDPOINT+"?ref="+BRANCH],capture_output=True,text=True,check=True,timeout=30)
    previous = json.loads(response.stdout)
    payload = {"message":"Update live overnight experiment scores", "branch":BRANCH,
        "sha":previous["sha"], "content":base64.b64encode(markdown.encode()).decode()}
    subprocess.run([gh,"api","--method","PUT",ENDPOINT,"--input","-"],input=json.dumps(payload),capture_output=True,text=True,check=True,timeout=30)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--once", action="store_true")
    parser.add_argument("--state", default="/tmp/csts-overnight-publisher-state.json")
    args = parser.parse_args()
    state_path = Path(args.state)
    try:
        state = json.loads(state_path.read_text()) if state_path.exists() else {}
    except (OSError, json.JSONDecodeError):
        state = {}
    deadline = dt.datetime(2026,10,26,13,15,tzinfo=dt.timezone.utc)
    while dt.datetime.now(dt.timezone.utc) < deadline:
        try:
            records = snapshot()
            completed = [(r.get("summary_path"),r.get("completed"),r.get("summary",{}).get("status"),r.get("summary",{}).get("in_flight")) for r in records]
            important = hashlib.sha256(json.dumps(completed,sort_keys=True).encode()).hexdigest()
            now = time.time()
            if important != state.get("important") or now-state.get("published_at",0) >= 300:
                github_publish(render(records))
                state = {"important":important,"published_at":now}
                temporary = state_path.with_suffix(".tmp")
                temporary.write_text(json.dumps(state))
                temporary.replace(state_path)
                print(json.dumps({"event":"status_published","attempts":len(records),"at":now}),flush=True)
        except Exception as error:
            print(json.dumps({"event":"publisher_error","type":type(error).__name__,"error":str(error)}),flush=True)
        if args.once: break
        time.sleep(45)


if __name__ == "__main__":
    main()
