"""Offline tests; never call Google, read credentials or change GPU resources."""
import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

P = Path(__file__).resolve().parents[1] / 'tools/admin_columbia_mantra_access.py'
spec=importlib.util.spec_from_file_location('bootstrap',P)
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)


def worker():
    return {'name':'jep-full-prompt-test','id':'123','zone':'zones/asia-east1-b',
            'status':'RUNNING','labels':{'task':m.TASK},
            'serviceAccounts':[{'email':m.WORKER_SA}],
            'metadata':{'fingerprint':'fp','items':[{'key':'startup-script','value':'unchanged'},
                        {'key':'ssh-keys','value':'other:ssh-ed25519 old other\n'}]}}

class Tests(unittest.TestCase):
    def test_scoped_live_workers(self):
        other=worker();other['labels']['task']='different'
        stopped=worker();stopped['status']='TERMINATED'
        self.assertEqual(len(m.select_workers([other,stopped,worker()],{})),1)
    def test_no_worker_is_not_success(self):
        with self.assertRaises(ValueError):m.select_workers([],{})
    def test_maximum_two_workers(self):
        with self.assertRaises(ValueError):m.select_workers([worker(),worker(),worker()],{})
    def test_wrong_region_rejected(self):
        w=worker();w['zone']='zones/us-central1-a'
        with self.assertRaises(ValueError):m.select_workers([w],{})
    def test_wrong_name_rejected(self):
        w=worker();w['name']='unrelated-worker'
        with self.assertRaises(ValueError):m.select_workers([w],{})
    def test_wrong_service_account_rejected(self):
        w=worker();w['serviceAccounts'][0]['email']='different@example.test'
        with self.assertRaises(ValueError):m.select_workers([w],{})
    def test_oslogin_preserved(self):
        with self.assertRaises(ValueError):m.select_workers([worker()],{'enable-oslogin':'TRUE'})
    def test_instance_metadata_override(self):
        w=worker();w['metadata']['items'].append({'key':'enable-oslogin','value':'FALSE'})
        self.assertEqual(len(m.select_workers([w],{'enable-oslogin':'TRUE'})),1)
    def test_append_preserves_prior_metadata_and_keys(self):
        old=worker()['metadata'];saved=copy.deepcopy(old)
        new,changed=m.append_public_key(old)
        self.assertTrue(changed);self.assertEqual(old,saved)
        before=m.metadata_values(old);after=m.metadata_values(new)
        self.assertEqual(before['startup-script'],after['startup-script'])
        self.assertTrue(after['ssh-keys'].startswith(before['ssh-keys']))
        self.assertEqual(new['fingerprint'],'fp')
    def test_public_key_append_idempotent(self):
        new,_=m.append_public_key(worker()['metadata'])
        again,changed=m.append_public_key(new)
        self.assertFalse(changed);self.assertEqual(again,new)
    def test_policy_etag_existing_members_preserved(self):
        old={'etag':'abc','bindings':[{'role':'roles/example','members':['user:owner@example.test']}],'version':1}
        new,changed=m.additive_policy(old,'roles/example')
        self.assertTrue(changed);self.assertEqual(new['etag'],'abc')
        self.assertEqual(old['bindings'][0]['members'],['user:owner@example.test'])
        self.assertIn('user:owner@example.test',new['bindings'][0]['members'])
    def test_condition_requires_version3_and_separate_binding(self):
        old={'etag':'abc','bindings':[{'role':'roles/example','members':[m.MEMBER]}],'version':1}
        cond={'title':'ssh','expression':'destination.port == 22'}
        new,_=m.additive_policy(old,'roles/example',cond)
        self.assertEqual(new['version'],3);self.assertEqual(len(new['bindings']),2)
    def test_policy_addition_idempotent(self):
        a,_=m.additive_policy({},'roles/example')
        b,changed=m.additive_policy(a,'roles/example')
        self.assertFalse(changed);self.assertEqual(a,b)
    def test_permissions_have_no_deletion_or_admin(self):
        all_perms=sum(m.ROLES.values(),[])
        self.assertFalse(any(p.endswith(('.delete','.setIamPolicy','.create')) for p in all_perms if p!='storage.objects.create'))
        self.assertNotIn('storage.objects.list',all_perms)
        self.assertNotIn('compute.projects.setCommonInstanceMetadata',all_perms)
        self.assertNotIn('compute.instances.setServiceAccount',all_perms)
    def test_plan_makes_no_grant_or_metadata_writes(self):
        with tempfile.TemporaryDirectory() as td:
            s=m.Setup(False,Path(td)/'receipt.json');calls=[]
            def cli(args):
                calls.append(args)
                if args[:3]==['compute','instances','list']:return [worker()]
                if args[:3]==['compute','project-info','describe']:return {'commonInstanceMetadata':{}}
                if args[:2]==['projects','describe']:return {'projectNumber':'123'}
                if args[:3]==['iam','roles','list']:return []
                self.fail('Unexpected write during plan '+str(args))
            def api(url,method='GET',body=None):
                self.assertEqual(method,'GET')
                return {'iamConfiguration':{'uniformBucketLevelAccess':{'enabled':True}}}
            result=type('R',(),{'returncode':0,'stdout':m.ADMIN+'\n'})()
            with patch.object(s,'cli',side_effect=cli),patch.object(s,'api',side_effect=api),patch.object(m.subprocess,'run',return_value=result):s.run()
            self.assertEqual(s.records[-1]['operation'],'PLAN_OK')
    def test_apply_has_no_vm_lifecycle_or_delete_calls(self):
        with tempfile.TemporaryDirectory() as td:
            s=m.Setup(True,Path(td)/'receipt.json');calls=[]
            w=worker();w['metadata'],_=m.append_public_key(w['metadata'])
            def cli(args):
                calls.append(args)
                if args[:3]==['compute','instances','list']:return [w]
                if args[:3]==['compute','project-info','describe']:return {'commonInstanceMetadata':{}}
                if args[:2]==['projects','describe']:return {'projectNumber':'123'}
                if args[:3]==['iam','roles','list']:return [{'name':'projects/x/roles/'+r,'includedPermissions':p,'stage':'GA'} for r,p in m.ROLES.items()]
                self.assertIn('add-iam-policy-binding',args);return {}
            result=type('R',(),{'returncode':0,'stdout':m.ADMIN+'\n'})()
            with patch.object(s,'cli',side_effect=cli),patch.object(s,'api',return_value={'iamConfiguration':{'uniformBucketLevelAccess':{'enabled':True}}}),patch.object(s,'worker',return_value=w),patch.object(s,'iap_binding'),patch.object(s,'storage_binding'),patch.object(m.subprocess,'run',return_value=result):s.run()
            self.assertEqual(s.records[-1]['operation'],'ACCESS_SETUP_APPLIED')
            self.assertFalse(any(x in ['stop','start','reset','delete','set-service-account','ssh'] for c in calls for x in c))
            self.assertFalse(s.records[-1]['runtime_ready'])
    def test_no_wrong_account(self):
        with tempfile.TemporaryDirectory() as td:
            s=m.Setup(True,Path(td)/'r.json')
            result=type('R',(),{'returncode':0,'stdout':'other@example.test\n'})()
            with patch.object(m.subprocess,'run',return_value=result),patch.object(s,'cli') as cli:
                with self.assertRaises(ValueError):s.run()
                cli.assert_not_called()

if __name__=='__main__': unittest.main()
