"""Train the archived ratings-only Qwen control with condition-last prompts.

One change to original model: baseline_models.PROMPT is condition-last at the source commit.
No evidence/proposition gradients are used. The original prefix subset, ratings loss,
matched stage settings, and held-out dataset are SHA-checked before training.
"""
import argparse
import fcntl
import json
import time
import uuid
from pathlib import Path

from viper import execution
from viper.authoring import experiment, input, plan, replicate, stage, variant
from viper.metrics import measure, max as maximize
from viper.outputs import StageOutputs, output
from viper.references import GitFileRef
from viper.repository import read_source, resolve_root
from viper.runtime import CUDAComputeSpec, LocalEnvSpec, observe_python_env

from csts_pilot.baseline_models import PROMPT, ScoreConfig
from csts_pilot.baseline_stages import capture_predictions
from csts_pilot.convergence import (
    file_sha256, training_objective, validation_mse, validation_spearman, write_json
)
from csts_pilot.convergence_run import artifact_path, artifact_source, check_inputs
from csts_pilot.diagnostics import summarize
from csts_pilot.evidence_run import evidence_training_outputs
from csts_pilot.proposition_evidence_run import phase_config
from csts_pilot.qwen_evidence import fit_qwen_evidence
from jep_pilot.loaders import load_json, load_model

EXPECTED_PROMPT = (
    "Query: {passage}\n"
    "Instruct: Represent the passage for semantic similarity with respect to this condition: {condition}"
)
HISTORICAL_CONFIG_SHA = "4c52be688d8fb52a8a1a7ce18275c5e1aa775a623b4acb74a35a46fd29bf45dc"
PREPARED_SHA = "0b63e159ecb8eb211636b9b509baf6035dc1e22b81f5404c1caaecc78203f67f"
BASELINE_TEST_SPEARMAN = 0.855375
PREFIX_EPOCHS = 5
PREFIX_ROWS = 5885
PREFIX_UPDATES = 920
TRAINING_ROWS = 6051
VALIDATION_ROWS = 1576
TEST_ROWS = 2430
SEED = 7


def announce(event: str, **kwargs: object) -> None:
    print(json.dumps({"event": event, **kwargs}, allow_nan=False), flush=True)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--microbatch-size", type=int, default=32)
    parser.add_argument("--gpu-model", default="NVIDIA L4")
    args = parser.parse_args()
    root = resolve_root()
    if PROMPT != EXPECTED_PROMPT:
        raise ValueError("The only permitted prompt ablation is condition-last.")
    config_path = root / "configs/csts-qwen-jep-v1-full-propositions-converged.json"
    if file_sha256(config_path) != HISTORICAL_CONFIG_SHA:
        raise ValueError("Original training-plan SHA is not the archived control.")
    settings = load_json(config_path)
    if settings["training"]["seed"] != SEED or settings["training"]["learning_rate"] != 2e-5:
        raise ValueError("The historical ratings optimizer changed.")
    if (settings["training"]["batch_size"], settings["training"]["microbatch_size"]) != (32, 32):
        raise ValueError("The archived logical/physical batch settings changed.")
    if args.microbatch_size not in (2, 4, 8, 16, 32) or 32 % args.microbatch_size:
        raise ValueError("Physical microbatch must divide the unchanged logical batch of 32.")
    # Only an OOM-driven physical microbatch override is allowed; preserve the logical loss.
    settings["training"]["microbatch_size"] = args.microbatch_size
    settings["gpu_model"] = args.gpu_model
    settings["phases"]["pretrain"]["max_epochs"] = PREFIX_EPOCHS
    settings["phases"]["pretrain"]["max_seconds"] = 36000
    settings["phases"]["ratings"]["max_seconds"] = 36000
    prepared_rel = "csts_data/ratings_matched_prepared.json"
    prepared_path = root / prepared_rel
    if file_sha256(prepared_path) != PREPARED_SHA:
        raise ValueError("Prepared prefix cohort differs from the archived ratings control.")
    prepared = load_json(prepared_path)
    if len(prepared["training"]) != PREFIX_ROWS:
        raise ValueError("Prefix training exposure is not the archived 5,885 rows.")
    for split, n in (("training", TRAINING_ROWS), ("validation", VALIDATION_ROWS),
                     ("test", TEST_ROWS)):
        item = settings["splits"][split]
        if item["rows"] != n or file_sha256(root / item["path"]) != item["sha256"]:
            raise ValueError(f"Original {split} source or hash changed.")
    check_inputs(root, settings)
    source = read_source(root)
    protocol = {
        "name": "ratings_only_retrain_condition_last",
        "source_commit": source.commit,
        "original_training_config_sha256": HISTORICAL_CONFIG_SHA,
        "prepared_sha256": PREPARED_SHA,
        "seed": SEED,
        "original_ratings_test_spearman": BASELINE_TEST_SPEARMAN,
        "prompt": EXPECTED_PROMPT,
        "microbatch_size": args.microbatch_size,
        "original_microbatch_size": 32,
        "full_training_initialization": "fresh pretrained Qwen, fresh seed-7 LoRA",
        "rating_prefix_epochs": PREFIX_EPOCHS,
        "rating_full_phase_patience": 1,
        "no_proposition_or_evidence_gradient": True,
        "splits": settings["splits"],
    }
    out = root / "ratings_only_order_results/condition_last"
    out.mkdir(parents=True, exist_ok=True)
    protocol_path = out / "protocol.json"
    if protocol_path.exists():
        prior_protocol = load_json(protocol_path)
        if args.resume and all(
            prior_protocol.get(k) == v
            for k, v in protocol.items() if k != "source_commit"
        ):
            # Training stages remain pinned to their original source commit.
            # A later evaluation-only source repair must not rebind training.
            protocol = prior_protocol
        elif prior_protocol != protocol:
            raise ValueError("Existing run differs from frozen protocol.")
    else:
        write_json(protocol_path, protocol)
    announce("preflight_passed", commit=source.commit, microbatch=args.microbatch_size,
             train=TRAINING_ROWS, validation=VALIDATION_ROWS, test=TEST_ROWS)
    if not args.execute:
        return
    with (root / "ratings_only_order_results/condition_last/run.lock").open("a+") as fh:
        fcntl.flock(fh, fcntl.LOCK_EX | fcntl.LOCK_NB)
        run(root, settings, protocol, out, args)


def run(root: Path, settings: dict, protocol: dict, out: Path, args) -> None:
    source = read_source(root)
    trusted = frozenset({str(source.repository)})
    env = LocalEnvSpec(
        compute=CUDAComputeSpec(model=args.gpu_model, count=1),
        lockfile=GitFileRef(repository=source.repository, commit=source.commit,
                            path="tranche2_requirements.txt"),
        python_env=observe_python_env(),
    )
    runs_path = out / "runs.json"
    records = load_json(runs_path) if runs_path.exists() else []
    if records and not args.resume:
        raise ValueError("Existing native runs require explicit --resume.")
    metrics = tuple(measure(m) for m in (training_objective, validation_mse,
                                          validation_spearman))

    def execute(name: str, configured, ceiling_seconds: int = 36000):
        existing = next((r for r in records if r["name"] == name), None)
        if existing:
            if existing["status"] != "succeeded":
                raise RuntimeError("Inspect incomplete native stage before resumption.")
            announce("native_stage_reused", stage=name)
            return existing
        trial = experiment(
            experiment_id=f"csts_rating_order_{source.commit[:8]}_{name}_{uuid.uuid4().hex[:8]}",
            variants=(variant(name, stages=(configured,),
                              estimator=configured.outputs["model"]
                              if "model" in configured.outputs
                              else configured.outputs["predictions"]),),
            replicates=(replicate(seed=SEED),),
        )
        write_json(out / "in_flight.json", {"stage": name, "trial": trial.experiment_id})
        announce("native_stage_start", stage=name, experiment_id=trial.experiment_id)
        start = time.monotonic()
        result = execution.run(
            plan(experiment=trial, source=source, env=env),
            timeout_seconds=ceiling_seconds,
            trusted_source_repositories=trusted,
        )
        item = {
            "name": name,
            "status": result.status,
            "path": str(result.path),
            "reference": result.reference.model_dump(mode="json"),
            "duration_seconds": time.monotonic() - start,
        }
        records.append(item)
        write_json(runs_path, records)
        (out / "in_flight.json").unlink(missing_ok=True)
        if result.status != "succeeded":
            raise RuntimeError(f"Native stage {name} was {result.status}.")
        announce("native_stage_complete", stage=name,
                 seconds=item["duration_seconds"])
        return item

    parent_record = next((r for r in records if r["name"] == "ratings_prefix_5"), None)
    if not parent_record:
        prefix = phase_config(settings, "ratings", "pretrain",
                              root / "csts_data/ratings_matched_prepared.json", None)
        prefix = prefix.model_copy(update={"max_epochs": PREFIX_EPOCHS,
                                           "start_epoch": 0})
        stage_cfg = stage(
            fit_qwen_evidence,
            stage_id="train",
            config=prefix,
            inputs=(
                input("training", path=settings["splits"]["training"]["path"],
                      data_role="training"),
                input("validation", path=settings["splits"]["validation"]["path"],
                      data_role="training"),
                input("prepared", path="csts_data/ratings_matched_prepared.json",
                      data_role="training"),
            ),
            outputs=evidence_training_outputs(),
            metrics=metrics,
            objective=maximize(metrics[-1]),
            reuse="never",
        )
        parent_record = execute("ratings_prefix_5", stage_cfg, 36000)
    prefix_trace = load_json(artifact_path(parent_record, "train", "trace", "trace.json"))
    if (prefix_trace["completed_epoch"], prefix_trace["actual_updates"],
        prefix_trace["training_rows"], prefix_trace["stop_reason"]) != (
            PREFIX_EPOCHS, PREFIX_UPDATES, PREFIX_ROWS, "fixed_update_budget"
        ):
        raise RuntimeError("First phase diverged from the original five-epoch control.")
    announce("prefix_complete", epochs=PREFIX_EPOCHS, updates=PREFIX_UPDATES,
             terminal_sha256=prefix_trace["terminal_model_sha256"])
    parent_path = artifact_path(parent_record, "train", "last_model", "model.pt")
    full_cfg = phase_config(settings, "ratings", "ratings",
                            root / "csts_data/ratings_matched_prepared.json", parent_path)
    full_cfg = full_cfg.model_copy(update={"max_epochs":24, "patience":1})
    stage_cfg = stage(
        fit_qwen_evidence,
        stage_id="train",
        config=full_cfg,
        inputs=(
            input("training", path=settings["splits"]["training"]["path"],
                  data_role="training"),
            input("validation", path=settings["splits"]["validation"]["path"],
                  data_role="training"),
            input("prepared", path="csts_data/ratings_matched_prepared.json",
                  data_role="training"),
            input("parent_model", source=artifact_source(parent_record,"train","last_model")),
        ),
        outputs=evidence_training_outputs(),
        metrics=metrics,
        objective=maximize(metrics[-1]),
        reuse="never",
    )
    final = execute("ratings_full", stage_cfg, 36000)
    model_path = artifact_path(final,"train","model","model.pt")
    trace_path = artifact_path(final,"train","trace","trace.json")
    trace = load_json(trace_path)
    if trace.get("stop_reason") != "validation_patience":
        raise RuntimeError("The full ratings run has not reached the selected patience stop.")
    selected_epoch = trace["selected"]["epoch"]
    selected_val = trace["selected"]["validation"]["spearman"]
    candidate_hash = file_sha256(model_path)
    selection = {
        "status": "checkpoints_frozen",
        "test_scores_used_for_selection": False,
        "candidates": {"lora":{"sha256": candidate_hash, "epoch":selected_epoch}},
        "selected_epoch": selected_epoch,
        "validation_spearman": selected_val,
        "original_baseline_validation_spearman": 0.871875,
        "source_commit": protocol["source_commit"],
        "prefix_updates": PREFIX_UPDATES,
    }
    selection_rel = "ratings_only_order_results/condition_last/selection.json"
    selection_path = root / selection_rel
    if selection_path.exists() and load_json(selection_path) != selection:
        raise ValueError("Frozen selection changed.")
    write_json(selection_path, selection)
    announce("validation_selection_frozen", epoch=selected_epoch,
             spearman=selected_val, model_sha256=candidate_hash)
    test_rows = TEST_ROWS  # Do not deserialize test rows until selection is frozen.
    holdout_rel = "ratings_only_order_results/condition_last/holdout.json"
    holdout_path = root / holdout_rel
    write_json(holdout_path, list(range(test_rows)))
    score_cfg = ScoreConfig.model_validate({
        **settings["encoder"],"kind":"lora",
        "model_sha256":candidate_hash,
        "selection_sha256":file_sha256(selection_path),
        "test_sha256":settings["splits"]["test"]["sha256"],
    })
    from csts_pilot.convergence import file_sha256 as hash_
    prediction_cfg = stage(
        capture_predictions,
        stage_id="capture",
        config=score_cfg,
        inputs=(
            input("test",path=settings["splits"]["test"]["path"],data_role="eval"),
            input("holdout",path=holdout_rel,data_role="eval"),
            input("model",source=artifact_source(final,"train","model")),
            input("selection",path=selection_rel,data_role="training"),
        ),
        outputs=StageOutputs(
            predictions=output(path="predictions.json",loader=load_json,data_role="eval"),
            timing=output(path="timing.json",loader=load_json,data_role="eval"),
        ),
        reuse="never",
    )
    predicted = execute("test_predictions",prediction_cfg, 36000)
    pred_path=artifact_path(predicted,"capture","predictions","predictions.json")
    rows=load_json(pred_path)
    if len(rows)!=TEST_ROWS:
        raise RuntimeError("Incomplete held-out prediction coverage.")
    scores=summarize(rows)
    import shutil
    shutil.copyfile(pred_path, out/"test_predictions.json")
    result={
        "status":"complete",
        "protocol":protocol,
        "source_commit":source.commit,
        "prefix_updates":PREFIX_UPDATES,
        "selected_epoch":selected_epoch,
        "validation_spearman":selected_val,
        "test":scores,
        "original_ratings_only_test_spearman":BASELINE_TEST_SPEARMAN,
        "delta_test_spearman":scores["spearman"]-BASELINE_TEST_SPEARMAN,
        "selected_model_sha256":candidate_hash,
        "test_predictions_sha256":hash_(out/"test_predictions.json"),
        "native_runs":records,
        "no_proposition_gradients":True,
    }
    write_json(out/"results.json",result)
    announce("experiment_complete",test_spearman=scores["spearman"],
             delta=result["delta_test_spearman"],
             selected_epoch=selected_epoch, test_count=scores["n"])


if __name__=="__main__":
    main()