"""Replicate terminal COLOR evidence independently of scientific completion."""

import argparse
import json
import time
from pathlib import Path

from google.auth.compute_engine import Credentials
from google.cloud import storage
from viper.cloud import GcsRepository, ViperCloud, ViperCloudDestination
from viper.execution import export_run
from viper.gcs import GcsProvider
from viper.repository import read_source


def replicate(root: Path) -> None:
    """Retain a local portable outbox and retry immutable cloud publication."""
    root = root.resolve(strict=True)
    results = root / "color_results" / "run-20261104"
    receipt = results / "upload-status.json"

    def record(state: str, **details) -> None:
        """Replace the independent upload receipt atomically."""
        temporary = receipt.with_suffix(".tmp")
        temporary.write_text(
            json.dumps(dict(state=state, updated_at=time.time(), **details), indent=2)
            + "\n"
        )
        temporary.replace(receipt)

    record("waiting_for_local_completion")
    deadline = time.monotonic() + 8 * 3600
    while time.monotonic() < deadline:
        status = json.loads((results / "status.json").read_text())
        if status["status"] == "complete":
            break
        time.sleep(15)
    else:
        record("pending", reason="Local run did not complete within eight hours.")
        return
    terminal = status["runs"][-1]
    outbox = results / ("cloud-outbox-" + Path(terminal["path"]).parent.name)
    trusted = frozenset({str(read_source(root).repository)})
    record("exporting", local_run=terminal["path"], outbox=str(outbox))
    if not outbox.exists():
        exported = export_run(
            root,
            Path(terminal["path"]),
            outbox,
            trusted_source_repositories=trusted,
        )
        (results / "export-receipt.json").write_text(exported.model_dump_json(indent=2))
    cloud = ViperCloud(
        root,
        GcsRepository(bucket="mantra-mlfg-prod-uscentral1-8e7a", prefix="viper"),
        provider=GcsProvider(
            root,
            "mantra-mlfg-prod-uscentral1-8e7a",
            prefix="viper",
            client=storage.Client(project="mantra-477901", credentials=Credentials()),
            max_workers=2,
        ),
    )
    destination = ViperCloudDestination(
        owner="pvd232", workspace="jep_csts_color_20261104"
    )
    sources = {
        p.relative_to(outbox).as_posix(): p
        for p in sorted(outbox.rglob("*"))
        if p.is_file()
    }
    for attempt in range(1, 9):
        record("uploading", attempt=attempt, outbox=str(outbox), files=len(sources))
        try:
            snapshot, files = cloud.publish(destination, sources)
        except Exception as error:
            record(
                "retry_pending", attempt=attempt, outbox=str(outbox), error=str(error)
            )
            if attempt < 8:
                time.sleep(min(60 * 2 ** (attempt - 1), 900))
        else:
            record(
                "complete",
                outbox=str(outbox),
                snapshot=snapshot.model_dump(mode="json"),
                files=len(files),
            )
            return


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    replicate(parser.parse_args().root)
