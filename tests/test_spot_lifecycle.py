"""Observe Spot placement, explicit recovery, VIPER publication and cleanup boundaries."""
import copy
import importlib.util
import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch

from csts_pilot.full_data_prompt_protocol import digest_file
from csts_pilot.full_data_prompt_uploads import publish_one
from csts_pilot.full_data_prompt_worker import rebind_resume_state, require_training_compatibility

ROOT = Path(__file__).resolve().parents[1]


def load_script(name):
    """Load a project lifecycle adapter without running its cloud entrypoint."""
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts/full_data_prompt_20261107" / (name + ".py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ResumeTests(unittest.TestCase):
    """Preserve successful epochs while requiring exact prior-state authorization."""
    def setUp(self):
        self.state = {"source_commit": "a"*40, "protocol_sha256": "b"*64, "worker": "worker1",
                      "lease": {"execution_id": "c"*32}, "trials": {"finished": {"records": [1,2,3,4,5]}},
                      "status": "failed_preserved", "failure": {"message": "serializer"}}
        self.approval = {"training_source_commit": "a"*40, "resumes": {"worker1": {
            "state_sha256": "d"*64, "previous_source_commit": "a"*40, "previous_execution_id": "c"*32}}}

    def test_hash_bound_rebind_preserves_completed_records(self):
        state = rebind_resume_state(copy.deepcopy(self.state), self.approval, "worker1",
                                    "e"*40, "b"*64, {"execution_id": "f"*32}, "d"*64)
        self.assertEqual(state["trials"], self.state["trials"])
        self.assertEqual(state["training_source_commit"], "a"*40)
        self.assertEqual(state["status"], "running")
        self.assertNotIn("failure", state)

    def test_changed_preserved_state_cannot_rebind(self):
        with self.assertRaisesRegex(ValueError, "Explicit resume"):
            rebind_resume_state(self.state, self.approval, "worker1",
                                "e"*40, "b"*64, {"execution_id": "f"*32}, "0"*64)

    def test_scientific_code_change_cannot_reuse_training_revision(self):
        with patch("subprocess.check_output", return_value="csts_pilot/baseline_stages.py\n"):
            with self.assertRaisesRegex(ValueError, "scientific"):
                require_training_compatibility(ROOT, "a"*40, "b"*40)


class PlacementTests(unittest.TestCase):
    """Use current manifest regions instead of an embedded Tokyo worker mapping."""
    def test_taiwan_capacity_can_be_selected_without_tokyo(self):
        deploy = load_script("deploy_spot")
        advice = [{"recommendations": [{"shards": [{"zone": "zones/asia-east1-b", "machineType": "g2-standard-4"}]}]}]
        result = deploy.candidates(["asia-east1"], ["asia-east1-a", "asia-east1-b", "asia-northeast1-b"], advice)
        self.assertEqual(result[0], ("asia-east1-b", "g2-standard-4"))
        self.assertTrue(all(zone.startswith("asia-east1-") for zone, _ in result))

    def test_outside_region_cannot_enter_candidate_search(self):
        with self.assertRaises(ValueError):
            load_script("deploy_spot").candidates(["us-east1"], ["us-east1-a"], [])


class AllocationObservationTests(unittest.TestCase):
    """Permit fallback only after a recorded operation is authoritatively terminal."""
    def test_nonzero_wait_terminal_stockout_is_observed_before_fallback(self):
        deploy = load_script("deploy_spot")
        done = {"name": "op-1", "status": "DONE",
                "error": {"errors": [{"code": "ZONE_RESOURCE_POOL_EXHAUSTED"}]}}
        responses = [subprocess.CompletedProcess([], 1, "", "capacity failed"),
                     subprocess.CompletedProcess([], 0, json.dumps(done), "")]
        with patch.object(deploy, "command", side_effect=responses) as run:
            self.assertEqual(deploy.terminal_operation("op-1", "asia-east1-b", []), done)
        self.assertEqual(run.call_args_list[1].args[0][3], "describe")

    def test_pending_operation_never_authorizes_fallback(self):
        deploy = load_script("deploy_spot")
        responses = [subprocess.CompletedProcess([], 1, "", "observation failed"),
                     subprocess.CompletedProcess([], 0, '{"status":"RUNNING"}', "")]
        with patch.object(deploy, "command", side_effect=responses), \
             patch.object(deploy.time, "monotonic", side_effect=[0, 901]):
            with self.assertRaisesRegex(RuntimeError, "intent retained"):
                deploy.terminal_operation("op-1", "asia-east1-b", [])

    def test_running_wait_is_polled_to_done_without_another_create(self):
        deploy = load_script("deploy_spot")
        done = {"status": "DONE", "name": "op-1"}
        responses = [subprocess.CompletedProcess([], 0, '{"status":"RUNNING"}', ""),
                     subprocess.CompletedProcess([], 0, json.dumps(done), "")]
        with patch.object(deploy, "command", side_effect=responses) as run, \
             patch.object(deploy.time, "sleep"), \
             patch.object(deploy.time, "monotonic", side_effect=[0, 10]):
            self.assertEqual(deploy.terminal_operation("op-1", "asia-east1-b", []), done)
        self.assertEqual(run.call_count, 2)
        self.assertTrue(all(call.args[0][3] == "wait" for call in run.call_args_list))

    def test_operation_observation_timeout_never_cleans_resources(self):
        deploy = load_script("deploy_spot")
        with patch.object(deploy, "command", side_effect=subprocess.TimeoutExpired("wait", 900)), \
             patch.object(deploy, "cleanup_failed_create") as cleanup:
            with self.assertRaises(subprocess.TimeoutExpired):
                deploy.terminal_operation("op-1", "asia-east1-b", [])
        cleanup.assert_not_called()


class PublicationTests(unittest.TestCase):
    """Require VIPER's streamed cloud verification before a durable generation ACK."""
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.folder = self.root / "transfer/epoch1"
        self.folder.mkdir(parents=True)
        self.archive = self.folder / "native.tar"
        self.archive.write_bytes(b"sealed native checkpoint")
        self.manifest = self.folder / "ready.json"
        self.manifest.write_text(json.dumps({"worker": "worker1", "generation": "epoch1",
            "source_commit": "a"*40, "execution_id": "b"*32, "instance_id": "123",
            "archive": str(self.archive), "archive_sha256": digest_file(self.archive),
            "archive_size": self.archive.stat().st_size}))

    def cloud(self):
        cloud = Mock()
        def references(destination, sources):
            result = {}
            for name, path in sources.items():
                digest = digest_file(path)
                size = path.stat().st_size
                result[name] = SimpleNamespace(sha256=digest, bytes=size,
                    model_dump=lambda mode, digest=digest, size=size: {"sha256":digest,"bytes":size,"stored_at":{"kind":"gcs"}})
            return result
        cloud.resolved_files.side_effect = references
        return cloud

    def test_verified_publication_writes_bound_viper_ack(self):
        cloud = self.cloud()
        ack = publish_one(self.root, self.manifest, cloud, "owner", "study")
        self.assertEqual(cloud.verify_file.call_count, 2)
        self.assertEqual(ack["archive_sha256"], digest_file(self.archive))
        self.assertEqual(ack["transport"], "viper_cloud")
        self.assertTrue((self.folder / "ack.json").exists())

    def test_cloud_verification_failure_preserves_local_without_ack(self):
        cloud = self.cloud()
        cloud.verify_file.side_effect = RuntimeError("remote SHA differs")
        with self.assertRaises(RuntimeError):
            publish_one(self.root, self.manifest, cloud, "owner", "study")
        self.assertTrue(self.archive.exists())
        self.assertFalse((self.folder / "ack.json").exists())


class CleanupTests(unittest.TestCase):
    """Limit deletion to exact task identities and retain unverified recovery bytes."""
    def setUp(self):
        self.collector = load_script("collect_epochs")
        self.assignment = {"instance_name": "jep-test", "instance_id": "123",
                           "project": "mantra-477901", "zone": "asia-east1-b",
                           "boot_disk": {"name": "jep-test", "id": "456"}}

    def test_replacement_instance_cannot_be_deleted(self):
        response = subprocess.CompletedProcess([], 0, json.dumps({"id":"999","labels":{"task":"jep-full-data-20261107"}}), "")
        with patch.object(self.collector, "run", return_value=response):
            with self.assertRaises(PermissionError):
                self.collector.describe(self.assignment, "admin@example.test")

    def test_unverified_failure_keeps_recovery_disk(self):
        with patch.object(self.collector, "describe", return_value={"id":"123"}), patch.object(
                self.collector, "run", return_value=subprocess.CompletedProcess([],0,"","")) as run:
            receipt = self.collector.cleanup(self.assignment, "admin@example.test", False, True)
        self.assertTrue(receipt["recovery_disk_preserved"])
        self.assertEqual(run.call_count, 1)
        self.assertIn("--keep-disks=all", run.call_args.args[0])

    def test_changed_recovery_disk_cannot_be_deleted(self):
        responses = [subprocess.CompletedProcess([],0,"",""), subprocess.CompletedProcess([],0,
            json.dumps({"id":"999","labels":{"task":"jep-full-data-20261107"}}),"")]
        with patch.object(self.collector, "describe", return_value={"id":"123"}), patch.object(
                self.collector, "run", side_effect=responses) as run:
            with self.assertRaises(PermissionError):
                self.collector.cleanup(self.assignment, "admin@example.test", True, True)
        self.assertEqual(run.call_count, 2)


class ReviewRegressionTests(unittest.TestCase):
    """Observe the preserved-lease, terminal-resume and shared-admission review findings."""
    def test_pending_old_generation_is_published_with_original_identity(self):
        from csts_pilot.full_data_prompt_uploads import require_generation_authorization
        case = PublicationTests();case.setUp()
        self.addCleanup(case.doCleanups)
        manifest = json.loads(case.manifest.read_text())
        preserved = {"manifest_sha256": digest_file(case.manifest),
                     **{k:manifest[k] for k in ['archive_sha256','instance_id','execution_id','source_commit']}}
        resume = {"preserved_generations": {"epoch1":preserved}}
        assignment = {"instance_id":"999", "execution_id":"c"*32}
        require_generation_authorization(case.manifest, manifest, assignment, resume)
        ack = publish_one(case.root, case.manifest, case.cloud(), 'owner', 'study')
        self.assertEqual(ack['execution_id'],manifest['execution_id'])
        self.assertEqual(ack['archive_sha256'],manifest['archive_sha256'])
        with self.assertRaises(PermissionError):
            require_generation_authorization(case.manifest, manifest, assignment, {})

    def test_resume_cannot_relabel_scientific_source(self):
        case=ResumeTests();case.setUp();original=copy.deepcopy(case.state)
        case.state['training_source_commit']='a'*40
        case.approval['training_source_commit']='e'*40
        with self.assertRaisesRegex(ValueError,'scientific source'):
            rebind_resume_state(case.state,case.approval,'worker1','e'*40,'b'*64,
                                {'execution_id':'f'*32},'d'*64)
        self.assertEqual(case.state['trials'],original['trials'])
        self.assertEqual(case.state['training_source_commit'],'a'*40)

    def test_distinct_journals_share_project_admission_lock(self):
        import fcntl
        deploy=load_script('deploy_spot')
        with tempfile.TemporaryDirectory() as folder, patch.object(Path,'home',return_value=Path(folder)):
            first,_=deploy.admission_paths('mantra-477901')
            second,_=deploy.admission_paths('mantra-477901')
            with first.open('a+') as a,second.open('a+') as b:
                fcntl.flock(a,fcntl.LOCK_EX|fcntl.LOCK_NB)
                with self.assertRaises(BlockingIOError):
                    fcntl.flock(b,fcntl.LOCK_EX|fcntl.LOCK_NB)

    def test_preserved_native_runtime_cannot_change_gpu_or_packages(self):
        from csts_pilot.full_data_prompt_worker import require_preserved_runtime
        import yaml
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder)
            runtime={'gpu_model':'NVIDIA L4','python_env':{'python_version':'3.13.15','distributions':[]}}
            spec=root/'spec.yaml'
            spec.write_text(yaml.safe_dump({'env':{'compute':{'model':'NVIDIA L4','count':1},
                                                  'python_env':runtime['python_env']}}))
            record=root/'resolved.yaml';record.write_text(yaml.safe_dump({'spec':{'sha256':digest_file(spec)}}))
            state={'trials':{'trial':{'records':[{'path':str(record)}]}}}
            require_preserved_runtime(state,runtime)
            for changed in [dict(runtime,gpu_model='NVIDIA T4'),
                            dict(runtime,python_env={'python_version':'3.12','distributions':[]})]:
                with self.assertRaises(ValueError):require_preserved_runtime(state,changed)

    def test_completed_resume_publishes_current_lease_without_training(self):
        import csts_pilot.full_data_prompt_worker as worker
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);output=root/'out';output.mkdir()
            selected={'seed':7,'initial_trainable_sha256':'a'*64}
            state={'source_commit':'b'*40,'worker':'worker1','trials':{'A_seed7':{'selection':selected}},'lease':{'execution_id':'c'*32}}
            with patch.object(worker,'trial_matrix',return_value=[{'trial_id':'A_seed7','arm':'A','seed':7}]), \
                 patch('viper.repository.read_source',return_value=SimpleNamespace(commit='b'*40)), \
                 patch.object(worker,'publish_generation') as publish, \
                 patch('viper.execution.run') as execute:
                worker.run_training(root,output,{},state,[7],'NVIDIA L4')
            execute.assert_not_called()
            self.assertEqual(publish.call_args_list[0].args[2],'training-final-'+'c'*32)
            self.assertEqual(publish.call_args_list[1].args[2],'publication-complete-'+'c'*32)
            self.assertEqual(state['final_generation'],'training-final-'+'c'*32)


class TerminalUploadRegressionTests(unittest.TestCase):
    """Keep a resumed publisher alive until inherited and current generations finish."""
    def test_same_lease_resume_requires_new_attempt_identity(self):
        case=ResumeTests();case.setUp()
        with self.assertRaisesRegex(ValueError,'fresh execution lease'):
            rebind_resume_state(case.state,case.approval,'worker1','a'*40,'b'*64,
                                {'execution_id':'c'*32},'d'*64)

    def test_final_ack_does_not_bypass_a_transient_pending_upload(self):
        import csts_pilot.full_data_prompt_uploads as uploads
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);output=root/'baseline_results/full_data_prompt_20261107/worker1'
            current={'project':'mantra-477901','service_account':'job@example.test',
                     'instance_id':'999','execution_id':'c'*32}
            inherited={};failures=[]
            for generation,instance,execution in [('publication-complete-'+'c'*32,'999','c'*32),
                                                   ('worker-failed-old','123','b'*32)]:
                q=output/'transfer'/generation;q.mkdir(parents=True)
                (q/'native.tar').write_bytes(generation.encode())
                m={'worker':'worker1','generation':generation,'instance_id':instance,
                   'execution_id':execution,'source_commit':'a'*40,'archive':str(q/'native.tar'),
                   'archive_sha256':digest_file(q/'native.tar'),'archive_size':(q/'native.tar').stat().st_size}
                (q/'ready.json').write_text(json.dumps(m))
                if instance=='123':inherited[generation]={'manifest_sha256':digest_file(q/'ready.json'),
                    **{k:m[k] for k in ['archive_sha256','instance_id','execution_id','source_commit']}}
            def publish(root,path,cloud,owner,workspace):
                m=json.loads(path.read_text())
                if m['generation']=='worker-failed-old' and not failures:
                    failures.append(True)
                    self.assertFalse((output/'upload-complete.json').exists())
                    raise RuntimeError('temporary transport failure')
                ack={**m,'cloud_roundtrip_verified':True,'transport':'viper_cloud'}
                (path.parent/'ack.json').write_text(json.dumps(ack))
                return ack
            with patch.object(uploads,'require_workload_identity'),patch.object(uploads,'cloud_service'), \
                 patch.object(uploads,'publish_one',side_effect=publish) as publish_mock, \
                 patch.object(uploads.time,'sleep'):
                uploads.run(root,'worker1',current,{'owner':'owner','workspace':'study'},.01,
                            {'preserved_generations':inherited})
            self.assertEqual(publish_mock.call_count,3)
            self.assertTrue((output/'upload-complete.json').exists())


class CompletionAndStorageRegressionTests(unittest.TestCase):
    """Keep recovery bytes until every generation validates and reserve space before work."""
    def test_verified_tar_is_reclaimed_without_losing_native_artifacts(self):
        from test_full_data_worker_persistence import WorkerPersistenceTests
        case=WorkerPersistenceTests();case.setUp();self.addCleanup(case.doCleanups)
        case.execute()
        self.assertFalse((case.out/'transfer/epoch1/native.tar').exists())
        self.assertTrue((case.out/'transfer/epoch1/ready.json').exists())
        self.assertTrue((case.out/'transfer/epoch1/ack.json').exists())
        self.assertTrue(case.file.exists())
        import csts_pilot.full_data_prompt_worker as worker
        worker.publish_generation(case.root,case.out,'epoch1',{},case.state,[])

    def test_low_disk_reserve_blocks_another_epoch(self):
        from csts_pilot.full_data_prompt_worker import require_epoch_space
        with patch('shutil.disk_usage',return_value=SimpleNamespace(free=1024**3)):
            with self.assertRaises(OSError):require_epoch_space(ROOT)

    def test_invalid_inherited_ack_never_permits_disk_cleanup(self):
        collector=load_script('collect_epochs')
        assignment={'instance_name':'jep-test','project':'mantra-477901','zone':'asia-east1-b',
                    'instance_id':'999','execution_id':'c'*32}
        manifest={'worker':'worker1','generation':'epoch1','source_commit':'a'*40,
                  'instance_id':'999','execution_id':'c'*32,'archive_sha256':'d'*64}
        ack={**manifest,'archive_sha256':'e'*64,'cloud_roundtrip_verified':True}
        state={'source_commit':'a'*40,'status':'assigned_training_complete_test_not_opened',
               'lease':{'execution_id':'c'*32,'deadline_verified':True},
               'completion_generation':'publication-complete-'+'c'*32,'trials':{}}
        obj={'state':state,'generations':[{'manifest':manifest,'ack':ack}], 'ready':[], 'completion':{}}
        with tempfile.TemporaryDirectory() as folder:
            args=SimpleNamespace(source='a'*40,max_hours=1,local=Path(folder),delete_verified_disks=True,
                approval={'assignments':{'worker1':assignment},'controller_account':'admin@example.test'})
            with patch.object(collector,'describe',return_value={'status':'RUNNING'}), \
                 patch.object(collector,'read_worker',return_value=obj), \
                 patch.object(collector,'cleanup',return_value={'recovery_disk_preserved':True}) as cleanup:
                with self.assertRaisesRegex(ValueError,'mismatched generation'):
                    collector.monitor('worker1',args)
            self.assertFalse(cleanup.call_args.args[2])


if __name__ == "__main__":
    unittest.main()
