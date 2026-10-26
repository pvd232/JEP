"""Export retained clean-test predictions and saved development candidates on CPU."""

import base64
import hashlib
import importlib.util
import json
import traceback
import zlib
from pathlib import Path

WORK = Path("/tmp/jep-tranche8-worker-20261026")
RUNTIME_SHA256 = "7ab0c10b3b36b7156e2a7d975d2633921b26d7b6697b645dac78550ee8c913f5"
TEST_EXPORT = "training_outputs/csts_qwen_selected_clean_test_export.json"
DEV_EXPORT = "training_outputs/csts_saved_development_candidates_export.json"
MODEL_SHA256 = "8805f9a7241e4e19ffc481341ebad6f1ddb6dd6ff04bbf710f9f0896469e34ff"
TEST_SHA256 = "2c8b6f2b62740c85c376eacd02ef222c2bfacdfe8df5f772a4dd7d52b6d38f1e"
DEV_SHA256 = "f01ec22320c590e381ede0b378895cdd241cd8079e06b18715bc13d2921a4273"


def runtime():
    for path in (WORK / "actions").glob("*/operator.py"):
        if not path.is_file() or path.is_symlink() or hashlib.sha256(path.read_bytes()).hexdigest() != RUNTIME_SHA256:
            continue
        spec = importlib.util.spec_from_file_location("reviewed_subset_runtime", path)
        if spec is None or spec.loader is None:
            break
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    raise RuntimeError("The reviewed task transport runtime is unavailable.")


def common(native):
    return native.preamble("a75fa36a8d709c25d7efccdd5c9dcdcfab3b3ec1") + r'''
import math,statistics

def ranks(values):
    order=sorted(range(len(values)),key=lambda i:values[i]);result=[0.0]*len(values);start=0
    while start<len(order):
        end=start+1
        while end<len(order) and values[order[end]]==values[order[start]]:end+=1
        rank=(start+1+end)/2
        for index in order[start:end]:result[index]=rank
        start=end
    return result

def metrics(rows,scores):
    observed=[scores[row['row_id']] for row in rows];targets=[row['target'] for row in rows]
    return {'spearman':statistics.correlation(ranks(observed),ranks(targets)),'mse_0_1':statistics.fmean((score-target)**2 for score,target in zip(observed,targets,strict=True))}

def checked_scores(path,rows,strict_caption=True):
    saved=json.loads(path.read_text());lookup={row['row_id']:row for row in saved}
    assert len(saved)==len(lookup)==len(rows) and set(lookup)=={row['row_id'] for row in rows}
    scores={}
    for row in rows:
        prediction=lookup[row['row_id']]
        if strict_caption:assert {key:value for key,value in prediction.items() if key!='prediction'}==row
        else:
            for key in ('rating','target','condition','pair_id','group_id'):assert prediction[key]==row[key]
        value=float(prediction['prediction']);assert math.isfinite(value);scores[row['row_id']]=value
    return scores
'''


def subset_script(native):
    return common(native) + r'''
attempt=root/'answer_input_results/proposition_subset_v2'
summary=json.loads((attempt/'summary.json').read_text());assert summary['status']=='complete'
assert summary['source_commit']=='a75fa36a8d709c25d7efccdd5c9dcdcfab3b3ec1'
def artifact(record,stage,name,filename):return pathlib.Path(record['path']).parent/'artifacts'/stage/name/filename
prepared=next(record for record in summary['runs'] if record['name']=='prepare')
zero=next(record for record in summary['runs'] if record['name']=='epoch_zero')
fit=next(record for record in summary['runs'] if record['name']=='fit')
rows_path=artifact(prepared,'prepare','original_validation','original_validation.json')
rows=json.loads(rows_path.read_text());assert len(rows)==30
full=json.loads((parent/'csts_data/dev.json').read_text());lookup={row['row_id']:row for row in full}
assert all(lookup[row['row_id']]==row for row in rows)
paths={'frozen_answers':artifact(zero,'infer','predictions','predictions.json'),'adapted_answers':attempt/'adapted_original_predictions.json'}
scores={name:checked_scores(path,rows) for name,path in paths.items()}
study=json.loads((parent/'qwen_evidence_results/initial/summary.json').read_text())
native=next(record for record in study['runs'] if record['name']=='ratings_ratings')
baseline_path=artifact(native,'train','validation_predictions','predictions.json')
all_scores=checked_scores(baseline_path,full)
scores['saved_qwen']={row['row_id']:all_scores[row['row_id']] for row in rows}
model=artifact(fit,'train','model','model.pt');model_hash=digest(model)
assert model_hash=='1513a9dbdd4c77de1d1e8b4adebc7a111d62837ab56dafa60871ec0ec544dd52'
result={'phase':'subset_saved_predictions','status':'complete','source_commit':summary['source_commit'],'row_count':len(rows),'source_rows':rows,'original_validation_rows_sha256':'f01ec22320c590e381ede0b378895cdd241cd8079e06b18715bc13d2921a4273','subset_rows_sha256':digest(rows_path),'model_sha256':{'saved_qwen':'8805f9a7241e4e19ffc481341ebad6f1ddb6dd6ff04bbf710f9f0896469e34ff','frozen_answers':'8805f9a7241e4e19ffc481341ebad6f1ddb6dd6ff04bbf710f9f0896469e34ff','adapted_answers':model_hash},'source_prediction_files':{key:{'path':str(path),'sha256':digest(path)} for key,path in paths.items()},'scores':scores,'metrics':{name:metrics(rows,values) for name,values in scores.items()},'new_model_inference':False,'optimizer_updates':0,'gpu_used':False}
print(json.dumps(result,ensure_ascii=False,allow_nan=False))
'''


def main():
    try:
        module=runtime();directory=WORK/'subset30_scores_export';directory.mkdir(parents=True,exist_ok=True)
        native=module.native_helper(directory)
        result=native.remote(subset_script(native),directory,'retained_subset30_scores_export')
        content=(json.dumps(result,ensure_ascii=False,indent=2,allow_nan=False)+'\n').encode()
        path='training_outputs/csts_tranche8_subset30_saved_predictions.json'
        module.RESULT_PATH=path;module.publish(path,content)
        brief={key:value for key,value in result.items() if key not in {'source_rows','scores'}}
        brief.update(artifact_path=path,artifact_sha256=hashlib.sha256(content).hexdigest(),artifact_bytes=len(content))
    except Exception as error:
        brief={'phase':'subset_saved_predictions','status':'failed','exception_type':type(error).__name__,'error':'Retained CPU read failed; all original artifacts remain unchanged.'}
    print('OPERATOR_RESULT '+json.dumps(brief,allow_nan=False),flush=True)


if __name__=='__main__':main()
