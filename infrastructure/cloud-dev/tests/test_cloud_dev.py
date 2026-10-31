import copy
import contextlib
import hashlib
import importlib.util
import json
import io
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'implementation'))
sys.path.insert(0, str(ROOT / 'tools'))
import cloud_job
import project
import preflight
import install
import identity
import probe_identity


class CloudDevelopmentTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.host = json.loads((ROOT / 'profiles/columbia.json').read_text())
        for name in self.host['paths']:
            self.host['paths'][name] = str(self.root / name)
        self.host['resolved'] = {
            'node_bin_dir': '/usr/bin', 'bin_dir': str(self.root / 'bin'),
            'linux_home': str(self.root),
        }
        self.definition = json.loads((ROOT / 'projects/jep.json').read_text())

    def configured_project(self, name='jep'):
        definition = dict(self.definition, id=name)
        profile = project.project_profile(self.host, definition)
        for key in ['state_root', 'config_root', 'workspace_root']:
            Path(profile['paths'][key]).mkdir(parents=True)
        (Path(profile['paths']['state_root']) / 'jobs').mkdir()
        config = Path(profile['paths']['config_root']) / 'profile.json'
        config.write_text(json.dumps(profile))
        return profile, config

    def queued_job(self, profile, status='queued', argv=None, resume=None):
        identifier = 'a' * 32
        directory = Path(profile['paths']['state_root']) / 'jobs' / identifier
        directory.mkdir()
        data = {
            'id': identifier, 'status': status, 'cwd': profile['paths']['workspace_root'],
            'argv': argv or [sys.executable, '-c', 'print("completed")'],
            'resume_argv': resume,
        }
        (directory / 'job.json').write_text(json.dumps(data))
        return identifier, directory

    def test_project_paths_are_disjoint_and_input_is_preserved(self):
        original = copy.deepcopy(self.host)
        left = project.project_profile(self.host, self.definition)
        right = project.project_profile(self.host, dict(self.definition, id='another'))
        for key in ['workspace_root', 'state_root', 'config_root']:
            self.assertNotEqual(left['paths'][key], right['paths'][key])
        left['project_definition']['memory_max_mib'] = 2048
        self.assertIsNone(self.definition['memory_max_mib'])
        self.assertEqual(original, self.host)

    def test_project_environment_selects_separate_credentials_and_runtime(self):
        profile = project.project_profile(self.host, self.definition)
        with mock.patch.dict(os.environ, {'GOOGLE_APPLICATION_CREDENTIALS': '/another/project.json', 'CLOUDSDK_AUTH_ACCESS_TOKEN': 'do-not-inherit'}):
            environment = project.project_environment(profile)
        self.assertNotIn('CLOUDSDK_AUTH_ACCESS_TOKEN', environment)
        self.assertNotIn('GOOGLE_APPLICATION_CREDENTIALS', environment)
        self.assertEqual(environment['CLOUDSDK_CORE_ACCOUNT'], self.host['job_identity']['service_account_email'])
        self.assertTrue(environment['PATH'].startswith(environment['VIRTUAL_ENV'] + '/bin:'))

    def test_host_jobs_also_select_keyless_metadata_identity(self):
        environment = project.project_environment(self.host)
        self.assertEqual(environment['CLOUDSDK_CORE_ACCOUNT'], self.host['job_identity']['service_account_email'])
        self.assertEqual(environment['CLOUDSDK_CONFIG'], self.host['paths']['config_root'] + '/gcloud-jobs')
        self.assertNotIn('GOOGLE_APPLICATION_CREDENTIALS', environment)

    def test_keyless_environment_rejects_local_user_adc_file(self):
        profile, _ = self.configured_project()
        cloud_config = Path(profile['resolved']['project_environment']['CLOUDSDK_CONFIG'])
        cloud_config.mkdir()
        (cloud_config / 'application_default_credentials.json').write_text('{}')
        with self.assertRaisesRegex(RuntimeError, 'without a local ADC'):
            project.project_environment(profile)

    def test_keyless_preflight_rejects_broad_owner_grant(self):
        host = copy.deepcopy(self.host)
        host['job_identity']['iam_bindings'][0]['role'] = 'roles/owner'
        path = self.root / 'bad-profile.json'
        path.write_text(json.dumps(host))
        with self.assertRaisesRegex(ValueError, 'Owner/Editor'):
            preflight.load_profile(path)

    def test_identity_plan_uses_scoped_grants_and_no_private_keys(self):
        result = identity.plan(self.host)
        self.assertFalse(result['private_key_files'])
        self.assertIn('roles/compute.viewer', ' '.join(result['commands']))
        for command in result['commands']:
            self.assertIn('--account=pvd2112@columbia.edu', command)
            self.assertIn('--project=pvd-dev-232', command)
            self.assertNotIn('keys create', command)

    def test_identity_attachment_matches_account_and_scope(self):
        definition = self.host['job_identity']
        instance = {'serviceAccounts': [{'email': definition['service_account_email'], 'scopes': definition['oauth_scopes']}]}
        self.assertTrue(identity.matches(instance, definition))
        instance['serviceAccounts'][0]['scopes'] = []
        self.assertFalse(identity.matches(instance, definition))

    def test_identity_setup_cannot_restart_implicitly(self):
        response = subprocess.CompletedProcess([], 0, stdout=json.dumps({'name': 'dev', 'status': 'RUNNING', 'serviceAccounts': []}))
        with mock.patch.object(identity, 'run', return_value=response) as command, mock.patch.object(identity, 'snapshots') as snapshot:
            with self.assertRaisesRegex(RuntimeError, 'controlled stop/start'):
                identity.apply(self.host, False, self.root / 'receipt.json')
            self.assertEqual(command.call_count, 1)
            snapshot.assert_not_called()

    def test_identity_setup_is_idempotent_when_account_and_grants_match(self):
        configured = self.host['job_identity']
        instance = {'name': 'dev', 'status': 'RUNNING', 'serviceAccounts': [{'email': configured['service_account_email'], 'scopes': configured['oauth_scopes']}]}
        policy = {'bindings': [{'role': 'roles/compute.viewer', 'members': ['serviceAccount:' + configured['service_account_email']]}]}
        commands = []

        def run(command, **kwargs):
            commands.append(command)
            data = policy if 'get-iam-policy' in command else instance
            return subprocess.CompletedProcess(command, 0, stdout=json.dumps(data))

        with mock.patch.object(identity, 'run', side_effect=run), mock.patch.object(identity.subprocess, 'run', return_value=subprocess.CompletedProcess([], 0, stdout='{}')), contextlib.redirect_stdout(io.StringIO()):
            identity.apply(self.host, False, self.root / 'receipt.json')
        self.assertTrue(json.loads((self.root / 'receipt.json').read_text())['attachment_verified'])
        self.assertFalse(any(action in command for command in commands for action in ['stop', 'start', 'set-service-account', 'add-iam-policy-binding']))

    def test_identity_probe_verifies_api_access_without_returning_token(self):
        token = 'private-short-lived-test-token'
        metadata = ['pvd-dev-232', 'dev', self.host['job_identity']['service_account_email'], json.dumps({'access_token': token, 'token_type': 'Bearer', 'expires_in': 3599})]
        response = mock.MagicMock()
        response.__enter__.return_value = response
        response.status = 200
        response.read.return_value = b'{"name":"dev"}'
        with mock.patch.object(probe_identity, 'metadata', side_effect=metadata), mock.patch.object(probe_identity.urllib.request, 'urlopen', return_value=response):
            result = probe_identity.probe(self.host)
        self.assertTrue(result['keyless_identity_verified'])
        self.assertEqual(result['compute_api_http_status'], 200)
        self.assertNotIn(token, json.dumps(result))

    def test_job_credential_setup_failure_is_recorded_as_failed(self):
        profile, _ = self.configured_project()
        directory = Path(profile['resolved']['project_environment']['CLOUDSDK_CONFIG'])
        directory.mkdir()
        (directory / 'application_default_credentials.json').write_text('{}')
        identifier, job = self.queued_job(profile)
        cloud_job.run_job(profile, identifier)
        record = json.loads((job / 'job.json').read_text())
        self.assertEqual(record['status'], 'failed')
        self.assertIn('local ADC', record['error'])

    def test_project_validation_rejects_path_traversal_and_credentials_in_url(self):
        for patch in [{'id': '../escape'}, {'repository_url': 'https://token@github.com/pvd232/JEP.git'}, {'repository_revision': 'main'}]:
            with self.subTest(patch=patch), self.assertRaises(ValueError):
                project.project_profile(self.host, dict(self.definition, **patch))

    def test_memory_limit_preserves_headroom_and_rejects_overcommit(self):
        memory = {'MemAvailable': 8 * 1024**2, 'MemTotal': 16 * 1024**2}
        limit = project.memory_limit(self.definition, memory)
        self.assertGreaterEqual(limit, 512)
        self.assertLessEqual(limit, 4096)
        with self.assertRaises(ValueError):
            project.memory_limit(dict(self.definition, memory_max_mib=8192), memory)

    def test_wrong_host_stops_project_setup_before_writes(self):
        with mock.patch.object(project, 'collect', return_value={'target_verified': False, 'identity_mismatches': {'vm_name': 'wrong'}}):
            with self.assertRaisesRegex(RuntimeError, 'identity mismatch'):
                project.setup(self.host, self.definition)
        self.assertFalse(Path(self.host['paths']['project_root']).exists())

    def test_wrong_metadata_stops_installer_before_sudo(self):
        config = self.root / 'host.json'
        config.write_text(json.dumps(self.host))
        opener = mock.Mock()
        opener.open.return_value.read.return_value = b'wrong-project'
        with mock.patch.object(sys, 'argv', ['install.py', '--profile', str(config)]), mock.patch.object(install.urllib.request, 'build_opener', return_value=opener), mock.patch.object(install.subprocess, 'run') as command:
            with self.assertRaisesRegex(RuntimeError, 'identity mismatch'):
                install.main()
            command.assert_not_called()

    def test_job_runs_real_child_in_project_environment_and_is_not_repeated(self):
        profile, _ = self.configured_project()
        argv = [sys.executable, '-c', 'import os;print(os.environ["CLOUD_PROJECT_ID"]);print(os.environ["CLOUDSDK_CONFIG"])']
        identifier, directory = self.queued_job(profile, argv=argv)
        self.assertEqual(cloud_job.run_job(profile, identifier), 0)
        record = json.loads((directory / 'job.json').read_text())
        self.assertEqual((record['status'], record['exit_code']), ('succeeded', 0))
        output = (directory / 'output.log').read_text()
        self.assertIn(profile['resolved']['project_environment']['CLOUDSDK_CONFIG'], output)
        cloud_job.run_job(profile, identifier)
        self.assertEqual(output, (directory / 'output.log').read_text())

    def test_failed_child_keeps_exit_status_and_output(self):
        profile, _ = self.configured_project()
        identifier, directory = self.queued_job(profile, argv=[sys.executable, '-c', 'print("failure evidence");raise SystemExit(7)'])
        cloud_job.run_job(profile, identifier)
        record = json.loads((directory / 'job.json').read_text())
        self.assertEqual((record['status'], record['exit_code']), ('failed', 7))
        self.assertIn('failure evidence', (directory / 'output.log').read_text())

    def test_interrupted_job_requires_explicit_resume_command(self):
        profile, _ = self.configured_project()
        identifier, directory = self.queued_job(profile, status='running')
        cloud_job.run_job(profile, identifier)
        self.assertEqual(json.loads((directory / 'job.json').read_text())['status'], 'interrupted')
        self.assertFalse((directory / 'output.log').exists())

    def test_resume_command_reads_checkpoint_and_log_is_persistent(self):
        profile, config = self.configured_project()
        checkpoint = self.root / 'checkpoint'
        checkpoint.write_text('step 12')
        resume = [sys.executable, '-c', 'from pathlib import Path;import sys;print(Path(sys.argv[1]).read_text())', str(checkpoint)]
        identifier, directory = self.queued_job(profile, status='interrupted', resume=resume)
        cloud_job.run_job(profile, identifier)
        self.assertEqual(json.loads((directory / 'job.json').read_text())['status'], 'succeeded')
        result = subprocess.run([sys.executable, str(ROOT / 'implementation/cloud_job.py'), '--config', str(config), 'logs', identifier, '--offset', '2', '--limit', '3'], check=True, capture_output=True, text=True)
        log = json.loads(result.stdout)
        self.assertEqual((log['offset'], log['next_offset'], log['text']), (2, 5, 'ep '))

    def test_job_id_cannot_escape_project_directory(self):
        with self.assertRaises(ValueError):
            cloud_job.job_dir(self.host, '../../outside')

    def test_project_cli_preserves_submit_arguments(self):
        profile, _ = self.configured_project()
        controller = Path(self.host['paths']['install_root']) / 'bin/cloud_job.py'
        controller.parent.mkdir(parents=True)
        controller.write_text('import json,os,sys\nprint(json.dumps({"argv":sys.argv[1:],"project":os.environ["CLOUD_PROJECT_ID"]}))\n')
        host_config = self.root / 'host.json'
        host_config.write_text(json.dumps(self.host))
        arguments = ['--cwd', profile['paths']['workspace_root'], '--checkpoint', '/checkpoint', '--', '/bin/echo', 'literal space', '$NO_EXPANSION']
        result = subprocess.run([sys.executable, str(ROOT / 'implementation/project.py'), '--host-profile', str(host_config), '--project', 'jep', 'submit', *arguments], check=True, capture_output=True, text=True)
        data = json.loads(result.stdout)
        self.assertEqual(data['argv'][2:], ['submit', *arguments])
        self.assertEqual(data['project'], 'jep')

    def test_toolchain_and_complete_npm_lock_match(self):
        lock = json.loads((ROOT / 'toolchain.lock.json').read_text())
        self.assertEqual(hashlib.sha256((ROOT / 'desktop-commander.package-lock.json').read_bytes()).hexdigest(), lock['package_lock_sha256'])

    def test_setup_is_idempotent_preserves_checkout_and_installs_aggregate_limits(self):
        workspace = Path(self.host['paths']['workspace_root']) / 'jep'
        workspace.mkdir(parents=True)
        subprocess.run(['git', 'init', str(workspace)], check=True, capture_output=True)
        subprocess.run(['git', '-C', str(workspace), 'remote', 'add', 'origin', self.definition['repository_url']], check=True)
        sentinel = workspace / 'uncommitted-research.txt'
        sentinel.write_text('preserve existing work')
        state = Path(self.host['paths']['state_root'])
        state.mkdir()
        (state / 'cloud-dev-columbia-job@.service').write_text('[Service]\nEnvironment=CLOUD_DEV_CONFIG=' + self.host['paths']['config_root'] + '/profile.json\nExecStart=/example\n')
        runtime = Path(self.host['paths']['project_root']) / 'jep' / 'venv' / 'bin'
        runtime.mkdir(parents=True)
        (runtime / 'python').symlink_to(sys.executable)
        installed = {}
        real_run = subprocess.run

        def systemd(command, **kwargs):
            if command[0] != 'sudo':
                return real_run(command, **kwargs)
            if command[2] == 'cmp':
                source, destination = command[-2:]
                return subprocess.CompletedProcess(command, 0 if installed.get(destination) == Path(source).read_text() else 1)
            if command[2] == 'install':
                installed[command[-1]] = Path(command[-2]).read_text()
            return subprocess.CompletedProcess(command, 0)

        output = io.StringIO()
        with mock.patch.object(project, 'collect', return_value={'target_verified': True}), mock.patch.object(project.subprocess, 'run', side_effect=systemd), mock.patch.object(project.shutil, 'disk_usage', return_value=type('Usage', (), {'free': 20 * 1024**3})()), contextlib.redirect_stdout(output):
            project.setup(self.host, self.definition)
            first = json.JSONDecoder().raw_decode(output.getvalue())[0]
            output.seek(0)
            output.truncate(0)
            project.setup(self.host, self.definition)
            second = json.loads(output.getvalue())
        self.assertTrue(first['changed'])
        self.assertFalse(second['changed'])
        self.assertEqual(sentinel.read_text(), 'preserve existing work')
        service = installed['/etc/systemd/system/cloud-dev-columbia-jep-job@.service']
        self.assertIn('Slice=cloud-dev-columbia-jep.slice', service)
        self.assertIn('/projects/jep/profile.json', service)
        self.assertIn('CPUQuota=100%', installed['/etc/systemd/system/cloud-dev-columbia-jep.slice'])


if __name__ == '__main__':
    unittest.main()
