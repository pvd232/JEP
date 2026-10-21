"""Retain source data until the cloud copy and retrieval receipt are verified."""

import hashlib
from types import SimpleNamespace

import pytest
from csts_pilot.archive_storage import archive_file


@pytest.mark.parametrize("verification_fails", [True, False, "corrupt"])
def test_archive_deletes_source_after_verified_restore(tmp_path, verification_fails):
    source = tmp_path / "source.bin"
    payload = b"preserve these research bytes"
    source.write_bytes(payload)
    scratch = tmp_path / "verification"
    scratch.mkdir()
    digest = hashlib.sha256(payload).hexdigest()
    receipts = []
    ref = SimpleNamespace(
        sha256=digest, bytes=len(payload), model_dump=lambda **_: {"sha256": digest}
    )

    class Cloud:
        def resolved_files(self, destination, sources):
            assert source.exists()
            key = next(iter(sources))
            if key.startswith("receipts/"):
                receipts.append(True)
            return {key: ref}

        def fetch_to_path(self, reference, path):
            assert source.exists()
            if verification_fails is True:
                raise RuntimeError("verification failed")
            path.write_bytes(b"corrupt" if verification_fails == "corrupt" else payload)

    if verification_fails:
        with pytest.raises(RuntimeError, match="verification failed|Restored payload"):
            archive_file(source, tmp_path, scratch, Cloud(), None)
        assert source.read_bytes() == payload
        assert not receipts
    else:
        archive_file(source, tmp_path, scratch, Cloud(), None)
        assert receipts
        assert not source.exists()
        assert source.with_name(source.name + ".viper.json").exists()
