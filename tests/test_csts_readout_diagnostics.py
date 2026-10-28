"""Check that diagnostic claims use real source positions and equal row sets."""

import pytest
import torch

from scripts.diagnose_evidence_readout import (
    edit_tokens,
    position_summary,
    simple_vectors,
)


def test_concentration_uses_each_sentences_actual_last_token():
    result = position_summary([torch.tensor([0.0, 1.0]), torch.tensor([1.0, 0.0, 0.0])])
    assert result["top_token_first_fraction"] == 0.5
    assert result["top_token_last_fraction"] == 0.5
    assert result["mass_over_099_fraction"] == 1
    assert result["top_position_deciles"] == [1, 0, 0, 0, 0, 0, 0, 0, 0, 1]
    with pytest.raises(ValueError):
        position_summary([torch.tensor([0.2, 0.2])])


def test_exact_state_equality_under_an_edit_is_measured_separately_from_position():
    cache = {
        "left": [0, 1],
        "pointers": [0, 2, 4],
        "token_values": torch.tensor([[1.0, 0.0], [0.0, 1.0], [1.0, 0.0], [0.0, -1.0]]),
    }
    rows = [{"case": "toy", "edit": "base"}, {"case": "toy", "edit": "relevant"}]
    same_prefix = edit_tokens(cache, rows, [torch.tensor([1.0, 0.0])] * 2)[0]
    changed_suffix = edit_tokens(cache, rows, [torch.tensor([0.0, 1.0])] * 2)[0]
    assert same_prefix["selected_state_exactly_equal"]
    assert not changed_suffix["selected_state_exactly_equal"]
    assert (
        changed_suffix["base_top_position"] == changed_suffix["relevant_top_position"]
    )


def test_quotation_pooling_retains_full_values_and_ignores_unselected_words():
    cache = {
        "pointers": [0, 2],
        "token_values": torch.tensor([[1.0, 0.0, 0.0, 0.0], [0.0, 2.0, 0.0, 0.0]]),
        "span_targets": torch.tensor([0.0, 1.0]),
        "eod_vectors": torch.tensor([[0.0, 0.0, 1.0, 0.0]]),
    }
    vectors = simple_vectors(cache)
    assert vectors["quotation"].shape == (1, 4)
    assert torch.equal(vectors["quotation"], vectors["last"])
    assert not torch.equal(vectors["quotation"], vectors["A"])
