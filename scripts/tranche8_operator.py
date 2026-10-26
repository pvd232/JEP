"""Fetch only owner-verified formatting changes as a compressed source bundle."""

import argparse
import json
import shlex
import subprocess


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-commit", required=True)
    args = parser.parse_args()
    if len(args.source_commit) != 40 or any(c not in "0123456789abcdef" for c in args.source_commit):
        parser.error("Use a complete source commit.")
    script = """import pathlib,subprocess,json,hashlib,zlib,base64,ast
root=pathlib.Path('/home/machina/jep-csts-proposition-lora-20261026')
commit=COMMIT
assert subprocess.check_output(['git','-C',str(root),'rev-parse','HEAD'],text=True).strip()==commit
receipt=json.loads((root/'answer_input_results/owner_checks'/commit/'receipt.json').read_text())
files=[]
for name,expected in receipt['owned_source_sha256'].items():
 assert name.startswith(('csts_pilot/proposition_','tests/test_csts_proposition_')) and name.endswith('.py') and '..' not in name
 path=root/name
 assert path.is_file() and not path.is_symlink()
 content=path.read_bytes()
 assert hashlib.sha256(content).hexdigest()==expected
 old=subprocess.check_output(['git','-C',str(root),'show',commit+':'+name])
 assert ast.dump(ast.parse(old))==ast.dump(ast.parse(content))
 files.append({'path':name,'sha256':expected,'content':content.decode()})
data=json.dumps(files,ensure_ascii=False).encode()
encoded=base64.b64encode(zlib.compress(data)).decode()
print(json.dumps({'phase':'formatted_source_bundle','status':'complete','source_commit':commit,'bundle_sha256':hashlib.sha256(data).hexdigest(),'files':len(files),'uncompressed_bytes':len(data),'chunks':[encoded[i:i+12000] for i in range(0,len(encoded),12000)]}))
""".replace("COMMIT", repr(args.source_commit))
    command = "sudo -n -u machina /home/machina/jep-format-env/bin/python -c " + shlex.quote(script)
    result = subprocess.run([
        "/Users/machina/google-cloud-sdk/bin/gcloud", "compute", "ssh",
        "jep-csts-format-20261021", "--account=pvd2112@columbia.edu",
        "--project=mantra-477901", "--zone=asia-northeast3-a",
        "--tunnel-through-iap", "--command=" + command,
    ], capture_output=True, text=True, timeout=120, check=False)
    if result.returncode:
        raise SystemExit("Owner formatting export failed; native files preserved.")
    value = json.loads(result.stdout)
    print("OPERATOR_RESULT " + json.dumps(value, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
