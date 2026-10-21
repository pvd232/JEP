"""Load VIPER artifacts from a self-contained, verifiable source file."""

import json
from pathlib import Path


def load_bytes(path: Path):
    """Read captured inference evidence without importing experiment code."""
    return path.read_bytes()


def load_json(path: Path):
    """Read a saved data, trace or prediction artifact."""
    return json.loads(path.read_text())


def load_answers(path: Path):
    """Read caption answers using only this file and the standard library."""
    records = {}
    for line in path.read_text().splitlines():
        row = json.loads(line)
        records[row["id"]] = row
    return records


def load_model(path: Path):
    """Read a tensor checkpoint with restricted pickle loading."""
    import torch

    return torch.load(path, map_location="cpu", weights_only=True)


def load_state(path: Path):
    """Load the complete native VIPER training state."""
    from viper.resume import load_resume_state

    return load_resume_state(path)
