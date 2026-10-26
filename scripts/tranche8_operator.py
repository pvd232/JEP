from _operator import *
if __name__ == "__main__":
    import sys, os
    if not sys.flags.isolated:
        os.execv(sys.executable, [sys.executable, "-I", __file__, *sys.argv[1:]])
    import json, re
    from pathlib import Path
    root = Path("/tmp/jep-tranche8-worker-20261026")
    wanted = {"fresh_audit_v2_seed61029", "inspect_fresh_audit_v2_failure1", "inspect_tranche8_runtime_v3"}
    actions = []
    for path in sorted((root / "actions").glob("*/receipt.json")):
        receipt = json.loads(path.read_text())
        if receipt.get("action_id") not in wanted:
            continue
        directory = path.parent
        entry = {"action_id":receipt["action_id"], "state":receipt.get("status"), "exit_code":receipt.get("returncode"), "exceptions":[], "frames":[]}
        log = directory / "stderr.log"
        if log.exists():
            for line in log.read_text(errors="replace").splitlines():
                if re.match(r"^[A-Za-z_.]*(Error|Exception|Failure):", line):
                    entry["exceptions"].append(line[:1500])
                if line.lstrip().startswith('File "') or "can't open file" in line:
                    entry["frames"].append(line[:500])
        out = directory / "stdout.log"
        if out.exists():
            for line in out.read_text(errors="replace").splitlines():
                if line.startswith("OPERATOR_RESULT "):
                    entry["reported_result"] = json.loads(line[len("OPERATOR_RESULT "):])
        actions.append(entry)
    print("OPERATOR_RESULT " + json.dumps({"phase":"inspect_failure","status":"complete","diagnostic":{"python_runtime":sys.version,"python_executable":sys.executable,"actions":actions}}), flush=True)
