"""Stream one manifest-pinned public HF file to stdout with inline verification.

Use only in a binary pipeline, for example into `gcloud storage cp - gs://...`.
This program never writes model bytes to local disk. The caller checks both
pipeline exit statuses and verifies the completed file again on the GPU VM.
"""

import argparse
import hashlib
import json
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--file", required=True)
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    manifest = json.loads(args.manifest.read_text())
    entry = next(x for x in manifest["files"] if x["name"] == args.file)
    if not args.execute:
        print(json.dumps({"status": "planned", "file": entry,
                          "model_revision": manifest["revision"]}, indent=2))
        return 0
    url = (
        "https://huggingface.co/" + manifest["model_id"] + "/resolve/"
        + manifest["revision"] + "/" + urllib.parse.quote(entry["name"], safe="/")
    )
    digest = hashlib.sha256()
    git_digest = hashlib.sha1()
    git_digest.update(f"blob {entry['size_bytes']}\0".encode())
    transferred = 0
    reported = 0
    attempts = 0
    started = time.monotonic()
    while transferred < entry["size_bytes"]:
        attempts += 1
        headers = {"User-Agent": "JEP-InstructUIE-pinned-relay/1"}
        if transferred:
            headers["Range"] = f"bytes={transferred}-"
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=headers),
                                        timeout=90) as response:
                if transferred and (
                    response.status != 206
                    or not response.headers.get("Content-Range", "").startswith(
                        f"bytes {transferred}-"
                    )
                ):
                    raise ValueError("Resume response does not match requested offset.")
                while True:
                    chunk = response.read(8 * 1024 * 1024)
                    if not chunk:
                        break
                    if transferred + len(chunk) > entry["size_bytes"]:
                        raise ValueError("Source exceeded pinned file size.")
                    sys.stdout.buffer.write(chunk)
                    digest.update(chunk)
                    git_digest.update(chunk)
                    transferred += len(chunk)
                    if transferred - reported >= 256 * 1024 * 1024:
                        reported = transferred
                        print(json.dumps({"event": "source_progress", "file": entry["name"],
                                          "bytes_sent": transferred,
                                          "seconds": round(time.monotonic() - started, 2)}),
                              file=sys.stderr, flush=True)
        except (urllib.error.URLError, TimeoutError, ConnectionError) as error:
            if attempts >= 4:
                raise RuntimeError("Source stream failed after four attempts.") from error
            print(json.dumps({"event": "source_retry", "file": entry["name"],
                              "bytes_sent": transferred, "attempt": attempts}),
                  file=sys.stderr, flush=True)
            continue
        if transferred < entry["size_bytes"] and attempts >= 4:
            raise RuntimeError("Source stream ended before the pinned file size.")
    sys.stdout.buffer.flush()
    if entry.get("sha256"):
        if digest.hexdigest() != entry["sha256"]:
            raise ValueError("LFS SHA-256 mismatch; uploaded bytes must not be used.")
    elif git_digest.hexdigest() != entry["git_blob_sha1"]:
        raise ValueError("Git blob SHA-1 mismatch; uploaded bytes must not be used.")
    print(json.dumps({"status": "verified", "file": entry["name"],
                      "bytes": transferred, "sha256": digest.hexdigest(),
                      "seconds": round(time.monotonic() - started, 3)}),
          file=sys.stderr, flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
