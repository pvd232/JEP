"""Resume the frozen 21 October study after its checkpoint copy filled the disk.

Run this file from outside the frozen checkout, with that checkout on PYTHONPATH.
The adapter reuses verified runs and retries the failed frozen plan. New trials
use the original controller and training implementation.
"""

import json
from pathlib import Path
from types import SimpleNamespace
from typing import Any

from viper import api, execution
from viper.repository import read_source, resolve_root
from viper.runs import ResolvedRun
from viper.serialization import parse_yaml_bytes

from csts_pilot.run import main as run_study

SOURCE = "344207017dc36a4fe243fa15ae84bcf00bc6f165"
FAILED_TRIAL = "without_question_lr3e_05_seed7"


def main() -> None:
    """Preserve the original source, labels, optimization and completed trials."""
    root = resolve_root()
    if read_source(root).commit != SOURCE:
        raise RuntimeError("Recovery requires the original frozen source commit.")
    original_run = execution.run
    results = root / "csts_results"
    backup = results / "summary_before_storage_recovery.json"
    if not backup.exists():
        backup.write_bytes((results / "summary.json").read_bytes())

    def resume_run(draft: Any, **kwargs: Any) -> Any:
        if draft.source.commit != SOURCE:
            raise RuntimeError("The requested source differs from this recovery.")
        name = str(draft.variant)
        pattern = (
            f"experiments/csts_natural_20261021_{SOURCE[:7]}_{name}"
            f"/runs/{name}/*/resolved.yaml"
        )
        candidates = list(root.glob(pattern))
        if not candidates:
            return original_run(draft, **kwargs)
        if len(candidates) != 1:
            raise RuntimeError(f"Recovery found several runs for {name}.")
        path: Path = candidates[0]
        record = ResolvedRun.model_validate(parse_yaml_bytes(path.read_bytes()))
        if record.status == "failed":
            if name != FAILED_TRIAL:
                raise RuntimeError(f"Unexpected failed trial: {name}.")
            print(
                json.dumps({"recovery": "retry_frozen_plan", "name": name}), flush=True
            )
            return execution.retry(root, path.with_name("spec.yaml"), **kwargs)
        if record.status != "succeeded":
            raise RuntimeError(f"Unexpected trial status: {record.status}.")
        api.verify_run(
            api.VerifyRunRequest(
                root=root,
                path=path,
                trusted_source_repositories=kwargs["trusted_source_repositories"],
            )
        )
        print(json.dumps({"recovery": "reuse_verified_run", "name": name}), flush=True)
        return SimpleNamespace(
            path=path,
            status="succeeded",
            reference=execution.resolve_run_reference(root, path),
        )

    execution.run = resume_run
    try:
        run_study()
    finally:
        execution.run = original_run


if __name__ == "__main__":
    main()
