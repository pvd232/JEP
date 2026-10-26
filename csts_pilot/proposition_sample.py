"""Compare old spans and blind-screened v1 answers on the same source 60 pairs.

This development diagnostic changes both generation and semantic screening. It
does not select a checkpoint, evaluate test, or replace the fresh fidelity gate.
"""

import argparse
import fcntl
import os
import shutil
import time
import uuid
from pathlib import Path
from typing import Any, Literal

import numpy as np
import torch
from pydantic import Field
from viper import execution
from viper.authoring import experiment, input, plan, replicate, stage, variant
from viper.outputs import StageOutputs, output
from viper.references import GitFileRef
from viper.repository import read_source
from viper.runtime import CUDAComputeSpec, LocalEnvSpec, observe_python_env
from viper.stages import StageContext, build
from viper.storage import LocalStorageDestination, ViperCloudDestination, load_storage_settings

from csts_pilot import proposition_inputs as frozen
from csts_pilot.answer_input import baseline_scores, emit
from csts_pilot.answers import answer_id
from csts_pilot.background_storage import queue_publication
from csts_pilot.baseline_models import EncoderConfig, FitConfig, validate_rows
from csts_pilot.condition_reference import MODEL_SHA256, arm_metrics, recall_cutoff
from csts_pilot.convergence import file_sha256, synchronize, write_json
from csts_pilot.convergence_run import artifact_path, artifact_source
from csts_pilot.data import canonical
from csts_pilot.evidence_controls import checked_cache
from csts_pilot.proposition_capture import checked_records
from jep_pilot.loaders import load_json, load_model


AUDIT_FILES = {
    "source_sample": "proposition_blind_sample.json",
    "pair_mapping": "proposition_audit_pair_mapping.json",
    "old_records": "proposition_old_audit120.json",
    "generated_records": "proposition_generated_audit120.json",
    "variant_mapping": "proposition_variant_mapping.json",
    "judgments_left": "proposition_judgments_left.json",
    "judgments_right": "proposition_judgments_right.json",
    "references_left": "proposition_reference_left.json",
    "references_right": "proposition_reference_right.json",
    "capture_manifest": "proposition_capture_audit_manifest.json",
}
ARMS = ("old_spans", "checked_generated_v1")


def unique_records(records: list[dict[str, Any]], identities: set[str], label: str) -> dict[str, dict[str, Any]]:
    """Require exactly one record for every audited source identity."""
    result = {record["id"]: record for record in records}
    if len(result) != len(records) or set(result) != identities:
        raise ValueError(f"Incomplete or duplicate {label} identities.")
    return result


def prepare_sample(validation: list[dict[str, Any]], audits: dict[str, Any]) -> tuple[list[dict[str, Any]], dict[str, Any], dict[str, Any]]:
    """Bind the original source sample before inspecting any similarity labels."""
    validate_rows(validation)
    mapping = audits["pair_mapping"]
    if len(mapping) != 60 or any(not isinstance(row, list) or len(row) != 3 for row in mapping):
        raise ValueError("The original sample must identify exactly 60 source pairs.")
    wanted = {tuple(row) for row in mapping}
    identities = {identity for _, left, right in mapping for identity in (left, right)}
    if len(wanted) != 60 or len({row[0] for row in mapping}) != 60 or len(identities) != 120:
        raise ValueError("Sample requires 60 distinct source groups and 120 identities.")
    items = unique_records(audits["source_sample"], identities, "source")
    selected, matched = [], set()
    for row in validation:
        key = (row["group_id"], answer_id(row["sentence1"], row["condition"]), answer_id(row["sentence2"], row["condition"]))
        if key not in wanted:
            continue
        if key in matched:
            raise ValueError("The audit mapping ambiguously identifies multiple source rows.")
        for side, identity in zip(("sentence1", "sentence2"), key[1:], strict=True):
            if items[identity] != {"id": identity, "passage": row[side], "condition": row["condition"]}:
                raise ValueError("Audited passage/condition differs from the exact native source.")
        selected.append(dict(row))
        matched.add(key)
    if matched != wanted or len(selected) != 60:
        raise ValueError("The original 60 audited comparisons are not present exactly once.")
    old = unique_records(audits["old_records"], identities, "old answer")
    generated = {record["id"]: record for record in checked_records(list(items.values()), {"records": audits["generated_records"]})}
    references = unique_records(audits["references_left"] + audits["references_right"], identities, "reference")
    variants = audits["variant_mapping"]
    if set(variants) != identities or any(set(value) != {"A", "B"} or set(value.values()) != {"old", "new"} for value in variants.values()):
        raise ValueError("Blind variant assignments do not cover old/new exactly once.")
    raw_judgments = audits["judgments_left"] + audits["judgments_right"]
    judgments = {(record["id"], record["variant"]): record for record in raw_judgments}
    if len(judgments) != len(raw_judgments) or set(judgments) != {(identity, variant) for identity in identities for variant in ("A", "B")}:
        raise ValueError("Blind judgments must cover all 240 source/variant combinations.")
    for record in judgments.values():
        if type(record.get("fully_faithful")) is not bool or type(record.get("severe_unsupported")) is not bool:
            raise ValueError("Blind judgment decisions must be literal booleans.")
    replacements = {arm: {} for arm in ARMS}
    records = []
    for identity, item in items.items():
        previous = old[identity]
        if previous.get("status") not in {"answered", "withheld"}:
            raise ValueError("Unexpected original cached-span status.")
        if previous["status"] == "answered":
            if not isinstance(previous.get("answer"), str) or not previous["answer"].strip() or canonical(previous["answer"]) not in canonical(item["passage"]):
                raise ValueError("An old accepted span is not copied from its source.")
            replacements["old_spans"][identity] = previous["answer"]
        elif previous.get("answer") != "":
            raise ValueError("An old withheld record must retain an empty answer.")
        new_variant = next(key for key, value in variants[identity].items() if value == "new")
        judgment = judgments[(identity, new_variant)]
        accepted = judgment["fully_faithful"] is True and judgment["severe_unsupported"] is False
        new = generated[identity]
        if accepted and new["status"] == "answered":
            replacements["checked_generated_v1"][identity] = new["answer"]
        occurrences = [{"row_id": row["row_id"], "group_id": row["group_id"], "side": side} for row in selected for side in ("sentence1", "sentence2") if answer_id(row[side], row["condition"]) == identity]
        records.append({
            **item, "source_occurrences": occurrences,
            "old_record": previous, "generated_v1_record": new,
            "blind_variants": variants[identity],
            "blind_judgments": {variant: judgments[(identity, variant)] for variant in ("A", "B")},
            "generated_v1_passes_blind_fidelity": accepted,
            "reference_for_audit_only": references[identity],
            "selected_inputs": {arm: {"passage": replacements[arm].get(identity, item["passage"]), "condition": item["condition"], "uses_answer": identity in replacements[arm]} for arm in ARMS},
        })
    transformed, coverage = {}, {}
    for arm in ARMS:
        counts = []
        transformed[arm] = []
        for row in selected:
            changed, count = dict(row), 0
            for side in ("sentence1", "sentence2"):
                identity = answer_id(row[side], row["condition"])
                if identity in replacements[arm]:
                    changed[side] = replacements[arm][identity]
                    count += 1
            transformed[arm].append(changed)
            counts.append(count)
        frozen.validate_replacements(selected, transformed[arm])
        coverage[arm] = {"comparisons": len(selected), "accepted_side_occurrences": sum(counts), "fallback_side_occurrences": 120 - sum(counts), "comparison_coverage": {name: counts.count(n) for n, name in ((2, "both"), (1, "one"), (0, "neither"))}, "accepted_count_per_row": counts}
    return selected, transformed, {"records": records, "coverage": coverage, "audit_inputs": audits}


class SampleInferenceConfig(EncoderConfig):
    """Pin all source, model and audit bytes for this development diagnostic."""

    parent_model_sha256: str = Field(default=MODEL_SHA256, pattern=r"^[0-9a-f]{64}$")
    input_sha256: dict[str, str]
    encode_batch_size: Literal[4] = 4
    max_seconds: float = Field(default=1800, gt=0, allow_inf_nan=False)


@build(config=SampleInferenceConfig)
def infer_sample(context: StageContext[SampleInferenceConfig]) -> None:
    """Share one frozen parent model between both answer-and-screening policies."""
    started = time.monotonic()
    config = context.config
    expected = {"model", "validation", "baseline_predictions", "old_cache", *AUDIT_FILES}
    if set(context.inputs) != expected or set(config.input_sha256) != expected:
        raise ValueError("Sample inference inputs differ from the declared audit contract.")
    for name, digest in config.input_sha256.items():
        if file_sha256(context.inputs[name]) != digest:
            raise ValueError(f"Changed frozen sample input: {name}.")
    if config.input_sha256["model"] != config.parent_model_sha256:
        raise ValueError("Sample model differs from the selected parent checkpoint.")
    validation = load_json(context.inputs["validation"])
    audits = {name: load_json(context.inputs[name]) for name in AUDIT_FILES}
    manifest = audits["capture_manifest"]
    if manifest.get("status") != "complete" or manifest.get("items") != 120 or manifest.get("records_sha256") != config.input_sha256["generated_records"]:
        raise ValueError("The v1 generation receipt does not bind these 120 generated records.")
    original, transformed, audit = prepare_sample(validation, audits)
    old_cache = checked_cache(context.inputs["old_cache"])
    for record in audit["records"]:
        cached = old_cache[record["id"]]
        previous = record["old_record"]
        if cached["valid"] != (previous["status"] == "answered") or cached["valid"] and cached["answer"] != previous["answer"]:
            raise ValueError("The old sample no longer implements the original cached-span policy.")
    full_baseline = baseline_scores(validation, load_json(context.inputs["baseline_predictions"]))
    by_id = {row["row_id"]: score for row, score in zip(validation, full_baseline, strict=True)}
    baseline = np.asarray([by_id[row["row_id"]] for row in original], dtype=np.float64)
    if not any(row["rating"] >= 4 for row in original):
        raise ValueError("The source sample has no positives for descriptive recall metrics.")
    full_metrics = arm_metrics(validation, full_baseline, recall_cutoff(validation, full_baseline))
    native = arm_metrics(original, baseline, recall_cutoff(original, baseline))
    if native["condition_changes"]["n"] != 0:
        raise ValueError("The one-pair-per-group sample unexpectedly supplies condition contrasts.")
    saved = load_model(context.inputs["model"])
    fit = FitConfig.model_validate(saved["config"])
    if saved.get("kind") != "lora" or fit.kind != "lora":
        raise ValueError("Frozen sample inference requires the saved LoRA encoder.")
    for name in ("model_id", "revision", "max_length", "embedding_dimension"):
        if getattr(fit, name) != getattr(config, name):
            raise ValueError(f"Frozen sample encoder setting differs: {name}.")
    fit = fit.model_copy(update={"device": config.device})
    tokenizer = frozen.load_tokenizer(fit)
    emit("sample_inference_loading", comparisons=60, audited_inputs=120, model_loads=1)
    model = frozen.load_backbone(fit, adapters=fit)
    frozen.restore_parameters(model, saved["state"])
    before = frozen.state_digest(frozen.trainable_state(model))
    parameters = {name: value for name, value in model.named_parameters() if value.requires_grad}
    del saved
    model.eval()
    model.requires_grad_(False)
    if config.device == "cuda":
        torch.cuda.reset_peak_memory_stats()
    metrics, predictions, token_counts = {"saved_qwen_sample": native}, {}, {}
    for arm in ARMS:
        pairs = frozen.TokenPairs(transformed[arm], fit, tokenizer)
        counts = audit["coverage"][arm]["accepted_count_per_row"]
        values = baseline.copy()
        with torch.inference_mode():
            for start in range(0, len(original), 2):
                if time.monotonic() - started > config.max_seconds:
                    raise TimeoutError("Frozen source-sample allowance exhausted.")
                indices = list(range(start, min(start + 2, len(original))))
                if not any(counts[index] for index in indices):
                    continue
                # Keep the fixed sample positions and native left-left-right-right
                # batching; ignore scores for unchanged pairs in a mixed batch.
                scores = pairs.scores(model, torch.tensor(indices)).float().cpu().tolist()
                for index, score in zip(indices, scores, strict=True):
                    if counts[index]:
                        values[index] = score
        synchronize(config.device)
        after = frozen.state_digest(parameters)
        if before != after:
            raise ValueError("Adapter bytes changed during frozen sample inference.")
        cutoff = recall_cutoff(original, values, recall=native["operating_point"]["recall"] - 1e-12)
        metrics[arm] = arm_metrics(original, values, cutoff)
        predictions[arm] = [dict(row, prediction=float(score)) for row, score in zip(original, values, strict=True)]
        token_counts[arm] = pairs.nonpadding_tokens
        emit("sample_arm_result", arm=arm, **metrics[arm])
        del pairs
    predictions["saved_qwen_sample"] = [dict(row, prediction=float(score)) for row, score in zip(original, baseline, strict=True)]
    write_json(context.outputs["source_pairs"], original)
    write_json(context.outputs["transformed_pairs"], transformed)
    write_json(context.outputs["audited_records"], audit["records"])
    write_json(context.outputs["audit"], {**audit, "input_sha256": config.input_sha256})
    write_json(context.outputs["predictions"], predictions)
    write_json(context.outputs["result"], {
        "metrics": metrics, "full_validation_saved_qwen_reference": full_metrics,
        "coverage": audit["coverage"], "optimizer_updates": 0, "baseline_rerun": False,
        "model_loads": 1, "expert_verified": False,
        "comparison": "Old production answer policy versus generated-v1 answers accepted by blinded model judgments; otherwise original passage and condition.",
        "selection_use": "Development diagnostic only; no checkpoint eligibility or full-pipeline fidelity decision.",
        "reference_policy": "Independent checked source references are audit evidence only and never replace model answers.",
        "cohort_policy": "All original 60 pairs, one per source group, in original validation order; full-validation reference is not a matched sample comparator.",
        "unchanged_pair_policy": "Copy saved native score when neither side is replaced in either arm.",
        "batch_layout": "Two fixed sample pairs, left sides then right sides. A wholly unchanged batch is skipped; unchanged scores in mixed batches are ignored.",
        "condition_ordering": "Undefined: one comparison per source group supplies zero eligible within-pair condition contrasts.",
        "config": config.model_dump(),
    })
    write_json(context.outputs["timing"], {"total_seconds": time.monotonic() - started, "nonpadding_tokens": token_counts, "adapter_state_before_sha256": before, "adapter_state_after_sha256": after, "optimizer_updates": 0, "peak_cuda_memory_bytes": torch.cuda.max_memory_allocated() if config.device == "cuda" else 0})


def release_verified_model_cache(root: Path, immutable_original: Path, receipt: Path, wait_seconds: float = 300) -> dict[str, Any]:
    """Release only the fixed parent model's reconstructible cache duplicate."""
    root = root.resolve(strict=True)
    candidate = root / ".viper/cache/verified-objects" / MODEL_SHA256
    journal = {"status": "not_deleted", "candidate": str(candidate), "immutable_original": str(immutable_original), "sha256": MODEL_SHA256, "free_bytes_before": shutil.disk_usage(root).free}
    write_json(receipt, journal)
    queue = root / ".viper/publication_queue"
    deadline = time.monotonic() + wait_seconds
    while True:
        try:
            with (queue / "enqueue.lock").open("a+") as enqueue, (queue / "worker.lock").open("a+") as worker:
                fcntl.flock(enqueue.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                fcntl.flock(worker.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                if any(load_json(path).get("status") != "published" for path in queue.glob("*.json")):
                    raise BlockingIOError("Publication is not terminal and published.")
                if not candidate.exists():
                    journal["reason"] = "The fixed model cache duplicate does not exist."
                    break
                original = immutable_original.absolute()
                if original != original.resolve(strict=True) or "/.viper/store/" not in str(original) or not original.is_file() or candidate.absolute() != candidate.resolve(strict=True) or not candidate.is_file():
                    raise ValueError("Eviction requires nonsymlink cache and immutable-store files.")
                left, right = candidate.stat(), original.stat()
                if left.st_dev == right.st_dev and left.st_ino == right.st_ino or left.st_nlink != 1:
                    journal["reason"] = "Hardlinked cache has no guaranteed disk-space gain."
                    break
                if left.st_size != right.st_size or file_sha256(original) != MODEL_SHA256 or file_sha256(candidate) != MODEL_SHA256:
                    raise ValueError("Cache bytes do not match the retained immutable original.")
                stable = lambda value: (value.st_dev, value.st_ino, value.st_size, value.st_mtime_ns, value.st_ctime_ns, value.st_nlink)
                if stable(candidate.stat()) != stable(left) or stable(original.stat()) != stable(right):
                    raise ValueError("Verified cache or original changed before unlink.")
                journal.update(status="verified_before_unlink", bytes=left.st_size)
                write_json(receipt, journal)
                candidate.unlink()
                journal.update(status="deleted_duplicate", free_bytes_after=shutil.disk_usage(root).free)
                break
        except BlockingIOError:
            if time.monotonic() >= deadline:
                journal["reason"] = "Publication is active or unfinished; preserved model cache."
                break
            time.sleep(min(5, max(0, deadline - time.monotonic())))
        except (OSError, ValueError, KeyError) as exc:
            journal.update(status="preserved_verification_failed", error_type=type(exc).__name__)
            break
    write_json(receipt, journal)
    return journal


def run(root: Path, parent_root: Path, name: str, audit_directory: Path) -> None:
    """Seal one sample stage, promote it, then release its verified input cache."""
    root, parent_root = root.resolve(strict=True), parent_root.resolve(strict=True)
    if Path(name).name != name or name in {"", ".", ".."}:
        raise ValueError("Use a single new sample attempt-directory name.")
    if audit_directory.is_absolute() or not (root / audit_directory).resolve().is_relative_to(root):
        raise ValueError("The audited sample must remain inside the native workspace.")
    if not isinstance(load_storage_settings(root).destination, LocalStorageDestination):
        raise TypeError("Seal the native sample locally before asynchronous publication.")
    settings = load_json(parent_root / "configs/csts-qwen-evidence.json")
    study = load_json(parent_root / "qwen_evidence_results/initial/summary.json")
    parent = next(record for record in study["runs"] if record["name"] == "ratings_ratings")
    model_path = artifact_path(parent, "train", "model", "model.pt")
    baseline_path = artifact_path(parent, "train", "validation_predictions", "predictions.json")
    if file_sha256(model_path) != MODEL_SHA256:
        raise ValueError("Sample parent checkpoint differs from the selected comparator.")
    selected = load_json(artifact_path(parent, "train", "trace", "trace.json"))["selected"]
    if selected["sha256"] != MODEL_SHA256:
        raise ValueError("The parent checkpoint trace identifies a different model.")
    relative = Path(settings["splits"]["validation"]["path"])
    if relative.is_absolute() or not (root / relative).resolve().is_relative_to(root):
        raise ValueError("Original validation path escapes the workspace.")
    (root / relative).parent.mkdir(parents=True, exist_ok=True)
    if not (root / relative).exists():
        shutil.copyfile(parent_root / relative, root / relative)
    if file_sha256(root / relative) != settings["splits"]["validation"]["sha256"]:
        raise ValueError("Changed native original validation bytes.")
    paths = {"validation": relative, **{key: audit_directory / filename for key, filename in AUDIT_FILES.items()}}
    old_relative = Path(settings["answers"]["path"])
    if old_relative.is_absolute() or not (root / old_relative).resolve().is_relative_to(root):
        raise ValueError("The original cached-answer path escapes the workspace.")
    (root / old_relative).parent.mkdir(parents=True, exist_ok=True)
    if not (root / old_relative).exists():
        shutil.copyfile(parent_root / old_relative, root / old_relative)
    if file_sha256(root / old_relative) != settings["answers"]["sha256"]:
        raise ValueError("Changed original cached-answer bank bytes.")
    paths["old_cache"] = old_relative
    hashes = {key: file_sha256(root / path) for key, path in paths.items()}
    hashes.update(model=MODEL_SHA256, baseline_predictions=file_sha256(baseline_path))
    # Fail before the native model-input clone if sample/audit coverage is wrong.
    prepare_sample(load_json(root / relative), {key: load_json(root / paths[key]) for key in AUDIT_FILES})
    directory = root / "answer_input_results" / name
    directory.mkdir(parents=True, exist_ok=False)
    events = directory / "events.jsonl"
    events.touch()
    os.environ["CSTS_ANSWER_INPUT_EVENTS"] = str(events)
    source = read_source(root)
    summary = {"status": "running", "source_commit": source.commit, "input_sha256": hashes, "parent_model_sha256": MODEL_SHA256, "baseline_rerun": False, "optimizer_updates": 0, "runs": []}
    summary_path = directory / "summary.json"
    write_json(summary_path, summary)
    outputs = {"source_pairs": "source_pairs.json", "transformed_pairs": "transformed_pairs.json", "audited_records": "audited_records.json", "audit": "audit.json", "predictions": "predictions.json", "result": "result.json", "timing": "timing.json"}
    configured = stage(infer_sample, stage_id="infer", config=SampleInferenceConfig(**settings["encoder"], input_sha256=hashes), inputs=(input("model", source=artifact_source(parent, "train", "model")), input("baseline_predictions", source=artifact_source(parent, "train", "validation_predictions")), *(input(key, path=path.as_posix(), data_role="eval") for key, path in paths.items())), outputs=StageOutputs(**{key: output(path=filename, loader=load_json, data_role="eval") for key, filename in outputs.items()}), reuse="never")
    trial = experiment(experiment_id=f"csts_proposition_sample_{source.commit[:8]}_{uuid.uuid4().hex[:8]}", variants=(variant("old_vs_checked_v1", stages=(configured,), estimator=configured.outputs["result"]),), replicates=(replicate(seed=7),))
    env = LocalEnvSpec(compute=CUDAComputeSpec(model="NVIDIA L4", count=1), lockfile=GitFileRef(repository=source.repository, commit=source.commit, path="tranche2_requirements.txt"), python_env=observe_python_env())
    try:
        result = execution.run(plan(experiment=trial, source=source, env=env), timeout_seconds=2100, trusted_source_repositories=frozenset({str(source.repository)}))
        record = {"name": "old_vs_checked_v1", "status": result.status, "path": str(result.path), "reference": result.reference.model_dump(mode="json")}
        summary["runs"].append(record)
        write_json(summary_path, summary)
        if result.status != "succeeded":
            raise RuntimeError(f"Native frozen sample diagnostic failed: {result.path}")
        record["publication_queue"] = str(queue_publication(root, result.reference, ViperCloudDestination.model_validate(settings["publication_destination"])))
        for key, filename in outputs.items():
            shutil.copyfile(artifact_path(record, "infer", key, filename), directory / filename)
        summary.update(status="complete", result=load_json(directory / "result.json"))
        write_json(summary_path, summary)
        summary["cache_release"] = release_verified_model_cache(root, model_path, directory / "model-cache-release.json")
        write_json(summary_path, summary)
        emit("sample_study_complete", metrics=summary["result"]["metrics"], cache_release=summary["cache_release"]["status"])
    except Exception as exc:
        summary.update(status="failed", error=str(exc))
        write_json(summary_path, summary)
        raise


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--parent-root", type=Path, required=True)
    parser.add_argument("--name", required=True)
    parser.add_argument("--audit-directory", type=Path, default=Path("training_outputs/proposition_audit"))
    args = parser.parse_args()
    with (args.parent_root / ".viper/overnight_gpu.lock").open("a") as lock:
        fcntl.flock(lock.fileno(), fcntl.LOCK_EX)
        run(args.root, args.parent_root, args.name, args.audit_directory)
