"""Offline cross-project identity checks; no cloud mutations or GPU access."""
import copy
import hashlib
import io
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock
import urllib.error

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'implementation'))
sys.path.insert(0, str(ROOT / 'tools'))
import project
import identity
import probe_identity


class WorkloadIdentityTests(unittest.TestCase):
    """Keep host, destination, identity, manifests and readiness distinguishable."""

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.host = json.loads((ROOT / 'profiles/columbia.json').read_text())
        for key in self.host['paths']:
            self.host['paths'][key] = str(self.root / key)
        self.host['resolved'] = {'node_bin_dir': '/usr/bin', 'bin_dir': '/usr/bin'}
        self.definition = json.loads((ROOT / 'projects/jep.json').read_text())
        self.account = self.host['job_identity']['service_account_email']
        self.manifest = self.root / 'assignment.json'
        self.assignment = {'project': 'mantra-477901', 'zone': 'asia-northeast3-a',
                           'instance_name': 'jep-test-worker', 'instance_id': '123'}
        self.approval = {'source_commit': 'a' * 40, 'user_execution_approved': True,
                         'controller_account': self.account,
                         'assignments': {'worker1': self.assignment}}
        self.save_manifest()
        self.definition['workload'] = {'resource_project': 'mantra-477901',
            'instance_manifest': str(self.manifest), 'artifact_prefix': 'gs://example-test/jep/task/'}
        self.profile = project.project_profile(self.host, self.definition)

    def save_manifest(self):
        self.manifest.write_text(json.dumps(self.approval))

    def test_host_identity_is_not_resource_project(self):
        env = project.project_environment(self.profile)
        self.assertEqual(self.profile['target']['gcp_project'], 'pvd-dev-232')
        self.assertEqual(env['CLOUDSDK_CORE_PROJECT'], 'mantra-477901')
        self.assertEqual(env['CLOUDSDK_CORE_ACCOUNT'], self.account)
        self.assertNotIn('CLOUDSDK_COMPUTE_ZONE', env)
        self.assertNotIn('CLOUDSDK_COMPUTE_REGION', env)
        self.assertEqual(env['CLOUDSDK_CORE_DISABLE_PROMPTS'], 'true')

    def test_legacy_profile_keeps_host_default(self):
        del self.definition['workload']
        old = project.project_profile(self.host, self.definition)
        self.assertEqual(project.project_environment(old)['CLOUDSDK_CORE_PROJECT'], 'pvd-dev-232')
        self.assertIsNone(project.workload_definition(old))

    def test_context_binds_exact_approved_bytes(self):
        ctx = project.workload_context(self.profile)
        self.assertEqual(ctx['manifest_sha256'], hashlib.sha256(self.manifest.read_bytes()).hexdigest())
        self.assertEqual(ctx['account'], self.account)
        self.assertEqual(ctx['approval']['assignments']['worker1']['instance_id'], '123')

    def test_no_configuration_mutation(self):
        before = copy.deepcopy(self.profile)
        project.project_environment(self.profile)
        project.workload_context(self.profile)
        self.assertEqual(before, self.profile)

    def test_explicit_human_account_rejected(self):
        self.approval['controller_account'] = 'person@example.test'
        self.save_manifest()
        with self.assertRaises(PermissionError):
            project.workload_context(self.profile)

    def test_no_implicit_launch_authorization(self):
        self.approval['user_execution_approved'] = False
        self.save_manifest()
        with self.assertRaises(PermissionError):
            project.workload_context(self.profile)

    def test_source_must_be_full_revision(self):
        for source in ('main', '', None, 123):
            self.approval['source_commit'] = source
            self.save_manifest()
            with self.subTest(source=source), self.assertRaises(PermissionError):
                project.workload_context(self.profile)

    def test_foreign_resource_rejected(self):
        self.assignment['project'] = 'unrelated-project'
        self.save_manifest()
        with self.assertRaises(ValueError):
            project.workload_context(self.profile)

    def test_immutable_id_required(self):
        for bad in ('', 'foo', None, 123):
            self.assignment['instance_id'] = bad
            self.save_manifest()
            with self.subTest(value=bad), self.assertRaises(ValueError):
                project.workload_context(self.profile)

    def test_duplicate_worker_identity_rejected(self):
        self.approval['assignments']['worker2'] = dict(self.assignment)
        self.save_manifest()
        with self.assertRaisesRegex(ValueError, 'share'):
            project.workload_context(self.profile)

    def test_missing_or_three_workers_rejected(self):
        for n in (0, 3):
            self.approval['assignments'] = {f'worker{i}': dict(self.assignment, instance_id=str(i)) for i in range(n)}
            self.save_manifest()
            with self.subTest(n=n), self.assertRaises(ValueError):
                project.workload_context(self.profile)

    def test_manifest_symlink_rejected(self):
        other = self.root / 'actual.json'; self.manifest.rename(other); self.manifest.symlink_to(other)
        with self.assertRaises(ValueError):
            project.workload_context(self.profile)

    def test_manifest_type_rejected(self):
        self.manifest.write_text('[]')
        with self.assertRaisesRegex(ValueError, 'JSON object'):
            project.workload_context(self.profile)

    def test_bad_workload_schema_rejected(self):
        for change in ({'token': 'do-not-save'}, {'resource_project': 'wrong/project'},
                       {'instance_manifest': '../x'}, {'artifact_prefix': 'gs://bucket/jep/../other/'},
                       {'artifact_prefix': 'gs://bucket/jep/*/'}):
            d = copy.deepcopy(self.definition); d['workload'].update(change)
            with self.subTest(change=change), self.assertRaises(ValueError):
                project.project_profile(self.host, d)

    def test_workload_requires_service_account(self):
        self.host['job_identity']['service_account_email'] = 'person@example.test'
        with self.assertRaises(ValueError):
            project.project_profile(self.host, self.definition)

    def test_inherited_credentials_and_target_overrides_removed(self):
        bad = {k: 'do-not-use' for k in project.CREDENTIAL_OVERRIDES}
        bad.update(CLOUDSDK_API_ENDPOINT_OVERRIDES_COMPUTE='https://example.test',
                   CLOUDSDK_AUTH_UNKNOWN_NEW_OVERRIDE='bad', CLOUDSDK_COMPUTE_ZONE='wrong-zone')
        with mock.patch.dict(os.environ, bad):
            result = project.project_environment(self.profile)
        self.assertFalse(any(k in result for k in bad))

    def test_explicit_runtime_override_rejected(self):
        self.profile['resolved']['project_environment']['GOOGLE_APPLICATION_CREDENTIALS'] = '/tmp/private.json'
        with self.assertRaises(RuntimeError):
            project.project_environment(self.profile)

    def test_explicit_profile_human_account_rejected(self):
        self.profile['resolved']['project_environment']['CLOUDSDK_CORE_ACCOUNT'] = 'person@example.test'
        with self.assertRaises(RuntimeError):
            project.project_environment(self.profile)

    def test_saved_sdk_override_rejected_without_printing_value(self):
        d = Path(self.profile['resolved']['project_environment']['CLOUDSDK_CONFIG']) / 'configurations'
        d.mkdir(parents=True)
        (d / 'config_default').write_text('[auth]\ncredential_file_override=/private/SECRET\n')
        with self.assertRaises(RuntimeError) as err:
            project.project_environment(self.profile)
        self.assertNotIn('SECRET', str(err.exception))

    def test_adc_rejected_without_reading_content(self):
        d = Path(self.profile['resolved']['project_environment']['CLOUDSDK_CONFIG']); d.mkdir(parents=True)
        (d / 'application_default_credentials.json').write_text('not parsed')
        with self.assertRaisesRegex(RuntimeError, 'local ADC'):
            project.project_environment(self.profile)

    def test_default_host_probe_does_not_claim_target_ready(self):
        with mock.patch.object(probe_identity, 'verify_host', return_value={
                'gcp_project': 'pvd-dev-232', 'vm': 'dev', 'service_account': self.account}), \
                mock.patch.object(probe_identity, 'compute_get', return_value=(200, {'name': 'dev'}, 3000)):
            result = probe_identity.probe(self.profile)
        self.assertEqual(result['scope'], 'host_only')
        self.assertFalse(result['workload_access_verified'])

    def test_host_success_target_403_not_ready(self):
        err = urllib.error.HTTPError('https://compute.googleapis.com', 403, 'Forbidden', {}, None)
        with mock.patch.object(probe_identity, 'probe', return_value={'keyless_identity_verified': True}), \
                mock.patch.object(probe_identity, 'compute_get', side_effect=err):
            result = probe_identity.probe_workload(self.profile)
        self.assertFalse(result['workload_access_verified'])
        self.assertFalse(result['execution_ready'])
        self.assertEqual(result['targets'][0]['required_permission'], 'compute.instances.get')

    def test_correct_instance_get_does_not_prove_ssh_or_storage(self):
        with mock.patch.object(probe_identity, 'probe', return_value={'keyless_identity_verified': True}), \
                mock.patch.object(probe_identity, 'compute_get', return_value=(200, {'name': 'jep-test-worker', 'id': '123'}, 100)):
            result = probe_identity.probe_workload(self.profile)
        self.assertTrue(result['workload_access_verified'])
        self.assertFalse(result['execution_ready'])
        self.assertIn('guest_SSH', result['not_checked'])
        self.assertNotIn('approval', result)

    def test_replacement_instance_fails_readiness(self):
        with mock.patch.object(probe_identity, 'probe', return_value={'keyless_identity_verified': True}), \
                mock.patch.object(probe_identity, 'compute_get', return_value=(200, {'name': 'jep-test-worker', 'id': '999'}, 100)):
            result = probe_identity.probe_workload(self.profile)
        self.assertEqual(result['targets'][0]['error'], 'TARGET_IDENTITY_MISMATCH')

    def test_host_failure_does_not_call_destination(self):
        with mock.patch.object(probe_identity, 'probe', side_effect=RuntimeError('private details')), \
                mock.patch.object(probe_identity, 'compute_get') as target:
            result = probe_identity.probe_workload(self.profile)
        target.assert_not_called()
        self.assertFalse(result['workload_access_verified'])
        self.assertNotIn('private details', json.dumps(result))

    def test_bad_manifest_fails_before_metadata(self):
        self.approval['controller_account'] = 'wrong@example.test'; self.save_manifest()
        with mock.patch.object(probe_identity, 'probe') as host, self.assertRaises(PermissionError):
            probe_identity.probe_workload(self.profile)
        host.assert_not_called()

    def test_metadata_token_values_never_enter_receipt(self):
        token = 'NEVER_RETURN_THIS'
        responses = ['pvd-dev-232', 'dev', self.account,
                     json.dumps({'token_type': 'Bearer', 'access_token': token, 'expires_in': 3599})]
        response = mock.MagicMock(); response.__enter__.return_value = response
        response.status = 200; response.read.return_value = b'{"name":"dev"}'
        with mock.patch.object(probe_identity, 'metadata', side_effect=responses), \
                mock.patch.object(probe_identity.urllib.request, 'build_opener', return_value=mock.Mock(open=mock.Mock(return_value=response))):
            result = probe_identity.probe(self.profile)
        self.assertNotIn(token, json.dumps(result))

    def test_redirects_never_forward_authorization(self):
        self.assertIsNone(probe_identity.NoRedirect().redirect_request(None, None, 302, 'redirect', {}, 'https://other.test'))

    def test_admin_workload_plan_never_changes_infrastructure(self):
        with mock.patch.object(identity, 'run') as run, mock.patch.object(identity.subprocess, 'run') as subprocess_run:
            result = identity.workload_plan(self.profile)
        run.assert_not_called(); subprocess_run.assert_not_called()
        self.assertFalse(result['mutations_performed'])
        self.assertEqual(result['mode'], 'ADMINISTRATOR_PLAN_ONLY')
        self.assertEqual(result['instances'][0]['permissions'],
                         ['compute.instances.get', 'compute.instances.start', 'compute.instances.stop'])
        self.assertFalse(result['storage']['object_listing_granted'])
        self.assertNotIn('storage.objects.delete', result['storage']['permissions'])
        self.assertEqual(result['member'], 'serviceAccount:' + self.account)

    def test_each_api_request_gets_current_metadata_credentials(self):
        response = mock.MagicMock(); response.__enter__.return_value = response
        response.status = 200; response.read.return_value = b'{"name":"dev"}'
        with mock.patch.object(probe_identity, 'access_token', side_effect=[
                {'access_token':'first','expires_in':1}, {'access_token':'second','expires_in':3600}]) as refresh, \
                mock.patch.object(probe_identity.urllib.request, 'build_opener', return_value=mock.Mock(open=mock.Mock(return_value=response))):
            probe_identity.compute_get('pvd-dev-232','us-central1-a','dev')
            probe_identity.compute_get('pvd-dev-232','us-central1-a','dev')
        self.assertEqual(refresh.call_count, 2)  # Unit contract, not a live expiry test.


if __name__ == '__main__':
    unittest.main()
