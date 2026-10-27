"""Check causal evidence supervision and the matched Qwen phase transition."""

import copy
import json
from types import SimpleNamespace

import pytest
import torch
from torch import nn
from torch.nn import functional as F
from transformers import Qwen3Config, Qwen3Model
from viper.resume import load_resume_state

from csts_pilot import baseline_models
from csts_pilot import qwen_evidence as module
from csts_pilot.answers import answer_id
from csts_pilot.baseline_models import EOD, FitConfig, state_digest, token_sequences
from csts_pilot.convergence import file_sha256
from csts_pilot.qwen_evidence import (
    answer_loss_sum,
    evidence_tokens,
    validate_matched_phases,
)
from csts_pilot.qwen_head_prepare import vocabulary
from jep_pilot.loaders import load_json, load_model


class Tokenizer:
    padding_side = "left"

    def get_vocab(self):
        return {EOD: 1}

    def __call__(self, texts, **kwargs):
        def encode(text):
            return [2 + sum(word.encode()) % 25 for word in text.split()]

        return {
            "input_ids": encode(texts)
            if isinstance(texts, str)
            else [encode(s) for s in texts]
        }


def test_only_answer_tokens_and_terminator_are_labels():

    row = {"condition": "color", "sentence1": "red car", "sentence2": "blue car"}
    config = FitConfig(kind="lora", device="cpu")
    tokenizer = Tokenizer()
    key = answer_id("red car", "color")
    sequences = evidence_tokens([row], {key: "red"}, tokenizer, config, 8)
    prefix = token_sequences(tokenizer, [("color", "red car")], config)[0]
    ids, labels = sequences[key]
    assert ids[: len(prefix)] == prefix
    assert labels[: len(prefix)] == [-100] * len(prefix)
    assert labels[len(prefix) :] == tokenizer("red")["input_ids"] + [1]
    assert ids[len(prefix) :] == labels[len(prefix) :]
    assert set(sequences) == {key}


def test_evidence_preparation_batches_vocabulary_and_tokenizer_work():

    class CountingTokenizer(Tokenizer):
        vocabulary_calls = 0
        encode_calls = 0

        def get_vocab(self):
            self.vocabulary_calls += 1
            return super().get_vocab()

        def __call__(self, texts, **kwargs):
            self.encode_calls += 1
            return super().__call__(texts, **kwargs)

    rows = [
        {
            "condition": "color",
            "sentence1": f"red car {i}",
            "sentence2": f"blue car {i}",
        }
        for i in range(20)
    ]
    mapping = {
        answer_id(row[side], row["condition"]): "red"
        for row in rows
        for side in ("sentence1", "sentence2")
    }
    tokenizer = CountingTokenizer()
    result = evidence_tokens(
        rows, mapping, tokenizer, FitConfig(kind="lora", device="cpu"), 8
    )
    assert len(result) == 40
    assert tokenizer.encode_calls == 2
    assert tokenizer.vocabulary_calls == 2


def test_evidence_ce_matches_manual_causal_per_answer_average():
    torch.manual_seed(42)
    hidden = torch.randn(2, 6, 8, requires_grad=True)
    head = nn.Linear(8, 11, bias=False)
    head.requires_grad_(False)
    labels = torch.tensor([[-100, -100, -100, 4, 6, 1], [-100, -100, -100, -100, 7, 1]])
    actual = answer_loss_sum(hidden, labels, head)
    expected = F.cross_entropy(head(hidden[0, 2:5]), torch.tensor([4, 6, 1]))
    expected += F.cross_entropy(head(hidden[1, 3:5]), torch.tensor([7, 1]))
    torch.testing.assert_close(actual, expected)
    actual.backward()
    assert hidden.grad[0, 2].abs().sum() > 0  # prefix EOD predicts first answer token
    assert hidden.grad[0, :2].count_nonzero() == 0
    assert hidden.grad[:, -1].count_nonzero() == 0
    assert head.weight.grad is None


def test_answer_weighting_is_invariant_to_microbatch_boundaries():
    torch.manual_seed(33)
    head = nn.Linear(5, 9, bias=False).requires_grad_(False)
    hidden = torch.randn(3, 5, 5, requires_grad=True)
    labels = torch.tensor(
        [[-100, -100, 3, 4, 1], [-100, -100, -100, 5, 1], [-100, -100, 7, 6, 1]]
    )
    (answer_loss_sum(hidden, labels, head) / 3).backward()
    full_gradient = hidden.grad.clone()
    hidden.grad = None
    (answer_loss_sum(hidden[:2], labels[:2], head) / 3).backward()
    (answer_loss_sum(hidden[2:], labels[2:], head) / 3).backward()
    torch.testing.assert_close(hidden.grad, full_gradient)


def test_future_answer_tokens_cannot_change_embedding_prefix():
    torch.manual_seed(7)
    model = Qwen3Model(
        Qwen3Config(
            vocab_size=32,
            hidden_size=16,
            intermediate_size=32,
            num_hidden_layers=1,
            num_attention_heads=2,
            num_key_value_heads=1,
            head_dim=8,
            attention_dropout=0.0,
        )
    ).eval()
    prefix = torch.tensor([[3, 4, 8, 1]])
    full = torch.cat([prefix, torch.tensor([[9, 10, 1]])], dim=1)
    with torch.no_grad():
        first = model(input_ids=prefix).last_hidden_state
        second = model(input_ids=full).last_hidden_state[:, : len(prefix[0])]
    torch.testing.assert_close(first, second, atol=1e-6, rtol=1e-6)


def matched_traces():
    result = {}
    for arm in ("ratings", "evidence"):
        result[arm] = {
            "pretrain": {
                "initial_trainable_sha256": "same",
                "actual_updates": 4,
                "training_rows": 8,
                "initial_rng": {"torch": "same"},
                "completed_epoch": 2,
                "stop_reason": "fixed_update_budget",
                "terminal_trainable_sha256": arm + "weights",
                "terminal_model_sha256": arm + "file",
                "epochs": [{"batch_order_sha256": "a"}, {"batch_order_sha256": "b"}],
            },
            "ratings": {
                "stop_reason": "validation_patience",
                "initial_trainable_sha256": arm + "weights",
                "parent_sha256": arm + "file",
                "initial_rng": {"torch": "same2"},
                "epochs": [{"batch_order_sha256": "x"}],
            },
        }
    return result


def test_matched_budget_and_terminal_transition():
    validate_matched_phases(matched_traces(), 2)


@pytest.mark.parametrize(
    "field,value",
    [
        ("actual_updates", 3),
        ("completed_epoch", 1),
        ("training_rows", 9),
        ("initial_trainable_sha256", "different"),
    ],
)
def test_reject_unmatched_auxiliary_exposure(field, value):
    traces = matched_traces()
    traces["evidence"]["pretrain"][field] = value
    with pytest.raises(ValueError):
        validate_matched_phases(traces, 2)


def test_reject_selected_instead_of_terminal_phase_a_weights():
    traces = copy.deepcopy(matched_traces())
    traces["evidence"]["ratings"]["parent_sha256"] = "selected-other-epoch"
    with pytest.raises(ValueError, match="terminal"):
        validate_matched_phases(traces, 2)


def test_reject_changed_rating_batch_order():
    traces = matched_traces()
    traces["evidence"]["ratings"]["epochs"][0]["batch_order_sha256"] = "other"
    with pytest.raises(ValueError, match="second-phase"):
        validate_matched_phases(traces, 2)


def test_reject_time_budget_stop_before_comparison():
    traces = matched_traces()
    traces["evidence"]["ratings"]["stop_reason"] = "resource_budget"
    with pytest.raises(ValueError, match="budget-censored"):
        validate_matched_phases(traces, 2)


def test_declared_pilot_accepts_resource_stop_and_keeps_trace_reason():
    """A bounded pilot can score sealed checkpoints while exposing its time limit."""
    traces = matched_traces()
    traces["evidence"]["ratings"]["stop_reason"] = "resource_budget"
    original = copy.deepcopy(traces)
    validate_matched_phases(traces, 2, allow_budget_censoring=True)
    assert traces == original


def test_declared_pilot_still_rejects_incomplete_first_phase():
    """The pilot allowance preserves the required matched initial exposure."""
    traces = matched_traces()
    traces["evidence"]["pretrain"]["completed_epoch"] = 1
    with pytest.raises(ValueError, match="Incomplete"):
        validate_matched_phases(traces, 2, allow_budget_censoring=True)


def test_added_tokens_are_included_in_head_compatibility_check():
    assert vocabulary(
        {"model": {"vocab": {"word": 0}}, "added_tokens": [{"content": EOD, "id": 1}]}
    ) == {"word": 0, EOD: 1}


@pytest.mark.parametrize("initial_epochs", [2, 4])
def test_both_training_phases_share_initialization_and_restore_terminal_adapters(
    tmp_path, monkeypatch, initial_epochs
):
    """Exercise the complete two-arm transition with real tiny Qwen and PEFT."""

    class PaddedTokenizer(Tokenizer):
        def pad(self, encoded, **kwargs):
            width = max(map(len, encoded["input_ids"]))
            return {
                name: torch.tensor([[0] * (width - len(row)) + row for row in values])
                for name, values in encoded.items()
            }

    def backbone(*args, **kwargs):
        return Qwen3Model(
            Qwen3Config(
                vocab_size=32,
                hidden_size=16,
                intermediate_size=32,
                num_hidden_layers=1,
                num_attention_heads=2,
                num_key_value_heads=1,
                head_dim=8,
                attention_dropout=0.0,
            )
        )

    monkeypatch.setattr(baseline_models.AutoModel, "from_pretrained", backbone)
    monkeypatch.setattr(module, "load_tokenizer", lambda config: PaddedTokenizer())
    head = nn.Linear(16, 32, bias=False).requires_grad_(False)
    monkeypatch.setattr(module, "load_head", lambda *args: head)
    rows = [
        {
            "row_id": f"r{i}",
            "group_id": f"g{i}",
            "pair_id": f"p{i}",
            "condition": "color",
            "sentence1": f"red car {i}",
            "sentence2": f"blue bus {i}",
            "rating": 1 + 2 * (i % 3),
            "target": (i % 3) / 2,
        }
        for i in range(8)
    ]
    mapping = {
        answer_id(row[side], row["condition"]): "red" if side == "sentence1" else "blue"
        for row in rows
        for side in ("sentence1", "sentence2")
    }
    inputs = {}
    for name, value in (
        ("training", rows),
        ("validation", rows),
        ("prepared", {"training": rows, "aligned": mapping}),
    ):
        inputs[name] = tmp_path / f"{name}.json"
        inputs[name].write_text(json.dumps(value))
    inputs["head"] = tmp_path / "unused-head"
    traces = {}
    previous_threads = torch.get_num_threads()
    torch.set_num_threads(2)
    try:
        for arm in ("ratings", "evidence"):
            traces[arm] = {}
            parent = None
            for phase in ("pretrain", "ratings"):
                directory = tmp_path / f"{arm}_{phase}"
                directory.mkdir()
                outputs = {
                    k: directory / filename
                    for k, filename in {
                        "model": "best.pt",
                        "last_model": "last.pt",
                        "resume_state": "resume.pt",
                        "trace": "trace.json",
                        "validation_predictions": "validation.json",
                    }.items()
                }
                cfg = module.QwenEvidenceConfig(
                    kind="lora",
                    arm=arm,
                    phase=phase,
                    device="cpu",
                    embedding_dimension=16,
                    lora_rank=2,
                    lora_alpha=2,
                    batch_size=4,
                    microbatch_size=2,
                    learning_rate=2e-5,
                    max_epochs=2,
                    max_seconds=120,
                    training_sha256=file_sha256(inputs["training"]),
                    validation_sha256=file_sha256(inputs["validation"]),
                    prepared_sha256=file_sha256(inputs["prepared"]),
                    head_sha256="0" * 64,
                    parent_sha256=file_sha256(parent) if parent is not None else None,
                )
                current = dict(inputs)
                if parent is not None:
                    current["parent_model"] = parent
                metrics = {
                    k: SimpleNamespace(record=lambda *args, **kwargs: None)
                    for k in (
                        "training_objective",
                        "validation_mse",
                        "validation_spearman",
                    )
                }
                module.fit_qwen_evidence(
                    SimpleNamespace(
                        config=cfg,
                        inputs=current,
                        outputs=outputs,
                        metrics=metrics,
                        numpy_generators={},
                    )
                )
                if phase == "pretrain" and initial_epochs == 4:
                    original_outputs = dict(outputs)
                    original_bytes = {
                        k: p.read_bytes() for k, p in outputs.items() if p.exists()
                    }
                    history = load_json(outputs["trace"])["epochs"]
                    cfg4 = cfg.model_copy(
                        update={
                            "max_epochs": 4,
                            "train_until_patience": True,
                            "patience": 1,
                        }
                    )
                    reference_dir = tmp_path / f"{arm}_uninterrupted_four"
                    reference_dir.mkdir()
                    reference_outputs = {
                        k: reference_dir / p.name for k, p in outputs.items()
                    }
                    module.fit_qwen_evidence(
                        SimpleNamespace(
                            config=cfg4,
                            inputs=dict(inputs),
                            outputs=reference_outputs,
                            metrics=metrics,
                            numpy_generators={},
                        )
                    )
                    resumed_dir = tmp_path / f"{arm}_continued_four"
                    resumed_dir.mkdir()
                    outputs = {
                        k: resumed_dir / p.name for k, p in original_outputs.items()
                    }
                    resumed_inputs = {
                        **inputs,
                        "parent_model": original_outputs["last_model"],
                        "parent_resume": original_outputs["resume_state"],
                        "parent_trace": original_outputs["trace"],
                    }
                    resumed_cfg = cfg4.model_copy(
                        update={
                            "start_epoch": 2,
                            "parent_sha256": file_sha256(
                                original_outputs["last_model"]
                            ),
                        }
                    )
                    with pytest.raises(ValueError, match="frozen training setting"):
                        module.fit_qwen_evidence(
                            SimpleNamespace(
                                config=resumed_cfg.model_copy(
                                    update={"learning_rate": 3e-5}
                                ),
                                inputs=resumed_inputs,
                                outputs=outputs,
                                metrics=metrics,
                                numpy_generators={},
                            )
                        )
                    module.fit_qwen_evidence(
                        SimpleNamespace(
                            config=resumed_cfg,
                            inputs=resumed_inputs,
                            outputs=outputs,
                            metrics=metrics,
                            numpy_generators={},
                        )
                    )
                    resumed = load_json(outputs["trace"])
                    reference = load_json(reference_outputs["trace"])
                    assert resumed["epochs"][:2] == history
                    assert resumed["actual_updates"] == reference["actual_updates"] == 8
                    assert state_digest(
                        load_model(outputs["last_model"])["state"]
                    ) == state_digest(
                        load_model(reference_outputs["last_model"])["state"]
                    )
                    for actual, expected in zip(
                        resumed["epochs"], reference["epochs"], strict=True
                    ):
                        for key in (
                            "batch_order_sha256",
                            "training_objective",
                            "rating_input_tokens",
                            "validation",
                        ):
                            assert actual[key] == expected[key]
                    actual_state = load_resume_state(outputs["resume_state"])
                    expected_state = load_resume_state(
                        reference_outputs["resume_state"]
                    )
                    assert (
                        actual_state.main_process_rng == expected_state.main_process_rng
                    )
                    torch.testing.assert_close(
                        actual_state.dataloader.state_dict["generator_state"],
                        expected_state.dataloader.state_dict["generator_state"],
                        rtol=0,
                        atol=0,
                    )
                    for key, value in actual_state.optimizer_state["optimizer"][
                        "state"
                    ].items():
                        for field, tensor in value.items():
                            torch.testing.assert_close(
                                tensor,
                                expected_state.optimizer_state["optimizer"]["state"][
                                    key
                                ][field],
                                rtol=0,
                                atol=0,
                            )
                    assert {
                        k: original_outputs[k].read_bytes() for k in original_bytes
                    } == original_bytes
                traces[arm][phase] = load_json(outputs["trace"])
                parent = outputs["last_model"]
        validate_matched_phases(traces, initial_epochs)
        assert traces["evidence"]["pretrain"]["first_shared_adapter_gradient_norm"] > 0
        assert (
            traces["ratings"]["pretrain"]["terminal_trainable_sha256"]
            != traces["evidence"]["pretrain"]["terminal_trainable_sha256"]
        )
    finally:
        torch.set_num_threads(previous_threads)
