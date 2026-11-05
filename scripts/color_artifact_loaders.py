"""Load COLOR artifacts using only standalone standard-library imports."""

import json
from pathlib import Path


def load_json(path: Path):
    """Read a native JSON artifact in VIPER's isolated loader worker."""
    return json.loads(path.read_text(encoding="utf-8"))


def load_path(path: Path) -> Path:
    """Expose a verified binary artifact without eagerly loading its bytes."""
    return path
