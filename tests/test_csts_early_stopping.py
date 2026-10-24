"""Check patience boundaries, resets, thresholds and fixed-budget compatibility."""

import math

import pytest

from csts_pilot.early_stopping import ValidationPatience


def test_strict_improvement_resets_all_five_epochs():
    """Ties and regressions count; a new best starts a fresh window."""
    stopping = ValidationPatience()
    assert [stopping.observe(s) for s in [0.5, 0.4, 0.5, 0.6]] == [False] * 4
    assert stopping.stale_epochs == 0
    assert [stopping.observe(0.6) for _ in range(5)] == [False] * 4 + [True]


def test_min_delta_is_cumulative_since_the_last_patience_reset():
    """Several small gains can eventually cross the declared threshold."""
    stopping = ValidationPatience(patience=5, min_delta=0.01)
    for score in [0.5, 0.502, 0.505]:
        assert stopping.observe(score) is False
    assert stopping.stale_epochs == 2
    assert stopping.observe(0.52) is False
    assert stopping.stale_epochs == 0


def test_none_retains_the_historical_fixed_update_budget():
    """A disabled stop rule keeps observing without halting training."""
    stopping = ValidationPatience(patience=None)
    assert all(stopping.observe(0.5) is False for _ in range(20))


@pytest.mark.parametrize("score", [math.nan, math.inf, -math.inf])
def test_nonfinite_validation_is_an_error(score):
    """An invalid score cannot silently exhaust patience."""
    with pytest.raises(ValueError, match="finite"):
        ValidationPatience().observe(score)
