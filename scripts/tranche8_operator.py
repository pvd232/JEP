"""Export retained selected-Qwen validation scores using CPU-only file reads."""

import hashlib
import importlib.util
import json
from pathlib import Path

WORK = Path("/tmp/jep-tranche8-worker-20261026")
RUNTIME_SHA256 = "7ab0c10b3b36b7156e2a7d975d2633921b26d7b6697b645dac78550ee8c913f5"
EXPORT = "training_outputs/csts_qwen_selected_validation_scores.json"
MODEL_SHA256 = "8805f9a7241e4e19ffc481341ebad6f1ddb6dd6ff04bbf710f9f0896469e34ff"
ROWS_SHA256 = "f01ec22320c590e381ede0b378895cdd241cd8079e06b18715bc13d2921a4273"


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


def export_script(native):
    return native.preamble("a75fa36a8d709c25d7efccdd5c9dcdcfab3b3ec1") + (
        "import math,statistics\n"
        f"expected_model={MODEL_SHA256!r};expected_rows={ROWS_SHA256!r}\n"
        "dev=parent/'csts_data/dev.json';assert digest(dev)==expected_rows\n"
        "rows=json.loads(dev.read_text());assert len(rows)==1830\n"
        "study=json.loads((parent/'qwen_evidence_results/initial/summary.json').read_text())\n"
        "record=next(item for item in study['runs'] if item['name']=='ratings_ratings')\n"
        "assert record['status']=='succeeded'\n"
        "run=pathlib.Path(record['path']).parent\n"
        "model=run/'artifacts/train/model/model.pt';assert digest(model)==expected_model\n"
        "predictions=run/'artifacts/train/validation_predictions/predictions.json'\n"
        "saved=json.loads(predictions.read_text());lookup={row['row_id']:row for row in saved}\n"
        "assert len(saved)==len(lookup)==1830 and set(lookup)=={row['row_id'] for row in rows}\n"
        "scores={}\n"
        "for row in rows:\n"
        " prediction=lookup[row['row_id']]\n"
        " assert {key:value for key,value in prediction.items() if key!='prediction'}==row\n"
        " value=float(prediction['prediction']);assert math.isfinite(value);scores[row['row_id']]=value\n"
        "def ranks(values):\n"
        " order=sorted(range(len(values)),key=lambda index:values[index]);result=[0.0]*len(values);start=0\n"
        " while start<len(order):\n"
        "  end=start+1\n"
        "  while end<len(order) and values[order[end]]==values[order[start]]:end+=1\n"
        "  rank=(start+1+end)/2\n"
        "  for index in order[start:end]:result[index]=rank\n"
        "  start=end\n"
        " return result\n"
        "observed=[scores[row['row_id']] for row in rows];targets=[row['target'] for row in rows]\n"
        "rho=statistics.correlation(ranks(observed),ranks(targets));assert abs(rho-0.7825746597420997)<1e-12\n"
        "mse=statistics.fmean((score-target)**2 for score,target in zip(observed,targets,strict=True))\n"
        "result={'phase':'selected_validation_scores','status':'complete','rows':1830,'source_model_sha256':expected_model,'original_validation_rows_sha256':expected_rows,'source_predictions_sha256':digest(predictions),'source_predictions_path':str(predictions),'source_groups':len({row['group_id'] for row in rows}),'caption_pairs':len({row['pair_id'] for row in rows}),'metrics':{'spearman':rho,'mse_0_1':mse},'scores':scores,'new_model_inference':False,'optimizer_updates':0,'gpu_used':False}\n"
        "assert len(json.dumps(result).encode())<160000\nprint(json.dumps(result,allow_nan=False))\n"
    )


def main():
    try:
        module = runtime()
        directory = WORK / "selected_validation_export"
        directory.mkdir(parents=True, exist_ok=True)
        native = module.native_helper(directory)
        result = native.remote(export_script(native), directory, "retained_selected_validation_export")
        content = (json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False) + "\n").encode()
        module.RESULT_PATH = EXPORT
        module.publish(EXPORT, content)
        result = {key: value for key, value in result.items() if key != "scores"}
        result.update(artifact_path=EXPORT, artifact_sha256=hashlib.sha256(content).hexdigest(), artifact_bytes=len(content))
    except Exception:
        result = {"phase": "selected_validation_scores", "status": "failed", "error": "Retained validation export failed; all source/model artifacts remain unchanged."}
    print("OPERATOR_RESULT " + json.dumps(result, allow_nan=False), flush=True)


if __name__ == "__main__":
    main()
