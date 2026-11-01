#!/usr/bin/python3
"""Check the exact deployed-v1 migration and transactional writes in private copies."""
import argparse
import base64
import hashlib
import json
from pathlib import Path
import shutil
import sys
import tarfile
import tempfile
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "implementation"))
import desktop_commander_preview as preview


def snapshot(root, names):
    return {name: ((root / name).read_bytes(), (root / name).stat().st_mode & 0o777)
            if (root / name).exists() else None for name in names}


def restore(root, values):
    for name, saved in values.items():
        path = root / name
        if saved is None:
            path.unlink(missing_ok=True)
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(saved[0])
            path.chmod(saved[1])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--installed", required=True, type=Path)
    parser.add_argument("--upgraded", required=True, type=Path)
    args = parser.parse_args()
    names = set(preview.BASE_SHA256) | {preview.HELPER_PATH, preview.MARKER_PATH}
    original = snapshot(args.installed, names)
    marker = json.loads(original[preview.MARKER_PATH][0])
    assert marker["fingerprint"] == preview.V1_FINGERPRINT
    assert marker["sha256"] == preview.V1_SHA256
    expected = snapshot(args.upgraded, names)
    with tempfile.TemporaryDirectory(prefix="dc-preview-upgrade-check-") as temporary:
        installed = Path(temporary) / "installed"
        installed.mkdir()
        shutil.copy2(args.installed / "package.json", installed / "package.json")
        restore(installed, original)
        assert preview.apply_overlay(installed) is True
        assert snapshot(installed, names) == expected
        assert preview.apply_overlay(installed) is False
        boundaries = len(names)
        real_write = preview.atomic_write
        for after in [False, True]:
            for failure in range(1, boundaries + 1):
                restore(installed, original)
                calls = 0

                def interrupted(path, content, mode=0o644):
                    nonlocal calls
                    calls += 1
                    if calls == failure and not after:
                        raise OSError("injected before write")
                    real_write(path, content, mode)
                    if calls == failure and after:
                        raise OSError("injected after write")

                with mock.patch.object(preview, "atomic_write", interrupted):
                    try:
                        preview.apply_overlay(installed)
                    except OSError:
                        pass
                    else:
                        raise AssertionError("write failure was not observed")
                assert snapshot(installed, names) == original, (after, failure)
        # Clean installs and deployed-v1 upgrades must generate the same bytes.
        lock = json.loads((args.installed.parents[2] / "package-lock.json").read_text())
        integrity = lock["packages"]["node_modules/@wonderwhy-er/desktop-commander"]["integrity"]
        algorithm, encoded = integrity.split("-", 1)
        digest = base64.b64decode(encoded)
        hex_digest = digest.hex()
        archive_path = Path.home() / ".npm/_cacache/content-v2" / algorithm / hex_digest[:2] / hex_digest[2:4] / hex_digest[4:]
        assert hashlib.new(algorithm, archive_path.read_bytes()).digest() == digest
        pristine = Path(temporary) / "pristine"
        pristine.mkdir()
        with tarfile.open(archive_path, "r:gz") as archive:
            for name in set(preview.BASE_SHA256) | {"package.json"}:
                path = pristine / name
                path.parent.mkdir(parents=True, exist_ok=True)
                member = archive.getmember("package/" + name)
                path.write_bytes(archive.extractfile(member).read())
                path.chmod(member.mode)
        assert preview.apply_overlay(pristine) is True
        observed = snapshot(pristine, names)
        assert observed == expected, [name for name in names if observed[name] != expected[name]]
    print(json.dumps({"passed": True, "upgrade": preview.V1_FINGERPRINT,
                      "writeBoundaries": boundaries, "beforeAndAfterFaults": boundaries * 2,
                      "pristineEqualsUpgrade": True}))


if __name__ == "__main__":
    main()
