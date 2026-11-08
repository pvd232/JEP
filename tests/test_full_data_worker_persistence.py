"""Local persistence fault injections, not claims of cloud-transport verification."""
import json,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
import csts_pilot.full_data_prompt_worker as worker

class WorkerPersistenceTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name);self.out=self.root/'baseline_results/w1';self.out.mkdir(parents=True)
        self.file=self.root/'artifact.pt';self.file.write_bytes(b'valid checkpoint bytes')
        self.state={'worker':'worker1','source_commit':'a'*40,'protocol_sha256':'b'*64,'lease':{'execution_id':'d'*32,'instance_id':'123'}}
    def test_atomic_reject_nan_preserves_last_record(self):
        p=self.out/'state.json';worker.atomic_json(p,{'status':'valid'})
        with self.assertRaises(ValueError):worker.atomic_json(p,{'broken':float('nan')})
        self.assertEqual(json.loads(p.read_text()),{'status':'valid'})
    def execute(self,wrong=False):
        original=worker.atomic_json
        def hook(path,obj):
            original(path,obj)
            if path.name=='ready.json':
                original(path.parent/'ack.json',{'generation':obj['generation'],'source_commit':obj['source_commit'],
                    'archive_sha256':'c'*64 if wrong else obj['archive_sha256'],'cloud_roundtrip_verified':True,
                    'execution_id':obj['execution_id'],'instance_id':obj['instance_id']})
        with patch.object(worker,'atomic_json',hook):
            worker.publish_generation(self.root,self.out,'epoch1',{},self.state,[self.file])
    def test_verified_exact_generation_advances(self):
        self.execute()
        p=json.loads((self.out/'verified-cloud-generation.json').read_text())
        self.assertEqual(p['generation'],'epoch1')
        self.assertTrue(p['cloud_roundtrip_verified'])
    def test_ack_for_different_bytes_rejected(self):
        with self.assertRaisesRegex(ValueError,'acknowledgment'):self.execute(wrong=True)
        self.assertFalse((self.out/'verified-cloud-generation.json').exists())
    def test_changed_archive_cannot_reuse_ack(self):
        self.execute()
        (self.out/'transfer/epoch1/native.tar').write_bytes(b'corrupted')
        with self.assertRaisesRegex(ValueError,'archive changed'):
            worker.publish_generation(self.root,self.out,'epoch1',{},self.state,[])
    def test_symlink_does_not_enter_generation(self):
        link=self.root/'bad-link';link.symlink_to(self.file)
        with self.assertRaisesRegex(ValueError,'symlinks'):
            worker.publish_generation(self.root,self.out,'epoch1',{},self.state,[link])
    def test_missing_artifact_stops_before_ready(self):
        with self.assertRaises(ValueError):
            worker.publish_generation(self.root,self.out,'epoch1',{},self.state,[self.root/'missing'])
        self.assertFalse((self.out/'transfer/epoch1/ready.json').exists())

if __name__=='__main__':unittest.main()
