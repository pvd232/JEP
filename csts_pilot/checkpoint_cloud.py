"""Publish immutable fitting snapshots through the native VIPER file API."""

import hashlib
import shutil
import time
import uuid
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from viper.storage import ViperCloud, ViperCloudDestination, publish_resolved_files

from csts_pilot import evidence_readout_progress as progress
from csts_pilot.background_storage import _save


class CheckpointCloud:
    """Copy completed writes, publish on one CPU thread, and retain receipts."""

    def __init__(self, root, destination, config, *, wait_for_first=True, prefix=None):
        self.root = Path(root).resolve(strict=True)
        self.destination = ViperCloudDestination.model_validate(destination)
        self.config = config
        self.wait_for_first = wait_for_first
        self.prefix = prefix or "csts_readout_convergence_20261028/checkpoints"
        self.identity = uuid.uuid4().hex
        self.directory = (
            self.root / ".viper" / "checkpoint_publications" / self.identity
        )
        self.directory.mkdir(parents=True)
        self.pool = ThreadPoolExecutor(max_workers=1)
        self.futures = []
        self.previous = None

    def submit(self, paths, state):
        number = len(self.futures) + 1
        directory = self.directory / f"{number:05d}"
        directory.mkdir()
        files = {}
        for name, source in paths.items():
            source = Path(source)
            if source.is_file():
                target = directory / name
                shutil.copyfile(source, target)
                files[name] = target
        _save(directory / "request.json", {"status": "pending", "state": state})
        future = self.pool.submit(self._publish, number, directory, files, state)
        self.futures.append(future)
        # Establish a real Cloud round trip before the second fitting epoch.
        if number == 1 and self.wait_for_first:
            future.result()
        return future

    def _publish(self, number, directory, files, state):
        prefix = f"{self.prefix}/{self.identity}/{number:05d}"
        metadata = directory / "metadata.json"
        _save(
            metadata, {"config": self.config, "state": state, "previous": self.previous}
        )
        files = {**files, "metadata.json": metadata}
        for attempt in range(3):
            try:
                refs = publish_resolved_files(
                    self.root,
                    self.destination,
                    {f"{prefix}/{name}": path for name, path in files.items()},
                )
                if number == 1:
                    name = "resume.pt"
                    reference = refs[f"{prefix}/{name}"]
                    verified = directory / "roundtrip.pt"
                    verified.unlink(missing_ok=True)
                    ViperCloud.for_reference(
                        self.root, reference.stored_at
                    ).fetch_to_path(reference, verified)
                    with verified.open("rb") as stream:
                        assert (
                            hashlib.file_digest(stream, "sha256").hexdigest()
                            == reference.sha256
                        )
                    verified.unlink()
                receipt = directory / "receipt.json"
                record = {
                    "status": "published",
                    "state": state,
                    "previous": self.previous,
                    "references": {
                        k: r.model_dump(mode="json") for k, r in refs.items()
                    },
                }
                _save(receipt, record)
                durable = publish_resolved_files(
                    self.root, self.destination, {f"{prefix}/receipt.json": receipt}
                )
                self.previous = durable[f"{prefix}/receipt.json"].model_dump(
                    mode="json"
                )
                record["receipt_reference"] = self.previous
                _save(receipt, record)
                progress.append(
                    "checkpoint_published",
                    name=f"Cloud checkpoint {self.identity}/{number:05d}",
                    seed=state.get("seed", ""),
                    epoch=state.get("epoch", ""),
                    status="sealed",
                )
                return record
            except Exception as error:
                _save(
                    directory / "request.json",
                    {
                        "status": "failed",
                        "state": state,
                        "error_type": type(error).__name__,
                    },
                )
                if attempt == 2:
                    raise
                time.sleep(2**attempt)

    def finish(self):
        try:
            for future in self.futures:
                future.result()
        finally:
            self.pool.shutdown(wait=True)
