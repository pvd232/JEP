"""Restore the recorded vanilla LoRA packages in a task-owned Colab runtime."""

import argparse
import importlib.metadata
import json
import subprocess
import sys
from pathlib import Path

EXPECTED = {
    "torch": "2.14.0",
    "transformers": "5.20.2",
    "numpy": "2.5.4",
    "scipy": "1.18.1",
    "peft": "0.21.2",
    "accelerate": "1.15.0",
    "psutil": "7.2.2",
}


def main() -> None:
    """Install the experiment manifest and retain the observed runtime."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    args = parser.parse_args()
    root = args.root.resolve()
    receipt = root / "runtime-setup.json"
    state = {"status": "installing", "python": sys.version, "executable": sys.executable}
    receipt.write_text(json.dumps(state, indent=2) + "\n")
    try:
        optional = {}
        for name in ("torchvision", "torchaudio", "librosa", "numba", "torchao"):
            try:
                optional[name] = importlib.metadata.version(name)
            except importlib.metadata.PackageNotFoundError:
                pass
        state["removed_optional_packages"] = optional
        if optional:
            # Colab's optional binaries target its original torch/numpy.
            # This dedicated text-only runtime does not use these packages.
            subprocess.run(
                [sys.executable, "-m", "pip", "uninstall", "-y", *optional],
                check=True,
            )
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "--no-cache-dir",
             "-r", str(root / "condition_order_requirements.txt")],
            check=True,
        )
        versions = {name: importlib.metadata.version(name) for name in EXPECTED}
        for name, expected in EXPECTED.items():
            if versions[name].split("+")[0] != expected:
                raise RuntimeError(f"{name} differs from the recorded runtime.")
        import torch
        import transformers
        import peft
        import viper

        gpu = subprocess.check_output(
            ["nvidia-smi", "--query-gpu=name,memory.total,driver_version",
             "--format=csv,noheader"], text=True,
        ).strip()
        if not torch.cuda.is_available():
            raise RuntimeError("The task runtime has no usable CUDA device.")
        state.update(
            status="ready",
            versions=versions,
            viper_version=importlib.metadata.version("viper-provenance"),
            gpu=gpu,
            torch_cuda=torch.version.cuda,
            python_patch_difference="Original 3.13.15; retain observed patch version.",
        )
    except Exception as error:
        state.update(status="failed", error_type=type(error).__name__, error=str(error))
        raise
    finally:
        receipt.write_text(json.dumps(state, indent=2) + "\n")
        print(json.dumps(state), flush=True)


if __name__ == "__main__":
    main()
