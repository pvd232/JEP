"""Check preserved geometry, actual updates, matched exposure and saved replay."""

import json
from types import SimpleNamespace

import pytest
import torch
from scipy.stats import spearmanr
from torch.nn import functional as F

import csts_pilot.residual_codebook as residual
from csts_pilot.codebook import (
    CacheConfig,
    compact_cache,
    objective,
    representations,
    scored_rows,
)
from csts_pilot.condition_reference import MODEL_SHA256, native_layout
from csts_pilot.convergence import file_sha256
from csts_pilot.diagnostics import summarize


def example_cache(split="train", seed=11):
    rows = []
    for index in range(12):
        rating = [1.0, 2.0, 4.0, 5.0][index % 4]
        rows.append(
            {
                "row_id": f"{split}-{index}",
                "pair_id": f"{split}-pair-{index}",
                "group_id": f"{split}-group-{index // 2}",
                "condition": "activity",
                "sentence1": f"{split} left {index}",
                "sentence2": f"{split} right {index}",
                "rating": rating,
                "target": (rating - 1) / 4,
            }
        )
    keys, left, right = native_layout(rows)
    return compact_cache(
        {
            "keys": keys,
            "left": left,
            "right": right,
            "native": torch.randn(
                len(keys), 8, generator=torch.Generator().manual_seed(seed)
            ),
            "rows_sha256": "1" * 64,
            "model_sha256": MODEL_SHA256,
        },
        rows,
        CacheConfig(kind="matched", rows_sha256="1" * 64, source_cache_sha256="2" * 64),
    )


def configuration(validation, **overrides):
    baseline = summarize(
        scored_rows(validation, F.normalize(validation["vectors"], dim=1))
    )["spearman"]
    return residual.ResidualConfig(
        **{
            "seeds": (7,),
            "rank": 2,
            "codes": 4,
            "max_epochs": 2,
            "batch_size": 4,
            "kmeans_iterations": 2,
            "expected_baseline_spearman": baseline,
            "training_cache_sha256": "1" * 64,
            "validation_cache_sha256": "2" * 64,
            **overrides,
        }
    )


@pytest.fixture(autouse=True)
def one_thread():
    previous = torch.get_num_threads()
    torch.set_num_threads(1)
    yield
    torch.set_num_threads(previous)


def test_full_vector_initialization_preserves_geometry_and_can_learn():
    torch.manual_seed(7)
    model = residual.ResidualEncoder(4096, 32, 4)
    features = F.normalize(torch.randn(8, 4096), dim=1)
    initial = model(features)
    assert initial.shape == features.shape
    torch.testing.assert_close(initial, F.normalize(features, dim=1), rtol=0, atol=0)
    model.dictionary.data.copy_(F.normalize(torch.randn(4, 4096), dim=1))
    loss, _ = objective(
        model, features, torch.linspace(0, 1, 4), "prototype", 0.1, 0.25
    )
    loss.backward()
    assert model.projection.up.weight.grad.norm() > 0
    assert torch.isfinite(model.projection.up.weight.grad).all()
    assert torch.count_nonzero(model.projection.down.weight.grad) == 0
    torch.optim.SGD(model.projection.parameters(), lr=0.1).step()
    assert not torch.equal(model(features), initial)


def test_paired_updates_replay_and_selected_states_are_independent():
    training, validation = example_cache(), example_cache("dev", 12)
    chosen, traces, terminal = residual.fit_pair(
        training, validation, configuration(validation), 7
    )
    first, second = (traces[arm] for arm in residual.ARMS)
    assert first["initial_state_sha256"] == second["initial_state_sha256"]
    assert first["updates"] == second["updates"] == 6
    for left, right in zip(first["epochs"], second["epochs"], strict=True):
        assert left["batch_order_sha256"] == right["batch_order_sha256"]
        assert left["updates"] == right["updates"]
    for arm in residual.ARMS:
        replay = summarize(
            scored_rows(
                validation,
                representations(residual.restore_residual(chosen[arm]), validation),
            )
        )
        assert replay == chosen[arm]["validation"]
        assert chosen[arm]["group_metrics_validation"]["achieved_recall"] == 0.9
        terminal_before = terminal[arm]["state"]["projection.up.weight"].clone()
        chosen[arm]["state"]["projection.up.weight"].zero_()
        torch.testing.assert_close(
            terminal[arm]["state"]["projection.up.weight"], terminal_before
        )
        assert terminal_before.norm() > 0


def test_baseline_mismatch_stops_before_training(monkeypatch):
    validation = example_cache("dev", 12)
    monkeypatch.setattr(
        residual.torch.optim,
        "AdamW",
        lambda *_a, **_k: pytest.fail("Optimizer allocated after baseline mismatch"),
    )
    with pytest.raises(ValueError, match="baseline|Baseline"):
        residual.fit_pair(
            example_cache(),
            validation,
            configuration(validation, expected_baseline_spearman=0.99),
            7,
        )


def test_group_false_merge_rate_has_exact_coverage_when_all_scores_tie():
    cache = example_cache()
    cache["vectors"].zero_()
    cache["vectors"][:, 0] = 1
    model = residual.ResidualEncoder(8, 2, 2)
    model.dictionary.data.zero_()
    model.dictionary.data[0, 0] = 1
    model.dictionary.data[1, 0] = -1
    measured = residual.matched_group_metrics(model, cache)
    assert measured["requested_recall"] == measured["achieved_recall"] == 0.9
    assert measured["tie_acceptance_probability"] == pytest.approx(0.9)
    assert measured["false_positive_rate"] == pytest.approx(0.9)
    assert measured["positives"] == measured["negatives"] == 6


def test_gradient_diagnostics_measure_weighted_actual_training_force():
    torch.manual_seed(7)
    model = residual.ResidualEncoder(8, 2, 4)
    model.dictionary.data.copy_(F.normalize(torch.randn(4, 8), dim=1))
    features, ratings = F.normalize(torch.randn(8, 8), dim=1), torch.linspace(0, 1, 4)
    config = configuration(example_cache("dev", 12))
    first = residual.gradient_diagnostics(model, features, ratings, config)
    doubled = residual.gradient_diagnostics(
        model,
        features,
        ratings,
        config.model_copy(update={"auxiliary_weight": 2 * config.auxiliary_weight}),
    )
    assert first["rating_grad_norm"] > 0
    assert first["weighted_aux_grad_norm"] > 0
    assert doubled["rating_grad_norm"] == pytest.approx(first["rating_grad_norm"])
    assert doubled["weighted_aux_grad_norm"] == pytest.approx(
        2 * first["weighted_aux_grad_norm"], rel=1e-5
    )
    assert doubled["cosine"] == pytest.approx(first["cosine"], abs=1e-5)
    control = residual.gradient_diagnostics(
        model, features, ratings, config, "projection"
    )
    assert control["weighted_aux_grad_norm"] == 0
    assert control["cosine"] is None
    assert all(parameter.grad is None for parameter in model.parameters())


def test_shared_patience_retains_starting_state_and_equal_updates(monkeypatch):
    validation = example_cache("dev", 12)
    config = configuration(validation, max_epochs=20, expected_baseline_spearman=0.25)
    summarize_real = residual.summarize

    def constant_score(rows):
        measured = summarize_real(rows)
        measured["spearman"] = 0.25
        return measured

    monkeypatch.setattr(residual, "summarize", constant_score)
    chosen, traces, _ = residual.fit_pair(example_cache(), validation, config, 7)
    for arm in residual.ARMS:
        assert chosen[arm]["epoch"] == 0
        assert traces[arm]["updates"] == 15
        assert len(traces[arm]["epochs"]) == 5
        assert traces[arm]["stop_reason"] == "paired_validation_patience"


def test_native_development_replay_recomputes_scores_and_paired_gain(tmp_path):
    from csts_pilot.residual_codebook_analysis import (
        ReplayConfig,
        evaluate_residual_codebooks,
        mean_spearman_gain,
    )

    training, validation = example_cache(), example_cache("dev", 12)
    inputs = {
        name: tmp_path / f"{name}.pt" for name in ("training", "validation", "model")
    }
    for name, cache in (("training", training), ("validation", validation)):
        torch.save(cache, inputs[name])
    hashes = {
        name + "_cache_sha256": file_sha256(inputs[name])
        for name in ("training", "validation")
    }
    config = configuration(validation, seeds=(7, 8), max_epochs=1, **hashes)
    models = {}
    for seed in config.seeds:
        selected, _, _ = residual.fit_pair(training, validation, config, seed)
        models.update({f"{seed}:{arm}": selected[arm] for arm in residual.ARMS})
    torch.save(
        {"config": config.model_dump(mode="json"), "models": models}, inputs["model"]
    )
    for name, data in (("test", validation["rows"]), ("holdout", list(range(12)))):
        inputs[name] = tmp_path / f"{name}.json"
        inputs[name].write_text(json.dumps(data))
    outputs = {name: tmp_path / f"{name}.json" for name in ("predictions", "report")}
    context = SimpleNamespace(
        config=ReplayConfig(models_sha256=file_sha256(inputs["model"]), **hashes),
        inputs=inputs,
        outputs=outputs,
        metrics={},
    )
    evaluate_residual_codebooks(context)
    predictions = json.loads(outputs["predictions"].read_text())
    report = json.loads(outputs["report"].read_text())
    targets = [row["target"] for row in validation["rows"]]
    gains = [
        float(spearmanr(targets, predictions["scores"][f"{seed}:prototype"]).statistic)
        - float(
            spearmanr(targets, predictions["scores"][f"{seed}:projection"]).statistic
        )
        for seed in config.seeds
    ]
    expected = sum(gains) / len(gains)
    assert report["paired"]["mean_seed_spearman_gain"] == pytest.approx(expected)
    assert mean_spearman_gain(
        SimpleNamespace(artifacts={"predictions": outputs["predictions"]})
    ) == pytest.approx(expected)
    inputs["holdout"].write_text("[0]")
    with pytest.raises(ValueError, match="cohort|indices"):
        evaluate_residual_codebooks(context)
