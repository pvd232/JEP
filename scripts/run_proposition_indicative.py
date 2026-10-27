"""Run the fixed short continuation from the selected Qwen adapter."""

import argparse
import json
import subprocess
from pathlib import Path

from csts_pilot.baseline_models import FitConfig
from csts_pilot.convergence import file_sha256, write_json
from csts_pilot.proposition_indicative import run_indicative
from csts_pilot.proposition_indicative_report import build_indicative_report
from csts_pilot.proposition_pretraining import prepare_frozen_proposition_pretraining


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--settings", type=Path, default=Path("configs/csts-qwen-proposition-indicative.json"))
    args = parser.parse_args()
    root = Path.cwd()
    settings_path = root / args.settings
    settings = json.loads(settings_path.read_text())
    binding = {"training": settings["splits"]["training"], "validation": settings["splits"]["validation"], "records": settings["answers"], "provenance": settings["provenance"]}
    prepared = prepare_frozen_proposition_pretraining(
        {name: (root / spec["path"]).read_bytes() for name, spec in binding.items()},
        {name: spec["sha256"] for name, spec in binding.items()},
    )
    for name in ("initial_model", "baseline_predictions", "head", "audit_gate", "report_cohorts"):
        spec = settings[name]
        if file_sha256(root / spec["path"]) != spec["sha256"]:
            raise ValueError(f"Changed indicative input: {name}.")
    gate = json.loads((root / settings["audit_gate"]["path"]).read_text())
    manifest = prepared["audit"]["capture_provenance"]
    if gate.get("passed") is not True or gate.get("generation_frozen") is not True or manifest["audit_gate_sha256"] != settings["audit_gate"]["sha256"]:
        raise ValueError("Frozen teacher fidelity gate differs.")
    for field in ("generation_template_sha256", "schema_sha256", "model_alias", "reasoning_effort", "capture_source_sha256"):
        if gate.get(field) != manifest.get(field):
            raise ValueError("The teacher policy differs from its passed audit.")
    training = json.loads((root / settings["splits"]["training"]["path"]).read_text())
    validation = json.loads((root / settings["splits"]["validation"]["path"]).read_text())
    baseline = json.loads((root / settings["baseline_predictions"]["path"]).read_text())
    source_commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip()
    config = FitConfig.model_validate({**settings["encoder"], **settings["training"], "kind": "lora", "max_epochs": 1, "max_seconds": settings["indicative"]["max_seconds"]})
    output = root / "indicative_results" / settings["indicative"]["name"]
    outcome = run_indicative(
        config, training, validation, prepared,
        root / settings["initial_model"]["path"], settings["initial_model"]["sha256"],
        root / settings["head"]["path"], settings["head"]["sha256"], output,
        {"source_commit": source_commit, "settings_sha256": file_sha256(settings_path), "preparation": prepared["audit"]},
        auxiliary_steps=settings["indicative"]["auxiliary_steps"],
        rating_steps=settings["indicative"]["rating_steps"], max_answer_tokens=settings["max_answer_tokens"],
    )
    protocol = {"source_commit": source_commit, "settings_sha256": file_sha256(settings_path), "validation": settings["splits"]["validation"], "report_cohorts": settings["report_cohorts"], "parent_model_sha256": settings["initial_model"]["sha256"], "baseline_predictions_sha256": settings["baseline_predictions"]["sha256"], "auxiliary_steps": settings["indicative"]["auxiliary_steps"], "rating_steps": settings["indicative"]["rating_steps"], "bootstrap_draws": settings["bootstrap_draws"], "bootstrap_seed": settings["bootstrap_seed"], "preparation": prepared["audit"], "training": settings["training"], "full_comparison_queued": True}
    write_json(output / "results.json", {"arms": outcome["arms"], "baseline": baseline, "protocol": protocol, "traces": outcome["traces"]})
    report = build_indicative_report(root, output)
    print(json.dumps({"event": "indicative_report_complete", "overall": report["cohorts"]["all"]["scores"]}), flush=True)


if __name__ == "__main__":
    main()
