"""Native PyTorch/VIPER resume counterexamples on a tiny dropout model, no Qwen download."""
from __future__ import annotations
import json,tempfile,unittest,os
from pathlib import Path
from types import SimpleNamespace
import torch
from torch import nn
from torch.nn import functional as F
from csts_pilot.baseline_models import FitConfig, ScoreConfig, state_digest, validate_rows
from csts_pilot.baseline_stages import fit_neural, verify_test_inputs
from csts_pilot.convergence import reset_rng,file_sha256
from jep_pilot.loaders import load_model
from viper.resume import load_resume_state

DEVICE='cuda' if os.environ.get('JEP_NATIVE_TEST_CUDA')=='1' else 'cpu'

class Meter:
    def record(self,*args,**kwargs):pass

class Pairs:
    def __init__(self,split):
        gen=torch.Generator().manual_seed(3 if split=='training' else 9)
        self.a=torch.randn(6,4,generator=gen).to(DEVICE)
        self.b=torch.randn(6,4,generator=gen).to(DEVICE)
        self.rows=[{'row_id':f'{split}{i}','pair_id':f'{split}{i}','group_id':f'{split}{i}',
                    'sentence1':f'left {i}','sentence2':f'right {i}','condition':'aspect',
                    'target':i/5,'rating':1+4*i/5} for i in range(6)]
        self.nonpadding_tokens=0
    def scores(self,model,indices):
        self.nonpadding_tokens+=int(len(indices))*8
        return (F.normalize(model(self.a[indices]),dim=-1)*F.normalize(model(self.b[indices]),dim=-1)).sum(-1)

class NativeRuntimeTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.root=Path(self.tmp.name)
        self.pairs={s:Pairs(s) for s in ('training','validation')}
        self.inputs={s:self.root/f'{s}.json' for s in self.pairs}
        for s,p in self.inputs.items():p.write_text(json.dumps(self.pairs[s].rows))
        self.contract={s:{'sha256':file_sha256(p),'rows':6,'groups':6} for s,p in self.inputs.items()}
    def stage(self,name,max_epochs,start=0,parent=None):
        folder=self.root/name;folder.mkdir()
        outputs={k:folder/f'{k}.{suffix}' for k,suffix in [('model','pt'),('last_model','pt'),('resume_state','pt'),('trace','json'),('validation_predictions','json')]}
        inputs=dict(self.inputs)
        if parent:
            inputs.update({new:parent.outputs[old] for new,old in [('parent_model','model'),('parent_last_model','last_model'),('parent_resume','resume_state'),('parent_trace','trace'),('parent_validation_predictions','validation_predictions')]})
        cfg=FitConfig(kind='lora',device=DEVICE,embedding_dimension=4,seed=7,batch_size=2,microbatch_size=2,learning_rate=2e-5,max_epochs=max_epochs,start_epoch=start,patience=99,max_seconds=120,data_contract=self.contract,trial_id='A_condition_first_seed7',prompt_template='Instruct: {condition}\nQuery: {passage}')
        ctx=SimpleNamespace(config=cfg,inputs=inputs,outputs=outputs,metrics={k:Meter() for k in ('training_objective','validation_mse','validation_spearman')},numpy_generators={})
        reset_rng(7)
        model=nn.Sequential(nn.Linear(4,4,bias=False),nn.Dropout(.05)).to(DEVICE)
        return ctx,model
    def run_stage(self,c,m):
        fit_neural(c,m,Pairs('training'),Pairs('validation'))
        return load_model(c.outputs['last_model'])
    def test_segmented_resume_equals_uninterrupted_with_dropout(self):
        whole,m=self.stage('whole',2);a=self.run_stage(whole,m)
        first,m=self.stage('first',1);self.run_stage(first,m)
        second,m=self.stage('second',2,1,first);b=self.run_stage(second,m)
        self.assertEqual(state_digest(a['state']),state_digest(b['state']))
        x=load_resume_state(whole.outputs['resume_state']);y=load_resume_state(second.outputs['resume_state'])
        self.assertEqual(x.optimizer_state['scheduler'],y.optimizer_state['scheduler'])
        self.assertTrue(torch.equal(x.dataloader.state_dict['generator_state'],y.dataloader.state_dict['generator_state']))
        self.assertEqual(x.main_process_rng,y.main_process_rng)
        ox=x.optimizer_state['optimizer']['state'];oy=y.optimizer_state['optimizer']['state']
        self.assertEqual(ox.keys(),oy.keys())
        for p in ox:
            for k in ox[p]:self.assertTrue(torch.equal(ox[p][k],oy[p][k]),(p,k))
        tx=json.loads(whole.outputs['trace'].read_text());ty=json.loads(second.outputs['trace'].read_text())
        self.assertEqual([e['batch_order_sha256'] for e in tx['epochs']],[e['batch_order_sha256'] for e in ty['epochs']])
    def test_scientifically_stopped_parent_cannot_resume(self):
        first,m=self.stage('first',1);self.run_stage(first,m)
        d=json.loads(first.outputs['trace'].read_text());d['stop_reason']='validation_patience';first.outputs['trace'].write_text(json.dumps(d))
        second,m=self.stage('second',2,1,first)
        with self.assertRaisesRegex(ValueError,'scientifically stopped'):self.run_stage(second,m)
    def test_stale_selected_predictions_cannot_resume(self):
        first,m=self.stage('first',1);self.run_stage(first,m)
        first.outputs['validation_predictions'].write_text('[]')
        second,m=self.stage('second',2,1,first)
        with self.assertRaisesRegex(ValueError,'generation'):self.run_stage(second,m)
    def test_wrong_seed_checkpoint_rejected_before_test_deserialization(self):
        first,m=self.stage('first',1);self.run_stage(first,m)
        model_sha=file_sha256(first.outputs['model'])
        selection=self.root/'selection.json';selection.write_text(json.dumps({'status':'checkpoints_frozen','candidates':{'lora':{'sha256':model_sha}}}))
        test=self.root/'test.json';test.write_text('not json: must not be parsed')
        config=ScoreConfig(kind='lora',device=DEVICE,embedding_dimension=4,expected_seed=8,model_sha256=model_sha,selection_sha256=file_sha256(selection),test_sha256=file_sha256(test),prompt_template=first.config.prompt_template)
        context=SimpleNamespace(config=config,inputs={'selection':selection,'model':first.outputs['model'],'test':test})
        with self.assertRaisesRegex(ValueError,'different seed'):verify_test_inputs(context)
    def test_nan_historical_label_is_rejected(self):
        row=dict(self.pairs['training'].rows[0]);row['rating']=float('nan')
        with self.assertRaises(ValueError):validate_rows([row])

if __name__=='__main__':unittest.main(verbosity=2)
