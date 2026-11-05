"""Replicate a portable VIPER export through the existing authorized Mac account."""

import datetime
import json
import os
import subprocess
import sys
import time
from pathlib import Path

BASE = Path(__file__).resolve().parent / "cloud-replication"
GCLOUD = "/Users/machina/google-cloud-sdk/bin/gcloud"
PROJECT = "mantra-477901"
ACCOUNT = "pvd2112@columbia.edu"
GPU_ROOT = "/home/machina/jep-color-clustering-20261104/repo"
RESULTS = GPU_ROOT + "/color_results/run-20261104"
OUTBOX = RESULTS + "/cloud-outbox-01M6N36Z5H7BR46X7RW01FZ5S9"
SSH = [
    GCLOUD,
    "compute",
    "ssh",
    "machina@jep-csts-format-20261021",
    "--project=" + PROJECT,
    "--zone=asia-northeast3-a",
    "--account=" + ACCOUNT,
    "--tunnel-through-iap",
    "--quiet",
]


def record(state: str, **details) -> None:
    """Retain the independent publication phase without affecting native run status."""
    BASE.mkdir(parents=True, exist_ok=True)
    path = BASE / "status.json"
    temporary = path.with_suffix(".tmp")
    temporary.write_text(
        json.dumps(dict(state=state, updated_at=time.time(), **details), indent=2)
        + "\n"
    )
    temporary.replace(path)
    print(state, flush=True)


def publish() -> None:
    """Publish exact export bytes with credentials refreshed locally by gcloud."""
    from google.auth.credentials import Credentials
    from google.cloud import storage
    from viper.cloud import GcsRepository, ViperCloud, ViperCloudDestination
    from viper.gcs import GcsProvider

    class LocalCredentials(Credentials):
        """Keep OAuth tokens in this Mac process and refresh the existing login."""

        def refresh(self, request) -> None:
            """Capture one short-lived token without writing or logging it."""
            self.token = subprocess.check_output(
                [GCLOUD, "auth", "print-access-token", "--account=" + ACCOUNT],
                text=True,
            ).strip()
            self.expiry = datetime.datetime.now(datetime.timezone.utc).replace(
                tzinfo=None
            ) + datetime.timedelta(minutes=45)

    root = BASE / "outbox"
    client = storage.Client(project=PROJECT, credentials=LocalCredentials())
    cloud = ViperCloud(
        root,
        GcsRepository(bucket="mantra-mlfg-prod-uscentral1-8e7a", prefix="viper"),
        provider=GcsProvider(
            root,
            "mantra-mlfg-prod-uscentral1-8e7a",
            prefix="viper",
            client=client,
            max_workers=2,
        ),
    )
    sources = {
        p.relative_to(root).as_posix(): p
        for p in sorted(root.rglob("*"))
        if p.is_file()
    }
    record("uploading", files=len(sources))
    snapshot, files = cloud.publish(
        ViperCloudDestination(owner="pvd232", workspace="jep_csts_color_20261104"),
        sources,
    )
    record("complete", snapshot=snapshot.model_dump(mode="json"), files=len(files))


def run() -> None:
    """Install the pinned publisher, mirror the local export, and publish asynchronously."""
    BASE.mkdir(parents=True, exist_ok=True)
    if (BASE / "status.json").exists() and json.loads(
        (BASE / "status.json").read_text()
    )["state"] == "complete":
        return
    record("preparing")
    subprocess.run(
        SSH + ["--command=systemctl --user stop jep-color-upload-20261104"], check=True
    )
    env = BASE / "env"
    if not (env / "bin/python").exists():
        subprocess.run(
            [sys.executable, "-m", "venv", "--system-site-packages", str(env)],
            check=True,
        )
    record("installing_publisher")
    subprocess.run(
        [
            str(env / "bin/python"),
            "-m",
            "pip",
            "install",
            "--quiet",
            "viper-provenance @ git+https://github.com/pvd232/viper.git@e4ce91fa0a9330e769644aba0fccdfe062d5d821",
        ],
        check=True,
        env={**os.environ, "GIT_TERMINAL_PROMPT": "0"},
    )
    target = BASE / "outbox"
    target.mkdir(exist_ok=True)
    if not (BASE / "mirror-complete").exists():
        record("mirroring_local_export")
        proc = subprocess.Popen(
            SSH + ["--command=tar -cf - -C " + OUTBOX + " ."], stdout=subprocess.PIPE
        )
        subprocess.run(
            ["/usr/bin/tar", "-xf", "-", "-C", str(target)],
            stdin=proc.stdout,
            check=True,
        )
        proc.stdout.close()
        if proc.wait() != 0:
            raise RuntimeError("Export mirror failed; GPU original remains retained")
        (BASE / "mirror-complete").write_text("complete\n")
    subprocess.run(
        [str(env / "bin/python"), str(Path(__file__).resolve()), "--publish"],
        check=True,
    )
    receipt = (BASE / "status.json").read_text()
    # Receipt bytes contain file identities and cloud references; OAuth tokens stay local.
    import base64

    encoded = base64.b64encode(receipt.encode()).decode()
    command = (
        "python3 -c \"import base64;from pathlib import Path;Path('"
        + RESULTS
        + "/upload-status.json').write_bytes(base64.b64decode('"
        + encoded
        + "'))\""
    )
    subprocess.run(SSH + ["--command=" + command], check=True)
    check = "python3 -c \"import os,json,subprocess;from pathlib import Path;me=os.getpid();other=[];[(other.append(int(p.name)) if p.name.isdigit() and int(p.name)!=me and p.stat().st_uid==os.getuid() and Path(os.readlink(p/'exe')).name.startswith(('python','torchrun')) else None) for p in Path('/proc').iterdir() if p.name.isdigit() and (p/'exe').exists()];print(json.dumps(other))\""
    others = json.loads(
        subprocess.check_output(SSH + ["--command=" + check], text=True)
    )
    if not others:
        subprocess.run(
            [
                GCLOUD,
                "compute",
                "instances",
                "stop",
                "jep-csts-format-20261021",
                "--project=" + PROJECT,
                "--zone=asia-northeast3-a",
                "--account=" + ACCOUNT,
                "--quiet",
            ],
            check=True,
        )


if __name__ == "__main__":
    if "--publish" in sys.argv:
        publish()
    else:
        for attempt in range(3):
            try:
                run()
                break
            except Exception as error:
                record("retry_pending", attempt=attempt + 1, error=str(error))
                if attempt == 2:
                    raise
                time.sleep(60)
