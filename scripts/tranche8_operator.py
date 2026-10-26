"""Read the retained 60-pair diagnostic and a bounded failed-fit traceback."""

import argparse
import hashlib
import importlib.util
import json
import re
from pathlib import Path

WORK = Path("/tmp/jep-tranche8-worker-20261026")
RUNTIME_SHA256 = "12ff5d29b032b354e6fee48493a42691e0d96729774397046e4296918492f8b6"


def runtime():
    for path in (WORK / "actions").glob("*/operator.py"):
        if path.is_file() and not path.is_symlink() and hashlib.sha256(path.read_bytes()).hexdigest() == RUNTIME_SHA256:
            spec = importlib.util.spec_from_file_location("reviewed_subset_runtime", path)
            if spec is None or spec.loader is None:
                break
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            return module
    raise RuntimeError("The reviewed subset runtime is unavailable.")


def diagnostic_script(native, commit):
    return native.preamble(commit) + r'''
import re
def read(path):
 return json.loads(path.read_text())
def redact(text):
 text=re.sub(r'(?:\bsk-[A-Za-z0-9_-]{16,}|\bgh[pousr]_[A-Za-z0-9_]{16,}|\bgithub_pat_[A-Za-z0-9_]{16,}|\bhf_[A-Za-z0-9_]{16,}|\bya29\.[A-Za-z0-9._-]{16,}|\bBearer\s+[A-Za-z0-9._~+/-]{16,})','[REDACTED]',text,flags=re.I)
 return re.sub(r'(?im)^.*(?:authorization|api[_-]?key|access[_-]?token|refresh[_-]?token|password)\s*[:=].*$','[REDACTED credential assignment]',text)
sample=root/'answer_input_results/source_sample_v1'
rows=read(sample/'source_pairs.json')
predictions=read(sample/'predictions.json')
audited=read(sample/'audited_records.json')
arms=('saved_qwen_sample','old_spans','checked_generated_v1')
assert len(rows)==60 and len({row['row_id'] for row in rows})==60
lookups={arm:{row['row_id']:row['prediction'] for row in predictions[arm]} for arm in arms}
assert all(set(lookup)=={row['row_id'] for row in rows} for lookup in lookups.values())
occurrences={}
for record in audited:
 for occurrence in record['source_occurrences']:
  key=(occurrence['row_id'],occurrence['side']);assert key not in occurrences;occurrences[key]=record
pairs=[]
for row in rows:
 sides=[occurrences[(row['row_id'],side)] for side in ('sentence1','sentence2')]
 pairs.append({**row,'predictions':{arm:lookups[arm][row['row_id']] for arm in arms},'answer_ids':[record['id'] for record in sides],'old_answers':[record['old_record'].get('answer','') for record in sides],'new_answers':[record['generated_v1_record'].get('answer','') for record in sides],'replacement_status':{arm:[record['selected_inputs'][arm]['uses_answer'] for record in sides] for arm in arms[1:]},'generated_status':[record['generated_v1_record']['status'] for record in sides],'generated_passes_fidelity':[record['generated_v1_passes_blind_fidelity'] for record in sides]})
subset=root/'answer_input_results/proposition_subset_v1'
summary=read(subset/'summary.json') if (subset/'summary.json').exists() else {}
assert not summary or summary.get('source_commit')==commit
supervisor=root/'answer_input_results/supervisors/proposition_subset_v1'
logs={}
for name in ('native.stderr','native.stdout'):
 path=supervisor/name
 if path.is_file():
  with path.open('rb') as stream:
   stream.seek(max(0,path.stat().st_size-12000));text=stream.read(12000).decode(errors='replace')
  logs[name]=redact(text)
result={'phase':'retained_pair_diagnostics','status':'complete','source_commit':commit,'pairs':pairs,'sample_metrics':read(sample/'result.json').get('metrics',{}),'sample_file_sha256':{name:digest(sample/name) for name in ('source_pairs.json','predictions.json','audited_records.json')},'subset':{'status':summary.get('status'),'error':redact(str(summary.get('error','')))[:2000],'epoch_zero_metrics':summary.get('epoch_zero',{}).get('metrics',{}),'fit_tracebacks':logs},'model_or_capture_changes':False,'training_started_by_diagnostic':False}
assert len(json.dumps(result,ensure_ascii=False).encode())<160000,'Diagnostic payload exceeds safe public status budget.'
print(json.dumps(result,ensure_ascii=False,allow_nan=False))
'''


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-commit", required=True)
    args = parser.parse_args()
    if re.fullmatch(r"[0-9a-f]{40}", args.source_commit) is None:
        parser.error("Use a complete immutable native source commit.")
    try:
        module = runtime()
        directory = WORK / "pair_diagnostics" / args.source_commit
        directory.mkdir(parents=True, exist_ok=True)
        native = module.native_helper(directory)
        result = native.remote(diagnostic_script(native, args.source_commit), directory, "retained_pair_diagnostics")
    except Exception:
        result = {"phase": "retained_pair_diagnostics", "status": "failed", "error": "Read-only diagnostic failed; all retained model and capture artifacts remain unchanged."}
    print("OPERATOR_RESULT " + json.dumps(result, ensure_ascii=False, allow_nan=False), flush=True)


if __name__ == "__main__":
    main()
