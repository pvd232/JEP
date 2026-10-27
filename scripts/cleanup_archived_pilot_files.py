"""Preview cloud-backed VIPER artifact files and their matching cached aliases."""

import argparse
import base64
import fcntl
import hashlib
import json
import os
import shutil
import stat
import sys
from collections import defaultdict
from pathlib import Path

from viper.cloud import ViperCloud
from viper.references import ResolvedFileRef, ResolvedRunRef
from viper.runs import ResolvedRun, RunAttempt
from viper.serialization import parse_yaml_bytes
from viper.workspace import RunWorkspaceLock


def fingerprint(path):
    s = path.stat()
    return [s.st_dev, s.st_ino, s.st_size, s.st_mtime_ns, s.st_ctime_ns]


def safe_file(root, path):
    try:
        relative = path.relative_to(root)
        if ".." in relative.parts:
            return False
        current = root
        for part in relative.parts:
            current /= part
            if current.is_symlink():
                return False
        return stat.S_ISREG(path.lstat().st_mode)
    except (OSError, ValueError):
        return False


def cloud_record(root, reference):
    if reference.stored_at.kind not in {"gcs", "huggingface", "viper_cloud"}:
        raise ValueError("Cloud reference required")
    raw = ViperCloud.for_reference(root, reference.stored_at).fetch(reference.stored_at)
    if len(raw) != reference.bytes or hashlib.sha256(raw).hexdigest() != reference.sha256:
        raise ValueError("Cloud record identity differs")
    return raw


def artifact_path(path):
    parts = Path(path).parts
    return len(parts) >= 9 and parts[0] == "experiments" and parts[5] == "artifacts"


def has_large_run_files(root, terminal_path, minimum):
    """Filter small local runs before requesting their cloud graph."""
    relative = Path(terminal_path)
    if len(relative.parts) != 6 or relative.parts[0] != "experiments" or relative.parts[2] != "runs" or ".." in relative.parts:
        return False
    artifacts = relative.parent / "artifacts"
    locations = [root / artifacts]
    store = root / ".viper/store"
    if store.is_dir() and not store.is_symlink():
        locations.extend(store.glob("*/" + artifacts.as_posix()))
    for location in locations:
        if location.is_symlink():
            continue
        for base, dirs, names in os.walk(location, followlinks=False):
            dirs[:] = [d for d in dirs if not (Path(base) / d).is_symlink()]
            for name in names:
                path = Path(base) / name
                if safe_file(root, path) and path.stat().st_size >= minimum:
                    return True
    return False


def verify_cloud_metadata(identity, files):
    """Match a sealed SHA identity to live GCS server-computed CRC32C."""
    ref = ResolvedFileRef.model_validate(identity["reference"])
    location = ref.stored_at
    if location.kind != "gcs":
        raise ValueError("Metadata verification requires GCS")
    provider = ViperCloud.for_reference(Path(identity["root"]), location).provider
    members = provider._load_manifest(location.owner, location.workspace, location.revision).files
    if not any(f.path == location.path and f.sha256 == ref.sha256 and f.bytes == ref.bytes for f in members):
        raise ValueError("Object is absent from its sealed manifest")
    # Use the provider's canonical address implementation.
    key = provider._file_key(location.owner, location.workspace, location.revision, location.path)
    blob = provider.bucket.blob(key)
    blob.reload(timeout=provider.operation_timeout)
    metadata = blob.metadata or {}
    crc = files[0].get("crc32c")
    if not crc or int(blob.size) != ref.bytes or metadata.get("sha256") != ref.sha256 or metadata.get("bytes") != str(ref.bytes) or blob.generation is None or blob.crc32c != crc:
        raise ValueError("Live GCS checksum, size or metadata differs")
    return {"method": "sealed_sha256_and_local_sha256_plus_live_server_crc32c", "generation": str(blob.generation), "crc32c": crc, "bytes": ref.bytes, "sha256": ref.sha256, "object_key": key}


def apply_plan(plan, args, verified_hashes=None):
    """Retain an exclusive durable restoration receipt before releasing copies."""
    if not (args.verify_cloud or getattr(args, "verify_cloud_metadata", False)) or not args.receipt or any(not p["cloud_verified"] for p in plan["candidates"]):
        raise ValueError("Apply requires verified cloud candidates and a new receipt")
    device = args.disk_path.stat().st_dev
    checked = {}
    for group in plan["candidates"]:
        for file in group["files"]:
            path = Path(file["path"])
            if not safe_file(Path(file["root"]), path) or fingerprint(path) != file["fingerprint"] or path.stat().st_dev != device:
                raise ValueError("Apply candidate identity or disk differs")
            key = tuple(file["fingerprint"])
            if verified_hashes is not None and key in verified_hashes:
                checked[key] = verified_hashes[key]
            elif key not in checked:
                with path.open("rb") as stream:
                    checked[key] = hashlib.file_digest(stream, "sha256").hexdigest()
            if checked[key] != group["sha256"] or fingerprint(path) != file["fingerprint"]:
                raise ValueError("Apply candidate bytes changed")
    args.receipt.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    descriptor = os.open(args.receipt, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    with os.fdopen(descriptor, "w") as stream:
        json.dump(plan, stream, indent=2)
        stream.write("\n")
        stream.flush()
        os.fsync(stream.fileno())
    directory = os.open(args.receipt.parent, os.O_RDONLY | os.O_DIRECTORY)
    os.fsync(directory)
    os.close(directory)
    deleted, groups = 0, 0
    for group in plan["candidates"]:
        if shutil.disk_usage(args.disk_path).free >= args.free_gib * 2**30:
            break
        for file in group["files"]:
            if not safe_file(Path(file["root"]), Path(file["path"])) or fingerprint(Path(file["path"])) != file["fingerprint"]:
                raise ValueError("Group changed after receipt was saved")
        for file in group["files"]:
            Path(file["path"]).unlink()
            deleted += 1
        for parent in {Path(f["path"]).parent for f in group["files"]}:
            descriptor = os.open(parent, os.O_RDONLY | os.O_DIRECTORY)
            os.fsync(descriptor)
            os.close(descriptor)
        groups += 1
        print(json.dumps({"event": "released_group", "sha256": group["sha256"], "files": len(group["files"]), "disk_free_bytes": shutil.disk_usage(args.disk_path).free}), file=sys.stderr, flush=True)
    free_bytes = shutil.disk_usage(args.disk_path).free
    return {"status": "applied", "target_met": free_bytes >= args.free_gib * 2**30, "deleted_files": deleted, "released_groups": groups, "disk_free_bytes": free_bytes, "restoration_receipt": str(args.receipt)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", action="append", type=Path, required=True)
    parser.add_argument("--minimum-mib", type=int, default=128)
    parser.add_argument("--target-gib", type=float, default=50)
    parser.add_argument("--verify-cloud", action="store_true")
    parser.add_argument("--verify-cloud-metadata", action="store_true")
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--receipt", type=Path)
    parser.add_argument("--free-gib", type=float, default=50)
    parser.add_argument("--disk-path", type=Path, default=Path("/home/machina"))
    parser.add_argument("--gpu-lock", type=Path, default=Path("/home/machina/jep-csts-qwen-evidence-20261024/.viper/overnight_gpu.lock"))
    args = parser.parse_args()
    if args.minimum_mib < 1 or args.target_gib <= 0 or args.free_gib <= 0:
        parser.error("Size limits require positive values")
    if args.verify_cloud and args.verify_cloud_metadata:
        parser.error("Choose one cloud verification mode")
    if args.apply and (not (args.verify_cloud or args.verify_cloud_metadata) or args.receipt is None or args.receipt.exists()):
        parser.error("--apply requires cloud verification and an unused --receipt path")
    roots = [r.resolve(strict=True) for r in args.root]
    identities, paths, issues, receipts = {}, {}, [], []
    hash_cache, crc_cache, held = {}, {}, []

    def digest(path):
        before = fingerprint(path)
        identity = tuple(before)
        if identity not in hash_cache:
            if args.verify_cloud_metadata:
                import google_crc32c

                sha, crc = hashlib.sha256(), google_crc32c.Checksum()
                with path.open("rb") as stream:
                    while block := stream.read(8 * 2**20):
                        sha.update(block)
                        crc.update(block)
                hash_cache[identity] = sha.hexdigest()
                crc_cache[identity] = base64.b64encode(crc.digest()).decode("ascii")
            else:
                with path.open("rb") as stream:
                    hash_cache[identity] = hashlib.file_digest(stream, "sha256").hexdigest()
        if fingerprint(path) != before:
            raise ValueError("Local file changed")
        return hash_cache[identity], before

    def file_entry(path, role, sha, fp, root):
        observed = path.stat()
        return {"root": str(root), "path": str(path), "role": role, "sha256": sha, "crc32c": crc_cache.get(tuple(fp)), "bytes": fp[2], "fingerprint": fp, "links": observed.st_nlink, "allocated_bytes": observed.st_blocks * 512, "mode": stat.S_IMODE(observed.st_mode), "uid": observed.st_uid, "gid": observed.st_gid}

    try:
        if args.apply:
            descriptor = os.open(args.gpu_lock, os.O_RDONLY)
            try:
                fcntl.flock(descriptor, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except OSError:
                os.close(descriptor)
                raise
            held.append(descriptor)
        for root in roots:
            busy = False
            for lock_path in (root / ".viper/workspaces").glob("*/.active.lock"):
                try:
                    # Opening existing locks read-only preserves their bytes and owners.
                    lock = RunWorkspaceLock.for_run(root / ".viper/workspaces", lock_path.parent.name)
                    descriptor = os.open(lock.path, os.O_RDONLY)
                    try:
                        fcntl.flock(descriptor, fcntl.LOCK_EX | fcntl.LOCK_NB)
                    except OSError:
                        os.close(descriptor)
                        raise
                    held.append(descriptor)
                except OSError:
                    issues.append({"root": str(root), "status": "active_or_unreadable_workspace", "lock": str(lock_path)})
                    busy = True
            if busy:
                continue
            sources = []
            for queue in sorted((root / ".viper/publication_queue").glob("*.json")):
                try:
                    entry = json.loads(queue.read_text())
                    if entry.get("status") != "published" or entry["request"]["root"] != str(root):
                        continue
                    sources.append((queue, ResolvedRunRef.model_validate(entry["reference"])))
                except Exception as error:
                    issues.append({"root": str(root), "source": str(queue), "error_type": type(error).__name__})
            for sidecar in sorted(root.glob("experiments/*/runs/*/*/resolved.ref.yaml")):
                try:
                    sources.append((sidecar, ResolvedRunRef.model_validate(parse_yaml_bytes(sidecar.read_bytes()))))
                except Exception as error:
                    issues.append({"root": str(root), "source": str(sidecar), "error_type": type(error).__name__})
            seen_cloud_runs = set()
            large_runs = {}
            for source, reference in sources:
                try:
                    if reference.stored_at.kind != "gcs" or reference.sha256 in seen_cloud_runs:
                        continue
                    relative = reference.stored_at.path
                    if relative not in large_runs:
                        large_runs[relative] = has_large_run_files(root, relative, args.minimum_mib * 2**20)
                    if not large_runs[relative]:
                        continue
                    print(json.dumps({"event": "read_cloud_run", "root": str(root), "source": str(source)}), file=sys.stderr, flush=True)
                    terminal = cloud_record(root, reference)
                    run = ResolvedRun.model_validate(parse_yaml_bytes(terminal))
                    if run.status != "succeeded" or run.successful_attempt_id is None:
                        continue
                    attempt = None
                    attempt_ref = None
                    for selected in run.attempts:
                        candidate = RunAttempt.model_validate(parse_yaml_bytes(cloud_record(root, selected)))
                        if candidate.attempt_id == run.successful_attempt_id:
                            attempt, attempt_ref = candidate, selected
                            break
                    if attempt is None or attempt.status != "succeeded" or attempt.purpose != "run":
                        raise ValueError("Successful cloud attempt unavailable")
                    seen_cloud_runs.add(reference.sha256)
                    receipts.append({"root": str(root), "source": str(source), "cloud_run": reference.model_dump(mode="json"), "cloud_attempt": attempt_ref.model_dump(mode="json")})
                    for stage in attempt.resolved_stages:
                        if stage.snapshot.kind == "local":
                            raise ValueError("Cloud attempt contains local stage")
                        cloud = ViperCloud.for_snapshot(root, stage.snapshot)
                        for file in cloud.list_files(stage.snapshot):
                            if not artifact_path(file.path) or file.bytes < args.minimum_mib * 2**20:
                                continue
                            key = (file.sha256, file.bytes)
                            ref = ResolvedFileRef(sha256=file.sha256, bytes=file.bytes, stored_at=cloud.file_ref(stage.snapshot, file.path))
                            identities.setdefault(key, {"root": str(root), "reference": ref.model_dump(mode="json")})
                            path = root / file.path
                            if safe_file(root, path):
                                sha, fp = digest(path)
                                if (sha, fp[2]) != key:
                                    raise ValueError("Local artifact differs from sealed cloud identity")
                                paths[str(path)] = file_entry(path, "artifact", sha, fp, root)
                except Exception as error:
                    issues.append({"root": str(root), "source": str(source), "error_type": type(error).__name__})
            # Every alias must match one sealed produced-artifact identity.
            sizes = {size for sha, size in identities}
            for subtree in (root / ".viper/store", root / ".viper/workspaces", root / ".viper/cache/verified-objects"):
                if subtree.is_symlink():
                    continue
                for base, dirs, names in os.walk(subtree, followlinks=False):
                    dirs[:] = [d for d in dirs if not (Path(base) / d).is_symlink()]
                    for name in names:
                        path = Path(base) / name
                        if not safe_file(root, path) or path.stat().st_size not in sizes:
                            continue
                        sha, fp = digest(path)
                        if (sha, fp[2]) in identities:
                            paths[str(path)] = file_entry(path, "cached_alias", sha, fp, root)
        groups = defaultdict(list)
        for file in paths.values():
            groups[(file["sha256"], file["bytes"])].append(file)
        plans, estimate = [], 0
        for key, files in sorted(groups.items(), key=lambda pair: -sum(f["allocated_bytes"] for f in pair[1])):
            if estimate >= args.target_gib * 2**30:
                break
            identity = identities[key]
            cloud_proof = None
            if args.verify_cloud:
                ref = ResolvedFileRef.model_validate(identity["reference"])
                print(json.dumps({"event": "verify_cloud", "sha256": key[0], "bytes": key[1]}), file=sys.stderr, flush=True)
                ViperCloud.for_reference(Path(identity["root"]), ref.stored_at).verify_file(ref)
                cloud_proof = {"method": "fresh_cloud_payload_sha256", "sha256": key[0], "bytes": key[1]}
            elif args.verify_cloud_metadata:
                print(json.dumps({"event": "verify_cloud_metadata", "sha256": key[0], "bytes": key[1]}), file=sys.stderr, flush=True)
                cloud_proof = verify_cloud_metadata(identity, files)
            inodes = defaultdict(list)
            for file in files:
                if fingerprint(Path(file["path"])) != file["fingerprint"]:
                    raise ValueError("Candidate changed during preview")
                inodes[tuple(file["fingerprint"][:2])].append(file)
            physical = sum(items[0]["allocated_bytes"] for items in inodes.values() if len(items) == items[0]["links"])
            estimate += physical
            plans.append({"sha256": key[0], "bytes": key[1], "reference": identity["reference"], "cloud_verified": bool(cloud_proof), "cloud_verification": cloud_proof, "estimated_releasable_bytes": physical, "files": files})
        plan = {"status": "preview_only", "deletions": 0, "estimated_releasable_bytes": estimate, "requires_apply_time_revalidation_and_locks": True, "receipts": receipts, "candidates": plans, "issues": issues}
        if args.apply:
            print(json.dumps(apply_plan(plan, args, hash_cache), indent=2), flush=True)
        else:
            print(json.dumps(plan, indent=2), flush=True)
    finally:
        for descriptor in held:
            os.close(descriptor)


if __name__ == "__main__":
    main()
