"""Check split isolation, conditional targets and shared gradient paths."""

import torch

from jep_pilot.data import QUESTIONS, make_data
from jep_pilot.model import JointModel, tiny_spec


def test_splits_and_conditions():
    """Exclude complete test cases and composed rating questions from training."""
    splits = make_data()
    ids = {
        k: {r[s]["case_id"] for r in rows for s in ("left", "right")}
        for k, rows in splits.items()
    }
    assert ids["train"].isdisjoint(ids["test"])
    assert ids["train"].isdisjoint(ids["dev"])
    assert ids["dev"].isdisjoint(ids["test"])
    assert all(r["transfer"] == "atomic" for r in splits["train"])
    assert any(r["transfer"] == "composed" for r in splits["test"])
    assert {
        r["target"] for r in splits["test"] if r["condition"] == "result_affected"
    } == {0.5, 0.75, 1.0}
    assert len({r["left"]["category"] for r in splits["train"]}) == 4
    for rows in splits.values():
        for row in rows:
            fields = QUESTIONS[row["condition"]][1]
            agreement = sum(row["left"][f] == row["right"][f] for f in fields) / len(
                fields
            )
            assert row["target"] == 0.5 + 0.5 * agreement


def test_both_losses_reach_encoder_and_gradients_add():
    """Verify the central claim with real autograd through a small T5."""
    torch.set_num_threads(2)
    torch.manual_seed(7)
    rows = make_data()["train"]
    model = JointModel(tiny_spec(rows))
    batch = [rows[i] for i in (0, 12, 24, 36)]
    mse, ce, _ = model.losses(batch)
    shared = model.t5.encoder.block[0].layer[0].SelfAttention.q.weight
    gs = torch.autograd.grad(mse, shared, retain_graph=True)[0]
    ga = torch.autograd.grad(ce, shared, retain_graph=True)[0]
    total = torch.autograd.grad(mse + 0.2 * ce, shared)[0]
    assert gs.norm() > 0 and ga.norm() > 0
    torch.testing.assert_close(total, gs + 0.2 * ga, rtol=2e-4, atol=2e-6)
