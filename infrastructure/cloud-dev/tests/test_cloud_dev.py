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
        self.assertEqual(environment['GOOGLE_APPLICATION_CREDENTIALS'], environment['CLOUDSDK_CONFIG'] + '/application_default_credentials.json')
        self.assertTrue(environment['PATH'].startswith(environment['VIRTUAL_ENV'] + '/bin:'))

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
