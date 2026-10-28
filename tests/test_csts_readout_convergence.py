"""Check rate selection, initial checkpoints and comparison on A's vectors."""

import copy

import numpy as np
import pytest
import torch
from test_csts_evidence_readout import config, fixture

from csts_pilot.evidence_readout import EvidenceReadout, SymmetricComparison, predict
from csts_pilot.evidence_readout_convergence import select_rates
from csts_pilot.evidence_readout_stages import fit_comparisons, train_pair


def candidate(ratings, evidence, censored=False):
    return {
        "model": {
            "selected": {
                "ratings": {"spearman": ratings},
                "evidence": {"spearman": evidence},
            }
        },
        "trace": {"budget_censored": censored},
    }


def test_rate_selection_uses_all_seeds_and_separate_objectives():
    pool = {
        "1e-05": {str(s): candidate(0.7, 0.75) for s in (7, 8, 9)},
        "3e-05": {str(s): candidate(0.8, 0.85) for s in (7, 8, 9)},
        "0.0001": {str(s): candidate(0.9, 0.8) for s in (7, 8, 9)},
    }
    selected = select_rates(pool, (7, 8, 9))
    assert selected["rates"] == {"ratings": "0.0001", "evidence": "3e-05"}
    missing = copy.deepcopy(pool)
    del missing["1e-05"]["9"]
    with pytest.raises(ValueError, match="complete seed"):
        select_rates(missing, (7, 8, 9))
    unfinished = copy.deepcopy(pool)
    unfinished["0.0001"]["8"]["trace"]["budget_censored"] = True
    with pytest.raises(ValueError, match="epoch ceiling"):
        select_rates(unfinished, (7, 8, 9))


def test_rate_ties_choose_the_smallest_rate_independent_of_insertion_order():
    pool = {"0.0001": {"7": candidate(0.8, 0.7)}, "0.00001": {"7": candidate(0.8, 0.7)}}
    assert select_rates(pool, (7,))["rates"] == {
        "ratings": "0.00001",
        "evidence": "0.00001",
    }


def test_initial_head_and_parent_comparison_are_eligible_and_frozen():
    torch.set_num_threads(1)
    training, rows = fixture()
    validation, heldout = fixture("validation")
    cfg = config().model_copy(
        update={
            "learning_rate": 1e-12,
            "include_initial": True,
            "fit_comparison": False,
            "record_attention": True,
            "patience": 1,
        }
    )
    snapshots = []
    model, trace, predictions, _ = train_pair(
        training,
        validation,
        rows,
        heldout,
        cfg,
        on_checkpoint=lambda state: snapshots.append(copy.deepcopy(state)),
    )
    assert "comparisons" not in model
    assert not trace["budget_censored"]
    assert trace["selected_epoch"] == {"ratings": 0, "evidence": 0}
    assert (
        snapshots
        and "optimizer" in snapshots[-1]
        and "generator_state" in snapshots[-1]
    )
    assert "attention" in trace["epochs"][0]
    heads = {arm: EvidenceReadout(5, 3) for arm in ("ratings", "evidence")}
    comparisons, comp_trace, comp_predictions, _ = fit_comparisons(
        heads,
        model["selected"],
        training,
        validation,
        rows,
        heldout,
        cfg,
        include_parent=True,
    )
    assert set(comparisons["selected"]) == {"ratings", "evidence", "parent"}
    assert comp_trace["readout_before_sha256"] == comp_trace["readout_after_sha256"]
    assert comparisons["selected"]["parent"]["epoch"] == 0
    comparator = SymmetricComparison(5)
    comparator.load_state_dict(comparisons["selected"]["parent"]["state"])
    actual = predict(None, validation, comparator=comparator)[0]
    np.testing.assert_array_equal(actual, predict(None, validation)[0])
    np.testing.assert_array_equal(actual, comp_predictions["parent_comparison"])
    assert all(
        not p.requires_grad and p.grad is None
        for h in heads.values()
        for p in h.parameters()
    )
    assert set(predictions) == {"ratings", "evidence"}
