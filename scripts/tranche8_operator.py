"""Pinned source deployment and owner-only native Tranche 8 orchestration.

The Mac worker invokes these phases separately while full capture runs in its
own supervisor.  Deployment and checks never launch model inference.  Training
requires complete capture, matching gate bindings and a clean checked commit.
"""

import argparse
import base64
import hashlib
import json
import os
import re
import shlex
import shutil
import subprocess
import sys
import tarfile
import time
from pathlib import Path
from typing import Any

REPO = "pvd232/JEP"
MAC_ROOT = Path("/tmp/jep-tranche8-worker-20261026/native")
GEN_ROOT = Path("/tmp/jep-proposition-input-20261026/full_v2_6895d17242704944")
GPU_ROOT = "/home/machina/jep-csts-proposition-lora-20261026"
PARENT_ROOT = "/home/machina/jep-csts-qwen-evidence-20261024"
GPU_PYTHON = "/home/machina/jep-format-env/bin/python"
GCLOUD = "/Users/machina/google-cloud-sdk/bin/gcloud"
FLAGS = ["--account=pvd2112@columbia.edu", "--project=mantra-477901", "--zone=asia-northeast3-a", "--tunnel-through-iap"]
SOURCE_HASHES = {"train.json": "4058b7f63a5285ebdb5061f24f7f2907e76e2ddc7c99480bfd39fc69062a7d01", "dev.json": "f01ec22320c590e381ede0b378895cdd241cd8079e06b18715bc13d2921a4273"}
OPERATION_LOGS = {
    "native_deploy": ["source_init", "source_fetch", "source_identity", "source_pin", "source_bundle", "source_bundle_scp", "source_bundle_permissions", "native_deploy"],
    "native_checks": ["native_checks"],
    "native_import_capture": ["capture_bank_scp", "capture_bank_permissions", "native_import_capture"],
    "native_launch": ["capture_bank_scp", "capture_bank_permissions", "native_import_capture", "native_supervisor_scp", "native_supervisor_permissions", "native_launch"],
    "native_status": ["native_status"],
    "native_archive": ["native_archive"],
    "native_sample": ["native_supervisor_scp", "native_supervisor_permissions", "native_launch"],
}
OWNED = [
    "csts_pilot/proposition_capture.py", "csts_pilot/proposition_inputs.py",
    "csts_pilot/proposition_lora.py", "csts_pilot/proposition_run.py",
    "csts_pilot/proposition_test.py", "csts_pilot/proposition_sample.py",
    "csts_pilot/proposition_archive.py",
    "tests/test_csts_proposition_capture.py", "tests/test_csts_proposition_inputs.py",
    "tests/test_csts_proposition_lora.py", "tests/test_csts_proposition_test.py",
    "tests/test_csts_proposition_sample.py",
    "tests/test_csts_proposition_archive.py",
]


class NativeFailure(RuntimeError):
    """Safe failure details; subprocess logs stay task-private."""


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def save(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n")


def run(argv: list[str], directory: Path, name: str, timeout: int = 120) -> bytes:
    result = subprocess.run(argv, capture_output=True, timeout=timeout, check=False)
    (directory / f"{name}.stdout").write_bytes(result.stdout)
    (directory / f"{name}.stderr").write_bytes(result.stderr)
    if result.returncode:
        raise NativeFailure(f"{name} exited with status {result.returncode}; private logs retained.")
    return result.stdout


def gh_path() -> str:
    executable = shutil.which("gh") or next((str(path) for path in (Path("/opt/homebrew/bin/gh"), Path("/usr/local/bin/gh")) if path.is_file()), None)
    if executable is None:
        raise NativeFailure("The existing gh executable is unavailable.")
    return executable


def fetch_file(path: str, commit: str, directory: Path) -> bytes:
    payload = json.loads(run([gh_path(), "api", f"repos/{REPO}/contents/{path}?ref={commit}"], directory, "fetch_" + Path(path).name))
    if payload.get("type") != "file" or payload.get("encoding") != "base64":
        raise NativeFailure("Pinned source is not a file.")
    data = base64.b64decode("".join(payload["content"].split()), validate=True)
    if hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest() != payload.get("sha"):
        raise NativeFailure("Pinned source Git blob differs.")
    return data


def remote(script: str, directory: Path, label: str, timeout: int = 120) -> dict[str, Any]:
    command = "sudo -n -u machina " + GPU_PYTHON + " -c " + shlex.quote(script)
    output = run([GCLOUD, "compute", "ssh", "jep-csts-format-20261021", *FLAGS, "--command=" + command], directory, label, timeout)
    return json.loads(output)


def copy_to_gpu(path: Path, directory: Path, label: str) -> tuple[str, str]:
    digest = sha(path.read_bytes())
    staging = f"/tmp/jep-tranche8-native-{digest}-{path.name}"
    run([GCLOUD, "compute", "scp", str(path), f"jep-csts-format-20261021:{staging}", *FLAGS], directory, label + "_scp", 240)
    run([GCLOUD, "compute", "ssh", "jep-csts-format-20261021", *FLAGS, "--command=chmod 644 " + shlex.quote(staging)], directory, label + "_permissions", 60)
    return staging, digest


def preamble(commit: str) -> str:
    return (
        "import pathlib,json,hashlib,subprocess,os,shutil,time\n"
        f"root=pathlib.Path({GPU_ROOT!r});parent=pathlib.Path({PARENT_ROOT!r})\n"
        f"commit={commit!r}\n"
        "def git(*args):\n return subprocess.check_output(['git','-C',str(root),*args],text=True).strip()\n"
        "def save(p,v):\n p.write_text(json.dumps(v,ensure_ascii=False,indent=2,allow_nan=False)+'\\n')\n"
        "def digest(p):\n return hashlib.sha256(p.read_bytes()).hexdigest()\n"
        "def clean():\n assert git('rev-parse','HEAD')==commit,'Source commit differs.'\n assert not git('status','--porcelain','--untracked-files=no'),'Tracked source is dirty.'\n"
    )


def native_deploy(commit: str, directory: Path) -> dict[str, Any]:
    """Transport one exact git object graph, preserving existing native stores."""
    source = directory / "source"
    source.mkdir(exist_ok=True)
    if not (source / ".git").exists():
        run(["git", "init", str(source)], directory, "source_init")
    helper = "!" + shlex.quote(gh_path()) + " auth git-credential"
    run(["git", "-C", str(source), "-c", "credential.helper=", "-c", "credential.helper=" + helper, "fetch", "--no-tags", f"https://github.com/{REPO}.git", commit], directory, "source_fetch", 240)
    actual = run(["git", "-C", str(source), "rev-parse", "FETCH_HEAD"], directory, "source_identity").decode().strip()
    if actual != commit:
        raise NativeFailure("Fetched source differs from the pinned commit.")
    run(["git", "-C", str(source), "update-ref", "refs/heads/tranche8-pinned", commit], directory, "source_pin")
    bundle = directory / "source.bundle"
    if bundle.exists():
        bundle = directory / f"source-{time.time_ns()}.bundle"
    run(["git", "-C", str(source), "bundle", "create", str(bundle), "refs/heads/tranche8-pinned"], directory, "source_bundle", 180)
    staging, digest = copy_to_gpu(bundle, directory, "source_bundle")
    script = preamble(commit) + (
        f"bundle=pathlib.Path({staging!r})\nassert digest(bundle)=={digest!r},'Bundle bytes differ.'\n"
        "subprocess.run(['git','-C',str(parent),'fetch',str(bundle),'refs/heads/tranche8-pinned'],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)\n"
        "if root.exists():\n"
        " assert (root/'.git').is_file(),'Existing native root is not a worktree.'\n"
        " dirty=git('diff','HEAD','--name-only').splitlines()\n"
        f" assert set(dirty)<=set({OWNED!r}),'Unexpected local source changes.'\n"
        " for path in dirty:\n"
        "  intended=subprocess.check_output(['git','-C',str(parent),'show',commit+':'+path])\n"
        "  assert (root/path).read_bytes()==intended,'Formatting differs from the published source.'\n"
        " if dirty:\n"
        "  subprocess.run(['git','-C',str(root),'add','--',*dirty],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)\n"
        " if git('rev-parse','HEAD')!=commit:\n"
        "  subprocess.run(['git','-C',str(root),'checkout','--detach',commit],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)\n"
        "else:\n"
        " subprocess.run(['git','-C',str(parent),'worktree','add','--detach',str(root),commit],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)\n"
        "clean()\n"
        "assert not root.is_symlink(),'Native root must be physical.'\n"
        "(root/'csts_data').mkdir(exist_ok=True)\n"
        f"for name,expected in {SOURCE_HASHES!r}.items():\n"
        " source=parent/'csts_data'/name;target=root/'csts_data'/name\n"
        " assert digest(source)==expected,'Original dataset differs.'\n"
        " if target.exists(): assert digest(target)==expected,'Existing dataset differs.'\n"
        " else: shutil.copyfile(source,target)\n"
        " assert not target.is_symlink(),'Native dataset must be physical.'\n"
        "assert (root/'viper.toml').is_file(),'Native storage configuration absent.'\n"
        "usage=shutil.disk_usage(root)\n"
        "print(json.dumps({'phase':'native_deploy','status':'complete','source_commit':commit,'root':str(root),'bundle_sha256':digest(bundle),'free_bytes':usage.free,'physical_datasets':True,'copied_existing_viper_store':False}))\n"
    )
    return remote(script, directory, "native_deploy", 240)


def native_checks(commit: str, directory: Path, allow_format: bool) -> dict[str, Any]:
    """Run owner checks and return only changed task source for publication."""
    script = preamble(commit) + (
        "import ast\nclean()\n"
        f"paths=[p for p in {OWNED!r} if (root/p).is_file()]\n"
        "required={'csts_pilot/proposition_inputs.py','csts_pilot/proposition_lora.py','csts_pilot/proposition_run.py'}\n"
        "assert required<=set(paths),'Native implementation is incomplete.'\n"
        "directory=root/'answer_input_results'/'owner_checks'/commit\ndirectory.mkdir(parents=True,exist_ok=True)\n"
        "before={p:(root/p).read_bytes() for p in paths}\n"
        "environment=os.environ.copy();environment['VIRTUAL_ENV']='/home/machina/jep-format-env';environment['PATH']='/home/machina/jep-format-env/bin:/usr/local/cuda/bin:/usr/local/bin:/usr/bin:/bin'\n"
        f"commands=([['ruff','format',*paths]] if {allow_format!r} else [])+[['ruff','check',*paths],['pyrefly','check','--python-interpreter-path',{GPU_PYTHON!r},*[p for p in paths if p.startswith('csts_pilot/')]],['pytest','-q',*[p for p in paths if p.startswith('tests/')]]]\n"
        "results=[]\n"
        "for index,args in enumerate(commands):\n"
        f" command=[{GPU_PYTHON!r},'-m',*args]\n"
        " outcome=subprocess.run(command,cwd=root,env=environment,capture_output=True,timeout=600,check=False)\n"
        " (directory/(str(index)+'.stdout')).write_bytes(outcome.stdout);(directory/(str(index)+'.stderr')).write_bytes(outcome.stderr)\n"
        " results.append({'check':args[0]+(' '+args[1] if len(args)>1 and args[0]=='ruff' else ''),'returncode':outcome.returncode})\n"
        "changed=[]\n"
        "for p in paths:\n"
        " if (root/p).read_bytes()!=before[p]:\n"
        "  text=(root/p).read_text()\n"
        "  assert ast.dump(ast.parse(before[p]))==ast.dump(ast.parse(text)),'Formatting changed the source AST.'\n"
        "  changed.append({'path':p,'chunks':[text[i:i+12000] for i in range(0,len(text),12000)],'sha256':digest(root/p)})\n"
        f"preflight=subprocess.run([{GPU_PYTHON!r},'-c',\"import json,os,sys;assert sys.prefix=='/home/machina/jep-format-env';assert os.environ.get('VIRTUAL_ENV')==sys.prefix;import torch,viper,ruff,pyrefly;print(json.dumps({{'owner_python_verified':True,'virtual_env_verified':True}}))\"],cwd=root,env=environment,capture_output=True,timeout=60,check=False)\n"
        "(directory/'preflight.stdout').write_bytes(preflight.stdout);(directory/'preflight.stderr').write_bytes(preflight.stderr);results.append({'check':'owner_environment_preflight','returncode':preflight.returncode})\n"
        "receipt={'source_commit':commit,'checks':results,'passed':all(item['returncode']==0 for item in results),'source_clean':not bool(changed),'owned_source_sha256':{p:digest(root/p) for p in paths}}\n"
        "save(directory/'receipt.json',receipt)\n"
        "result={'phase':'native_checks','status':'source_publication_required' if changed else ('complete' if receipt['passed'] else 'failed'),'source_commit':commit,'checks':results,'formatted_files':changed,'verification':receipt}\n"
        "if len(json.dumps(result).encode())>=180000:\n"
        " result['formatted_files']=[{k:v for k,v in item.items() if k!='chunks'} for item in changed];result['source_fetch_required']=True\n"
        "print(json.dumps(result,ensure_ascii=False))\n"
    )
    return remote(script, directory, "native_checks", 1900)


def native_source(commit: str, directory: Path, path: str) -> dict[str, Any]:
    if path not in OWNED:
        raise NativeFailure("Only the fixed owned source allowlist may be fetched.")
    script = preamble(commit) + (
        "assert git('rev-parse','HEAD')==commit,'Source checkout differs.'\n"
        f"path={path!r}\nsource=root/path\nassert source.is_file() and not source.is_symlink()\ntext=source.read_text()\n"
        "result={'phase':'native_source','status':'complete','source_commit':commit,'path':path,'sha256':digest(source),'chunks':[text[i:i+12000] for i in range(0,len(text),12000)]}\n"
        "assert len(json.dumps(result).encode())<180000,'One source file exceeds publication budget.'\nprint(json.dumps(result,ensure_ascii=False))\n"
    )
    return remote(script, directory, "native_source")


def import_capture(commit: str, directory: Path) -> dict[str, Any]:
    """Install a complete generated bank without exposing it in worker status."""
    paths = {"propositions_tranche8.json": GEN_ROOT / "propositions_tranche8.json", "propositions_tranche8_manifest.json": GEN_ROOT / "propositions_tranche8_manifest.json"}
    manifest = json.loads(paths["propositions_tranche8_manifest.json"].read_text())
    if manifest.get("items") != 17334 or manifest.get("records_sha256") != sha(paths["propositions_tranche8.json"].read_bytes()) or set(manifest.get("partitions", {})) != {"training", "validation"} or any(part.get("status") != "complete" for part in manifest["partitions"].values()):
        raise NativeFailure("Full capture is incomplete or its record binding differs.")
    gate = fetch_file("csts_data/propositions_tranche8_audit_gate.json", commit, directory)
    if sha(gate) != manifest.get("audit_gate_sha256"):
        raise NativeFailure("Native source gate differs from the completed capture gate.")
    gate_path = directory / "propositions_tranche8_audit_gate.json"
    gate_path.write_bytes(gate)
    paths[gate_path.name] = gate_path
    hashes = {name: sha(path.read_bytes()) for name, path in paths.items()}
    archive = directory / f"capture-bank-{time.time_ns()}.tar.gz"
    with tarfile.open(archive, "w:gz") as stream:
        for name, path in paths.items():
            stream.add(path, arcname=name, recursive=False)
    staging, digest = copy_to_gpu(archive, directory, "capture_bank")
    script = preamble(commit) + (
        "import tarfile\nclean()\n"
        f"archive=pathlib.Path({staging!r})\nassert digest(archive)=={digest!r}\nexpected={hashes!r}\n"
        "with tarfile.open(archive,'r:gz') as stream:\n"
        " assert set(stream.getnames())==set(expected),'Unexpected bank archive members.'\n"
        " for member in stream.getmembers():\n"
        "  assert member.isfile() and member.name in expected,'Only regular bank files are accepted.'\n"
        "  source=stream.extractfile(member);assert source is not None\n"
        "  data=source.read();assert hashlib.sha256(data).hexdigest()==expected[member.name]\n"
        "  target=root/'csts_data'/member.name\n"
        "  assert not target.is_symlink(),'Capture input must be physical.'\n"
        "  if target.exists(): assert target.read_bytes()==data,'Preserve existing capture input.'\n"
        "  else: target.write_bytes(data)\n"
        "print(json.dumps({'phase':'native_import_capture','status':'complete','source_commit':commit,'source_inputs':expected}))\n"
    )
    return remote(script, directory, "native_import_capture")


def native_launch(commit: str, directory: Path, name: str, module: str = "csts_pilot.proposition_run") -> dict[str, Any]:
    if module not in {"csts_pilot.proposition_run", "csts_pilot.proposition_sample"}:
        raise NativeFailure("Native launch module is outside the fixed allowlist.")
    imported = import_capture(commit, directory) if module == "csts_pilot.proposition_run" else None
    # The supervisor is task source fetched at the same commit, never shell text.
    supervisor = fetch_file("scripts/tranche8_native_supervisor.py", commit, directory)
    local = directory / "tranche8_native_supervisor.py"
    local.write_bytes(supervisor)
    staging, digest = copy_to_gpu(local, directory, "native_supervisor")
    script = preamble(commit) + (
        "clean()\n"
        "checks=json.loads((root/'answer_input_results'/'owner_checks'/commit/'receipt.json').read_text())\n"
        "assert checks.get('passed') is True and checks.get('source_clean') is True,'Owner checks must pass on the executed clean source.'\n"
        "assert all(digest(root/p)==value for p,value in checks['owned_source_sha256'].items()),'Checked source changed.'\n"
        f"name={name!r}\n"
        f"module={module!r}\n"
        "directory=root/'answer_input_results'/'supervisors'/name;directory.mkdir(parents=True,exist_ok=True)\n"
        "receipt=directory/'receipt.json'\n"
        "if receipt.exists():\n print(json.dumps({'phase':'native_launch',**json.loads(receipt.read_text())}))\n"
        "else:\n"
        f" source=pathlib.Path({staging!r});assert digest(source)=={digest!r}\n"
        " target=directory/'supervisor.py';shutil.copyfile(source,target)\n"
        " save(receipt,{'status':'launching','source_commit':commit,'name':name,'module':module,'started_unix':time.time(),'supervisor_sha256':digest(target)})\n"
        " environment=os.environ.copy();environment.update({'VIRTUAL_ENV':'/home/machina/jep-format-env','HF_HOME':'/home/machina/jep-model-cache','HF_HUB_OFFLINE':'1','TRANSFORMERS_OFFLINE':'1','PATH':'/home/machina/jep-format-env/bin:/usr/local/cuda/bin:/usr/local/bin:/usr/bin:/bin'})\n"
        " with (directory/'supervisor.log').open('ab') as log:\n"
        f"  child=subprocess.Popen([{GPU_PYTHON!r},str(target),'--root',str(root),'--parent-root',str(parent),'--name',name,'--source-commit',commit,'--module',module],cwd=root,env=environment,stdin=subprocess.DEVNULL,stdout=log,stderr=log,start_new_session=True)\n"
        " print(json.dumps({'phase':'native_launch','status':'running','source_commit':commit,'name':name,'pid':child.pid}))\n"
    )
    result = remote(script, directory, "native_launch")
    if imported is not None:
        result["capture_import"] = imported
    else:
        result["phase"] = "native_sample"
    return result


def native_status(commit: str, directory: Path, name: str) -> dict[str, Any]:
    script = preamble(commit) + (
        "import fcntl\n"
        f"name={name!r}\nresult={{'phase':'native_status','source_commit':commit,'name':name}}\n"
        "supervisor=root/'answer_input_results'/'supervisors'/name/'receipt.json'\n"
        "result.update(json.loads(supervisor.read_text()) if supervisor.exists() else {'status':'not_started'})\n"
        "if result['status'] in {'launching','running'} and time.time()-result.get('started_unix',time.time())>30:\n"
        " with (supervisor.parent/'supervisor.lock').open('a+') as lock:\n"
        "  try:\n   fcntl.flock(lock.fileno(),fcntl.LOCK_EX|fcntl.LOCK_NB)\n  except BlockingIOError: pass\n  else: result['status']='interrupted'\n"
        "summary=root/'answer_input_results'/name/'summary.json'\n"
        "if summary.exists():\n"
        " value=json.loads(summary.read_text());result['summary']={key:value[key] for key in ('status','in_flight','source_commit','selection','next_phase','selected','failure_reason','seconds') if key in value}\n"
        " result['runs']=[{key:item[key] for key in ('name','status','seconds') if key in item} for item in value.get('runs',[])]\n"
        " if 'result' in value:\n"
        "  result['result']={key:value['result'][key] for key in ('metrics','selection','selected_training_epoch','selected_training_step','completed_epochs','actual_updates','stop_reason','candidate_test_evaluation_ran') if key in value['result']}\n"
        "queue=root/'.viper'/'publication_queue'\n"
        "publication={}\n"
        "for path in queue.glob('*.json'):\n"
        " try:\n  status=json.loads(path.read_text()).get('status','unknown');publication[status]=publication.get(status,0)+1\n except (OSError,ValueError): pass\n"
        "result['publication_counts']=publication;result['free_bytes']=shutil.disk_usage(root).free\n"
        "events=root/'answer_input_results'/name/'events.jsonl'\ntrace_path=None\n"
        "if events.is_file():\n"
        " for line in events.read_text().splitlines():\n"
        "  try: event=json.loads(line)\n  except ValueError: continue\n"
        "  if event.get('event')=='proposition_lora_live_trace' and isinstance(event.get('trace_path'),str):\n"
        "   candidate=pathlib.Path(event['trace_path']).resolve()\n"
        "   if candidate.is_relative_to(root.resolve()): trace_path=candidate\n"
        "if trace_path is not None and trace_path.is_file():\n"
        " try: trace=json.loads(trace_path.read_text())\n except (OSError,ValueError): pass\n"
        " else:\n"
        "  live={key:trace[key] for key in ('status','current_epoch','actual_updates','completed_epoch','selected','epochs_without_improvement') if key in trace}\n"
        "  epochs=trace.get('epochs',[])\n"
        "  if epochs:\n"
        "   latest=epochs[-1];live['latest_epoch']={key:latest[key] for key in ('epoch','step','training_mse_0_1','validation','fit_seconds','validation_seconds','observed_epoch_seconds') if key in latest}\n"
        "  result['training']=live\n"
        "print(json.dumps(result,allow_nan=False))\n"
    )
    return remote(script, directory, "native_status")


def redact(text: str) -> str:
    expression = r"(?:\bsk-[A-Za-z0-9_-]{16,}|\bgh[pousr]_[A-Za-z0-9_]{16,}|\bgithub_pat_[A-Za-z0-9_]{16,}|\bhf_[A-Za-z0-9_]{16,}|\bya29\.[A-Za-z0-9._-]{16,}|\bAIza[A-Za-z0-9_-]{25,}|\bBearer\s+[A-Za-z0-9._~+/-]{16,})"
    text = re.sub(expression, "[REDACTED]", text, flags=re.IGNORECASE)
    return re.sub(r"(?im)^.*(?:authorization|api[_-]?key|access[_-]?token|refresh[_-]?token|password)\s*[:=].*$", "[REDACTED credential assignment]", text)


def operation_diagnostics(commit: str, operation: str) -> dict[str, Any]:
    if operation not in OPERATION_LOGS:
        raise NativeFailure("Operation logs are outside the fixed allowlist.")
    directory = MAC_ROOT / commit / operation
    records = []
    for label in OPERATION_LOGS[operation]:
        path = directory / (label + ".stderr")
        if path.is_file() and not path.is_symlink():
            text = redact(path.read_text(errors="replace")[-24000:])
            if text.strip():
                records.append({"operation": label, "stream": "stderr", "chunks": [text[i:i+12000] for i in range(0, len(text), 12000)]})
    return {"phase": "native_operation_diagnostics", "status": "complete", "source_commit": commit, "operation": operation, "diagnostics": records}


def check_diagnostics(commit: str, directory: Path) -> dict[str, Any]:
    script = preamble(commit) + (
        "assert git('rev-parse','HEAD')==commit\ndirectory=root/'answer_input_results'/'owner_checks'/commit\nrecords=[]\n"
        "for name in ['preflight',*[str(i) for i in range(4)]]:\n"
        " for suffix in ['stdout','stderr']:\n"
        "  path=directory/(name+'.'+suffix)\n"
        "  if path.is_file() and not path.is_symlink():\n"
        "   text=path.read_text(errors='replace')[-12000:]\n"
        "   if text.strip(): records.append({'check':name,'stream':suffix,'text':text})\n"
        "print(json.dumps({'phase':'native_check_diagnostics','status':'complete','source_commit':commit,'diagnostics':records},ensure_ascii=False))\n"
    )
    result = remote(script, directory, "native_check_diagnostics")
    for entry in result.get("diagnostics", []):
        text = redact(entry.pop("text"))
        entry["chunks"] = [text[i:i+12000] for i in range(0, len(text), 12000)]
    return result


def native_archive(commit: str, directory: Path) -> dict[str, Any]:
    script = preamble(commit) + (
        "clean()\n"
        "directory=root/'answer_input_results'/'archive_operator';directory.mkdir(parents=True,exist_ok=True)\n"
        "log_id=str(time.time_ns())\n"
        "environment=os.environ.copy();environment['VIRTUAL_ENV']='/home/machina/jep-format-env';environment['PATH']='/home/machina/jep-format-env/bin:/usr/local/bin:/usr/bin:/bin'\n"
        f"command=[{GPU_PYTHON!r},'-m','csts_pilot.proposition_archive','--root',str(root),'--archive-directory','/home/machina/jep-csts-answer-input-20261026/answer_input_results/proposition_capture_full/full_v2_6895d17242704944']\n"
        "outcome=subprocess.run(command,cwd=root,env=environment,capture_output=True,timeout=600,check=False)\n"
        "(directory/(log_id+'.stdout')).write_bytes(outcome.stdout);(directory/(log_id+'.stderr')).write_bytes(outcome.stderr)\n"
        "result={'phase':'native_archive','status':'failed' if outcome.returncode else 'complete','source_commit':commit,'returncode':outcome.returncode,'promotion_waited':False}\n"
        "for line in outcome.stdout.decode(errors='replace').splitlines():\n"
        " try: event=json.loads(line)\n except ValueError: continue\n"
        " if event.get('event')=='capture_archive_batch_complete':\n"
        "  result.update({key:event[key] for key in ('archives','sealed_bytes','promotion_waited') if key in event})\n"
        "save(directory/'latest.json',{'result':result,'log_id':log_id})\nprint(json.dumps(result,allow_nan=False))\n"
    )
    return remote(script, directory, "native_archive", 660)


def capture_diagnostics() -> dict[str, Any]:
    """Inspect timing and event types only, never prompts or event payload text."""
    now = time.time()
    running = []
    recent = []
    complete: dict[str, int] = {}
    failures = 0
    for split in ("training", "validation"):
        for directory in sorted((GEN_ROOT / split).glob("batch_*")):
            try:
                receipt = json.loads((directory / "receipt.json").read_text())
            except (OSError, ValueError):
                continue
            status = receipt.get("status", "unknown")
            item = {"split": split, "batch": directory.name, "status": status, "items": receipt.get("items"), "started_unix": receipt.get("started_unix")}
            if isinstance(receipt.get("started_unix"), (int, float)):
                item["elapsed_seconds"] = round(receipt.get("elapsed_seconds", now - receipt["started_unix"]), 1)
            if status == "complete":
                complete[split + "/" + directory.name.split("-attempt_")[0]] = receipt.get("items", 0)
                recent.append(item)
            elif status == "failed":
                failures += 1
                recent.append(item)
            elif status == "running":
                stderr_path = directory / "stderr.log"
                if stderr_path.is_file():
                    size = stderr_path.stat().st_size
                    with stderr_path.open("rb") as stream:
                        stream.seek(max(0, size - 262144))
                        inspected = stream.read(262144)
                    text = inspected.decode(errors="replace")
                    patterns = {
                        "capacity": r"capacity|overload|high demand|server busy",
                        "rate_limit": r"\b429\b|rate.?limit|too many requests",
                        "timeout": r"timed? out|timeout|deadline.exceeded",
                        "auth": r"unauthori[sz]ed|authentication|invalid.api.?key|token expired|\b401\b|\b403\b",
                        "policy": r"approval|policy|permission denied|not allowed|access denied",
                        "connection": r"connection|network|socket|\bdns\b|\btls\b|disconnect",
                        "retrying": r"retry|backoff|reconnect",
                    }
                    frequencies = {key: len(re.findall(pattern, text, flags=re.IGNORECASE)) for key, pattern in patterns.items()}
                    item.update(stderr_flags={key: count > 0 for key, count in frequencies.items()}, stderr_counts=frequencies, stderr_bytes_scanned=len(inspected), stderr_scan_truncated=size > len(inspected))
                events = directory / "events.jsonl"
                if events.is_file():
                    item["last_event_age_seconds"] = round(max(0, now - events.stat().st_mtime), 1)
                    event_count = 0
                    last_type = None
                    with events.open() as stream:
                        for line in stream:
                            try:
                                event = json.loads(line)
                            except ValueError:
                                continue
                            event_count += 1
                            value = event.get("type")
                            last_type = value if value in {"thread.started", "turn.started", "item.started", "item.updated", "item.completed", "turn.completed", "turn.failed", "error"} else "unrecognized"
                    item.update(event_count=event_count, last_cli_event_type=last_type)
                pid = receipt.get("pid")
                if isinstance(pid, int) and pid > 1:
                    try:
                        os.kill(pid, 0)
                    except ProcessLookupError:
                        item["process_alive"] = False
                    except PermissionError:
                        item["process_alive"] = True
                    else:
                        item["process_alive"] = True
                    item["pid"] = pid
                running.append(item)
    supervisors = []
    for path in sorted((MAC_ROOT.parent / "full_capture").glob("*/supervisor_receipt.json")):
        try:
            receipt = json.loads(path.read_text())
        except (OSError, ValueError):
            continue
        if receipt.get("output_path") != str(GEN_ROOT):
            continue
        item = {key: receipt[key] for key in ("status", "source_commit", "started_unix", "pid") if key in receipt}
        pid = receipt.get("pid")
        if isinstance(pid, int) and pid > 1:
            try:
                os.kill(pid, 0)
            except ProcessLookupError:
                item["process_alive"] = False
            except PermissionError:
                item["process_alive"] = True
            else:
                item["process_alive"] = True
        supervisors.append(item)
    return {"phase": "capture_diagnostics", "status": "complete", "counts": {"completed_items": sum(complete.values()), "total_items": 17334, "completed_batches": len(complete), "failed_attempts": failures, "running_batches": len(running)}, "running": running[:8], "recent_closed": sorted(recent, key=lambda item: item.get("started_unix") or 0, reverse=True)[:8], "supervisors": supervisors[:4], "observed_unix": now}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--phase", required=True, choices=("native_deploy", "native_checks", "native_source", "native_import_capture", "native_launch", "native_sample", "native_status", "native_check_diagnostics", "native_operation_diagnostics", "native_archive", "capture_diagnostics"))
    parser.add_argument("--source-commit", required=True)
    parser.add_argument("--name", default="proposition_lora_v2")
    parser.add_argument("--allow-format", action="store_true")
    parser.add_argument("--path", choices=OWNED)
    parser.add_argument("--operation", choices=tuple(OPERATION_LOGS))
    args = parser.parse_args()
    if re.fullmatch(r"[0-9a-f]{40}", args.source_commit) is None or re.fullmatch(r"[A-Za-z0-9_-]{1,80}", args.name) is None:
        parser.error("Use a complete source commit and a safe attempt name.")
    directory = MAC_ROOT / args.source_commit / args.phase
    directory.mkdir(parents=True, exist_ok=True)
    try:
        if args.phase == "native_deploy":
            result = native_deploy(args.source_commit, directory)
        elif args.phase == "native_checks":
            result = native_checks(args.source_commit, directory, args.allow_format)
        elif args.phase == "native_import_capture":
            result = import_capture(args.source_commit, directory)
        elif args.phase == "native_source":
            if args.path is None:
                raise NativeFailure("native_source requires a fixed allowlisted path.")
            result = native_source(args.source_commit, directory, args.path)
        elif args.phase == "native_launch":
            result = native_launch(args.source_commit, directory, args.name)
        elif args.phase == "native_sample":
            if args.name == "proposition_lora_v2":
                raise NativeFailure("Use a separate explicit --name for the frozen sample diagnostic.")
            result = native_launch(args.source_commit, directory, args.name, "csts_pilot.proposition_sample")
        elif args.phase == "native_check_diagnostics":
            result = check_diagnostics(args.source_commit, directory)
        elif args.phase == "native_operation_diagnostics":
            if args.operation is None:
                raise NativeFailure("native_operation_diagnostics requires an allowlisted operation.")
            result = operation_diagnostics(args.source_commit, args.operation)
        elif args.phase == "native_archive":
            result = native_archive(args.source_commit, directory)
        elif args.phase == "capture_diagnostics":
            result = capture_diagnostics()
        else:
            result = native_status(args.source_commit, directory, args.name)
    except Exception as error:
        result = {"phase": args.phase, "status": "failed", "error": str(error) if isinstance(error, NativeFailure) else "Native phase failed; private logs retained."}
        print("OPERATOR_RESULT " + json.dumps(result), flush=True)
        raise SystemExit(1) from None
    save(directory / "result.json", result)
    print("OPERATOR_RESULT " + json.dumps(result, ensure_ascii=False, allow_nan=False), flush=True)


if __name__ == "__main__":
    main()
