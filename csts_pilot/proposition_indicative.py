"""Fixed-step warm-start comparison of proposition and rating supervision."""

import hashlib
import json
import time
from collections.abc import Callable
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import torch
from torch import nn
from torch.nn import functional as F

from csts_pilot.answers import answer_id
from csts_pilot.baseline_models import (
    FitConfig,
    TokenPairs,
    encoder_settings,
    load_backbone,
    load_tokenizer,
    restore_parameters,
    state_digest,
    trainable_state,
    validate_rows,
)
from csts_pilot.baseline_stages import predict_pairs, save_neural
from csts_pilot.convergence import file_sha256, reset_rng, rng_digests, write_json
from csts_pilot.diagnostics import summarize
from csts_pilot.qwen_evidence import (
    answer_loss_sum,
    evidence_batch,
    evidence_tokens,
    load_head,
)
from jep_pilot.loaders import load_model


def fixed_batches(size: int, steps: int, batch_size: int, seed: int) -> list[list[int]]:
    """Select a fixed random prefix without repeated examples within a phase."""
    if steps < 1 or batch_size < 1 or steps * batch_size > size:
        raise ValueError("The fixed-step budget must fit one source permutation.")
    order = torch.randperm(size, generator=torch.Generator().manual_seed(seed)).tolist()
    return [order[i * batch_size : (i + 1) * batch_size] for i in range(steps)]


def fixed_updates(
    model: nn.Module,
    batches: list[list[int]],
    config: FitConfig,
    loss_for_microbatch: Callable[[list[int], list[int]], torch.Tensor],
    on_step: Callable[[dict[str, Any]], None],
) -> torch.optim.Optimizer:
    """Start fresh AdamW and apply exactly the declared accumulated updates."""
    parameters = [
        parameter for parameter in model.parameters() if parameter.requires_grad
    ]
    optimizer = torch.optim.AdamW(
        parameters, lr=config.learning_rate, weight_decay=config.weight_decay
    )
    if optimizer.state:
        raise ValueError("The fixed-step phase must start with empty optimizer state.")
    started = time.monotonic()
    model.train()
    for step, indices in enumerate(batches, 1):
        optimizer.zero_grad(set_to_none=True)
        objective = 0.0
        for offset in range(0, len(indices), config.microbatch_size):
            loss = loss_for_microbatch(
                indices[offset : offset + config.microbatch_size], indices
            )
            if not torch.isfinite(loss):
                raise ValueError("The fixed-step objective became nonfinite.")
            loss.backward()
            objective += float(loss.detach())
        gradient = float(
            torch.nn.utils.clip_grad_norm_(parameters, 1.0, error_if_nonfinite=True)
        )
        if step == 1 and gradient <= 0:
            raise ValueError("The phase objective has no adapter gradient.")
        optimizer.step()
        on_step(
            {
                "step": step,
                "objective": objective,
                "gradient_norm": gradient,
                "elapsed_seconds": time.monotonic() - started,
            }
        )
    return optimizer


def run_indicative(
    config: FitConfig,
    training: list[dict[str, Any]],
    validation: list[dict[str, Any]],
    prepared: dict[str, Any],
    parent_model: Path,
    parent_sha256: str,
    head_path: Path,
    head_sha256: str,
    output_directory: Path,
    provenance: dict[str, Any],
    *,
    auxiliary_steps: int = 8,
    rating_steps: int = 25,
    max_answer_tokens: int = 128,
) -> dict[str, Any]:
    """Reuse one frozen backbone and reset the selected parent adapters per arm."""
    if (
        config.kind != "lora"
        or config.schedule != "constant"
        or config.warmup_fraction
        or config.start_epoch
    ):
        raise ValueError("Use fresh constant-rate attention LoRA phases.")
    if file_sha256(parent_model) != parent_sha256:
        raise ValueError("The selected parent checkpoint bytes changed.")
    validate_rows(training)
    validate_rows(validation)
    saved = load_model(parent_model)
    parent_config = FitConfig.model_validate(saved["config"])
    if encoder_settings(parent_config) != encoder_settings(config) or any(
        getattr(parent_config, name) != getattr(config, name)
        for name in ("lora_rank", "lora_alpha", "lora_dropout")
    ):
        raise ValueError("The parent representation or adapter configuration differs.")
    auxiliary = prepared["training"]
    train_lookup = {row["row_id"]: row for row in training}
    if any(train_lookup.get(row["row_id"]) != row for row in auxiliary):
        raise ValueError("Auxiliary rows must retain exact original training metadata.")
    batches = {
        "pretrain": fixed_batches(
            len(auxiliary), auxiliary_steps, config.batch_size, config.seed + 100
        ),
        "ratings": fixed_batches(
            len(training), rating_steps, config.batch_size, config.seed + 200
        ),
    }
    selected_ids = {
        phase: [[rows[index]["row_id"] for index in batch] for batch in batches[phase]]
        for phase, rows in (("pretrain", auxiliary), ("ratings", training))
    }
    output_directory.mkdir(parents=True, exist_ok=False)
    result: dict[str, Any] = {
        "status": "running",
        "protocol": "fixed-step warm-start indicative comparison",
        "config": config.model_dump(mode="json"),
        "provenance": provenance,
        "parent_model_sha256": parent_sha256,
        "auxiliary_steps": auxiliary_steps,
        "rating_steps": rating_steps,
        "max_answer_tokens": max_answer_tokens,
        "selected_row_ids": selected_ids,
        "batch_order_sha256": hashlib.sha256(
            json.dumps(selected_ids, sort_keys=True).encode()
        ).hexdigest(),
        "checkpoint_selection": "Terminal fixed-step weights in each arm; no metric-based selection.",
        "test_inputs_used": False,
        "arms": {},
    }
    summary_path = output_directory / "summary.json"
    write_json(summary_path, result)
    reset_rng(config.seed)
    tokenizer = load_tokenizer(config)
    model = load_backbone(config, adapters=config)
    pairs = {
        "pretrain": TokenPairs(auxiliary, config, tokenizer),
        "ratings": TokenPairs(training, config, tokenizer),
    }
    validation_pairs = TokenPairs(validation, config, tokenizer)
    sequences = evidence_tokens(
        auxiliary, prepared["aligned"], tokenizer, config, max_answer_tokens
    )
    head = load_head(
        head_path,
        SimpleNamespace(
            head_sha256=head_sha256,
            embedding_dimension=config.embedding_dimension,
            device=config.device,
        ),
    )
    initial_digest = state_digest(saved["state"])
    predictions_by_arm: dict[str, list[dict[str, Any]]] = {}
    for arm in ("ratings", "evidence"):
        directory = output_directory / arm
        directory.mkdir()
        restore_parameters(model, saved["state"])
        if state_digest(trainable_state(model)) != initial_digest:
            raise ValueError(
                "The arm's initial adapter weights differ from the selected parent."
            )
        arm_result: dict[str, Any] = {
            "initial_trainable_sha256": initial_digest,
            "phases": {},
        }
        result["arms"][arm] = arm_result
        for phase, rows in (("pretrain", auxiliary), ("ratings", training)):
            reset_rng(config.seed + (1000 if phase == "pretrain" else 2000))
            trace: list[dict[str, Any]] = []
            phase_result = {
                "initial_rng": rng_digests(config.device),
                "optimizer_initial_state_entries": 0,
                "initial_trainable_sha256": state_digest(trainable_state(model)),
                "steps": trace,
            }
            if (
                phase == "ratings"
                and phase_result["initial_trainable_sha256"]
                != arm_result["phases"]["pretrain"]["terminal_trainable_sha256"]
            ):
                raise ValueError(
                    "Phase B did not retain the terminal auxiliary weights."
                )
            arm_result["phases"][phase] = phase_result
            targets = torch.tensor(
                [row["target"] for row in rows], device=config.device
            )

            def objective(
                micro: list[int],
                whole: list[int],
                *,
                phase: str = phase,
                arm: str = arm,
                rows: list[dict[str, Any]] = rows,
                targets: torch.Tensor = targets,
            ) -> torch.Tensor:
                if phase == "pretrain" and arm == "evidence":
                    chosen = [rows[index] for index in micro]
                    units = sum(
                        answer_id(rows[index][side], rows[index]["condition"])
                        in sequences
                        for index in whole
                        for side in ("sentence1", "sentence2")
                    )
                    batch, labels = evidence_batch(chosen, sequences, tokenizer, config)
                    with torch.autocast(
                        config.device,
                        enabled=config.device == "cuda",
                        dtype=torch.bfloat16,
                        cache_enabled=False,
                    ):
                        hidden = model(**batch).last_hidden_state
                        return answer_loss_sum(hidden, labels, head) / units
                indices = torch.tensor(micro)
                return F.mse_loss(
                    pairs[phase].scores(model, indices).float(),
                    targets[indices.to(config.device)].float(),
                    reduction="sum",
                ) / len(whole)

            def record_step(
                item: dict[str, Any],
                *,
                trace: list[dict[str, Any]] = trace,
                directory: Path = directory,
                phase: str = phase,
                arm: str = arm,
                phase_result: dict[str, Any] = phase_result,
            ) -> None:
                trace.append(item)
                write_json(directory / f"{phase}_trace.json", phase_result)
                print(
                    json.dumps(
                        {"event": "indicative_step", "arm": arm, "phase": phase, **item}
                    ),
                    flush=True,
                )

            optimizer = fixed_updates(
                model, batches[phase], config, objective, record_step
            )
            checkpoint = directory / f"{phase}_model.pt"
            save_neural(checkpoint, model, config, 0, len(batches[phase]))
            torch.save(
                {
                    "optimizer": optimizer.state_dict(),
                    "rng_cpu": torch.get_rng_state(),
                    "rng_cuda": torch.cuda.get_rng_state_all()
                    if config.device == "cuda"
                    else [],
                },
                directory / f"{phase}_optimizer.pt",
            )
            phase_result.update(
                actual_updates=len(trace),
                model_sha256=file_sha256(checkpoint),
                terminal_trainable_sha256=state_digest(trainable_state(model)),
                stop_reason="fixed_update_budget",
            )
            write_json(directory / f"{phase}_trace.json", phase_result)
            write_json(summary_path, result)
            del optimizer
        with torch.inference_mode():
            predictions = predict_pairs(model, validation_pairs, config.microbatch_size)
        write_json(directory / "validation_predictions.json", predictions)
        predictions_by_arm[arm] = predictions
        arm_result["validation"] = summarize(predictions)
        write_json(summary_path, result)
        print(
            json.dumps(
                {
                    "event": "indicative_validation",
                    "arm": arm,
                    **arm_result["validation"],
                }
            ),
            flush=True,
        )
    for phase in ("pretrain", "ratings"):
        left, right = [
            result["arms"][arm]["phases"][phase] for arm in ("ratings", "evidence")
        ]
        if (
            left["initial_rng"] != right["initial_rng"]
            or left["actual_updates"] != right["actual_updates"]
        ):
            raise ValueError("The indicative arms changed phase RNG or update budgets.")
    result["status"] = "complete"
    result["traces"] = result["arms"]
    result["arms"] = predictions_by_arm
    write_json(summary_path, result)
    return result
