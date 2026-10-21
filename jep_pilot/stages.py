"""Train and evaluate the pilot through native VIPER stages."""

import json
import random
from pathlib import Path

import numpy as np
import torch
from pydantic import Field
from scipy.stats import spearmanr
from viper.config import EvalConfig, MetricConfig, TrainConfig
from viper.metrics import MetricContext, metric
from viper.randomness import capture_main_process_rng
from viper.resume import (
    DataLoaderConfiguration,
    DataLoaderResumeState,
    ResumeState,
    load_resume_state,
    save_resume_state,
)
from viper.stages import StageContext, eval, train

from jep_pilot.model import JointModel, tiny_spec


class PilotConfig(TrainConfig):
    """Declare all settings that distinguish training arms."""

    mode: str = "tiny"
    model_id: str = "google/flan-t5-small"
    revision: str = ""
    annotation_weight: float = Field(default=0.2, ge=0)
    shuffle_annotations: bool = False
    steps: int = Field(default=8, ge=1)
    batch_size: int = Field(default=4, ge=1)
    learning_rate: float = 0.001
    seed: int = 7
    device: str = "cpu"


def load_json(path: Path):
    """Load a saved JSON data or prediction artifact."""
    return json.loads(path.read_text())


def load_model(path: Path):
    """Read a checkpoint without executing arbitrary pickle globals."""
    return torch.load(path, map_location="cpu", weights_only=True)


def load_state(path: Path):
    """Validate a native VIPER resume artifact."""
    return load_resume_state(path)


@metric(metric_id="training_mse", mode="stateless")
def training_mse(_context: MetricContext[MetricConfig], value: float) -> float:
    """Record the observed pair-rating error during optimization."""
    return value


@metric(metric_id="evaluation_mse", mode="stateless")
def evaluation_mse(context: MetricContext[MetricConfig]) -> float:
    """Recompute the evaluation error from saved predictions."""
    rows = load_json(context.artifacts["predictions"])
    return float(np.mean([(r["prediction"] - r["target"]) ** 2 for r in rows]))


@metric(metric_id="evaluation_spearman", mode="stateless")
def evaluation_spearman(context: MetricContext[MetricConfig]) -> float:
    """Recompute rank correlation from saved predictions."""
    rows = load_json(context.artifacts["predictions"])
    value = float(
        spearmanr(
            [r["prediction"] for r in rows], [r["target"] for r in rows]
        ).statistic
    )
    return value if np.isfinite(value) else 0.0


@train(config=PilotConfig)
def fit(context: StageContext[PilotConfig]) -> None:
    """Train one matched arm and save its complete terminal state."""
    config = context.config
    torch.set_num_threads(2)
    torch.manual_seed(config.seed)
    random.seed(config.seed)
    rows = load_json(context.inputs["dataset"])
    spec = (
        tiny_spec(rows)
        if config.mode == "tiny"
        else {
            "mode": "pretrained",
            "model_id": config.model_id,
            "revision": config.revision,
        }
    )
    if config.mode != "tiny" and not config.revision:
        raise ValueError("pretrained runs require an immutable model revision")
    model = JointModel(spec).to(config.device)
    model.train()
    optimizer = torch.optim.AdamW(model.parameters(), lr=config.learning_rate)
    rng = random.Random(config.seed)
    cases = {
        r[s]["case_id"]: r[s]["annotation"] for r in rows for s in ("left", "right")
    }
    labels = list(cases.values())
    random.Random(999).shuffle(labels)
    shuffled = (
        dict(zip(cases, labels, strict=True)) if config.shuffle_annotations else None
    )
    trace = []
    gradient_checks = None
    for step in range(config.steps):
        batch = [rows[rng.randrange(len(rows))] for _ in range(config.batch_size)]
        mse, ce, _ = model.losses(batch, shuffled=shuffled)
        if step == 0:
            shared = model.t5.encoder.block[0].layer[0].SelfAttention.q.weight
            gs = torch.autograd.grad(mse, shared, retain_graph=True)[0]
            ga = torch.autograd.grad(ce, shared, retain_graph=True)[0]
            gradient_checks = {
                "similarity_norm": float(gs.norm()),
                "annotation_norm": float(ga.norm()),
                "cosine": float(
                    torch.nn.functional.cosine_similarity(
                        gs.flatten(), ga.flatten(), dim=0
                    )
                ),
            }
            if (
                min(
                    gradient_checks["similarity_norm"],
                    gradient_checks["annotation_norm"],
                )
                <= 0
            ):
                raise RuntimeError("both losses must reach the shared encoder")
        loss = mse + config.annotation_weight * ce
        optimizer.zero_grad(set_to_none=True)
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        optimizer.step()
        trace.append(
            {
                "step": step + 1,
                "mse": float(mse.detach()),
                "annotation_ce": float(ce.detach()),
                "loss": float(loss.detach()),
            }
        )
        context.metrics["training_mse"].record(float(mse.detach()), step=step + 1)
    context.outputs["model"].parent.mkdir(parents=True, exist_ok=True)
    torch.save(
        {"spec": spec, "state": {k: v.cpu() for k, v in model.state_dict().items()}},
        context.outputs["model"],
    )
    save_resume_state(
        context.outputs["resume_state"],
        ResumeState(
            optimizer_state=optimizer.state_dict(),
            main_process_rng=capture_main_process_rng(
                context.numpy_generators, capture_legacy_global=True
            ),
            dataloader=DataLoaderResumeState(
                configuration=DataLoaderConfiguration(workers=0),
                state_dict={
                    "completed_steps": config.steps,
                    "python_sampler_state": rng.getstate(),
                },
            ),
        ),
    )
    context.outputs["trace"].parent.mkdir(parents=True, exist_ok=True)
    context.outputs["trace"].write_text(
        json.dumps(
            {
                "config": config.model_dump(),
                "parameter_count": sum(p.numel() for p in model.parameters()),
                "initial_shared_gradients": gradient_checks,
                "steps": trace,
            },
            indent=2,
        )
        + "\n"
    )


@eval(config=EvalConfig)
def evaluate(context: StageContext[EvalConfig]) -> None:
    """Evaluate frozen weights on atomic and previously unrated composed conditions."""
    torch.set_num_threads(2)
    saved = load_model(context.inputs["model"])
    model = JointModel(saved["spec"])
    model.load_state_dict(saved["state"])
    model.to("cuda" if torch.cuda.is_available() else "cpu")
    model.eval()
    rows = load_json(context.inputs["test"])
    indices = load_json(context.inputs["holdout"])
    predictions = []
    for start in range(0, len(indices), 16):
        batch = [rows[i] for i in indices[start : start + 16]]
        scores = model.score(batch)
        for row, value in zip(batch, scores, strict=True):
            predictions.append(
                {
                    "prediction": value,
                    "target": row["target"],
                    "condition": row["condition"],
                    "category": row["left"]["category"],
                    "transfer": row["transfer"],
                    "left_case": row["left"]["case_id"],
                    "right_case": row["right"]["case_id"],
                }
            )
    context.outputs["predictions"].parent.mkdir(parents=True, exist_ok=True)
    context.outputs["predictions"].write_text(json.dumps(predictions, indent=2) + "\n")
