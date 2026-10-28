"""Mirror one aggregate Colab Markdown report to its fixed GitHub branch path."""

import argparse
import base64
import hashlib
import json
import subprocess
import tempfile
import time
from pathlib import Path


def terminal_state(content: str) -> str | None:
    if "Evaluation status: succeeded." in content:
        return "complete"
    if "| controller failed |" in content:
        return "failed"
    return None


def publish_due(
    content: str,
    previous_hash: str | None,
    last_publish: float,
    now: float,
    interval: float,
) -> bool:
    digest = hashlib.sha256(content.encode()).hexdigest()
    return digest != previous_hash and (
        previous_hash is None
        or terminal_state(content) is not None
        or now - last_publish >= interval
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--session", required=True)
    parser.add_argument("--remote-progress", required=True)
    parser.add_argument("--report-path", required=True)
    parser.add_argument("--branch", required=True)
    parser.add_argument("--repository", default="pvd232/JEP")
    parser.add_argument("--directory", type=Path, required=True)
    parser.add_argument(
        "--colab",
        default="/Library/Frameworks/Python.framework/Versions/3.14/bin/colab",
    )
    parser.add_argument("--gh", default="/opt/homebrew/bin/gh")
    parser.add_argument("--interval", type=float, default=300)
    parser.add_argument("--poll", type=float, default=30)
    args = parser.parse_args()
    if args.interval <= 0 or not 0 < args.poll <= 60:
        raise ValueError(
            "Use positive publication intervals and polling of at most 60 seconds."
        )
    args.directory.mkdir(parents=True, exist_ok=True)
    endpoint = f"repos/{args.repository}/contents/{args.report_path}"
    previous_hash, blob_sha, last_publish = None, None, 0.0

    def command(argv):
        return subprocess.run(
            argv, check=True, capture_output=True, text=True, timeout=60
        ).stdout

    def status(**values):
        temporary = args.directory / "status.tmp"
        temporary.write_text(
            json.dumps({"checked_unix": time.time(), **values}, indent=2) + "\n"
        )
        temporary.replace(args.directory / "status.json")

    while True:
        try:
            local = args.directory / "latest-progress.md"
            command(
                [
                    args.colab,
                    "download",
                    "-s",
                    args.session,
                    args.remote_progress,
                    str(local),
                ]
            )
            content = local.read_text()
            if publish_due(
                content, previous_hash, last_publish, time.time(), args.interval
            ):
                if blob_sha is None:
                    current = json.loads(
                        command(
                            [
                                args.gh,
                                "api",
                                "--method",
                                "GET",
                                endpoint,
                                "-f",
                                f"ref={args.branch}",
                            ]
                        )
                    )
                    blob_sha = current["sha"]
                payload = {
                    "message": "Stream readout convergence results",
                    "branch": args.branch,
                    "sha": blob_sha,
                    "content": base64.b64encode(content.encode()).decode(),
                }
                with tempfile.NamedTemporaryFile(
                    mode="w", dir=args.directory, suffix=".json"
                ) as stream:
                    json.dump(payload, stream)
                    stream.flush()
                    try:
                        result = json.loads(
                            command(
                                [
                                    args.gh,
                                    "api",
                                    "--method",
                                    "PUT",
                                    endpoint,
                                    "--input",
                                    stream.name,
                                ]
                            )
                        )
                    except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
                        blob_sha = None
                        raise
                blob_sha = result["content"]["sha"]
                previous_hash = hashlib.sha256(content.encode()).hexdigest()
                last_publish = time.time()
                status(
                    status=terminal_state(content) or "running",
                    commit=result["commit"]["sha"],
                    report_bytes=len(content.encode()),
                )
                print(
                    json.dumps(
                        {
                            "event": "published",
                            "commit": result["commit"]["sha"],
                            "state": terminal_state(content) or "running",
                        }
                    ),
                    flush=True,
                )
            terminal = terminal_state(content)
            if terminal:
                return
        except (
            OSError,
            ValueError,
            subprocess.CalledProcessError,
            subprocess.TimeoutExpired,
        ) as exc:
            status(status="retrying", error_type=type(exc).__name__)
            print(
                json.dumps({"event": "retrying", "error_type": type(exc).__name__}),
                flush=True,
            )
        time.sleep(args.poll)


if __name__ == "__main__":
    main()
