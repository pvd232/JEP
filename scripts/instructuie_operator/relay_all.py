"""Relay the public pinned checkpoint through the existing private GCS bucket."""
import concurrent.futures
import json
import os
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parent
MANIFEST = ROOT / "relay-manifest.json"
DATA = json.loads(MANIFEST.read_text())
PREFIX = "gs://mantra-mlfg-prod-uscentral1-8e7a/jep/instructuie-pilot-20261026/model/" + DATA["revision"]
GCLOUD = "/opt/jep-gcloud/google-cloud-sdk/bin/gcloud"
ENV = dict(os.environ, CLOUDSDK_CORE_CUSTOM_CA_CERTS_FILE="/usr/local/share/ca-certificates/nebula-dns.crt", CLOUDSDK_CORE_DISABLE_USAGE_REPORTING="true")


def relay(entry):
    name = entry["name"]
    receipt = ROOT / (name + ".relay.json")
    if receipt.exists():
        old = json.loads(receipt.read_text())
        if old.get("status") == "verified" and old.get("entry") == entry:
            return old
        raise RuntimeError("Existing relay receipt needs review: " + name)
    started = time.time()
    with (ROOT / (name + ".source.jsonl")).open("a") as source_log, (ROOT / (name + ".upload.log")).open("a") as upload_log:
        producer = subprocess.Popen([sys.executable, str(ROOT / "hf_stream.py"), "--manifest", str(MANIFEST), "--file", name, "--execute"], stdout=subprocess.PIPE, stderr=source_log)
        uploader = subprocess.Popen([GCLOUD, "storage", "cp", "--account=pvd2112@columbia.edu", "--if-generation-match=0", "-", PREFIX + "/" + name], stdin=producer.stdout, stdout=upload_log, stderr=subprocess.STDOUT, env=ENV)
        producer.stdout.close()
        upload_rc = uploader.wait()
        if upload_rc and producer.poll() is None:
            producer.terminate()
        source_rc = producer.wait()
    result = {"status": "verified" if source_rc == upload_rc == 0 else "failed", "entry": entry, "object": PREFIX + "/" + name, "source_exit": source_rc, "upload_exit": upload_rc, "seconds": round(time.time() - started, 2)}
    if result["status"] == "verified":
        obj = subprocess.run([GCLOUD, "storage", "objects", "describe", PREFIX + "/" + name, "--account=pvd2112@columbia.edu", "--format=json"], env=ENV, check=True, capture_output=True, text=True)
        metadata = json.loads(obj.stdout)
        result["generation"] = metadata.get("generation")
        result["gcs_metadata"] = metadata
    receipt.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result), flush=True)
    if result["status"] != "verified":
        raise RuntimeError("Relay failed: " + name)
    return result


if __name__ == "__main__":
    ordered = sorted(DATA["files"], key=lambda e: e["size_bytes"])
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
        list(pool.map(relay, ordered))
    print(json.dumps({"status": "complete", "files": len(ordered), "prefix": PREFIX}), flush=True)
