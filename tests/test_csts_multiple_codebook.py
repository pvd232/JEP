"""Synthetic fixtures test coding mechanics, not expert JEP validity."""

import copy
from pathlib import Path
from types import SimpleNamespace

import pytest
import torch
from torch.nn import functional as F

from csts_pilot.convergence import file_sha256
from csts_pilot.multiple_codebook import (
    ARMS,
    MultipleCodebookConfig,
    MultiplePrototypeHead,
    classification_metrics,
    evaluate,
    fit_multiple_codebooks,
    fit_one,
    initialize,
    masked_loss,
    passage_or,
    predict,
    prepare_data,
)
from csts_pilot.multiple_codebook_run import preflight, run

SHA = "a" * 64


def fixture():
    """Provide explicit synthetic labels with independently identified source groups."""
    annotations = {
        "schema_version": 1,
        "expert_reviewed": True,
        "annotation_protocol": "Synthetic fixture; not expert data",
        "codebook_version": "fixture-v1",
        "reviewer_ids": ["synthetic-reviewer"],
        "codes": [
            {"id": "a", "condition": "condition", "definition": "synthetic code A"},
            {"id": "b", "condition": "condition", "definition": "synthetic code B"},
        ],
    }
    caches = {}
    for split, seed in (("training", 17), ("validation", 18)):
        rows = []
        for i in range(8):
            rows.append(
                {
                    "claim_id": f"{split}-claim-{i}",
                    "passage_id": f"{split}-passage-{i // 2}",
                    "source_group": f"{split}-group-{i // 2}",
                    "condition": "condition",
                    "text": f"{split} synthetic claim {i}",
                    "labels": {"a": i % 2, "b": (i // 2) % 2},
                }
            )
        annotations[split] = rows
        caches[split] = {
            "keys": [[row["condition"], row["text"]] for row in rows],
            "vectors": F.normalize(
                torch.randn(8, 6, generator=torch.Generator().manual_seed(seed)), dim=1
            ),
            "provenance": {"model_sha256": SHA},
        }
    config = MultipleCodebookConfig(
        seeds=(7,),
        output_dim=4,
        max_epochs=2,
        batch_size=3,
        min_groups_per_condition=2,
        annotations_sha256=SHA,
        training_sha256=SHA,
        validation_sha256=SHA,
        model_sha256=SHA,
    )
    return annotations, caches, config


def prepared_fixture():
    annotations, caches, config = fixture()
    prepared = prepare_data(annotations, caches, config)
    return prepared["splits"]["training"], prepared["splits"]["validation"], config


def test_strict_annotations_and_support_fail_closed():
    annotations, caches, config = fixture()
    prepare_data(annotations, caches, config)
    changes = [
        lambda a, c: a.update(expert_reviewed=False),
        lambda a, c: a["training"][0]["labels"].update(a=True),
        lambda a, c: a["training"][0]["labels"].update(unseen=1),
        lambda a, c: a["training"][0].update(labels={}),
        lambda a, c: a["validation"][0].update(source_group="training-group-0"),
        lambda a, c: a["validation"][0].update(text="  TRAINING synthetic claim 0  "),
        lambda a, c: c["training"]["provenance"].update(model_sha256="b" * 64),
        lambda a, c: c["training"]["keys"].__setitem__(0, c["training"]["keys"][1]),
        lambda a, c: c["training"]["vectors"].__setitem__(0, 0),
        lambda a, c: [row["labels"].update(a=0) for row in a["validation"]],
    ]
    for change in changes:
        a, c = copy.deepcopy(annotations), copy.deepcopy(caches)
        change(a, c)
        with pytest.raises(ValueError):
            prepare_data(a, c, config)
    with pytest.raises(ValueError, match="independent"):
        prepare_data(
            annotations,
            caches,
            config.model_copy(update={"min_groups_per_condition": 10}),
        )


def test_cross_condition_labels_and_canonical_split_text_leakage():
    annotations, caches, config = fixture()
    annotations["codes"].append(
        {"id": "foreign", "condition": "other", "definition": "Other code"}
    )
    annotations["training"][0]["labels"]["foreign"] = 1
    with pytest.raises(ValueError, match="cross conditions"):
        prepare_data(annotations, caches, config)
    annotations, caches, config = fixture()
    annotations["validation"][0]["text"] = "TRAINING synthetic claim 0"
    with pytest.raises(ValueError, match="disjoint"):
        prepare_data(annotations, caches, config)


def test_unknowns_have_zero_gradient_and_claims_have_equal_weight():
    logits = torch.zeros(2, 3, requires_grad=True)
    labels = torch.tensor([[1.0, 0.0, 0.0], [1.0, 1.0, 0.0]])
    mask = torch.tensor([[True, False, False], [True, True, False]])
    loss = masked_loss(logits, labels, mask)
    loss.backward()
    assert torch.allclose(
        logits.grad, torch.tensor([[-0.25, 0.0, 0.0], [-0.125, -0.125, 0.0]])
    )
    assert float(loss.detach()) == pytest.approx(0.69314718)


def test_or_aggregation_preserves_unknowns_and_allows_multilabel():
    data = {
        "rows": [{"passage_id": "p", "condition": "c"}] * 2,
        "labels": torch.tensor([[1.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 1.0]]),
        "mask": torch.tensor([[True, True, True, False], [False, False, True, True]]),
    }
    p, y, m = passage_or(
        data, torch.tensor([[0.9, 0.9, 0.1, 0.2], [0.2, 0.2, 0.2, 0.8]])
    )
    assert y.tolist() == [[1.0, 0.0, 0.0, 1.0]]
    assert m.tolist() == [[True, False, True, True]]
    assert (p >= 0.5).tolist() == [[True, True, False, True]]
    metrics = classification_metrics(p >= 0.5, y, m)
    assert metrics["micro_f1"] == 1


def test_pooling_matches_formula_and_both_heads_train_every_parameter():
    training, _, config = prepared_fixture()
    a, b = (initialize(training, config, 7) for _ in ARMS)
    assert all(
        torch.equal(a.state_dict()[k], b.state_dict()[k]) for k in a.state_dict()
    )
    assert sum(p.numel() for p in a.parameters()) == sum(
        p.numel() for p in b.parameters()
    )
    vectors = training["vectors"]
    z = F.normalize(a.projection(vectors), dim=1)
    s = torch.einsum("nd,kmd->nkm", z, F.normalize(a.prototypes, dim=2))
    assert torch.allclose(a(vectors, "centroid"), 5 * s.mean(2) + a.bias)
    assert torch.all(a(vectors, "multiple_prototype") >= a(vectors, "centroid") - 1e-6)
    for model, arm in ((a, ARMS[0]), (b, ARMS[1])):
        masked_loss(
            model(vectors, arm), training["labels"], training["mask"]
        ).backward()
        assert all(
            p.grad is not None
            and torch.isfinite(p.grad).all()
            and p.grad.abs().sum() > 0
            for p in model.parameters()
        )
    # Training-only initialization is unaffected by any development tensor/label.
    assert torch.equal(initialize(training, config, 7).prototypes, a.prototypes)


def test_paired_fits_selected_replay_and_terminal_state_is_not_selected_alias():
    training, validation, config = prepared_fixture()
    runs = [
        fit_one(training, validation, config, 7, arm, lambda *_: None) for arm in ARMS
    ]
    assert runs[0][0]["initial_state_sha256"] == runs[1][0]["initial_state_sha256"]
    assert [r["batch_order_sha256"] for r in runs[0][1]["epochs"]] == [
        r["batch_order_sha256"] for r in runs[1][1]["epochs"]
    ]
    for arm, (selected, trace, terminal) in zip(ARMS, runs, strict=True):
        restored = MultiplePrototypeHead(6, 2, config)
        restored.load_state_dict(selected["state"])
        p = predict(restored, validation, arm)
        assert torch.equal(p, selected["validation_probabilities"])
        assert evaluate(validation, p, selected["threshold"]) == selected["validation"]
        assert trace["selected_epoch"] <= config.max_epochs
        assert terminal["updates"] == 6
        assert all(
            terminal["state"][k].data_ptr() != selected["state"][k].data_ptr()
            for k in selected["state"]
        )
    # Force epoch zero to win: its exact predictions define labels, with independent both-class coverage.
    initial = initialize(training, config, 7)
    validation = copy.deepcopy(validation)
    validation["labels"] = (predict(initial, validation, "centroid") >= 0.5).float()
    selected, _, terminal = fit_one(
        training,
        validation,
        config.model_copy(update={"thresholds": (0.5,)}),
        7,
        "centroid",
        lambda *_: None,
    )
    assert selected["epoch"] == 0
    assert any(
        not torch.equal(selected["state"][k], terminal["state"][k])
        for k in selected["state"]
    )


class Metric:
    def __init__(self):
        self.values = []

    def record(self, value, step):
        self.values.append((step, value))


def write_inputs(tmp_path: Path):
    import json

    annotations, caches, config = fixture()
    paths = {
        "annotations": tmp_path / "annotations.json",
        "training": tmp_path / "training.pt",
        "validation": tmp_path / "validation.pt",
    }
    paths["annotations"].write_text(json.dumps(annotations))
    for name in ("training", "validation"):
        torch.save(caches[name], paths[name])
    config = config.model_copy(
        update={name + "_sha256": file_sha256(path) for name, path in paths.items()}
    )
    return annotations, paths, config


def test_native_stage_saves_replayable_models_and_resume(tmp_path):
    from viper.resume import load_resume_state

    _, paths, config = write_inputs(tmp_path)
    outputs = {
        "model": tmp_path / "models.pt",
        "trace": tmp_path / "trace.json",
        "resume_state": tmp_path / "resume.pt",
    }
    metrics = {name: Metric() for name in ("training_objective", "validation_macro_f1")}
    context = SimpleNamespace(
        config=config,
        inputs=paths,
        outputs=outputs,
        metrics=metrics,
        numpy_generators={},
    )
    fit_multiple_codebooks(context)
    saved = torch.load(outputs["model"], weights_only=True)
    assert set(saved["models"]) == {"7:centroid", "7:multiple_prototype"}
    resume = load_resume_state(outputs["resume_state"])
    assert set(resume.optimizer_state["terminal_runs"]) == set(saved["models"])
    assert len(metrics["validation_macro_f1"].values) == 4
    paths["annotations"].write_text("{}")
    with pytest.raises(ValueError, match="Changed expert"):
        fit_multiple_codebooks(context)


def test_cli_preflight_does_not_launch_or_create_attempt(tmp_path, monkeypatch, capsys):
    import json

    _, paths, config = write_inputs(tmp_path)
    training = config.model_dump(mode="json")
    for key in (
        "annotations_sha256",
        "training_sha256",
        "validation_sha256",
        "model_sha256",
    ):
        training.pop(key)
    settings = {"training": training}
    (tmp_path / "configs").mkdir()
    (tmp_path / "configs/csts-multiple-codebook.json").write_text(json.dumps(settings))
    supplied = {
        name: {"path": path.name, "sha256": file_sha256(path)}
        for name, path in paths.items()
    }
    supplied["model_sha256"] = SHA
    manifest = tmp_path / "manifest.json"
    manifest.write_text(json.dumps(supplied))
    checked, _, support = preflight(settings, manifest)
    assert checked.training_sha256 == file_sha256(paths["training"])
    assert support["validation"]["a"]["positive_groups"] == 4
    monkeypatch.setattr(
        "csts_pilot.multiple_codebook_run.execution.run",
        lambda *_a, **_k: pytest.fail("preflight launched training"),
    )
    run(tmp_path, manifest, "fixture")
    assert "preflight_passed" in capsys.readouterr().out
    assert not (tmp_path / "multiple_codebook_results").exists()
    with pytest.raises(ValueError, match="filename-safe"):
        run(tmp_path, manifest, "../escape")


def test_independent_native_development_replay_and_artifact_primary(tmp_path):
    import json

    from csts_pilot.multiple_codebook_analysis import (
        MultipleEvaluationConfig,
        evaluate_multiple_codebooks,
        mean_macro_f1_gain,
        paired_macro_f1_gain,
    )

    annotations, paths, config = write_inputs(tmp_path)
    outputs = {
        "model": tmp_path / "models.pt",
        "trace": tmp_path / "trace.json",
        "resume_state": tmp_path / "resume.pt",
    }
    fit_multiple_codebooks(
        SimpleNamespace(
            config=config,
            inputs=paths,
            outputs=outputs,
            metrics={
                name: Metric() for name in ("training_objective", "validation_macro_f1")
            },
            numpy_generators={},
        )
    )
    test, holdout = tmp_path / "development.json", tmp_path / "indices.json"
    test.write_text(json.dumps(annotations["validation"]))
    holdout.write_text(json.dumps(list(range(len(annotations["validation"])))))
    replay_outputs = {
        "predictions": tmp_path / "predictions.json",
        "report": tmp_path / "report.json",
    }
    replay_config = MultipleEvaluationConfig(
        models_sha256=file_sha256(outputs["model"]), fitting=config
    )
    context = SimpleNamespace(
        config=replay_config,
        inputs=dict(paths, model=outputs["model"], test=test, holdout=holdout),
        outputs=replay_outputs,
    )
    # There is intentionally no metrics recorder on an artifact-derived EVAL context.
    evaluate_multiple_codebooks(context)
    predictions = json.loads(replay_outputs["predictions"].read_text())
    report = json.loads(replay_outputs["report"].read_text())
    independent = mean_macro_f1_gain(SimpleNamespace(artifacts=replay_outputs))
    assert independent == report["comparison"]["mean_macro_f1_gain"]
    assert report["comparison"]["paired_seed_gains"]["7"] == pytest.approx(
        report["metrics"]["7:multiple_prototype"]["validation"]["macro_f1"]
        - report["metrics"]["7:centroid"]["validation"]["macro_f1"]
    )
    assert report["test_accessed"] is False
    holdout.write_text("[0]")
    with pytest.raises(ValueError, match="complete frozen"):
        evaluate_multiple_codebooks(context)
    holdout.write_text(json.dumps(list(range(len(annotations["validation"])))))
    test.write_text("[]")
    with pytest.raises(ValueError, match="Published development"):
        evaluate_multiple_codebooks(context)
    test.write_text(json.dumps(annotations["validation"]))
    bundle = torch.load(outputs["model"], weights_only=True)
    bundle["models"]["7:centroid"]["validation_probabilities"][0, 0] = 0
    torch.save(bundle, outputs["model"])
    context.config = replay_config.model_copy(
        update={"models_sha256": file_sha256(outputs["model"])}
    )
    with pytest.raises(ValueError, match="reproduce.*predictions"):
        evaluate_multiple_codebooks(context)
    predictions["probabilities"]["7:centroid"][0][0] = float("nan")
    with pytest.raises(ValueError, match="finite"):
        paired_macro_f1_gain(predictions)


def test_native_development_bindings_are_published_eval_sources(tmp_path):
    from csts_pilot.multiple_codebook_run import evaluation_inputs

    record = {
        "reference": {
            "kind": "resolved_run",
            "sha256": "1" * 64,
            "bytes": 1,
            "stored_at": {
                "kind": "local",
                "workspace": str(tmp_path),
                "store": ".viper/store",
                "store_id": "2" * 32,
                "commit": "3" * 64,
                "path": "experiments/example/runs/example/run/resolved.yaml",
            },
        }
    }
    bindings = evaluation_inputs(
        tmp_path,
        {name: tmp_path / name for name in ("annotations", "training", "validation")},
        record,
        record,
    )
    by_name = {binding.name: binding for binding in bindings}
    assert set(by_name) == {
        "annotations",
        "training",
        "validation",
        "model",
        "test",
        "holdout",
    }
    assert by_name["model"].source.data_role == "training"
    for name in ("test", "holdout"):
        assert by_name[name].source.data_role == "eval"
        assert by_name[name].source.artifact.stage_id == "publish"
        assert by_name[name].source.artifact.artifact_name == name


@pytest.mark.parametrize("trigger", (2, 3))
def test_deadline_after_validation_and_selected_prediction(monkeypatch, trigger):
    from csts_pilot import multiple_codebook as module

    training, validation, config = prepared_fixture()
    real_predict = module.predict
    clock, calls = [0.0], [0]

    def timed_predict(*args):
        probabilities = real_predict(*args)
        calls[0] += 1
        if calls[0] == trigger:
            clock[0] = 2.0
        return probabilities

    monkeypatch.setattr(module, "predict", timed_predict)
    monkeypatch.setattr(module.time, "monotonic", lambda: clock[0])
    with pytest.raises(TimeoutError, match="budget"):
        fit_one(
            training,
            validation,
            config.model_copy(update={"seconds_per_fit": 1, "max_epochs": 1}),
            7,
            "centroid",
            lambda *_: None,
        )


def test_execute_rejects_dirty_source_before_native_launch(tmp_path, monkeypatch):
    from csts_pilot import multiple_codebook_run as module

    monkeypatch.setattr(module, "load_json", lambda _path: {})
    monkeypatch.setattr(module, "preflight", lambda *_args: (None, None, None))
    manifest = tmp_path / "manifest.json"
    manifest.write_text("{}")
    monkeypatch.setattr(
        module.subprocess,
        "run",
        lambda *_a, **_k: SimpleNamespace(stdout="?? unreviewed.py\n"),
    )
    monkeypatch.setattr(
        module.execution, "run", lambda *_a, **_k: pytest.fail("dirty source launched")
    )
    with pytest.raises(ValueError, match="clean reviewed"):
        module.run(tmp_path, manifest, "dirty", execute=True)
    assert not (tmp_path / "multiple_codebook_results").exists()
