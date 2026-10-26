"""Exercise matched-baseline semantics, gradients and selection boundaries."""

import copy
import json
from types import SimpleNamespace

import pytest
import torch
from torch.nn import functional as F

from csts_pilot.matched_baselines import (
    ARMS,
    FITTED_ARMS,
    CorrectedHead,
    HeadConfig,
    choose_bank,
    emit,
    fit_head,
    head_fit_rows,
    make_features,
    scores_from_cache,
    select_candidates,
    validate_cache_rows,
    validate_feature_cache,
)


def comparison(index, group=None, condition="color"):
    """Make valid comparison identities with independent source captions."""
    return {
        "row_id": f"row-{index}",
        "pair_id": f"pair-{index}",
        "group_id": group or f"group-{index}",
        "sentence1": f"A red car numbered {index}.",
        "sentence2": f"A blue car numbered {index}.",
        "condition": condition,
        "rating": 2.0,
        "target": 0.25,
    }


def feature_cache():
    """Use two conditions and noncollinear, unequal-norm raw states."""
    return {
        "keys": [
            ("color", "a red car"),
            ("color", "a blue car"),
            ("activity", "a person running"),
            ("activity", "a person walking"),
        ],
        "left": [0, 2],
        "right": [1, 3],
        "native": torch.tensor(
            [[3.0, 1.0, 2.0], [1.0, 4.0, 1.0], [2.0, 3.0, 4.0], [4.0, 2.0, 3.0]]
        ),
        "generic": torch.tensor(
            [[1.0, 0.0, 1.0], [0.0, 1.0, 1.0], [1.0, 1.0, 0.0], [0.0, 1.0, 2.0]]
        ),
        "case": torch.tensor(
            [[2.0, 3.0, 1.0], [4.0, 1.0, 2.0], [1.0, 4.0, 3.0], [3.0, 2.0, 4.0]]
        ),
        "condition_keys": ["color", "activity"],
        "corrections": torch.tensor([[1.0, 2.0, 0.0], [0.0, 1.0, 2.0]]),
        "case_references": torch.tensor([[0.0, 1.0, 0.0], [1.0, 0.0, 1.0]]),
        "embedding_dimension": 3,
        "rows_sha256": "1" * 64,
        "bank_sha256": "2" * 64,
        "model_sha256": "8805f9a7241e4e19ffc481341ebad6f1ddb6dd6ff04bbf710f9f0896469e34ff",
    }


def metric(spearman, fpr, ordering):
    """Supply only the public measurements used for candidate eligibility."""
    return {
        "spearman": spearman,
        "operating_point": {"false_positive_rate": fpr, "recall": 0.9, "cutoff": 0.5},
        "condition_changes": {"accuracy_ties_half": ordering},
    }


def selection_metrics():
    """Compare every alternative with the existing sealed native scorer."""
    metrics = {arm: metric(0.79, 0.14, 0.89) for arm in FITTED_ARMS}
    metrics["native_direct"] = metric(0.80, 0.10, 0.90)
    return metrics


def test_bank_is_training_only_group_distinct_and_order_independent():
    training = [comparison(i) for i in range(20)]
    training += [comparison(100, group="group-0")]
    validation = [comparison(200), comparison(201)]
    first = choose_bank(training, validation, bank_size=16, seed=7)
    second = choose_bank(
        list(reversed(training)), list(reversed(validation)), bank_size=16, seed=7
    )
    assert first == second
    assert len(first["passages"]) == len(first["groups"]) == 16
    assert len(set(first["groups"])) == 16
    assert set(first["groups"]) <= {row["group_id"] for row in training}
    assert set(first["passages"]) <= {
        row[side] for row in training for side in ("sentence1", "sentence2")
    }
    assert set(first["excluded_training_groups"]) == set(first["groups"])
    fitted = head_fit_rows(training, first)
    expected = [r for r in training if r["group_id"] not in first["groups"]]
    assert fitted == expected
    assert not {r["group_id"] for r in fitted} & set(first["groups"])


def test_bank_rejects_overlapping_source_groups_and_canonical_captions():
    training = [comparison(i) for i in range(5)]
    validation = [comparison(20, group="group-0")]
    with pytest.raises(ValueError):
        choose_bank(training, validation, bank_size=2, seed=7)
    validation = [comparison(20)]
    validation[0]["sentence1"] = "  A RED CAR NUMBERED 0.  "
    with pytest.raises(ValueError):
        choose_bank(training, validation, bank_size=2, seed=7)


def test_bank_rejects_insufficient_groups_and_conflicting_caption_components():
    training = [comparison(i, group="one-group") for i in range(4)]
    with pytest.raises(ValueError):
        choose_bank(training, [comparison(20)], bank_size=2, seed=7)
    training = [comparison(i) for i in range(4)]
    training[1]["sentence1"] = training[0]["sentence1"]
    with pytest.raises(ValueError):
        choose_bank(training, [comparison(20)], bank_size=2, seed=7)


def test_features_keep_the_raw_norms_and_join_references_by_condition():
    cache = feature_cache()
    validate_feature_cache(cache)
    raw, reference = make_features(cache, "same_passage")
    torch.testing.assert_close(raw, cache["native"])
    torch.testing.assert_close(reference, cache["generic"])
    assert not torch.allclose(raw.norm(dim=1), torch.ones(len(raw)))
    raw, reference = make_features(cache, "population")
    torch.testing.assert_close(raw, cache["native"])
    torch.testing.assert_close(reference, cache["corrections"][[0, 0, 1, 1]])
    raw, reference = make_features(cache, "case")
    torch.testing.assert_close(raw, cache["case"])
    torch.testing.assert_close(reference, cache["case_references"][[0, 0, 1, 1]])


@pytest.mark.parametrize(
    "mutation",
    [
        lambda c: c["native"].__setitem__((0, 1), torch.nan),
        lambda c: c.__setitem__("generic", torch.zeros(3, 3)),
        lambda c: c.__setitem__("left", [0, 10]),
        lambda c: c.__setitem__("condition_keys", ["color", "color"]),
        lambda c: c.__setitem__("model_sha256", "invalid"),
        lambda c: c.__setitem__("rows_sha256", "invalid"),
        lambda c: c.__setitem__("bank_sha256", "invalid"),
    ],
)
def test_cache_rejects_nonfinite_shape_index_and_identity_corruption(mutation):
    cache = feature_cache()
    mutation(cache)
    with pytest.raises(ValueError):
        validate_feature_cache(cache)


def test_projection_rejects_an_undefined_direction():
    cache = feature_cache()
    cache["corrections"][0].zero_()
    with pytest.raises(ValueError):
        make_features(cache, "projection")


@pytest.mark.parametrize(
    "field", ("native", "generic", "case", "corrections", "case_references")
)
def test_every_feature_population_rejects_nonfinite_values(field):
    cache = feature_cache()
    cache[field][0, 0] = torch.inf
    with pytest.raises(ValueError):
        validate_feature_cache(cache)


def test_zero_native_state_is_rejected_before_scoring():
    cache = feature_cache()
    cache["native"][0].zero_()
    with pytest.raises(ValueError):
        validate_feature_cache(cache)


@pytest.mark.parametrize("arm", ARMS)
def test_residual_operator_matches_its_declared_formula(arm):
    raw, reference = make_features(feature_cache(), arm)
    head = CorrectedHead(arm, input_dim=3, output_dim=3, dropout=0)
    expected = raw
    if arm in {"same_passage", "population", "case"}:
        expected = raw - head.alpha * reference
    elif arm == "projection":
        component = (
            (raw * reference).sum(1, keepdim=True)
            / reference.square().sum(1, keepdim=True)
            * reference
        )
        expected = raw - head.alpha * component
    torch.testing.assert_close(head.residual(raw, reference), expected)


def test_full_projection_is_orthogonal_and_idempotent():
    raw, reference = make_features(feature_cache(), "projection")
    head = CorrectedHead("projection", input_dim=3, output_dim=3, dropout=0).double()
    # A large finite logit rounds sigmoid to the exact endpoint in float64.
    with torch.no_grad():
        head.alpha_logit.fill_(50)
    assert float(head.alpha.detach()) == 1
    raw, reference = raw.double(), reference.double()
    once = head.residual(raw, reference)
    torch.testing.assert_close(
        (once * reference).sum(1),
        torch.zeros(len(raw), dtype=torch.float64),
        atol=1e-12,
        rtol=0,
    )
    torch.testing.assert_close(head.residual(once, reference), once, atol=1e-12, rtol=0)


def test_projection_keeps_inputs_already_orthogonal_to_the_direction():
    head = CorrectedHead("projection", input_dim=3, output_dim=3, dropout=0).double()
    raw = torch.tensor([[2.0, -1.0, 4.0]], dtype=torch.float64)
    reference = torch.tensor([[1.0, 2.0, 0.0]], dtype=torch.float64)
    torch.testing.assert_close(head.residual(raw, reference), raw, atol=0, rtol=0)


def test_projection_raw_and_reference_jacobians_match_the_derivations():
    head = CorrectedHead("projection", input_dim=3, output_dim=3, dropout=0).double()
    raw = torch.tensor([[2.0, 3.0, 4.0]], dtype=torch.float64, requires_grad=True)
    reference = torch.tensor(
        [[1.0, -0.5, 2.0]], dtype=torch.float64, requires_grad=True
    )
    incoming = torch.tensor([[0.4, -0.3, 0.8]], dtype=torch.float64)
    (head.residual(raw, reference) * incoming).sum().backward()
    h, b, u = raw.detach()[0], reference.detach()[0], incoming[0]
    alpha = head.alpha.detach()
    identity = torch.eye(3, dtype=torch.float64)
    squared_norm = b @ b
    coefficient = (b @ h) / squared_norm
    projection = torch.outer(b, b) / squared_norm
    raw_jacobian = identity - alpha * projection
    reference_jacobian = -alpha * (
        coefficient * identity
        + torch.outer(b, h) / squared_norm
        - 2 * coefficient * torch.outer(b, b) / squared_norm
    )
    assert raw.grad is not None and reference.grad is not None
    torch.testing.assert_close(raw.grad[0], raw_jacobian.T @ u, atol=1e-12, rtol=1e-12)
    torch.testing.assert_close(
        reference.grad[0], reference_jacobian.T @ u, atol=1e-12, rtol=1e-12
    )


def test_alpha_initialization_and_head_initialization_are_matched():
    initial = None
    for arm in ARMS:
        torch.manual_seed(7)
        head = CorrectedHead(arm, input_dim=3, output_dim=5, dropout=0.15)
        weight = head.linear.weight.detach().clone()
        if initial is None:
            initial = weight
        else:
            torch.testing.assert_close(weight, initial, atol=0, rtol=0)
        expected = 0.0 if arm == "native" else 1.0 if arm == "case" else 0.5
        assert float(head.alpha.detach()) == expected
        if arm in {"same_passage", "population", "projection"}:
            assert head.alpha_logit.requires_grad


@pytest.mark.parametrize("arm", FITTED_ARMS)
def test_head_preserves_float32_under_worker_autocast(arm):
    torch.manual_seed(19)
    head = CorrectedHead(arm, input_dim=3, output_dim=4, dropout=0).eval()
    raw, reference = make_features(feature_cache(), arm)
    expected = head(raw, reference)
    with torch.autocast("cpu", dtype=torch.bfloat16):
        observed = head(raw, reference)
    assert observed.dtype == torch.float32
    torch.testing.assert_close(observed, expected, atol=0, rtol=0)
    observed.square().sum().backward()
    assert head.linear.weight.grad is not None
    assert head.linear.weight.grad.dtype == torch.float32
    assert torch.isfinite(head.linear.weight.grad).all()


@pytest.mark.parametrize("arm", ARMS)
def test_head_weight_and_alpha_gradients_match_finite_differences(arm):
    torch.manual_seed(19)
    head = CorrectedHead(arm, input_dim=3, output_dim=4, dropout=0).double().eval()
    raw, reference = make_features(feature_cache(), arm)
    raw, reference = raw.double(), reference.double()

    def objective():
        vectors = head(raw, reference)
        score = (vectors[[0, 2]] * vectors[[1, 3]]).sum(1)
        return (score - torch.tensor([0.2, 0.7], dtype=torch.float64)).square().mean()

    objective().backward()
    checked = [(head.linear.weight, (0, 0))]
    if arm in {"same_passage", "population", "projection"}:
        checked.append((head.alpha_logit, ()))
    for parameter, index in checked:
        assert parameter.grad is not None
        analytic = float(parameter.grad[index])
        original = float(parameter.detach()[index])
        epsilon = 1e-6
        with torch.no_grad():
            parameter[index] = original + epsilon
            plus = float(objective())
            parameter[index] = original - epsilon
            minus = float(objective())
            parameter[index] = original
        assert analytic == pytest.approx(
            (plus - minus) / (2 * epsilon), abs=2e-7, rel=2e-5
        )


def test_native_head_normalization_jacobian_matches_the_analytic_expression():
    head = CorrectedHead("native", input_dim=3, output_dim=3, dropout=0).double().eval()
    with torch.no_grad():
        head.linear.weight.copy_(torch.eye(3, dtype=torch.float64))
    raw = torch.tensor([[0.4, 0.7, 1.1]], dtype=torch.float64, requires_grad=True)
    direction = torch.tensor([[1.0, -0.5, 0.3]], dtype=torch.float64)
    normalized = head(raw, torch.zeros_like(raw))
    (normalized * direction).sum().backward()
    unit = F.normalize(raw.detach(), dim=1)
    expected = (
        direction - unit * (unit * direction).sum(1, keepdim=True)
    ) / raw.detach().norm(dim=1, keepdim=True)
    assert raw.grad is not None
    torch.testing.assert_close(raw.grad, expected, atol=1e-12, rtol=1e-12)


def test_candidate_must_beat_the_existing_control_and_preserve_both_guards():
    metrics = selection_metrics()
    metrics["same_passage"] = metric(0.8049, 0.10, 0.90)
    assert select_candidates(metrics)["selected_arm"] is None
    metrics["same_passage"] = metric(0.805, 0.11, 0.89)
    assert select_candidates(metrics)["selected_arm"] == "same_passage"
    metrics["same_passage"] = metric(0.805, 0.1101, 0.89)
    assert select_candidates(metrics)["selected_arm"] is None
    metrics["same_passage"] = metric(0.805, 0.11, 0.8899)
    assert select_candidates(metrics)["selected_arm"] is None


def test_selection_ties_use_fpr_then_condition_ordering_then_fixed_arm_order():
    metrics = selection_metrics()
    for arm in ("same_passage", "population", "projection"):
        metrics[arm] = metric(0.82, 0.10, 0.90)
    assert select_candidates(metrics)["selected_arm"] == "same_passage"
    metrics["population"] = metric(0.82, 0.099, 0.90)
    assert select_candidates(metrics)["selected_arm"] == "population"
    metrics["projection"] = metric(0.82, 0.099, 0.905)
    assert select_candidates(metrics)["selected_arm"] == "projection"


def test_selection_rejects_undefined_metrics_and_keeps_inputs_unchanged():
    metrics = selection_metrics()
    original = copy.deepcopy(metrics)
    assert select_candidates(metrics)["selected_arm"] is None
    assert metrics == original
    metrics["population"] = metric(float("nan"), 0.09, 0.91)
    with pytest.raises(ValueError):
        select_candidates(metrics)


def test_events_are_broadcast_to_the_correct_sidecar(tmp_path, monkeypatch, capsys):
    events = tmp_path / "events.jsonl"
    monkeypatch.setenv("CSTS_TRANCHE5_EVENTS", str(events))
    emit("arm_progress", arm="native", completed=1)
    expected = {"event": "arm_progress", "arm": "native", "completed": 1}
    assert json.loads(capsys.readouterr().out) == expected
    assert [json.loads(line) for line in events.read_text().splitlines()] == [expected]
    before = events.read_bytes()
    with pytest.raises(ValueError):
        emit("arm_progress", loss=float("nan"))
    assert events.read_bytes() == before


def test_semantic_cache_join_rejects_an_in_range_permutation():
    cache = feature_cache()
    rows = [comparison(0, condition="color"), comparison(1, condition="activity")]
    for i, row in enumerate(rows):
        row["sentence1"] = cache["keys"][cache["left"][i]][1]
        row["sentence2"] = cache["keys"][cache["right"][i]][1]
    validate_cache_rows(cache, rows)
    cache["left"] = [2, 0]
    validate_feature_cache(cache)  # Index multiplicity remains valid.
    with pytest.raises(ValueError):
        validate_cache_rows(cache, rows)


def test_toy_head_fit_and_selection_use_the_sealed_selected_weights(tmp_path):
    from csts_pilot.convergence import file_sha256, write_json
    from csts_pilot.matched_baselines_run import (
        SelectionConfig,
        freeze_selection,
    )
    from jep_pilot.loaders import load_json, load_model

    def pair(index, group):
        color = comparison(index, group=group)
        color.update(rating=1.0, target=0.0)
        activity = dict(
            color,
            row_id=f"activity-{index}",
            condition="activity",
            rating=5.0,
            target=1.0,
        )
        return [color, activity]

    training = pair(0, "train-zero") + pair(1, "train-one")
    validation = pair(20, "validation")
    paths = {
        name: tmp_path / f"{name}.json" for name in ("training", "validation", "bank")
    }
    write_json(paths["training"], training)
    write_json(paths["validation"], validation)
    bank = choose_bank(training, validation, bank_size=1, seed=7)
    write_json(paths["bank"], bank)

    def cache_for(rows, digest):
        template = feature_cache()
        cache = dict(template)
        cache["keys"] = [
            (row["condition"], row[side])
            for row in rows
            for side in ("sentence1", "sentence2")
        ]
        cache["left"] = [2 * i for i in range(len(rows))]
        cache["right"] = [2 * i + 1 for i in range(len(rows))]
        for field in ("native", "generic", "case"):
            cache[field] = template[field].repeat(len(rows) // 2, 1)
        cache["rows_sha256"] = digest
        cache["bank_sha256"] = file_sha256(paths["bank"])
        return cache

    for split, rows in (("training", training), ("validation", validation)):
        paths[split + "_cache"] = tmp_path / f"{split}_cache.pt"
        torch.save(cache_for(rows, file_sha256(paths[split])), paths[split + "_cache"])

    class Recorder:
        def __init__(self):
            self.values = []

        def record(self, value, *, step):
            self.values.append((step, value))

    fitted = {}
    for arm in FITTED_ARMS:
        directory = tmp_path / arm
        directory.mkdir()
        outputs = {
            name: directory / filename
            for name, filename in (
                ("model", "model.pt"),
                ("validation_predictions", "predictions.json"),
                ("trace", "trace.json"),
                ("resume_state", "resume.pt"),
            )
        }
        config = HeadConfig(
            arm=arm,
            device="cpu",
            output_dim=4,
            dropout=0,
            max_epochs=2,
            patience=2,
            batch_size=2,
            max_seconds=60,
            training_sha256=file_sha256(paths["training"]),
            validation_sha256=file_sha256(paths["validation"]),
            bank_sha256=file_sha256(paths["bank"]),
            training_cache_sha256=file_sha256(paths["training_cache"]),
            validation_cache_sha256=file_sha256(paths["validation_cache"]),
        )
        context = SimpleNamespace(
            config=config,
            inputs=paths,
            outputs=outputs,
            numpy_generators={},
            metrics={
                name: Recorder()
                for name in (
                    "training_objective",
                    "validation_spearman",
                    "validation_mse",
                )
            },
        )
        fit_head(context)
        trace, saved = load_json(outputs["trace"]), load_model(outputs["model"])
        expected_rows = head_fit_rows(training, bank)
        assert saved["head_fit_row_ids"] == [row["row_id"] for row in expected_rows]
        assert trace["training_rows"] == len(expected_rows)
        assert trace["frozen_encoder_optimizer_updates"] == 0
        assert trace["selected_model_sha256"] == file_sha256(outputs["model"])
        predictions = load_json(outputs["validation_predictions"])
        reproduced = scores_from_cache(
            saved, load_model(paths["validation_cache"]), "cpu"
        )
        assert reproduced == [row["prediction"] for row in predictions]
        assert outputs["resume_state"].exists()
        fitted[arm] = outputs

    val_cache = load_model(paths["validation_cache"])
    old = tmp_path / "native_predictions.json"
    # The saved control scores are independent of the newly extracted states.
    write_json(
        old,
        [
            dict(row, prediction=value)
            for row, value in zip(validation, (0.1, 0.9), strict=True)
        ],
    )
    selection_inputs = {
        "validation": paths["validation"],
        "cache": paths["validation_cache"],
        "bank": paths["bank"],
        "native_predictions": old,
    }
    for arm, outputs in fitted.items():
        selection_inputs.update(
            {
                f"model_{arm}": outputs["model"],
                f"predictions_{arm}": outputs["validation_predictions"],
                f"trace_{arm}": outputs["trace"],
            }
        )
    selection_outputs = {
        "selection": tmp_path / "selection.json",
        "models": tmp_path / "models.pt",
        "predictions": tmp_path / "selected_predictions.json",
    }
    context = SimpleNamespace(
        config=SelectionConfig(
            model_sha256=val_cache["model_sha256"],
            bank_sha256=file_sha256(paths["bank"]),
            validation_sha256=file_sha256(paths["validation"]),
            validation_cache_sha256=file_sha256(paths["validation_cache"]),
        ),
        inputs=selection_inputs,
        outputs=selection_outputs,
    )
    freeze_selection(context)
    selection = load_json(selection_outputs["selection"])
    assert (
        selection["selected_arm"] is None
    )  # Direct native ranking is already perfect.
    assert not selection["test_scores_used_for_selection"]
    assert set(selection["heads"]) == set(FITTED_ARMS)
    bundled = load_model(selection_outputs["models"])
    assert set(bundled["models"]) == set(FITTED_ARMS)
    scored = load_json(selection_outputs["predictions"])
    assert [row["prediction"] for row in scored["native_direct"]] == [0.1, 0.9]
