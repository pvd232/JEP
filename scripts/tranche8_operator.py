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


def test_script(native):
    return common(native) + f"expected_model={MODEL_SHA256!r};expected_rows={TEST_SHA256!r}\n" + r'''
source=parent/'csts_data/evaluation.json';assert digest(source)==expected_rows
rows=json.loads(source.read_text());assert len(rows)==2620
study=json.loads((parent/'qwen_evidence_results/initial/summary.json').read_text())
record=next(item for item in study['runs'] if item['name']=='ratings_ratings');assert record['status']=='succeeded'
run=pathlib.Path(record['path']).parent
model=run/'artifacts/train/model/model.pt';assert digest(model)==expected_model
predictions=parent/'qwen_evidence_results/initial/ratings_predictions.json'
if not predictions.is_file():
    test_record=next(item for item in study['runs'] if item['name']=='predict_ratings')
    predictions=pathlib.Path(test_record['path']).parent/'artifacts/predict/predictions/predictions.json'
scores=checked_scores(predictions,rows)
result={'phase':'selected_clean_test_export','status':'complete','row_count':len(rows),'source_model_sha256':expected_model,'original_rows_sha256':expected_rows,'source_predictions_sha256':digest(predictions),'source_predictions_path':str(predictions),'source_groups':len({row['group_id'] for row in rows}),'caption_pairs':len({row['pair_id'] for row in rows}),'metrics':metrics(rows,scores),'source_rows':rows,'scores':scores,'original_labels_preserved':True,'new_model_inference':False,'optimizer_updates':0,'gpu_used':False}
print(json.dumps(result,ensure_ascii=False,allow_nan=False))
'''


def candidates_script(native):
    return common(native) + f"expected_rows={DEV_SHA256!r}\n" + r'''
source=parent/'csts_data/dev.json';assert digest(source)==expected_rows
rows=json.loads(source.read_text());assert len(rows)==1830
homes=sorted(path for path in pathlib.Path('/home/machina').glob('jep*') if path.is_dir() and ('csts' in path.name or 'tranche' in path.name))
paths=[]
for home in homes:
    paths.extend(home.glob('experiments/*/runs/*/*/artifacts/train/*validation_predictions/predictions.json'))
# Current two selected Qwen arms first; preserve distinct retained candidates afterward.
paths=sorted(set(paths),key=lambda path:('qwen_evidence_cd720270_6b877324' not in str(path),str(path)))
entries=[];score_maps={};seen_models={};unmatched=[]
for path in paths:
    try:
        scores=checked_scores(path,rows,strict_caption=False)
    except (AssertionError,KeyError,TypeError,ValueError):
        unmatched.append(str(path));continue
    prediction_hash=digest(path)
    train=path.parent.parent
    model=train/'model/model.pt';trace=train/'trace/trace.json'
    selected={}
    if trace.is_file():
        value=json.loads(trace.read_text());selected=value.get('selected',{})
    model_hash=selected.get('sha256')
    if model.is_file():
        key=str(model.resolve())
        if key not in seen_models:seen_models[key]=digest(model)
        model_hash=seen_models[key]
    entry={'source_predictions_path':str(path),'source_predictions_sha256':prediction_hash,'model_path':str(model) if model.is_file() else None,'model_sha256':model_hash,'rows':len(scores),'metrics':metrics(rows,scores),'trace_selected':{key:value for key,value in selected.items() if key in {'epoch','step','sha256','updates','actual_updates'}},'scores_key':prediction_hash}
    entries.append(entry)
    if len(score_maps)<48 or prediction_hash in score_maps:score_maps[prediction_hash]=scores
    else:entry['scores_key']=None
summary_paths=[]
for home in homes:
    for pattern in ('*_results/summary.json','*_results/*/summary.json','*_results/*/selection.json'):
        for path in home.glob(pattern):summary_paths.append(str(path))
result={'phase':'saved_development_candidates','status':'complete','source_rows_sha256':expected_rows,'rows':1830,'worktrees':[str(path) for path in homes],'candidate_count':len(entries),'candidates':entries,'score_maps':score_maps,'unmatched_prediction_files':unmatched,'retained_summary_paths':sorted(set(summary_paths)),'new_model_inference':False,'optimizer_updates':0,'gpu_used':False}
print(json.dumps(result,ensure_ascii=False,allow_nan=False))
'''


def publish_compressed(module,path,value):
    raw=(json.dumps(value,ensure_ascii=False,separators=(",",":"),allow_nan=False)+"\n").encode()
    envelope={'encoding':'zlib+base64','decoded_sha256':hashlib.sha256(raw).hexdigest(),'decoded_bytes':len(raw),'payload':base64.b64encode(zlib.compress(raw,9)).decode()}
    content=(json.dumps(envelope,indent=2)+"\n").encode()
    module.RESULT_PATH=path
    module.publish(path,content)
    return {'artifact_path':path,'artifact_sha256':hashlib.sha256(content).hexdigest(),'artifact_bytes':len(content),'decoded_sha256':envelope['decoded_sha256'],'decoded_bytes':len(raw)}


def main():
    phase='selected_clean_test_export'
    try:
        module=runtime();directory=WORK/'clean_test_and_candidates_export';directory.mkdir(parents=True,exist_ok=True)
        native=module.native_helper(directory)
        test=native.remote(test_script(native),directory,'retained_selected_clean_test_export')
        binding=publish_compressed(module,TEST_EXPORT,test)
        brief={key:value for key,value in test.items() if key not in {'source_rows','scores'}}
        brief.update(binding)
        print('OPERATOR_PROGRESS '+json.dumps(brief,allow_nan=False),flush=True)
        phase='saved_development_candidates'
        candidates=native.remote(candidates_script(native),directory,'retained_saved_development_candidates',timeout=240)
        candidates_binding=publish_compressed(module,DEV_EXPORT,candidates)
        result={'phase':'retained_cpu_exports','status':'complete','clean_test':brief,'development_candidates':{**candidates_binding,'candidate_count':candidates['candidate_count'],'score_maps':len(candidates['score_maps'])},'new_model_inference':False,'optimizer_updates':0,'gpu_used':False}
    except Exception as error:
        result={'phase':phase,'status':'failed','exception_type':type(error).__name__,'error':'Retained CPU export failed; all original model/data artifacts remain unchanged.'}
    print('OPERATOR_RESULT '+json.dumps(result,allow_nan=False),flush=True)


if __name__=='__main__':main()
