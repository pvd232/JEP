"""Check scorer replay, probe interpretation and squared error attribution."""

import importlib.util
from pathlib import Path

import numpy as np
import pytest

spec = importlib.util.spec_from_file_location(
    "comparison_diagnostics",
    Path(__file__).parents[1] / "scripts/analyze_csts_comparison.py",
)
analysis = importlib.util.module_from_spec(spec)
spec.loader.exec_module(analysis)


def test_saved_head_replay_matches_native_symmetric_comparison():
    torch = pytest.importorskip("torch")
    from csts_pilot.evidence_readout import SymmetricComparison

    generator = np.random.default_rng(23)
    left, right = generator.normal(size=(2, 9, 5))
    left /= np.linalg.norm(left, axis=1, keepdims=True)
    right /= np.linalg.norm(right, axis=1, keepdims=True)
    weights, bias = generator.normal(size=10), 0.17
    model = SymmetricComparison(5).double()
    with torch.no_grad():
        model.residual.weight.copy_(torch.from_numpy(weights[None]))
        model.residual.bias.fill_(bias)
        expected = model(torch.from_numpy(left), torch.from_numpy(right)).numpy()
    actual = analysis.pair_score(left, right, weights, bias)
    np.testing.assert_allclose(actual, expected, atol=1e-12)
    np.testing.assert_allclose(
        actual, analysis.pair_score(right, left, weights, bias), atol=1e-12
    )


def test_margin_scaling_retains_order_and_condition_ignoring_cancels():
    ids = ["implicit", "explicit", "positive", "negative"]
    vectors = np.array([[1.0, 0.0], [1.0, 0.0], [1.0, 0.0], [-1.0, 0.0]])
    probe = {
        "inputs": [{"id": i} for i in ids],
        "families": [
            {
                "id": "implied",
                "stratum": "implied",
                "implicit": ids[0],
                "explicit": ids[1],
                "positive": ids[2],
                "negative": ids[3],
            }
        ],
    }
    cosine = analysis.probe_scores(probe, ids, vectors)
    doubled = analysis.probe_scores(
        probe, ids, vectors, np.array([0.0, 0.0, 1.0, 1.0]), 4.0
    )
    assert (
        doubled["summary"]["implicit_margin"]
        == 2 * cosine["summary"]["implicit_margin"]
    )
    assert (
        doubled["summary"]["correct_order"] == cosine["summary"]["correct_order"] == 1
    )
    target = ["t" + str(i) for i in range(4)]
    distractor = ["d" + str(i) for i in range(4)]
    ids = target + distractor
    square = np.array([[1.0, 0.0], [0.0, 1.0], [-1.0, 0.0], [0.0, -1.0]])
    probe = {
        "inputs": [{"id": i} for i in ids],
        "families": [
            {
                "id": "multi",
                "stratum": "multiple",
                "grid": target,
                "distractor_grid": distractor,
            }
        ],
    }
    # Supply the implied family as well so both reported strata are represented.
    probe["families"].append(
        {
            "id": "implied",
            "stratum": "implied",
            "implicit": target[0],
            "explicit": target[1],
            "positive": target[2],
            "negative": target[3],
        }
    )
    scored = analysis.probe_scores(
        probe,
        ids,
        np.concatenate([square, square]),
        np.array([0.2, -0.1, 0.3, -0.4]),
        0.5,
    )
    assert scored["summary"]["C"] == pytest.approx(0, abs=1e-12)


def test_squared_error_attribution_and_fresh_error_flag():
    rows = [{"row_id": "r", "target": 0.25}]
    result = analysis.error_records(
        rows,
        np.array([0.8]),
        {"7": np.array([0.6]), "8": np.array([0.7])},
        {"7": np.array([0.9]), "8": np.array([0.95])},
    )[0]
    assert result["comparison_mse_gain"] == pytest.approx(0.14)
    assert result["all_fresh_errors_larger"]
    assert result["target"] == 0.25


def test_family_interval_averages_heads_before_resampling():
    result = analysis.family_interval(np.array([[1.0] * 30, [3.0] * 30]), draws=50)
    assert result["mean"] == result["low"] == result["high"] == 2
    assert result["families"] == 30
