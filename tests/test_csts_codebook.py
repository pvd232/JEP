"""Observe prototype gradients, split isolation, paired fits and checkpoint replay."""

import copy
from types import SimpleNamespace

import pytest
import torch
from torch.nn import functional as F

from csts_pilot.codebook import (
    CacheConfig,
    CodebookConfig,
    PrototypeEncoder,
    check_disjoint,
    code_diagnostics,
    compact_cache,
    fit_codebooks,
    fit_one,
    objective,
    representations,
    restore_model,
    scored_rows,
    spherical_kmeans,
    unique_positions,
    validate_compact,
)
from csts_pilot.codebook_analysis import (
    EvaluationConfig,
    evaluate_codebooks,
    mean_spearman_gain,
    paired_seed_bootstrap,
)
from csts_pilot.condition_reference import MODEL_SHA256, native_layout
from csts_pilot.convergence import file_sha256
from csts_pilot.diagnostics import summarize


def example_cache(split="train", seed=11):
    """Keep source identities disjoint while exercising all extreme rating bins."""
    rows = []
    for i in range(12):
        rating = [1.0, 2.0, 4.0, 5.0][i % 4]
        rows.append(
            {
                "row_id": f"{split}-{i}",
                "pair_id": f"{split}-pair-{i}",
                "group_id": f"{split}-group-{i // 2}",
                "condition": "color" if i % 2 else "activity",
                "sentence1": f"{split} left passage {i}",
                "sentence2": f"{split} right passage {i}",
                "rating": rating,
                "target": (rating - 1) / 4,
            }
        )
    keys, left, right = native_layout(rows)
    raw = {
        "keys": keys,
        "left": left,
        "right": right,
        "native": torch.randn(
            len(keys), 8, generator=torch.Generator().manual_seed(seed)
        ),
        "rows_sha256": "1" * 64,
        "model_sha256": MODEL_SHA256,
    }
    return compact_cache(
        raw,
        rows,
        CacheConfig(kind="matched", rows_sha256="1" * 64, source_cache_sha256="2" * 64),
    )


def configuration(**overrides):
    """Use a small CPU experiment while preserving the actual fitting code path."""
    return CodebookConfig(
        **{
            "seeds": (7,),
            "codes": 4,
            "output_dim": 4,
            "max_epochs": 3,
            "batch_size": 4,
            "kmeans_iterations": 2,
            "training_cache_sha256": "1" * 64,
            "validation_cache_sha256": "2" * 64,
            **overrides,
        }
    )


@pytest.fixture(autouse=True)
def one_thread():
    """Match production CPU reduction behavior without changing later tests."""
    previous = torch.get_num_threads()
    torch.set_num_threads(1)
    yield
    torch.set_num_threads(previous)


def test_compaction_checks_occurrence_binding_and_provenance():
    cache = example_cache()
    validate_compact(cache)
    assert len(unique_positions(cache)) == len(cache["keys"])
    for key in ("keys", "left", "vectors"):
        bad = copy.deepcopy(cache)
        if key == "keys":
            bad[key][0] = ("wrong condition", "wrong passage")
        elif key == "left":
            bad[key][0] = bad["right"][0]
        else:
            bad[key][0, 0] = float("nan")
        with pytest.raises(ValueError):
            validate_compact(bad)


def test_split_check_detects_group_and_unicode_normalized_caption_leakage():
    training, validation = example_cache(), example_cache("dev", 12)
    check_disjoint(training, validation)
    for caption in (False, True):
        other = copy.deepcopy(validation)
        if caption:
            other["rows"][0]["sentence1"] = "  TRAIN LEFT PASSAGE 0  "
            other["keys"], other["left"], other["right"] = native_layout(other["rows"])
        else:
            other["rows"][0]["group_id"] = training["rows"][0]["group_id"]
        with pytest.raises(ValueError):
            check_disjoint(training, other)


def test_quantizer_uses_nearest_unit_vector_and_straight_through_task_gradient():
    model = PrototypeEncoder(3, 3, 2)
    model.projection.weight.data.copy_(torch.eye(3))
    model.dictionary.data.copy_(torch.tensor([[1.0, 0.0, 0.0], [0.0, 1.0, 0.0]]))
    features = torch.tensor(
        [[1.0, 0.1, 0.2], [0.2, 1.0, 0.1], [0.8, 0.2, 0.1], [0.1, 0.8, 0.3]]
    )
    z = model(features)
    q, ids = model.quantize(z)
    assert ids.tolist() == [0, 1, 0, 1]
    torch.testing.assert_close(q, model.dictionary[ids])
    loss, parts = objective(
        model, features, torch.tensor([0.0, 0.5]), "prototype", 0.1, 0.25
    )
    loss.backward()
    assert torch.isfinite(model.projection.weight.grad).all()
    assert model.projection.weight.grad.norm() > 0
    assert torch.isfinite(model.dictionary.grad).all()
    assert model.dictionary.grad.norm() > 0
    assert set(parts) == {
        "continuous_mse",
        "discrete_mse",
        "dictionary_loss",
        "commitment_loss",
    }


def test_control_objective_has_no_prototype_force():
    torch.manual_seed(7)
    model = PrototypeEncoder(3, 3, 2)
    x, y = torch.randn(8, 3), torch.linspace(0, 1, 4)
    loss, parts = objective(model, x, y, "projection", 0.1, 0.25)
    a, b = model(x).chunk(2)
    torch.testing.assert_close(loss, F.mse_loss((a * b).sum(1), y))
    loss.backward()
    assert model.dictionary.grad is None
    assert list(parts) == ["continuous_mse"]


def test_kmeans_is_deterministic_training_only_and_rejects_degenerate_directions():
    training = F.normalize(torch.randn(30, 5), dim=1)
    a = spherical_kmeans(training, 4, 3, 7)
    b = spherical_kmeans(training, 4, 3, 7)
    torch.testing.assert_close(a, b, rtol=0, atol=0)
    torch.testing.assert_close(a.norm(dim=1), torch.ones(4))
    with pytest.raises(ValueError):
        spherical_kmeans(torch.ones(20, 5), 4, 3, 7)
    with pytest.raises(ValueError):
        spherical_kmeans(training, 31, 3, 7)


def test_paired_fit_matches_initialization_order_and_replays_best_snapshot():
    training, validation = example_cache(), example_cache("dev", 12)
    config = configuration()
    saved = {}
    traces = {}
    for arm in ("projection", "prototype"):
        saved[arm], traces[arm], terminal = fit_one(
            training, validation, config, 7, arm, lambda *_: None
        )
        assert terminal["updates"] == len(traces[arm]["epochs"]) * 3
        restored = restore_model(saved[arm])
        assert (
            summarize(scored_rows(validation, representations(restored, validation)))
            == saved[arm]["validation"]
        )
        # The saved dictionary and projection remain independent of mutable model state.
        before = saved[arm]["state"]["projection.weight"].clone()
        restored.projection.weight.data.zero_()
        torch.testing.assert_close(saved[arm]["state"]["projection.weight"], before)
        assert saved[arm]["codes_training"]["occupied_codes"] >= 1
    assert (
        traces["projection"]["initial_state_sha256"]
        == traces["prototype"]["initial_state_sha256"]
    )
    assert [r["batch_order_sha256"] for r in traces["projection"]["epochs"]] == [
        r["batch_order_sha256"] for r in traces["prototype"]["epochs"]
    ]
    assert saved["projection"]["dictionary_origin"] == "post_hoc_training_kmeans"
    assert saved["prototype"]["dictionary_origin"] == "joint_training"


def test_usage_reports_collapse_and_negative_merges_instead_of_hiding_them():
    cache = example_cache()
    model = PrototypeEncoder(8, 4, 4)
    model.dictionary.data[:, 0] = 1
    result = code_diagnostics(model, cache)
    assert result["occupied_codes"] == 1
    assert result["effective_codes"] == 1
    assert result["largest_code_share"] == 1
    assert result["negative_same_code"] == result["negative_pairs"]
    assert result["quantized_similarity"]["spearman"] is None


def test_group_bootstrap_and_independent_metric_keep_paired_seed_statistic(tmp_path):
    import json

    rows = example_cache()["rows"]
    y = [row["target"] for row in rows]
    scores = {
        "7:projection": list(reversed(y)),
        "7:prototype": y,
        "8:projection": y,
        "8:prototype": y,
    }
    report = paired_seed_bootstrap(rows, scores, [7, 8], 30, 9)
    path = tmp_path / "predictions.json"
    path.write_text(json.dumps({"rows": rows, "scores": scores, "seeds": [7, 8]}))
    measured = mean_spearman_gain(SimpleNamespace(artifacts={"predictions": path}))
    assert measured == pytest.approx(report["mean_seed_spearman_gain"])
    assert report["groups"] == 6
    assert report["valid_draws"] == 30
    assert report["paired_seed_gains"]["8"] == 0


@pytest.mark.parametrize("seeds", [(), (7, 7), (-1,)])
def test_config_rejects_ambiguous_seeds(seeds):
    with pytest.raises(ValueError):
        configuration(seeds=seeds)


def test_stage_outputs_resume_and_independent_evaluation_round_trip(tmp_path):
    """Exercise the complete fitter/evaluator boundary with real saved artifacts."""
    import json

    class Recorder:
        def record(self, value, **kwargs):
            assert isinstance(value, (int, float))

    paths = {}
    for split, cache in (
        ("training", example_cache()),
        ("validation", example_cache("dev", 12)),
    ):
        paths[split] = tmp_path / (split + ".pt")
        torch.save(cache, paths[split])
    config = configuration(
        seeds=(7, 8),
        max_epochs=2,
        training_cache_sha256=file_sha256(paths["training"]),
        validation_cache_sha256=file_sha256(paths["validation"]),
    )
    outputs = {
        name: tmp_path / filename
        for name, filename in (
            ("model", "models.pt"),
            ("trace", "trace.json"),
            ("resume_state", "resume.pt"),
        )
    }
    fit_codebooks(
        SimpleNamespace(
            config=config,
            inputs=paths,
            outputs=outputs,
            numpy_generators={},
            metrics={
                name: Recorder()
                for name in (
                    "training_objective",
                    "validation_mse",
                    "validation_spearman",
                )
            },
        )
    )
    assert outputs["resume_state"].exists()
    assert json.loads(outputs["trace"].read_text())["test_accessed"] is False
    holdout = tmp_path / "indices.json"
    holdout.write_text(json.dumps(list(range(12))))
    evaluated = {
        name: tmp_path / (name + ".json")
        for name in ("predictions", "report", "review")
    }
    evaluate_codebooks(
        SimpleNamespace(
            config=EvaluationConfig(
                models_sha256=file_sha256(outputs["model"]),
                training_cache_sha256=config.training_cache_sha256,
                validation_cache_sha256=config.validation_cache_sha256,
                bootstrap_draws=20,
            ),
            inputs={**paths, "models": outputs["model"], "holdout": holdout},
            outputs=evaluated,
            metrics={"codebook_mean_spearman_gain": Recorder()},
        )
    )
    report = json.loads(evaluated["report"].read_text())
    assert report["evaluation_split"] == "validation"
    assert len(report["metrics"]) == 4
    independent = mean_spearman_gain(
        SimpleNamespace(artifacts={"predictions": evaluated["predictions"]})
    )
    assert independent == pytest.approx(
        report["bootstrap"]["mean_seed_spearman_gain"], abs=1e-12
    )
    assert (
        json.loads(evaluated["review"].read_text())["status"] == "unreviewed_candidates"
    )
