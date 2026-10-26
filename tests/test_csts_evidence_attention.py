"""Check condition-guided evidence selection without loading an encoder or GPU."""

import copy
import math
import re
from types import SimpleNamespace

import pytest
import torch
from torch.nn import functional as F

from csts_pilot.baseline_models import EOD, EncoderConfig, token_sequences
from csts_pilot.evidence_attention import (
    ARMS,
    TEACHER_SHA256,
    AttentionFitConfig,
    AttentionHead,
    fit_attention,
    literal_span_targets,
    pack_batch,
    predict_head,
    scores_from_cache,
    span_loss,
    token_metadata,
    validate_token_cache,
)


class OffsetTokenizer:
    """Expose exact character offsets, including a real special-token position."""

    is_fast = True
    all_special_ids = (0, 1)

    def get_vocab(self):
        return {EOD: 1}

    def __call__(self, texts, **kwargs):
        def encode(text):
            pieces = list(re.finditer(r"<\|endoftext\|>|.", text, re.DOTALL))
            ids = [1 if m.group() == EOD else ord(m.group()) + 2 for m in pieces]
            offsets = [m.span() for m in pieces]
            return ids, offsets

        single = isinstance(texts, str)
        values = [encode(text) for text in ([texts] if single else texts)]
        result = {"input_ids": [ids for ids, _ in values]}
        if kwargs.get("return_offsets_mapping"):
            result["offset_mapping"] = [offsets for _, offsets in values]
        if single:
            return {key: value[0] for key, value in result.items()}
        return result


def attention_inputs(dtype=torch.float64):
    """Use noncollinear states and unequal passage lengths to expose masking bugs."""
    states = torch.tensor(
        [
            [[1.0, 0.4, -0.3], [0.2, 1.3, 0.1], [-0.6, 0.2, 1.7]],
            [[0.3, -1.0, 0.8], [1.8, 0.5, -0.2], [6.0, 8.0, 9.0]],
        ],
        dtype=dtype,
    )
    queries = torch.tensor([[0.8, -0.4, 1.2], [-0.5, 1.1, 0.7]], dtype=dtype)
    mask = torch.tensor([[True, True, True], [True, True, False]])
    return states, queries, mask


def test_metadata_preserves_original_encoder_tokens_and_excludes_specials():
    tokenizer = OffsetTokenizer()
    keys = [("car color", f"A red {EOD} car."), ("A red car.", "A red car.")]
    config = EncoderConfig(device="cpu", max_length=512, embedding_dimension=3)
    metadata = token_metadata(tokenizer, keys, config)
    expected = token_sequences(tokenizer, keys, config)
    for item, token_ids, (condition, passage) in zip(
        metadata, expected, keys, strict=True
    ):
        assert item["input_ids"] == token_ids
        assert item["condition_indices"]
        assert item["passage_indices"]
        assert not set(item["condition_indices"]) & set(item["passage_indices"])
        assert all(
            token_ids[i] not in tokenizer.all_special_ids
            for i in item["condition_indices"]
        )
        assert all(
            token_ids[i] not in tokenizer.all_special_ids
            for i in item["passage_indices"]
        )
        assert len(token_ids) - 1 not in item["passage_indices"]
        assert len(item["passage_offsets"]) == len(item["passage_indices"])
        assert all(
            0 <= start < end <= len(passage) for start, end in item["passage_offsets"]
        )
        for index, (start, end) in zip(
            item["passage_indices"], item["passage_offsets"], strict=True
        ):
            assert token_ids[index] == ord(passage[start:end]) + 2
        assert len(item["condition_indices"]) == len(condition)


def test_metadata_rejects_truncation_and_empty_token_blocks():
    tokenizer = OffsetTokenizer()
    config = EncoderConfig(device="cpu", max_length=128, embedding_dimension=3)
    with pytest.raises(ValueError):
        token_metadata(tokenizer, [("color", "x" * 200)], config)
    for key in (("", "a car"), ("color", ""), ("color", EOD)):
        with pytest.raises(ValueError):
            token_metadata(tokenizer, [key], config)


def test_span_targets_use_unique_literal_local_offsets_and_abstain_on_ambiguity():
    passage = "red car and red bus"
    offsets = [(0, 3), (4, 7), (8, 11), (12, 15), (16, 19)]
    actual = literal_span_targets(passage, "red", offsets)
    assert actual.sum() == 0  # Repeated copies cannot identify the teacher's entity.
    torch.testing.assert_close(
        literal_span_targets(passage, "red bus", offsets),
        torch.tensor([0.0, 0.0, 0.0, 0.5, 0.5]),
    )
    # A token crossing a span boundary still carries evidence from that span.
    crossing = literal_span_targets("a red car", "red", [(0, 3), (3, 6), (6, 9)])
    torch.testing.assert_close(crossing, torch.tensor([0.5, 0.5, 0.0]))
    for answer in ("RED", "blue", "NOT_SPECIFIED", ""):
        assert literal_span_targets(passage, answer, offsets).sum() == 0


def test_span_offsets_preserve_unicode_and_the_declared_literal_whitespace_policy():
    passage = "niño\u00a0rojo"
    offsets = [(0, 4), (4, 5), (5, 9)]
    torch.testing.assert_close(
        literal_span_targets(passage, "rojo", offsets), torch.tensor([0.0, 0.0, 1.0])
    )
    assert literal_span_targets(passage, "niño rojo", offsets).sum() == 0
    torch.testing.assert_close(
        literal_span_targets(passage, passage, offsets), torch.full((3,), 1 / 3)
    )


def test_attention_normalizes_only_passage_positions_and_ignores_padding():
    torch.manual_seed(7)
    head = (
        AttentionHead(input_dim=3, query_dim=2, output_dim=4, dropout=0).double().eval()
    )
    states, queries, mask = attention_inputs()
    vectors, logits, weights = head(states, queries, mask)
    torch.testing.assert_close(vectors.norm(dim=1), torch.ones(2, dtype=vectors.dtype))
    torch.testing.assert_close(weights.sum(dim=1), torch.ones(2, dtype=weights.dtype))
    assert weights[1, 2] == 0
    assert (weights[mask] > 0).all()
    assert torch.isfinite(logits[mask]).all()
    changed = states.clone()
    changed[1, 2] = torch.tensor([1e9, -2e9, 3e9], dtype=states.dtype)
    again, _, changed_weights = head(changed, queries, mask)
    torch.testing.assert_close(again, vectors)
    torch.testing.assert_close(changed_weights, weights)


def test_attention_query_key_and_value_paths_receive_rating_gradients():
    torch.manual_seed(7)
    head = AttentionHead(input_dim=3, query_dim=2, output_dim=4, dropout=0).double()
    states, queries, mask = attention_inputs()
    states.requires_grad_()
    queries.requires_grad_()
    vectors, _, weights = head(states, queries, mask)
    score = vectors[0] @ vectors[1]
    (score - 0.17).square().backward()
    assert queries.grad is not None and queries.grad.norm() > 1e-8
    assert states.grad is not None and states.grad[mask].norm() > 1e-8
    assert torch.equal(states.grad[~mask], torch.zeros_like(states.grad[~mask]))
    for name, parameter in head.named_parameters():
        assert parameter.grad is not None, name
        assert torch.isfinite(parameter.grad).all(), name
        assert parameter.grad.norm() > 1e-8, name
    assert weights.requires_grad


def test_attention_rating_gradient_matches_finite_difference_on_condition():
    torch.manual_seed(11)
    head = (
        AttentionHead(input_dim=3, query_dim=2, output_dim=4, dropout=0).double().eval()
    )
    states, queries, mask = attention_inputs()
    queries.requires_grad_()

    def objective(condition):
        vectors, _, _ = head(states, condition, mask)
        return (vectors[0] @ vectors[1] - 0.17).square()

    objective(queries).backward()
    assert queries.grad is not None
    step = 1e-6
    plus, minus = queries.detach().clone(), queries.detach().clone()
    plus[0, 0] += step
    minus[0, 0] -= step
    with torch.no_grad():
        finite_difference = (objective(plus) - objective(minus)) / (2 * step)
    torch.testing.assert_close(
        queries.grad[0, 0], finite_difference, rtol=2e-4, atol=1e-7
    )


def test_outer_autocast_preserves_the_head_float32_math():
    torch.manual_seed(7)
    head = AttentionHead(input_dim=3, query_dim=2, output_dim=4, dropout=0).eval()
    states, queries, mask = attention_inputs(torch.float32)
    expected = head(states, queries, mask)
    with torch.autocast("cpu", dtype=torch.bfloat16):
        actual = head(states, queries, mask)
    for observed, reference in zip(actual, expected, strict=True):
        assert observed.dtype == torch.float32
        torch.testing.assert_close(observed, reference, rtol=0, atol=0)


def test_span_objective_updates_query_and_key_then_rating_objective_updates_values():
    torch.manual_seed(7)
    head = AttentionHead(input_dim=3, query_dim=2, output_dim=4, dropout=0).double()
    states, queries, mask = attention_inputs()
    vectors, logits, _ = head(states, queries, mask)
    targets = torch.tensor([[1.0, 0.0, 0.0], [0.0, 1.0, 0.0]], dtype=logits.dtype)
    evidence, count = span_loss(logits, mask, targets)
    assert count == 2
    evidence.backward(retain_graph=True)
    for parameter in (head.query.weight, head.key.weight):
        assert parameter.grad is not None and parameter.grad.norm() > 1e-8
    assert head.projection.weight.grad is None
    head.zero_grad(set_to_none=True)
    ((vectors[0] @ vectors[1] - 0.17).square() + 0.1 * evidence).backward()
    assert head.projection.weight.grad is not None
    assert head.projection.weight.grad.norm() > 1e-8


@pytest.mark.parametrize("corruption", ("empty", "nan_states", "inf_query", "bad_mask"))
def test_attention_rejects_nonfinite_inputs_or_an_empty_passage(corruption):
    torch.manual_seed(7)
    head = AttentionHead(input_dim=3, query_dim=2, output_dim=4, dropout=0).double()
    states, queries, mask = attention_inputs()
    if corruption == "empty":
        mask[0] = False
    elif corruption == "nan_states":
        states[0, 0, 0] = torch.nan
    elif corruption == "inf_query":
        queries[0, 1] = torch.inf
    else:
        mask = mask[:, :-1]
    with pytest.raises(ValueError):
        head(states, queries, mask)


def test_attention_rejects_a_zero_projected_passage_direction():
    head = AttentionHead(input_dim=3, query_dim=2, output_dim=4, dropout=0)
    with pytest.raises(ValueError):
        head(torch.zeros(1, 2, 3), torch.ones(1, 3), torch.ones(1, 2, dtype=torch.bool))


def test_span_cross_entropy_counts_supervised_passages_and_ignores_padding():
    logits = torch.tensor(
        [[2.0, -1.0, 8.0], [0.1, 0.7, -0.2], [1.0, 2.0, 9.0]], requires_grad=True
    )
    mask = torch.tensor([[True, True, False], [True, True, True], [True, True, False]])
    targets = torch.tensor([[0.25, 0.75, 0.0], [0.0, 0.0, 0.0], [0.0, 1.0, 0.0]])
    loss, count = span_loss(logits, mask, targets)
    expected = (
        -0.25 * F.log_softmax(logits[0, :2], dim=0)[0]
        - 0.75 * F.log_softmax(logits[0, :2], dim=0)[1]
        - F.log_softmax(logits[2, :2], dim=0)[1]
    ) / 2
    assert count == 2
    torch.testing.assert_close(loss, expected)
    loss.backward()
    assert logits.grad is not None
    assert torch.equal(logits.grad[1], torch.zeros(3))
    assert torch.equal(logits.grad[~mask], torch.zeros_like(logits.grad[~mask]))


def test_no_teacher_target_is_a_differentiable_zero():
    logits = torch.tensor([[2.0, -1.0, 0.0]], requires_grad=True)
    loss, count = span_loss(
        logits, torch.ones_like(logits, dtype=torch.bool), torch.zeros_like(logits)
    )
    assert count == 0 and loss == 0 and loss.requires_grad
    loss.backward()
    assert logits.grad is not None and torch.equal(
        logits.grad, torch.zeros_like(logits)
    )


def test_no_teacher_target_is_finite_with_actual_masked_head_logits():
    torch.manual_seed(7)
    head = AttentionHead(input_dim=3, query_dim=2, output_dim=4, dropout=0).double()
    states, queries, mask = attention_inputs()
    _, logits, _ = head(states, queries, mask)
    loss, count = span_loss(logits, mask, torch.zeros_like(logits))
    assert count == 0 and torch.isfinite(loss) and loss == 0
    loss.backward()
    for parameter in head.parameters():
        if parameter.grad is not None:
            assert torch.isfinite(parameter.grad).all()
            assert parameter.grad.norm() == 0


@pytest.mark.parametrize("corruption", ("padding", "negative", "nonunit", "nan"))
def test_span_cross_entropy_rejects_invalid_teacher_distributions(corruption):
    logits = torch.tensor([[1.0, 2.0, 3.0]])
    mask = torch.tensor([[True, True, False]])
    targets = torch.tensor([[1.0, 0.0, 0.0]])
    if corruption == "padding":
        targets = torch.tensor([[0.0, 0.0, 1.0]])
    elif corruption == "negative":
        targets = torch.tensor([[1.2, -0.2, 0.0]])
    elif corruption == "nonunit":
        targets[0, 0] = 0.5
    else:
        targets[0, 0] = torch.nan
    with pytest.raises(ValueError):
        span_loss(logits, mask, targets)


def test_two_arms_have_exactly_the_same_seeded_trainable_parameters():
    assert ARMS == ("attention_ratings", "attention_evidence")
    states = []
    for _ in ARMS:
        torch.manual_seed(7)
        states.append(
            AttentionHead(
                input_dim=3, query_dim=2, output_dim=4, dropout=0
            ).state_dict()
        )
    assert states[0].keys() == states[1].keys()
    for name in states[0]:
        torch.testing.assert_close(states[0][name], states[1][name], rtol=0, atol=0)


def comparison(index, condition="color", group=None, target=0.0):
    return {
        "row_id": f"row-{index}-{condition}",
        "pair_id": f"pair-{index}",
        "group_id": group or f"group-{index}",
        "condition": condition,
        "sentence1": f"A red car {index}.",
        "sentence2": f"A blue car {index}.",
        "target": target,
        "rating": 1 + 4 * target,
    }


def packed_cache(rows=None, split="training"):
    """Use occurrence-specific states so a wrong semantic join changes the scores."""
    rows = rows or [comparison(0), comparison(1, "activity", target=1.0)]
    keys = [
        (row["condition"], row[side])
        for row in rows
        for side in ("sentence1", "sentence2")
    ]
    metadata = token_metadata(
        OffsetTokenizer(),
        keys,
        EncoderConfig(device="cpu", max_length=512, embedding_dimension=3),
    )
    pointers = [0]
    targets = []
    for item in metadata:
        width = len(item["passage_indices"])
        pointers.append(pointers[-1] + width)
        target = torch.zeros(width)
        if split == "training":
            target[0] = 1
        targets.append(target)
    generator = torch.Generator().manual_seed(17)
    return {
        "keys": keys,
        "left": [2 * i for i in range(len(rows))],
        "right": [2 * i + 1 for i in range(len(rows))],
        "pointers": pointers,
        "token_values": torch.randn(pointers[-1], 3, generator=generator),
        "condition_states": torch.randn(len(keys), 3, generator=generator),
        "span_targets": torch.cat(targets),
        "metadata": metadata,
        "embedding_dimension": 3,
        "split": split,
        "answers_sha256": TEACHER_SHA256 if split == "training" else None,
        "rows_sha256": "1" * 64,
        "bank_sha256": "2" * 64,
        "model_sha256": "8805f9a7241e4e19ffc481341ebad6f1ddb6dd6ff04bbf710f9f0896469e34ff",
    }


def test_packed_batch_respects_occurrence_order_lengths_targets_and_padding():
    cache = packed_cache([comparison(0), dict(comparison(1), sentence2="A bus.")])
    validate_token_cache(cache)
    positions = [3, 0, 3]
    tokens, queries, mask, targets = pack_batch(cache, positions)
    assert tokens.shape[:2] == mask.shape == targets.shape
    for output_row, occurrence in enumerate(positions):
        start, end = cache["pointers"][occurrence : occurrence + 2]
        width = end - start
        assert mask[output_row].sum() == width
        assert mask[output_row, :width].all()
        assert not mask[output_row, width:].any()
        torch.testing.assert_close(
            tokens[output_row, :width], cache["token_values"][start:end]
        )
        torch.testing.assert_close(
            queries[output_row], cache["condition_states"][occurrence]
        )
        torch.testing.assert_close(
            targets[output_row, :width], cache["span_targets"][start:end]
        )
        assert tokens[output_row, width:].count_nonzero() == 0
        assert targets[output_row, width:].count_nonzero() == 0
    for invalid in ([], [-1], [len(cache["keys"])]):
        with pytest.raises(ValueError):
            pack_batch(cache, invalid)


@pytest.mark.parametrize(
    "corruption",
    (
        "nan_tokens",
        "inf_condition",
        "empty_occurrence",
        "bad_width",
        "bad_hash",
        "overlapping_masks",
        "selected_eod",
        "offset_outside",
        "nonunit_target",
        "teacher_lineage",
        "unknown_split",
    ),
)
def test_token_cache_rejects_invalid_features_boundaries_offsets_and_identities(
    corruption,
):
    cache = packed_cache()
    if corruption == "nan_tokens":
        cache["token_values"][0, 0] = torch.nan
    elif corruption == "inf_condition":
        cache["condition_states"][0, 0] = torch.inf
    elif corruption == "empty_occurrence":
        cache["pointers"][1] = cache["pointers"][0]
    elif corruption == "bad_width":
        cache["embedding_dimension"] = 4
    elif corruption == "bad_hash":
        cache["rows_sha256"] = "wrong"
    elif corruption == "overlapping_masks":
        cache["metadata"][0]["condition_indices"] = cache["metadata"][0][
            "passage_indices"
        ][:1]
    elif corruption == "selected_eod":
        cache["metadata"][0]["passage_indices"][0] = (
            len(cache["metadata"][0]["input_ids"]) - 1
        )
    elif corruption == "offset_outside":
        cache["metadata"][0]["passage_offsets"][0] = (0, len(cache["keys"][0][1]) + 1)
    elif corruption == "nonunit_target":
        cache["span_targets"][0] = 0.5
    elif corruption == "teacher_lineage":
        cache["answers_sha256"] = "9" * 64
    else:
        cache["split"] = "unknown"
    with pytest.raises(ValueError):
        validate_token_cache(cache)


def test_token_cache_rejects_a_semantically_wrong_in_range_join():
    rows = [comparison(0), comparison(1, "activity", target=1)]
    cache = packed_cache(rows)
    validate_token_cache(cache, rows)
    cache["left"] = list(reversed(cache["left"]))
    validate_token_cache(cache)  # Packed tensor dimensions still agree.
    with pytest.raises(ValueError):
        validate_token_cache(cache, rows)


def test_held_out_cache_forbids_teacher_targets_and_predictions_do_not_read_them():
    rows = [comparison(0), comparison(1, "activity", target=1)]
    cache = packed_cache(rows, split="validation")
    validate_token_cache(cache, rows)
    torch.manual_seed(7)
    head = AttentionHead(input_dim=3, query_dim=2, output_dim=4, dropout=0)
    baseline = predict_head(head, cache)
    changed = copy.deepcopy(cache)
    for i in range(len(changed["keys"])):
        changed["span_targets"][changed["pointers"][i]] = 1
    with pytest.raises(ValueError):
        validate_token_cache(changed, rows)
    # Even an unvalidated caller cannot feed teacher labels into the scorer.
    assert predict_head(head, changed) == baseline


def test_matched_tiny_fits_keep_all_rating_rows_and_restore_selected_heads(
    tmp_path, monkeypatch
):
    """Exercise real optimization and checkpoint restore with the encoder absent."""
    from csts_pilot import evidence_attention as module
    from csts_pilot.convergence import file_sha256, write_json
    from csts_pilot.evidence_attention_run import SelectionConfig, freeze_selection
    from csts_pilot.matched_baselines import choose_bank, head_fit_rows
    from jep_pilot.loaders import load_json, load_model

    training = [
        comparison(i, condition, target=target)
        for i in (0, 1)
        for condition, target in (("color", 0.0), ("activity", 1.0))
    ]
    validation = [
        comparison(20, "color", target=0),
        comparison(20, "activity", target=1),
    ]
    bank = choose_bank(training, validation, bank_size=1, seed=7)
    fitted = head_fit_rows(training, bank)
    paths = {
        name: tmp_path / f"{name}.json" for name in ("training", "validation", "bank")
    }
    for name, value in (
        ("training", training),
        ("validation", validation),
        ("bank", bank),
    ):
        write_json(paths[name], value)
    for split, rows in (("training", training), ("validation", validation)):
        cache = packed_cache(rows, split=split)
        cache["rows_sha256"] = file_sha256(paths[split])
        cache["bank_sha256"] = file_sha256(paths["bank"])
        if split == "training":
            # One retained pair has no accepted span. Both arms must still fit it.
            omitted_row = training.index(fitted[1])
            for occurrence in (cache["left"][omitted_row], cache["right"][omitted_row]):
                start, end = cache["pointers"][occurrence : occurrence + 2]
                cache["span_targets"][start:end] = 0
        paths[split + "_cache"] = tmp_path / f"{split}_cache.pt"
        torch.save(cache, paths[split + "_cache"])

    class Recorder:
        def record(self, value, *, step):
            assert math.isfinite(value)
            assert step >= 0

    actual_pack = module.pack_batch
    orders = {}
    current_arm = None

    def observe_pack(cache, positions, device="cpu"):
        if isinstance(positions, torch.Tensor):
            orders[current_arm].append(positions.tolist())
        return actual_pack(cache, positions, device)

    monkeypatch.setattr(module, "pack_batch", observe_pack)
    saved_models, traces, fitted_outputs = {}, {}, {}
    for arm in ARMS:
        current_arm = arm
        orders[arm] = []
        directory = tmp_path / arm
        directory.mkdir()
        outputs = {
            name: directory / filename
            for name, filename in (
                ("model", "model.pt"),
                ("trace", "trace.json"),
                ("validation_predictions", "predictions.json"),
                ("resume_state", "resume.pt"),
            )
        }
        config = AttentionFitConfig(
            arm=arm,
            device="cpu",
            query_dim=2,
            output_dim=4,
            dropout=0,
            span_weight=0.3,
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
        fit_attention(
            SimpleNamespace(
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
        )
        saved = load_model(outputs["model"])
        trace = load_json(outputs["trace"])
        expected_ids = [row["row_id"] for row in fitted]
        assert saved["head_fit_row_ids"] == expected_ids
        assert trace["training_rows"] == len(fitted) == 2
        assert trace["frozen_encoder_optimizer_updates"] == 0
        assert trace["selected_model_sha256"] == file_sha256(outputs["model"])
        assert outputs["resume_state"].exists()
        predictions = load_json(outputs["validation_predictions"])
        cache = load_model(paths["validation_cache"])
        assert scores_from_cache(saved, cache) == [
            row["prediction"] for row in predictions
        ]
        invalid_identity = copy.deepcopy(cache)
        invalid_identity["model_sha256"] = "9" * 64
        with pytest.raises(ValueError):
            scores_from_cache(saved, invalid_identity)
        weight = 0.3 if arm == "attention_evidence" else 0
        assert trace["effective_span_weight"] == weight
        for epoch in trace["epochs"]:
            assert epoch["supervised_occurrences"] == 2
            assert epoch["training_objective"] == pytest.approx(
                epoch["training_mse"] + weight * epoch["span_cross_entropy"], abs=1e-7
            )
        saved_models[arm], traces[arm] = saved, trace
        fitted_outputs[arm] = outputs
    assert orders[ARMS[0]] == orders[ARMS[1]]
    assert (
        saved_models[ARMS[0]]["initial_head_sha256"]
        == saved_models[ARMS[1]]["initial_head_sha256"]
    )
    assert (
        traces[ARMS[0]]["head_fit_ids_sha256"] == traces[ARMS[1]]["head_fit_ids_sha256"]
    )

    native_predictions = tmp_path / "native_predictions.json"
    write_json(
        native_predictions,
        [
            dict(row, prediction=score)
            for row, score in zip(validation, (0.1, 0.9), strict=True)
        ],
    )
    selection_inputs = {
        "validation": paths["validation"],
        "cache": paths["validation_cache"],
        "bank": paths["bank"],
        "native_predictions": native_predictions,
    }
    for arm, outputs in fitted_outputs.items():
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
    val_cache = load_model(paths["validation_cache"])
    freeze_selection(
        SimpleNamespace(
            config=SelectionConfig(
                model_sha256=val_cache["model_sha256"],
                bank_sha256=file_sha256(paths["bank"]),
                validation_sha256=file_sha256(paths["validation"]),
                validation_cache_sha256=file_sha256(paths["validation_cache"]),
            ),
            inputs=selection_inputs,
            outputs=selection_outputs,
        )
    )
    selection = load_json(selection_outputs["selection"])
    assert selection["selected_arm"] is None  # Existing native ranking is perfect.
    assert not selection["test_scores_used_for_selection"]
    assert set(selection["heads"]) == set(ARMS)
    assert set(load_model(selection_outputs["models"])["models"]) == set(ARMS)
    captured = load_json(selection_outputs["predictions"])
    assert [row["prediction"] for row in captured["native_direct"]] == [0.1, 0.9]
