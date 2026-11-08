"""Offline collector regression tests; no VM, service or IAM mutations."""
import contextlib
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('keyless_collector', ROOT / 'scripts/full_data_prompt_20261107/collect_epochs.py')
collector = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(collector)


class KeylessCollectorTests(unittest.TestCase):
    """Account/manifest failures and observer interruptions must not clean up GPUs."""

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.account = 'dev-vm@pvd-dev-232.iam.gserviceaccount.com'
        self.assignment = {'instance_name': 'jep-test', 'instance_id': '123',
            'project': 'mantra-477901', 'zone': 'asia-northeast3-a', 'execution_id': 'b'*32}
        self.approval = {'user_execution_approved': True, 'source_commit': 'a'*40,
            'controller_account': self.account, 'assignments': {'worker1': self.assignment}}
        self.approval_path = self.root / 'approval.json'
        self.approval_path.write_text(json.dumps(self.approval))
        self.profile_path = self.root / 'profile.json'
        self.profile = {'paths': {'install_root': str(self.root), 'state_root': str(self.root/'state')},
            'job_identity': {'mode': 'attached_service_account','service_account_email':self.account},
            'resolved': {'project_environment': {'CLOUDSDK_CONFIG':str(self.root/'gcloud')}}}
        self.profile_path.write_text(json.dumps(self.profile))
        self.env = {'CLOUDSDK_CORE_ACCOUNT': self.account, 'CLOUDSDK_CONFIG':str(self.root/'gcloud'),
            'CLOUD_DEV_CONFIG':str(self.profile_path), 'CLOUDSDK_CORE_PROJECT':'mantra-477901'}
        self.receipt = {'workload_access_verified':True,'controller_account':self.account,
            'resource_project':'mantra-477901','manifest_sha256':hashlib.sha256(self.approval_path.read_bytes()).hexdigest(),
            'source_commit':'a'*40,'artifact_prefix':'gs://test-bucket/jep/'}
        self.args = SimpleNamespace(source='a'*40,max_hours=1,local=self.root,
            approval=self.approval,artifact_prefix=self.receipt['artifact_prefix'])

    def probe_response(self):
        return subprocess.CompletedProcess([],0,json.dumps(self.receipt),'')

    def test_verified_profile_and_exact_bytes_accepted(self):
        with patch.dict(os.environ,self.env,clear=True), patch.object(collector,'run',return_value=self.probe_response()) as run:
            profile, receipt = collector.load_keyless_context(self.profile_path,self.approval_path)
        self.assertEqual(receipt['controller_account'],self.account)
        self.assertIn('--workload',run.call_args.args[0])
        self.assertNotIn('auth',run.call_args.args[0])

    def test_direct_launch_outside_runner_rejected_without_cloud_call(self):
        with patch.dict(os.environ,{},clear=True), patch.object(collector,'run') as run:
            with self.assertRaises(PermissionError):
                collector.load_keyless_context(self.profile_path,self.approval_path)
        run.assert_not_called()

    def test_human_profile_rejected(self):
        self.profile['job_identity']['service_account_email']='person@example.test'
        self.profile_path.write_text(json.dumps(self.profile))
        with patch.dict(os.environ,self.env,clear=True), patch.object(collector,'run') as run:
            with self.assertRaises(PermissionError):collector.load_keyless_context(self.profile_path,self.approval_path)
        run.assert_not_called()

    def test_inherited_secret_override_rejected(self):
        for key in ('GOOGLE_APPLICATION_CREDENTIALS','CLOUDSDK_AUTH_ACCESS_TOKEN',
                    'CLOUDSDK_API_ENDPOINT_OVERRIDES_COMPUTE','GCE_METADATA_HOST','CLOUDSDK_ACTIVE_CONFIG_NAME'):
            with self.subTest(key=key), patch.dict(os.environ,{**self.env,key:'never-used'},clear=True), patch.object(collector,'run') as run:
                with self.assertRaises(PermissionError):collector.load_keyless_context(self.profile_path,self.approval_path)
                run.assert_not_called()

    def test_host_only_receipt_is_insufficient(self):
        self.receipt={'keyless_identity_verified':True}
        with patch.dict(os.environ,self.env,clear=True), patch.object(collector,'run',return_value=self.probe_response()):
            with self.assertRaises(PermissionError):collector.load_keyless_context(self.profile_path,self.approval_path)

    def test_failed_probe_never_runs_monitor_or_cleanup(self):
        result=subprocess.CompletedProcess([],1,'{"workload_access_verified":false}','TARGET_API_DENIED')
        with patch.dict(os.environ,self.env,clear=True), patch.object(collector,'run',return_value=result), \
                patch.object(collector,'monitor') as monitor,patch.object(collector,'cleanup') as cleanup:
            with self.assertRaises(RuntimeError):collector.load_keyless_context(self.profile_path,self.approval_path)
        monitor.assert_not_called();cleanup.assert_not_called()

    def test_wrong_instance_manifest_rejected(self):
        self.receipt['manifest_sha256']='f'*64
        with patch.dict(os.environ,self.env,clear=True),patch.object(collector,'run',return_value=self.probe_response()):
            with self.assertRaises(PermissionError):collector.load_keyless_context(self.profile_path,self.approval_path)

    def test_workload_project_override_rejected(self):
        with patch.dict(os.environ,{**self.env,'CLOUDSDK_CORE_PROJECT':'wrong-project'},clear=True), \
                patch.object(collector,'run',return_value=self.probe_response()):
            with self.assertRaises(PermissionError):collector.load_keyless_context(self.profile_path,self.approval_path)

    def test_approval_account_cannot_override_runtime(self):
        self.approval['controller_account']='person@example.test'
        self.approval_path.write_text(json.dumps(self.approval))
        self.receipt['manifest_sha256']=hashlib.sha256(self.approval_path.read_bytes()).hexdigest()
        with patch.dict(os.environ,self.env,clear=True),patch.object(collector,'run',return_value=self.probe_response()):
            with self.assertRaises(PermissionError):collector.load_keyless_context(self.profile_path,self.approval_path)

    def test_unexpected_access_error_does_not_stop_training(self):
        with patch.object(collector,'describe',side_effect=PermissionError('403')),patch.object(collector,'cleanup') as cleanup, \
                contextlib.redirect_stdout(io.StringIO()):
            with self.assertRaises(PermissionError):collector.monitor('worker1',self.args)
        cleanup.assert_not_called()
        result=json.loads((self.root/'worker1-cleanup.json').read_text())
        self.assertEqual(result['status'],'NO_LIFECYCLE_ACTION')

    def test_ssh_failure_does_not_stop_training(self):
        with patch.object(collector,'describe',return_value={'status':'RUNNING'}), \
                patch.object(collector,'read_worker',side_effect=RuntimeError('SSH unavailable')), \
                patch.object(collector,'cleanup') as cleanup,contextlib.redirect_stdout(io.StringIO()):
            with self.assertRaises(RuntimeError):collector.monitor('worker1',self.args)
        cleanup.assert_not_called()

    def test_interrupt_does_not_stop_training(self):
        with patch.object(collector,'describe',side_effect=KeyboardInterrupt),patch.object(collector,'cleanup') as cleanup, \
                contextlib.redirect_stdout(io.StringIO()):
            with self.assertRaises(KeyboardInterrupt):collector.monitor('worker1',self.args)
        cleanup.assert_not_called()

    def test_source_mismatch_does_not_stop_training(self):
        state={'source_commit':'z'*40,'lease':{'execution_id':'b'*32,'deadline_verified':True}}
        with patch.object(collector,'describe',return_value={'status':'RUNNING'}), \
                patch.object(collector,'read_worker',return_value={'state':state}), \
                patch.object(collector,'cleanup') as cleanup,contextlib.redirect_stdout(io.StringIO()):
            with self.assertRaises(ValueError):collector.monitor('worker1',self.args)
        cleanup.assert_not_called()

    def test_invalid_terminal_proof_does_not_stop_training(self):
        state={'source_commit':'a'*40,'status':'assigned_training_complete_test_not_opened',
               'lease':{'execution_id':'b'*32,'deadline_verified':True}}
        with patch.object(collector,'describe',return_value={'status':'RUNNING'}), \
                patch.object(collector,'read_worker',return_value={'state':state}), \
                patch.object(collector,'validate_completion',side_effect=ValueError('bad proof')), \
                patch.object(collector,'cleanup') as cleanup,contextlib.redirect_stdout(io.StringIO()):
            with self.assertRaises(ValueError):collector.monitor('worker1',self.args)
        cleanup.assert_not_called()

    def test_declared_terminal_failure_may_stop_owned_worker(self):
        state={'source_commit':'a'*40,'status':'failed_preserved',
               'lease':{'execution_id':'b'*32,'deadline_verified':True}}
        with patch.object(collector,'describe',return_value={'status':'RUNNING'}), \
                patch.object(collector,'read_worker',return_value={'state':state,'ready':[]}), \
                patch.object(collector,'cleanup',return_value={'status':'TERMINATED'}) as cleanup, \
                contextlib.redirect_stdout(io.StringIO()):
            with self.assertRaisesRegex(RuntimeError,'terminal failure'):collector.monitor('worker1',self.args)
        cleanup.assert_called_once_with(self.assignment,self.account,False,False)

    def test_explicit_delete_never_reaches_provider(self):
        with patch.object(collector,'run') as run,patch.object(collector,'describe') as describe:
            with self.assertRaises(PermissionError):collector.cleanup(self.assignment,self.account,True,True)
        run.assert_not_called();describe.assert_not_called()

    def test_already_stopped_worker_is_not_mutated(self):
        with patch.object(collector,'describe',return_value={'status':'TERMINATED'}), patch.object(collector,'run') as run:
            result=collector.cleanup(self.assignment,self.account,True)
        run.assert_not_called();self.assertTrue(result['recovery_disk_preserved'])

    def test_shutdown_not_reported_without_verified_stopped_state(self):
        with patch.object(collector,'describe',return_value={'status':'RUNNING'}), \
                patch.object(collector,'run',return_value=subprocess.CompletedProcess([],0,'','')):
            with self.assertRaises(RuntimeError):collector.cleanup(self.assignment,self.account,True)

    def test_artifact_outside_prefix_never_downloaded(self):
        with patch.object(collector.subprocess,'Popen') as process:
            with self.assertRaises(PermissionError):
                collector.verify_cloud_archive('gs://other/private',{},self.assignment,self.account,'gs://test-bucket/jep/')
        process.assert_not_called()

    def test_duplicate_local_controller_cannot_acquire_instance(self):
        assignments={'worker1':self.assignment}
        with collector.controller_locks(self.profile,assignments):
            with self.assertRaises(RuntimeError):
                with collector.controller_locks(self.profile,assignments):pass
        with collector.controller_locks(self.profile,assignments):pass

    def test_lock_is_per_instance_not_manifest_label(self):
        with collector.controller_locks(self.profile,{'worker1':self.assignment}):
            with self.assertRaises(RuntimeError):
                with collector.controller_locks(self.profile,{'worker2':self.assignment}):pass

    def test_main_defaults_to_observation(self):
        argv=['collector','--source','a'*40,'--local',str(self.root),'--approval',str(self.approval_path),'--profile',str(self.profile_path)]
        with patch.object(sys,'argv',argv),patch.object(collector,'load_keyless_context',return_value=(self.profile,self.receipt)), \
                patch.object(collector,'describe',return_value={'status':'RUNNING'}), \
                patch.object(collector,'monitor') as monitor,patch.object(collector,'cleanup') as cleanup, \
                contextlib.redirect_stdout(io.StringIO()) as output:
            collector.main()
        self.assertEqual(json.loads(output.getvalue())['mode'],'READ_ONLY')
        monitor.assert_not_called();cleanup.assert_not_called()

    def test_deleted_disk_option_is_not_an_entrypoint(self):
        with patch.object(sys,'argv',['collector','--delete-verified-disks']),contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit):collector.main()

    def test_inherited_approval_not_rewritten(self):
        before=self.approval_path.read_bytes()
        with patch.dict(os.environ,self.env,clear=True),patch.object(collector,'run',return_value=self.probe_response()):
            collector.load_keyless_context(self.profile_path,self.approval_path)
        self.assertEqual(before,self.approval_path.read_bytes())


if __name__=='__main__':unittest.main()
