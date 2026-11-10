"""Observe ranked allocation, uncertain failures and bounded host-memory fallback."""

import hashlib
import json
from pathlib import Path
import tempfile
import time
import unittest
from unittest import mock

import capacity_advisor as advisor
import controller


def forecast(region, probability=.9, seconds="3600s", machine=advisor.MACHINE_TYPE):
    return {"recommendations": [{"scores": {"obtainability": probability, "estimatedUptime": seconds},
            "shards": [{"zone": "https://example/zones/" + region + "-a", "machineType": machine,
                        "instanceCount": 1, "provisioningModel": "SPOT"}]}]}


class AdviceFixture:
    def __init__(self):
        self.responses = {"asia-east1": forecast("asia-east1", .8, "3600s"),
                          "asia-southeast1": forecast("asia-southeast1", .9, "600s")}
        self.nat = True
        self.ssd_quota = 2048
        self.cpu_quota = 100
        self.calls = []

    def compute(self, path, **kw):
        self.calls.append((path, kw))
        if path.startswith("aggregated/"):
            return {"items": {"zones/" + r + "-a": {"acceleratorTypes": [{"name": "nvidia-l4"}]}
                              for r in self.responses}}
        if path == "":
            return {"quotas": [{"metric": "GPUS_ALL_REGIONS", "limit": 2, "usage": 0},
                               {"metric": "CPUS_ALL_REGIONS", "limit": 32, "usage": 0}]}
        if path.endswith("/routers"):
            return {"items": [{"network": "https://example/global/networks/default", "nats": [
                {"natIpAllocateOption": "AUTO_ONLY", "sourceSubnetworkIpRangesToNat": "ALL_SUBNETWORKS_ALL_IP_RANGES"}]}]} if self.nat else {"items": []}
        if "/subnetworks/" in path:
            return {"network": "https://example/global/networks/default", "selfLink": "https://example/" + path}
        return {"quotas": [{"metric": metric, "limit": limit, "usage": 0} for metric, limit in
                           [("NVIDIA_L4_GPUS", 1), ("PREEMPTIBLE_NVIDIA_L4_GPUS", 1),
                            ("CPUS", self.cpu_quota), ("SSD_TOTAL_GB", self.ssd_quota)]]}

    def request(self, url, **kw):
        region = url.split("/regions/")[1].split("/")[0]
        response = self.responses[region]
        if isinstance(response, Exception):
            raise response
        return response

    def plan(self, machine=advisor.MACHINE_TYPE):
        return advisor.build_plan(self.compute, self.request, "test", clock=lambda: 1000,
                                  machine_type=machine)


class CapacityAdviceTests(unittest.TestCase):
    def test_probability_times_duration_controls_order(self):
        plan = AdviceFixture().plan()
        self.assertEqual([x["rank_score"] for x in plan["ranked"]], [2880, 540])
        self.assertEqual(plan["ranked"][0]["region"], "asia-east1")

    def test_bad_region_forecast_stays_unknown_and_other_region_survives(self):
        f = AdviceFixture(); f.responses["asia-east1"] = RuntimeError("400 unsupported specification")
        plan = f.plan()
        self.assertEqual(len(plan["ranked"]), 1)
        self.assertEqual(plan["region_reports"][0]["status"], "unknown")

    def test_permission_denial_stops_query(self):
        f = AdviceFixture(); f.responses["asia-east1"] = RuntimeError("403 permission denied")
        with self.assertRaisesRegex(RuntimeError, "403"):
            f.plan()

    def test_bad_scores_and_shapes_are_rejected(self):
        for value in [float("nan"), float("inf"), -1, 1.1, True, None]:
            with self.subTest(value=value), self.assertRaises(ValueError):
                advisor.recommendations(forecast("asia-east1", value), "asia-east1", {"asia-east1-a"}, 1)
        response = forecast("asia-east1"); response["recommendations"][0]["shards"][0]["instanceCount"] = 2
        with self.assertRaises(ValueError):
            advisor.recommendations(response, "asia-east1", {"asia-east1-a"}, 1)

    def test_uptime_is_numeric_seconds_and_invalid_values_fail(self):
        self.assertEqual(advisor.duration_seconds("600s"), 600)
        self.assertEqual(advisor.duration_seconds("60.5s"), 60.5)
        for value in [None, "0s", "-1s", "NaNs", "60", 3600]:
            with self.subTest(value=value), self.assertRaises(ValueError):
                advisor.duration_seconds(value)

    def test_missing_private_egress_marks_candidate_ineligible(self):
        f = AdviceFixture(); f.nat = False
        plan = f.plan()
        self.assertTrue(all(not x["eligible"] for x in plan["ranked"]))
        self.assertIn("existing_private_internet_egress_required", plan["ranked"][0]["allocation_checks"])

    def test_pd_balanced_checks_ssd_quota(self):
        f = AdviceFixture(); f.ssd_quota = 119
        plan = f.plan()
        self.assertIn("regional_quota:pd-balanced", plan["ranked"][0]["allocation_checks"])
        self.assertFalse(plan["ranked"][0]["eligible"])

    def test_larger_host_requests_eight_vcpus_and_fresh_advice(self):
        f = AdviceFixture(); f.cpu_quota = 4
        f.responses = {r: forecast(r, machine=advisor.HOST_MEMORY_FALLBACK) for r in f.responses}
        plan = f.plan(advisor.HOST_MEMORY_FALLBACK)
        self.assertEqual(plan["requested_machine_type"], advisor.HOST_MEMORY_FALLBACK)
        self.assertIn("regional_quota:vCPU", plan["ranked"][0]["allocation_checks"])

    def test_actual_16_gib_host_can_pass_or_fail_available_memory_check(self):
        enough = advisor.host_memory_preflight("MemTotal: 16777216 kB\nMemAvailable: 8388608 kB\n")
        low = advisor.host_memory_preflight("MemTotal: 16777216 kB\nMemAvailable: 2097152 kB\n")
        self.assertTrue(enough["passed"])
        self.assertFalse(low["passed"])


class AllocationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.run = Path(self.tmp.name)
        self.patch = mock.patch.object(controller, "RUN", self.run); self.patch.start()
        self.write("state.json", dict(phase="ready", jobs=[], recovery_launches=0))
        self.write("design_v2.json", dict(deadline_utc="2099-01-01T00:00:00Z", max_gpus=1,
                                        max_gpu_seconds=2700, max_recovery_launches=2))
        self.write("resources.json", dict(project=controller.PROJECT, allocations=[], intents=[], gpu_seconds=0))
        self.reconcile = mock.patch.object(controller, "reconcile_jobs"); self.reconcile.start()
        self.boot = mock.patch.object(controller, "startup", return_value=[dict(key="startup-script", value="fixture")]); self.boot.start()
        self.creates = []; self.step = 0; self.partial = False; self.unknown = False
        self.plan = {"started_at_epoch": time.time(), "ranked": [self.candidate("asia-east1-a", 3240), self.candidate("asia-south1-a", 2880)]}

    def tearDown(self):
        self.boot.stop(); self.reconcile.stop(); self.patch.stop(); self.tmp.cleanup()

    def write(self, name, value):
        path = self.run / name; path.parent.mkdir(parents=True, exist_ok=True); path.write_text(json.dumps(value))

    def candidate(self, zone, score):
        return dict(zone=zone, region=zone.rsplit("-", 1)[0], machine_type=advisor.MACHINE_TYPE,
                    eligible=True, rank_score=score, checked_at_epoch=time.time(),
                    network_interface=dict(network="global/networks/default", subnetwork="regions/" + zone.rsplit("-", 1)[0] + "/subnetworks/default"))

    def compute(self, path, **kw):
        if kw.get("method") == "POST":
            self.creates.append(kw["body"]); self.step += 1
            if self.unknown:
                raise RuntimeError("503 transport outcome unknown")
            return {"name": "op", "selfLink": "https://example/op", "status": "DONE", "attempt": self.step}
        if kw.get("absent"):
            return {"id": "88"} if self.partial and self.step and "/disks/" in path else None
        return dict(id="17", name=controller.NAME, labels={"task": controller.LABEL})

    def allocate(self, first_fails=False, machine=advisor.MACHINE_TYPE):
        def terminal(op):
            if first_fails and op["attempt"] == 1:
                return {"error": {"errors": [{"code": "ZONE_RESOURCE_POOL_EXHAUSTED_WITH_DETAILS"}]}}
            return op
        with mock.patch.object(controller, "compute", side_effect=self.compute), mock.patch.object(controller, "capacity_plan", return_value=self.plan), mock.patch.object(controller, "waitop", side_effect=terminal):
            return controller.allocate({}, machine_type=machine)

    def test_capacity_failure_moves_to_next_rank_and_uses_small_spot_shape(self):
        record = self.allocate(first_fails=True)
        self.assertEqual(record["zone"], "asia-south1-a")
        self.assertEqual([x["machineType"].split("/")[1] for x in self.creates], ["asia-east1-a", "asia-south1-a"])
        self.assertTrue(all(x["machineType"].endswith("g2-standard-4") for x in self.creates))
        self.assertTrue(all(x["scheduling"]["provisioningModel"] == "SPOT" for x in self.creates))
        self.assertLessEqual(record["provider_max_seconds"], 2700)

    def test_unknown_create_outcome_stops_fallback(self):
        self.unknown = True
        with self.assertRaisesRegex(RuntimeError, "unknown"):
            self.allocate()
        self.assertEqual(len(self.creates), 1)
        self.assertEqual(controller.ledger()["intents"][0]["status"], "unknown_or_denied")

    def test_larger_host_fallback_keeps_one_gpu_and_spot_model(self):
        for candidate in self.plan["ranked"]:
            candidate["machine_type"] = advisor.HOST_MEMORY_FALLBACK
        record = self.allocate(machine=advisor.HOST_MEMORY_FALLBACK)
        self.assertTrue(self.creates[0]["machineType"].endswith("g2-standard-8"))
        self.assertEqual(self.creates[0]["scheduling"]["provisioningModel"], "SPOT")
        self.assertEqual(record["gpu_count"], 1)

    def test_highest_unprepared_region_is_skipped_before_mutation(self):
        self.plan["ranked"][0]["eligible"] = False
        record = self.allocate()
        self.assertEqual(record["zone"], "asia-south1-a")
        self.assertEqual(len(self.creates), 1)

    def test_partial_resource_stops_next_allocation(self):
        self.partial = True
        with self.assertRaisesRegex(RuntimeError, "Partial allocation"):
            self.allocate(first_fails=True)
        self.assertEqual(len(self.creates), 1)

    def test_expired_deadline_blocks_create(self):
        self.write("design_v2.json", dict(deadline_utc="2000-01-01T00:00:00Z", max_gpus=1, max_gpu_seconds=2700, max_recovery_launches=2))
        with self.assertRaisesRegex(RuntimeError, "deadline"):
            self.allocate()
        self.assertEqual(self.creates, [])

    def test_consumed_admission_blocks_resume_create(self):
        self.write("state.json", dict(phase="ready", final_admission_consumed=True))
        with self.assertRaisesRegex(RuntimeError, "already consumed"):
            self.allocate()
        self.assertEqual(self.creates, [])

    def test_closed_resume_preserves_scientific_state(self):
        self.write("state.json", dict(phase="closed_partial_capacity_blocked"))
        before = (self.run / "state.json").read_bytes()
        with mock.patch("sys.argv", ["controller.py", "--resume"]), mock.patch.object(controller, "compute", side_effect=AssertionError("cloud mutation")):
            controller.main()
        self.assertEqual(before, (self.run / "state.json").read_bytes())

    def failure_bundle(self, code="HOST_MEMORY_PREFLIGHT_FAILED", machine=advisor.MACHINE_TYPE):
        self.write("gpu_return/compute.json", dict(status="failed", failure_code=code))
        source = controller.sha(controller.HERE / "capacity_advisor.py")
        self.write("gpu_return/host_memory_preflight.json", dict(passed=False, machine_type=machine, source_sha256=source))
        (self.run / "gpu_return.tar.gz").write_bytes(b"verified failure bytes")
        self.write("collection.json", dict(bundle_sha256=hashlib.sha256(b"verified failure bytes").hexdigest()))
        return dict(id="17", deleted=True, cleanup_verified_at="verified", placement=dict(machine_type=machine), capacity_advisor_sha256=source)

    def test_host_memory_failure_archives_bytes_and_requests_one_larger_host(self):
        record = self.failure_bundle()
        self.assertTrue(controller.prepare_host_memory_fallback(record))
        state = json.loads((self.run / "state.json").read_text())
        self.assertEqual(state["allocation_machine_type"], advisor.HOST_MEMORY_FALLBACK)
        self.assertEqual(state["recovery_launches"], 1)
        self.assertFalse(state["final_admission_consumed"])
        self.assertEqual((self.run / "attempts/17/gpu_return.tar.gz").read_bytes(), b"verified failure bytes")
        self.assertFalse((self.run / "collection.json").exists())

    def test_cuda_memory_failure_does_not_trigger_host_upgrade(self):
        record = self.failure_bundle("CUDA_OUT_OF_MEMORY")
        self.assertFalse(controller.prepare_host_memory_fallback(record))
        self.assertTrue((self.run / "collection.json").exists())

    def test_larger_host_preflight_failure_has_no_second_upgrade(self):
        record = self.failure_bundle(machine=advisor.HOST_MEMORY_FALLBACK)
        self.assertFalse(controller.prepare_host_memory_fallback(record))

    def test_host_upgrade_requires_verified_cleanup(self):
        record = self.failure_bundle(); record["deleted"] = False
        with self.assertRaisesRegex(RuntimeError, "cleanup proof"):
            controller.prepare_host_memory_fallback(record)

    def test_recovery_budget_blocks_host_upgrade(self):
        record = self.failure_bundle()
        self.write("state.json", dict(phase="inference_retained", recovery_launches=2))
        self.assertFalse(controller.prepare_host_memory_fallback(record))
        self.assertTrue((self.run / "collection.json").exists())

    def test_failure_flag_requires_matching_failed_memory_report(self):
        record = self.failure_bundle()
        self.write("gpu_return/host_memory_preflight.json", dict(passed=True, machine_type=advisor.MACHINE_TYPE))
        with self.assertRaisesRegex(RuntimeError, "proof mismatch"):
            controller.prepare_host_memory_fallback(record)

    def test_completed_inference_is_preserved_before_any_host_upgrade(self):
        record = self.failure_bundle()
        (self.run / "gpu_return/embeddings.npz").write_bytes(b"existing measurement")
        with self.assertRaisesRegex(RuntimeError, "checkpoint-aware"):
            controller.prepare_host_memory_fallback(record)
        self.assertEqual((self.run / "gpu_return/embeddings.npz").read_bytes(), b"existing measurement")

    def test_cleanup_preserves_old_vm_identity_and_sums_gpu_budget(self):
        old = dict(id="11", zone="asia-east1-a", deleted=True, gpu_seconds=100)
        current = dict(id="17", zone="asia-east1-a", deleted=False, gpu_seconds=200, created_epoch=time.time()-200)
        self.write("resources.json", dict(project=controller.PROJECT, allocations=[old, current], intents=[], gpu_seconds=100))
        with mock.patch.object(controller, "compute", return_value=None):
            controller.cleanup(current)
        records = controller.ledger()["allocations"]
        self.assertEqual(records[0]["id"], "11")
        self.assertEqual(records[0]["gpu_seconds"], 100)
        self.assertEqual(controller.ledger()["gpu_seconds"], 300)

    def test_full_run_orders_memory_failure_cleanup_upgrade_and_success(self):
        self.write("frozen_v2.json", dict(files={}))
        self.write("qwen_selection.json", dict(selected={}, archive={}))
        self.write("encoder_identity.json", dict(model="fixture"))
        self.write("tasks.json", [])
        self.write("extension_cases.json", [])
        events = []; active = {"vm": None, "disk": None, "number": 0}

        def compute(path, **kw):
            if kw.get("method") == "POST":
                self.assertIsNone(active["vm"])
                self.assertIsNone(active["disk"])
                shape = kw["body"]["machineType"].split("/")[-1]
                active.update(vm=shape, disk=shape, number=active["number"]+1)
                events.append("create:" + shape)
                return dict(status="DONE", selfLink="https://example/op")
            if kw.get("method") == "DELETE":
                key = "disk" if "/disks/" in path else "vm"
                events.append("delete:" + key + ":" + active[key]); active[key] = None
                return dict(status="DONE")
            key = "disk" if "/disks/" in path else "vm"
            if active[key] is None:
                return None
            return dict(id=str(16+active["number"]), name=controller.NAME, labels={"task": controller.LABEL})

        def plan(output, machine_type=advisor.MACHINE_TYPE):
            row = self.candidate("asia-east1-a", 3240); row["machine_type"] = machine_type
            return dict(started_at_epoch=time.time(), ranked=[row])

        def collect(payload):
            shape = active["vm"]; events.append("collect:" + shape)
            self.write("gpu_return/compute.json", dict(status="failed" if shape==advisor.MACHINE_TYPE else "complete",
                       failure_code="HOST_MEMORY_PREFLIGHT_FAILED" if shape==advisor.MACHINE_TYPE else None))
            self.write("gpu_return/host_memory_preflight.json", dict(passed=shape!=advisor.MACHINE_TYPE,
                       machine_type=shape, source_sha256=controller.sha(controller.HERE/"capacity_advisor.py")))
            (self.run/"gpu_return.tar.gz").write_bytes(shape.encode())
            self.write("collection.json", dict(bundle_sha256=hashlib.sha256(shape.encode()).hexdigest()))
            return True

        with mock.patch("sys.argv", ["controller.py", "--resume"]), \
             mock.patch.object(controller, "compute", side_effect=compute), \
             mock.patch.object(controller, "capacity_plan", side_effect=plan), \
             mock.patch.object(controller, "waitop", side_effect=lambda op: op), \
             mock.patch.object(controller, "collect", side_effect=collect), \
             mock.patch.object(controller, "closeout", side_effect=lambda: events.append("closeout")), \
             mock.patch.object(controller.subprocess, "check_output", return_value="fixture-source"):
            controller.main()
        self.assertEqual(events, ["create:g2-standard-4", "collect:g2-standard-4", "delete:vm:g2-standard-4",
                         "delete:disk:g2-standard-4", "create:g2-standard-8", "collect:g2-standard-8",
                         "delete:vm:g2-standard-8", "delete:disk:g2-standard-8", "closeout"])
        self.assertTrue((self.run/"attempts/17/collection.json").exists())
        self.assertEqual(json.loads((self.run/"gpu_return/compute.json").read_text())["status"], "complete")
        self.assertTrue(all(x["deleted"] for x in controller.ledger()["allocations"]))


if __name__ == "__main__":
    unittest.main()
