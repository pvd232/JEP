"""Rank one-L4 Spot placements using current capacity advice and existing resources."""

import math
import re
import time
import urllib.parse

MACHINE_TYPE = "g2-standard-4"
HOST_MEMORY_FALLBACK = "g2-standard-8"
MAX_ATTEMPTS = 9
ADVICE_TTL_SECONDS = 120


def duration_seconds(value):
    """Parse a positive protobuf Duration expressed in seconds."""
    if not isinstance(value, str) or not re.fullmatch(r"\d+(?:\.\d{1,9})?s", value):
        raise ValueError("Expected an estimatedUptime Duration ending in s")
    seconds = float(value[:-1])
    if not math.isfinite(seconds) or seconds <= 0:
        raise ValueError("Expected positive finite uptime")
    return seconds


def remaining(quotas, metric):
    """Return observed quota headroom, preserving missing values as unknown."""
    row = next((q for q in quotas if q.get("metric") == metric), None)
    if row is None:
        return None
    limit, usage = row.get("limit"), row.get("usage")
    if any(type(x) not in (int, float) or not math.isfinite(x) for x in [limit, usage]):
        return None
    return limit - usage


def spot_headroom(quotas, specific, ordinary):
    """Use a positive dedicated Spot quota, falling back to ordinary quota."""
    row = next((q for q in quotas if q.get("metric") == specific), {})
    if type(row.get("limit")) in (int, float) and row["limit"] > 0:
        return remaining(quotas, specific)
    return remaining(quotas, ordinary)


def existing_network(compute, region):
    """Find a default-VPC subnet covered by an existing public VM Cloud NAT."""
    routers = compute("regions/" + region + "/routers", timeout=20)
    for router in routers.get("items", []):
        network = router.get("network", "")
        if not network.endswith("/global/networks/default"):
            continue
        for nat in router.get("nats", []):
            if nat.get("type", "PUBLIC") != "PUBLIC":
                continue
            if nat.get("natIpAllocateOption") not in {"AUTO_ONLY", "MANUAL_ONLY"}:
                continue
            if "ENDPOINT_TYPE_VM" not in nat.get("endpointTypes", ["ENDPOINT_TYPE_VM"]):
                continue
            scope = nat.get("sourceSubnetworkIpRangesToNat")
            if scope in {"ALL_SUBNETWORKS_ALL_IP_RANGES", "ALL_SUBNETWORKS_ALL_PRIMARY_IP_RANGES"}:
                subnets = ["default"]
            elif scope == "LIST_OF_SUBNETWORKS":
                subnets = [x["name"].rsplit("/", 1)[-1] for x in nat.get("subnetworks", [])
                           if "PRIMARY_IP_RANGE" in x.get("sourceIpRangesToNat", [])
                           or "ALL_IP_RANGES" in x.get("sourceIpRangesToNat", [])]
            else:
                continue
            for name in subnets:
                subnet = compute("regions/" + region + "/subnetworks/" + name, timeout=20)
                if subnet.get("network") == network:
                    return {"network": network, "subnetwork": subnet["selfLink"]}
    return None


def recommendations(response, region, zones, checked_at, machine_type=MACHINE_TYPE):
    """Validate advisory placements and derive the requested probability-time score."""
    result = []
    for rec in response.get("recommendations", []):
        scores = rec.get("scores", {})
        probability = scores.get("obtainability")
        if type(probability) not in (int, float) or not math.isfinite(probability):
            raise ValueError("Missing finite obtainability")
        if not 0 <= probability <= 1:
            raise ValueError("Obtainability must be between zero and one")
        seconds = duration_seconds(scores.get("estimatedUptime"))
        shards = rec.get("shards", [])
        if len(shards) != 1:
            raise ValueError("Expected one VM placement")
        shard = shards[0]
        zone = shard.get("zone", "").rsplit("/", 1)[-1]
        if (zone not in zones or zone.rsplit("-", 1)[0] != region
                or shard.get("machineType") != machine_type
                or type(shard.get("instanceCount")) is not int
                or shard["instanceCount"] != 1
                or shard.get("provisioningModel") != "SPOT"):
            raise ValueError("Advisor returned a placement outside the requested one-L4 Spot shape")
        result.append(dict(region=region, zone=zone, machine_type=machine_type,
                           provisioning_model="SPOT", obtainability=probability,
                           estimated_spot_seconds=seconds, rank_score=probability * seconds,
                           checked_at_epoch=checked_at))
    if not result:
        raise ValueError("Capacity forecast unknown: empty recommendations")
    return result


def build_plan(compute, request, project, clock=time.time, machine_type=MACHINE_TYPE):
    """Query current advice; rank every forecast and mark deployable existing networks."""
    started = clock()
    if machine_type not in {MACHINE_TYPE, HOST_MEMORY_FALLBACK}:
        raise ValueError("Expected a supported single-L4 machine type")
    vcpus = 4 if machine_type == MACHINE_TYPE else 8
    inventory = []
    page = None
    seen = set()
    while True:
        query = {"filter": "name = nvidia-l4", "maxResults": 500}
        if page:
            query["pageToken"] = page
        listing = compute("aggregated/acceleratorTypes?" + urllib.parse.urlencode(query), timeout=20)
        inventory.extend(k.rsplit("/", 1)[-1] for k, v in listing.get("items", {}).items()
                         if any(a.get("name") == "nvidia-l4" for a in v.get("acceleratorTypes", [])))
        page = listing.get("nextPageToken")
        if not page:
            break
        if page in seen or len(seen) >= 10:
            raise ValueError("Accelerator catalog pagination is unresolved")
        seen.add(page)
    zones = set(inventory)
    global_quota = compute("", timeout=20).get("quotas", [])
    global_reasons = []
    for metric, needed in [("GPUS_ALL_REGIONS", 1), ("CPUS_ALL_REGIONS", vcpus)]:
        free = remaining(global_quota, metric)
        if free is None or free < needed:
            global_reasons.append("global_quota:" + metric)
    body = {"instanceProperties": {"scheduling": {"provisioningModel": "SPOT"}},
            "instanceFlexibilityPolicy": {"instanceSelections": {"l4": {"machineTypes": [machine_type]}}},
            "distributionPolicy": {"targetShape": "ANY_SINGLE_ZONE"}, "size": 1}
    reports, candidates = [], []
    for region in sorted({z.rsplit("-", 1)[0] for z in zones}):
        if clock() - started > 120:
            reports.append(dict(region=region, status="unknown", error="Planning time budget reached"))
            continue
        report = dict(region=region, status="unknown")
        try:
            url = "https://compute.googleapis.com/compute/beta/projects/" + project + "/regions/" + region + "/advice/capacity"
            response = request(url, method="POST", body=body, timeout=20)
            report["response"] = response
            rows = recommendations(response, region, zones, clock(), machine_type)
            quotas = compute("regions/" + region, timeout=20).get("quotas", [])
            reasons = list(global_reasons)
            for metric, needed, free in [
                ("L4", 1, spot_headroom(quotas, "PREEMPTIBLE_NVIDIA_L4_GPUS", "NVIDIA_L4_GPUS")),
                ("vCPU", vcpus, spot_headroom(quotas, "PREEMPTIBLE_CPUS", "CPUS")),
                ("pd-balanced", 120, remaining(quotas, "SSD_TOTAL_GB")),
            ]:
                if free is None or free < needed:
                    reasons.append("regional_quota:" + metric)
            interface = existing_network(compute, region)
            if interface is None:
                reasons.append("existing_private_internet_egress_required")
            for row in rows:
                row.update(network_interface=interface, allocation_checks=list(reasons),
                           eligible=not reasons and row["obtainability"] > 0)
                if row["obtainability"] == 0:
                    row["allocation_checks"].append("zero_obtainability")
                candidates.append(row)
            report.update(status="forecast", quotas=quotas, network_interface=interface)
        except (RuntimeError, ValueError, KeyError, TypeError, AttributeError) as error:
            report["error"] = str(error)
            if str(error).startswith(("401 ", "403 ")):
                raise
        reports.append(report)
    candidates.sort(key=lambda r: (-r["rank_score"], -r["obtainability"], r["zone"]))
    # A region can return alternative recommendations for the same zone.
    unique, seen_zones = [], set()
    for row in candidates:
        if row["zone"] not in seen_zones:
            unique.append(row)
            seen_zones.add(row["zone"])
    return dict(project=project, requested_machine_type=machine_type, gpu_count=1,
                provisioning_model="SPOT", score="obtainability * estimated_spot_seconds",
                created_at_epoch=clock(), started_at_epoch=started,
                ranked=unique, region_reports=reports, global_quota=global_quota)


def host_memory_preflight(text, minimum_total_gib=14, minimum_available_gib=4):
    """Check host memory before model loading and retain measured headroom."""
    fields = {line.split(":", 1)[0]: int(line.split()[1]) * 1024
              for line in text.splitlines() if line.startswith(("MemTotal:", "MemAvailable:"))}
    total, available = fields["MemTotal"] / 2**30, fields["MemAvailable"] / 2**30
    result = dict(total_gib=total, available_gib=available,
                  minimum_total_gib=minimum_total_gib, minimum_available_gib=minimum_available_gib)
    result["passed"] = total >= minimum_total_gib and available >= minimum_available_gib
    return result
