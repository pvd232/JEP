"""Publish captured closed-book LLM predictions and independently verify metrics.

Inference happens through the authenticated CLI outside VIPER. This module
records that evidence, joins reference labels only in an evaluation worker,
and verifies MSE and Spearman through VIPER's independent metric worker.
"""
from __future__ import annotations
import argparse,hashlib,json,math,shutil
from pathlib import Path
from viper import api,execution
from viper.artifacts import StageArtifactRef
from viper.authoring import experiment,input,plan,replicate,run_artifact,stage,variant
from viper.config import BuildConfig,EvalConfig
from viper.metrics import FloatComparator,MetricDependency,measure
from viper.metrics import min as minimize
from viper.outputs import EvalOutputs,StageOutputs,output
from viper.references import GitFileRef
from viper.repository import read_source,resolve_root
from viper.runtime import CPUComputeSpec,LocalEnvSpec,observe_python_env
from viper.stages import StageContext,build,eval
from jep_pilot.loaders import load_bytes,load_json
from jep_pilot.metrics import evaluation_mse,evaluation_spearman

@build(config=BuildConfig)
def publish_capture(context:StageContext[BuildConfig])->None:
    for name in ('test','holdout','scores','manifest','evidence'):
        context.outputs[name].parent.mkdir(parents=True,exist_ok=True)
        context.outputs[name].write_bytes(context.inputs[name].read_bytes())

@eval(config=EvalConfig)
def evaluate_capture(context:StageContext[EvalConfig])->None:
    rows=load_json(context.inputs['test']);indices=load_json(context.inputs['holdout'])
    manifest=load_json(context.inputs['manifest']);scores=load_json(context.inputs['scores'])
    if indices!=list(range(len(rows))) or len(rows)!=2620 or manifest['n']!=len(rows):
        raise ValueError('Reserved comparison coverage differs')
    if hashlib.sha256(context.inputs['test'].read_bytes()).hexdigest()!=manifest['data_sha256']:
        raise ValueError('Dataset fingerprint differs from inference manifest')
    if manifest['model']!='gpt-6.1-sol' or manifest['reasoning_effort']!='max' or manifest['labels_provided_to_model'] is not False:
        raise ValueError('Inference protocol differs')
    by_id={}
    for item in scores:
        if set(item)!= {'row_id','score'} or item['row_id'] in by_id:raise ValueError('Malformed or duplicate prediction')
        score=item['score']
        if isinstance(score,bool) or not isinstance(score,(int,float)) or not math.isfinite(score) or not 1<=score<=5:
            raise ValueError('Prediction out of range')
        by_id[item['row_id']]=score
    if set(by_id)!={r['row_id'] for r in rows}:raise ValueError('Prediction IDs differ')
    joined=[dict(r,prediction=(by_id[r['row_id']]-1)/4) for r in rows]
    context.outputs['predictions'].parent.mkdir(parents=True,exist_ok=True)
    context.outputs['predictions'].write_text(json.dumps(joined,indent=2))

def main()->None:
    parser=argparse.ArgumentParser();parser.add_argument('--bundle',type=Path,required=True);args=parser.parse_args()
    root=resolve_root();source=read_source(root);trusted=frozenset({str(source.repository)})
    supplied=args.bundle.resolve();target=root/'csts_data/sol61_max';target.mkdir(parents=True,exist_ok=True)
    files={'test':'evaluation.json','holdout':'evaluation_indices.json','scores':'scores.json','manifest':'manifest.json','evidence':'evidence.zip'}
    for name in files.values():shutil.copyfile(supplied/name,target/name)
    env=LocalEnvSpec(compute=CPUComputeSpec(),lockfile=GitFileRef(repository=source.repository,commit=source.commit,path='llm_baseline_requirements.txt'),python_env=observe_python_env())
    receipts=[]
    def execute(label,stages,estimator):
        study=experiment(experiment_id=f'csts_sol61_max_20261021_{source.commit[:7]}_{label}',variants=(variant(label,stages=stages,estimator=estimator),),replicates=(replicate(seed=0),))
        result=execution.run(plan(experiment=study,source=source,env=env),timeout_seconds=1800,trusted_source_repositories=trusted)
        if result.status!='succeeded':raise RuntimeError(f'VIPER {label} failed: {result.path}')
        verified=api.verify_run(api.VerifyRunRequest(root=root,path=result.path,trusted_source_repositories=trusted))
        receipts.append({'phase':label,'path':str(result.path),'reference':result.reference.model_dump(mode='json'),'verified_measurements':verified.measurement_count})
        return result
    published=stage(publish_capture,stage_id='publish',inputs=tuple(input(name,path=f'csts_data/sol61_max/{filename}',data_role='eval') for name,filename in files.items()),outputs=StageOutputs(**{name:output(path=filename,loader=load_bytes if name=='evidence' else load_json,data_role='eval') for name,filename in files.items()}),reuse='never')
    captured=execute('publish',(published,),published.outputs['scores'])
    refs={name:run_artifact(captured.reference,StageArtifactRef(stage_id='publish',artifact_name=name),path='inputs/'+filename,data_role='eval') for name,filename in files.items()}
    dependency=(MetricDependency(source='artifact',name='predictions',data_role='eval'),);comparator=FloatComparator(mode='absolute',tolerance=1e-12)
    mse=measure(evaluation_mse,dependencies=dependency,comparator=comparator);rho=measure(evaluation_spearman,dependencies=dependency,comparator=comparator)
    evaluated=stage(evaluate_capture,stage_id='eval',eval_id='csts_existing_2620',inputs=tuple(input(name,source=refs[name]) for name in ('test','holdout','scores','manifest')),split_inputs=('holdout',),outputs=EvalOutputs(predictions=output(path='predictions.json',loader=load_json,data_role='eval')),metrics=(mse,rho),objective=minimize(mse),reuse='never')
    evaluated_run=execute('evaluate',(evaluated,),evaluated.outputs['predictions'])
    receipt={'source_commit':source.commit,'inference_execution':'external authenticated Codex CLI; raw capture published as evidence','metric_execution':'native VIPER evaluation and independent metric verification','runs':receipts}
    out=root/'training_outputs/csts_sol61_max_verification.json';out.parent.mkdir(exist_ok=True);out.write_text(json.dumps(receipt,indent=2));print(json.dumps(receipt),flush=True)
if __name__=='__main__':main()
