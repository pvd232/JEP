"""Reject duplicate/wrong worker assignments and absent independent deadlines."""
import copy,fcntl,tempfile,unittest
from pathlib import Path
from csts_pilot.full_data_prompt_lease import validate_assignment

class LeaseTests(unittest.TestCase):
    def setUp(self):
        self.now=1000000.
        self.assignment={'instance_name':'jep-full-prompt-spot-1-20261107','zone':'asia-northeast3-a','instance_id':'123','gpu_uuid':'GPU-test','execution_id':'a'*32,'deadline_epoch':self.now+3600}
        self.actual={'project':'mantra-477901','name':self.assignment['instance_name'],'zone':self.assignment['zone'],'id':'123'}
    def check(self,a=None,m=None,gpu='GPU-test',timer='default'):
        if timer=='default':timer=int((self.now+3600)*1e6)
        return validate_assignment('worker1',a or self.assignment,m or self.actual,gpu,timer,self.now)
    def test_valid_lease(self):self.assertTrue(self.check()['deadline_verified'])
    def test_different_host_cannot_reuse_worker(self):
        m=dict(self.actual,id='999')
        with self.assertRaises(PermissionError):self.check(m=m)
    def test_wrong_region_cannot_reuse_worker(self):
        m=dict(self.actual,zone='asia-northeast1-b')
        with self.assertRaises(PermissionError):self.check(m=m)
    def test_wrong_project_cannot_reuse_worker(self):
        m=dict(self.actual,project='company')
        with self.assertRaises(PermissionError):self.check(m=m)
    def test_wrong_gpu_cannot_reuse_lease(self):
        with self.assertRaises(PermissionError):self.check(gpu='GPU-other')
    def test_missing_timer_blocks_launch(self):
        with self.assertRaises(PermissionError):self.check(timer=None)
    def test_changed_timer_blocks_launch(self):
        with self.assertRaises(PermissionError):self.check(timer=int((self.now+7200)*1e6))
    def test_expired_deadline_blocks_launch(self):
        a=dict(self.assignment,deadline_epoch=self.now-1)
        with self.assertRaises(PermissionError):self.check(a=a)
    def test_unbounded_deadline_blocks_launch(self):
        a=dict(self.assignment,deadline_epoch=self.now+90000)
        with self.assertRaises(PermissionError):self.check(a=a)
    def test_missing_execution_identity_blocks(self):
        a=dict(self.assignment,execution_id='')
        with self.assertRaises(PermissionError):self.check(a=a)
    def test_hostwide_lock_excludes_second_worker_name(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'gpu-exclusive.lock'
            with p.open('a+') as a,p.open('a+') as b:
                fcntl.flock(a,fcntl.LOCK_EX|fcntl.LOCK_NB)
                with self.assertRaises(BlockingIOError):fcntl.flock(b,fcntl.LOCK_EX|fcntl.LOCK_NB)

if __name__=='__main__':unittest.main()
