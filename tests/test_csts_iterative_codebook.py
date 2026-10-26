"""Check correction provenance, equal exposure, masked gradients and selected replay."""

import copy
from types import SimpleNamespace

import pytest
import torch
from torch.nn import functional as F

import csts_pilot.iterative_codebook as iterative
from csts_pilot.codebook import (
    CacheConfig,
    PrototypeEncoder,
    compact_cache,
    representations,
    restore_model,
    scored_rows,
)
from csts_pilot.condition_reference import MODEL_SHA256, native_layout
from csts_pilot.convergence import file_sha256
from csts_pilot.diagnostics import summarize
from csts_pilot.iterative_codebook_run import fitting_stage


def example_cache(split="train", seed=11):
    """Use disjoint source groups and captions with repeated condition/passage keys."""
    rows = []
    for i in range(12):
        rating = [1.0, 2.0, 4.0, 5.0][i % 4]
        rows.append(
            {
                "row_id": f"{split}-{i}",
                "pair_id": f"{split}-pair-{i}",
                "group_id": f"{split}-group-{i // 2}",
                "condition": "activity",
                "sentence1": f"{split} left passage {i // 2}",
                "sentence2": f"{split} right passage {i}",
                "rating": rating,
                "target": (rating - 1) / 4,
            }
        )
    keys, left, right = native_layout(rows)
    vectors = torch.randn(len(keys), 8, generator=torch.Generator().manual_seed(seed))
    # Duplicates intentionally have different feature bytes: a teacher must still
    # assign one target per exact semantic key, rather than target each occurrence.
    return compact_cache(
        {
            "keys": keys,
            "left": left,
            "right": right,
            "native": vectors,
            "rows_sha256": "1" * 64,
            "model_sha256": MODEL_SHA256,
        },
        rows,
        CacheConfig(kind="matched", rows_sha256="1" * 64, source_cache_sha256="2" * 64),
    )


def configuration(**overrides):
    return iterative.IterativeConfig(
        **{
            "seeds": (7,),
            "codes": 4,
            "output_dim": 4,
            "max_epochs": 5,
            "batch_size": 4,
            "kmeans_iterations": 2,
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


def test_teacher_clusters_only_unique_training_keys_and_broadcasts():
    cache, config = example_cache(), configuration()
    model = PrototypeEncoder(8, 4, 4)
    result = iterative.teacher_targets(model, cache, config, 7)
    assert len(result["unique_labels"]) == 18
    assert len(result["labels"]) == 24
    for i, key in enumerate(cache["keys"]):
        matches = [j for j, other in enumerate(cache["keys"]) if other == key]
        assert len(set(result["labels"][matches].tolist())) == 1
    assert torch.bincount(result["unique_labels"], minlength=4).sum() == 18


def test_masked_cluster_loss_trains_projection_and_classifier():
    torch.manual_seed(7)
    model, config = PrototypeEncoder(8, 4, 4), configuration()
    model.dictionary.data.copy_(F.normalize(torch.randn(4, 4), dim=1))
    features = F.normalize(torch.randn(8, 8), dim=1)
    generator = torch.Generator().manual_seed(7)
    mask = iterative.feature_mask(features.shape, 0.25, generator)
    assert (~mask).sum(1).tolist() == [2] * 8
    labels = torch.tensor([0, 1, 2, 3] * 2)
    loss, components = iterative.objective(
        model, features, torch.linspace(0, 1, 4), labels, mask, config
    )
    loss.backward()
    for parameter in (model.projection.weight, model.dictionary):
        assert torch.isfinite(parameter.grad).all() and parameter.grad.norm() > 0
    a, b = model(features).chunk(2)
    assert components["continuous_mse"] == pytest.approx(
        float(F.mse_loss((a * b).sum(1), torch.linspace(0, 1, 4)).detach())
    )
    assert components["cluster_cross_entropy"] > 0
    with pytest.raises(ValueError, match="erased"):
        iterative.objective(
            model, features, torch.zeros(4), labels, torch.zeros_like(mask), config
        )


def test_rand_agreement_treats_permuted_ids_as_same_partition():
    left = torch.tensor([0, 0, 1, 1, 2])
    assert iterative.partition_agreement(left, torch.tensor([2, 2, 0, 0, 1]), 3) == 1
    assert iterative.partition_agreement(left, torch.tensor([0, 1, 1, 1, 2]), 3) < 1


def test_pair_has_identical_batches_masks_updates_and_pre_refresh_states(monkeypatch):
    training, validation, config = (
        example_cache(),
        example_cache("dev", 12),
        configuration(),
    )
    observed_training = []
    original = iterative.teacher_targets

    def observed_teacher(model, cache, config, seed):
        observed_training.append(cache)
        return original(model, cache, config, seed)

    monkeypatch.setattr(iterative, "teacher_targets", observed_teacher)
    snapshots = {}
    original_objective = iterative.objective

    def observed_objective(model, *args):
        key = len(snapshots)
        snapshots[key] = {
            name: value.detach().clone() for name, value in model.state_dict().items()
        }
        return original_objective(model, *args)

    monkeypatch.setattr(iterative, "objective", observed_objective)
    selected, trace, terminal = iterative.fit_pair(training, validation, config, 7)
    assert all(cache is training for cache in observed_training)
    assert len(observed_training) == 3  # initial teacher, then epochs 3 and 5
    for index in range(0, 12, 2):  # three updates per epoch, two epochs before refresh
        for name in snapshots[index]:
            torch.testing.assert_close(
                snapshots[index][name], snapshots[index + 1][name], rtol=0, atol=0
            )
    a, b = trace["fixed"], trace["refreshed"]
    assert len(a["epochs"]) == len(b["epochs"]) == 5
    assert a["updates"] == b["updates"] == 15
    assert a["initial_state_sha256"] == b["initial_state_sha256"]
    for x, y in zip(a["epochs"], b["epochs"], strict=True):
        for key in (
            "batch_order_sha256",
            "feature_masks_sha256",
            "updates",
            "optimizer_resets",
            "refreshed_boundary",
        ):
            assert x[key] == y[key]
    assert len({record["target_labels_sha256"] for record in a["epochs"]}) == 1
    assert [record["optimizer_resets"] for record in a["epochs"]] == [0, 0, 1, 1, 2]
    assert not torch.equal(
        terminal["fixed"]["teacher"]["centers"],
        terminal["refreshed"]["teacher"]["centers"],
    )
    for arm in iterative.ARMS:
        replay = summarize(
            scored_rows(
                validation, representations(restore_model(selected[arm]), validation)
            )
        )
        assert replay == selected[arm]["validation"]
        selected[arm]["state"]["projection.weight"].zero_()
        assert terminal[arm]["state"]["projection.weight"].norm() > 0


def test_paired_patience_equal_selection_budget_and_epoch_zero(monkeypatch):
    real = iterative.summarize

    def constant_score(rows):
        measured = real(rows)
        measured["spearman"] = 0.25
        return measured

    monkeypatch.setattr(iterative, "summarize", constant_score)
    chosen, traces, _ = iterative.fit_pair(
        example_cache(), example_cache("dev", 12), configuration(max_epochs=20), 7
    )
    for arm in iterative.ARMS:
        assert chosen[arm]["epoch"] == 0
        assert len(traces[arm]["epochs"]) == 5
        assert traces[arm]["stop_reason"] == "paired_validation_patience"
        assert traces[arm]["paired_stale_epochs"] == 5
    leaking = copy.deepcopy(example_cache("dev", 12))
    leaking["rows"][0]["group_id"] = example_cache()["rows"][0]["group_id"]
    with pytest.raises(ValueError, match="overlap"):
        iterative.fit_pair(example_cache(), leaking, configuration(), 7)


def test_native_stage_hash_gates_outputs_and_monotonic_metrics(tmp_path):
    training, validation = example_cache(), example_cache("dev", 12)
    paths = {name: tmp_path / (name + ".pt") for name in ("training", "validation")}
    torch.save(training, paths["training"])
    torch.save(validation, paths["validation"])
    config = configuration(
        max_epochs=3,
        **{name + "_cache_sha256": file_sha256(path) for name, path in paths.items()},
    )
    outputs = {
        name: tmp_path / (name + suffix)
        for name, suffix in (
            ("model", ".pt"),
            ("trace", ".json"),
            ("resume_state", ".pt"),
        )
    }

    class Recorder:
        def __init__(self):
            self.steps = []

        def record(self, value, step):
            assert torch.isfinite(torch.tensor(value))
            self.steps.append(step)

    metrics = {
        name: Recorder()
        for name in ("training_objective", "validation_mse", "validation_spearman")
    }
    context = SimpleNamespace(
        config=config,
        inputs=paths,
        outputs=outputs,
        metrics=metrics,
        numpy_generators={},
    )
    iterative.fit_iterative_codebooks(context)
    assert all(path.is_file() for path in outputs.values())
    assert all(
        recorder.steps == sorted(set(recorder.steps)) for recorder in metrics.values()
    )
    saved = torch.load(outputs["model"], weights_only=False)
    assert set(saved["models"]) == {"7:fixed", "7:refreshed"}
    paths["training"].write_bytes(b"changed")
    with pytest.raises(ValueError, match="Changed fitting cache"):
        iterative.fit_iterative_codebooks(context)
    configured = fitting_stage({}, config)
    assert set(configured.outputs.keys()) == {"model", "resume_state", "trace"}


def test_native_development_replay_and_independently_recomputed_gain(tmp_path):
    import json

    from scipy.stats import spearmanr

    from csts_pilot.iterative_codebook_analysis import (
        ReplayConfig,
        evaluate_iterative_codebooks,
        mean_spearman_gain,
    )

    training, validation = example_cache(), example_cache("dev", 12)
    inputs = {
        name: tmp_path / (name + ".pt") for name in ("training", "validation", "model")
    }
    torch.save(training, inputs["training"])
    torch.save(validation, inputs["validation"])
    hashes = {
        name + "_cache_sha256": file_sha256(inputs[name])
        for name in ("training", "validation")
    }
    config = configuration(max_epochs=3, seeds=(7, 8), **hashes)
    models = {}
    for seed in config.seeds:
        chosen, _, _ = iterative.fit_pair(training, validation, config, seed)
        models.update({f"{seed}:{arm}": chosen[arm] for arm in iterative.ARMS})
    torch.save(
        {"config": config.model_dump(mode="json"), "models": models}, inputs["model"]
    )
    for name, data in (("test", validation["rows"]), ("holdout", list(range(12)))):
        inputs[name] = tmp_path / (name + ".json")
        inputs[name].write_text(json.dumps(data))
    outputs = {name: tmp_path / (name + ".json") for name in ("predictions", "report")}
    replay_config = ReplayConfig(models_sha256=file_sha256(inputs["model"]), **hashes)
    context = SimpleNamespace(
        config=replay_config, inputs=inputs, outputs=outputs, metrics={}
    )
    evaluate_iterative_codebooks(context)
    predictions, report = (
        json.loads(outputs[name].read_text()) for name in ("predictions", "report")
    )
    y = [row["target"] for row in validation["rows"]]
    differences = [
        float(spearmanr(y, predictions["scores"][f"{seed}:refreshed"]).statistic)
        - float(spearmanr(y, predictions["scores"][f"{seed}:fixed"]).statistic)
        for seed in config.seeds
    ]
    expected = sum(differences) / len(differences)
    assert report["paired"]["mean_seed_spearman_gain"] == pytest.approx(
        expected, abs=1e-12
    )
    assert mean_spearman_gain(
        SimpleNamespace(artifacts={"predictions": outputs["predictions"]})
    ) == pytest.approx(expected, abs=1e-12)
    assert report["paired"]["seed_gain_sample_sd"] == pytest.approx(
        float(torch.tensor(differences, dtype=torch.float64).std())
    )
    inputs["holdout"].write_text(json.dumps([0]))
    with pytest.raises(ValueError, match="indices"):
        evaluate_iterative_codebooks(context)
    inputs["holdout"].write_text(json.dumps(list(range(12))))
    models["7:fixed"]["state"]["projection.weight"].zero_()
    torch.save(
        {"config": config.model_dump(mode="json"), "models": models}, inputs["model"]
    )
    with pytest.raises(ValueError, match="Changed evaluation input"):
        evaluate_iterative_codebooks(context)
    context.config = replay_config.model_copy(
        update={"models_sha256": file_sha256(inputs["model"])}
    )
    with pytest.raises(ValueError, match="does not reproduce"):
        evaluate_iterative_codebooks(context)


def test_canonical_native_replay_plan_binds_published_development_and_artifact_metric(
    tmp_path,
):
    from pathlib import Path

    from viper.authoring import experiment, plan, replicate, variant
    from viper.references import GitFileRef
    from viper.repository import read_source
    from viper.runtime import CPUComputeSpec, LocalEnvSpec, observe_python_env

    from csts_pilot.iterative_codebook_analysis import ReplayConfig
    from csts_pilot.iterative_codebook_run import replay_stage

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
    configured = replay_stage(
        {"training": record, "validation": record},
        record,
        record,
        ReplayConfig(
            models_sha256="4" * 64,
            training_cache_sha256="5" * 64,
            validation_cache_sha256="6" * 64,
        ),
    )
    bindings = configured.spec.inputs
    assert set(bindings) == {"training", "validation", "model", "test", "holdout"}
    assert bindings["model"].data_role == "training"
    assert bindings["test"].data_role == bindings["holdout"].data_role == "eval"
    assert bindings["test"].artifact.stage_id == "publish"
    assert bindings["test"].artifact.artifact_name == "test"
    assert configured.spec.split_inputs == ("holdout",)
    assert configured.spec.metrics[0].dependencies[0].name == "predictions"
    source = read_source(Path(__file__).resolve().parents[1])
    native_plan = plan(
        experiment=experiment(
            experiment_id="iterative_replay_fixture",
            variants=(
                variant(
                    "replay", stages=(configured,), estimator=configured.outputs.report
                ),
            ),
            replicates=(replicate(seed=7),),
        ),
        source=source,
        env=LocalEnvSpec(
            compute=CPUComputeSpec(),
            python_env=observe_python_env(),
            lockfile=GitFileRef(
                repository=source.repository,
                commit=source.commit,
                path="tranche2_requirements.txt",
            ),
        ),
    )
    assert (
        native_plan is not None
    )  # construction validates canonical native EVAL contract; no execution


def test_pair_refuses_final_diagnostic_time_overrun(monkeypatch):
    clock = [0.0]
    monkeypatch.setattr(iterative.time, "monotonic", lambda: clock[0])
    real = iterative.code_diagnostics

    def overrun(model, cache):
        value = real(model, cache)
        clock[0] = 11.0
        return value

    monkeypatch.setattr(iterative, "code_diagnostics", overrun)
    with pytest.raises(TimeoutError, match="Pair budget"):
        iterative.fit_pair(
            example_cache(),
            example_cache("dev", 12),
            configuration(max_epochs=1, seconds_per_pair=10),
            7,
        )


def test_refresh_targets_change_with_terminal_training_projection():
    features = F.normalize(
        torch.tensor([[2.0, 0, 1], [2.0, 0, -1], [-2.0, 0, 1], [-2.0, 0, -1]]), dim=1
    )
    training = {"vectors": features, "keys": [("activity", str(i)) for i in range(4)]}
    model = PrototypeEncoder(3, 2, 2)
    config = configuration(codes=2, output_dim=2)
    model.projection.weight.data.copy_(torch.tensor([[1.0, 0, 0], [0, 1.0, 0]]))
    first = iterative.teacher_targets(model, training, config, 7)
    model.projection.weight.data.copy_(torch.tensor([[0, 0, 1.0], [0, 1.0, 0]]))
    second = iterative.teacher_targets(model, training, config, 7)
    assert (
        iterative.partition_agreement(
            first["unique_labels"], second["unique_labels"], 2
        )
        < 1
    )
