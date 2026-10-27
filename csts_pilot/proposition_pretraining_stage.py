"""Seal the frozen proposition targets in the native preparation stage."""

import json

from pydantic import Field
from viper.config import BuildConfig
from viper.stages import StageContext, build

from csts_pilot.convergence import file_sha256, write_json
from csts_pilot.proposition_pretraining import prepare_frozen_proposition_pretraining


class PropositionPretrainingPreparationConfig(BuildConfig):
    """Pin source rows, generated records, provenance and the passed audit gate."""

    training_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    validation_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    answers_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    provenance_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    audit_gate_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")


@build(config=PropositionPretrainingPreparationConfig)
def prepare_proposition_pretraining_stage(
    context: StageContext[PropositionPretrainingPreparationConfig],
) -> None:
    """Expose original captions and full proposition targets to the existing trainer."""
    aliases = {"training": "training", "validation": "validation", "records": "answers", "provenance": "provenance"}
    inputs = {name: context.inputs[alias].read_bytes() for name, alias in aliases.items()}
    expected = {name: getattr(context.config, f"{alias}_sha256") for name, alias in aliases.items()}
    prepared = prepare_frozen_proposition_pretraining(inputs, expected)
    gate_path = context.inputs["audit_gate"]
    if file_sha256(gate_path) != context.config.audit_gate_sha256:
        raise ValueError("The frozen proposition fidelity gate changed.")
    gate = json.loads(gate_path.read_text())
    provenance = prepared["audit"]["capture_provenance"]
    if gate.get("passed") is not True or gate.get("generation_frozen") is not True:
        raise ValueError("The frozen generation policy requires a passed fidelity gate.")
    if provenance["audit_gate_sha256"] != context.config.audit_gate_sha256:
        raise ValueError("The target provenance identifies a different fidelity gate.")
    for key in ("generation_template_sha256", "schema_sha256", "model_alias", "reasoning_effort", "capture_source_sha256"):
        if gate.get(key) != provenance.get(key):
            raise ValueError(f"The target and audited generation policy differ: {key}.")
    prepared["audit"]["fidelity_gate"] = gate
    prepared["audit"]["audit_gate_sha256"] = context.config.audit_gate_sha256
    write_json(context.outputs["prepared"], prepared)
