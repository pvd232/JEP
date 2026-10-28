"""Release follow on seeds after a completed positive validation checkpoint."""

import argparse
import json
import shutil
import subprocess
from pathlib import Path

from viper.storage import ViperCloudDestination, publish_resolved_files

from csts_pilot.background_storage import _save
from csts_pilot.convergence import file_sha256
from csts_pilot.native_comparison_run import continuation_decision
from jep_pilot.loaders import load_json


def release_follow_on(root: Path):
    settings_path = root / "configs/csts-native-comparison.json"
    settings = load_json(settings_path)
    settings_sha = file_sha256(settings_path)
    directory = root / "qwen_evidence_results/native_release_20261028"
    directory.mkdir(exist_ok=True)
    receipt_path = directory / "publication.json"
    if receipt_path.exists():
        receipt = load_json(receipt_path)
        if receipt["settings_sha256"] != settings_sha:
            raise ValueError("The published release uses another configuration.")
        return receipt
    candidates = []
    for path in (root / ".viper/checkpoint_publications").glob("*/*/receipt.json"):
        receipt = load_json(path)
        if (
            receipt.get("status") == "published"
            and receipt["state"].get("seed") == 7
            and receipt["state"].get("epoch", 0) >= 1
        ):
            candidates.append((receipt["state"]["epoch"], path, receipt))
    for epoch, path, receipt in sorted(
        candidates, key=lambda item: (item[0], str(item[1]))
    ):
        trace = load_json(path.parent / "trace.json")
        if trace["completed_epoch"] != epoch or trace["seed"] != 7:
            raise ValueError("The checkpoint receipt and epoch trace disagree.")
        if file_sha256(path.parent / "model.pt") != trace["selected"]["sha256"]:
            raise ValueError(
                "The selected weights differ from their published identity."
            )
        gate = continuation_decision(
            load_json(path.parent / "predictions.json"),
            load_json(root / settings["ratings_validation_predictions"]),
            load_json(root / settings["splits"]["validation"]["path"]),
        )
        if gate["status"] != "positive":
            continue
        gate.update(
            settings_sha256=settings_sha,
            validation_sha256=settings["splits"]["validation"]["sha256"],
            reference_predictions_sha256=file_sha256(
                root / settings["ratings_validation_predictions"]
            ),
            model_sha256=trace["selected"]["sha256"],
            trigger_epoch=epoch,
            selected_epoch=trace["selected"]["epoch"],
            source_commit=subprocess.check_output(
                ["git", "-C", str(root), "rev-parse", "HEAD"], text=True
            ).strip(),
            checkpoint_receipt_reference=receipt["receipt_reference"],
            rule="Release after the first completed positive epoch; seed 7 continues to validation patience. Its selected validation score is monotone.",
        )
        gate_path = directory / "release.json"
        _save(gate_path, gate)
        source = directory / "release_source.py"
        shutil.copyfile(Path(__file__), source)
        prefix = f"csts_native_comparison_20261028/release/{gate['model_sha256']}"
        refs = publish_resolved_files(
            root,
            ViperCloudDestination.model_validate(settings["publication_destination"]),
            {
                prefix + "/release.json": gate_path,
                prefix + "/release_source.py": source,
            },
        )
        result = {
            "status": "positive",
            "trigger_epoch": epoch,
            "settings_sha256": settings_sha,
            "difference": gate["difference"],
            "gate_reference": refs[prefix + "/release.json"].model_dump(mode="json"),
            "source_reference": refs[prefix + "/release_source.py"].model_dump(
                mode="json"
            ),
        }
        _save(receipt_path, result)
        durable = publish_resolved_files(
            root,
            ViperCloudDestination.model_validate(settings["publication_destination"]),
            {prefix + "/publication.json": receipt_path},
        )
        result["receipt_reference"] = durable[prefix + "/publication.json"].model_dump(
            mode="json"
        )
        _save(receipt_path, result)
        return result
    return {
        "status": "waiting",
        "completed_published_epochs": [epoch for epoch, _, _ in candidates],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", required=True, type=Path)
    args = parser.parse_args()
    print(json.dumps(release_follow_on(args.root.resolve(strict=True))), flush=True)


if __name__ == "__main__":
    main()
