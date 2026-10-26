"""Reproduce the Tranche 5 algebra checks with NumPy float64 on CPU.

Run ``python scripts/check_tranche5_math.py`` in the existing project environment.
These calculations exercise the derivations independently of experiment code.
The identity-residual head case is an auxiliary algebra check. The experiment's
existing native comparator reads sealed predictions and receives zero new fits.
They perform no model loading, inference, fitting, or external writes by default.
"""

import argparse
import json
from pathlib import Path

import numpy as np
from numpy.typing import NDArray

Array = NDArray[np.float64]


def example() -> dict[str, Array]:
    """Fix a small mathematical example and its inverted-dropout masks."""
    rng = np.random.default_rng(61026)
    width, output, bank = 5, 4, 4
    return {
        "passages": rng.normal(size=(2, width)),
        "same_generic": rng.normal(size=(2, width)),
        "reference": rng.normal(size=(bank, width)),
        "generic": rng.normal(size=(bank, width)),
        "case_reference": rng.normal(size=width),
        "weight": rng.normal(size=(output, width)),
        "logit": np.array(0.0),
        "dropout_mask": np.array([[1, 0, 1, 1], [1, 1, 0, 1]]) / 0.85,
    }


def objective(
    kind: str, parameters: dict[str, Array]
) -> tuple[float, dict[str, Array]]:
    """Return one-pair loss and the independently derived analytic gradients."""
    h = parameters["passages"]
    weight = parameters["weight"]
    keep = parameters["dropout_mask"]
    alpha = float(1 / (1 + np.exp(-parameters["logit"])))
    bank = (parameters["reference"] - parameters["generic"]).mean(0)
    projector = np.outer(bank, bank) / (bank @ bank)
    if kind == "I":
        correction = np.zeros_like(h)
    elif kind == "M":
        correction = parameters["same_generic"]
    elif kind == "B":
        correction = np.broadcast_to(bank, h.shape)
    elif kind == "P":
        correction = h @ projector
    elif kind == "C":
        correction = np.broadcast_to(parameters["case_reference"], h.shape)
        alpha = 1.0
    else:
        raise ValueError(f"Unknown arm: {kind}")
    residual = h - alpha * correction
    linear = residual @ weight.T
    activated = np.where(linear > 0, linear, 0.01 * linear)
    vector = activated * keep
    unit = vector / np.linalg.norm(vector, axis=1, keepdims=True)
    score = float(unit[0] @ unit[1])
    loss = (score - 0.3) ** 2
    gradient_vector = np.stack(
        [
            2
            * (score - 0.3)
            / np.linalg.norm(vector[i])
            * (unit[1 - i] - score * unit[i])
            for i in range(2)
        ]
    )
    gradient_linear = gradient_vector * keep * np.where(linear > 0, 1, 0.01)
    gradient_residual = gradient_linear @ weight
    gradients = {
        "weight": gradient_linear.T @ residual,
        "passages": gradient_residual,
    }
    if kind in {"M", "B", "P"}:
        gradient_alpha = -(correction * gradient_residual).sum()
        gradients["logit"] = np.asarray(gradient_alpha * alpha * (1 - alpha))
    if kind == "M":
        gradients["same_generic"] = -alpha * gradient_residual
    elif kind == "C":
        gradients["case_reference"] = -gradient_residual.sum(0)
    elif kind in {"B", "P"}:
        if kind == "B":
            gradient_bank = -alpha * gradient_residual.sum(0)
        else:
            gradients["passages"] = gradient_residual @ (
                np.eye(h.shape[1]) - alpha * projector
            )
            gradient_bank = np.zeros_like(bank)
            length_squared = bank @ bank
            for passage, gradient in zip(h, gradient_residual, strict=True):
                coefficient = bank @ passage / length_squared
                gradient_bank -= alpha * (
                    coefficient * gradient
                    + passage * (bank @ gradient) / length_squared
                    - 2 * coefficient * bank * (bank @ gradient) / length_squared
                )
        bank_size = len(parameters["reference"])
        gradients["reference"] = np.broadcast_to(
            gradient_bank / bank_size, parameters["reference"].shape
        )
        gradients["generic"] = np.broadcast_to(
            -gradient_bank / bank_size, parameters["generic"].shape
        )
    return loss, gradients


def central_difference(kind: str, parameters: dict[str, Array], name: str) -> Array:
    """Differentiate one array by central differences with step 1e-6."""
    value = parameters[name]
    answer = np.empty_like(value)
    for index in np.ndindex(value.shape):
        plus, minus = value.copy(), value.copy()
        plus[index] += 1e-6
        minus[index] -= 1e-6
        positive = objective(kind, {**parameters, name: plus})[0]
        negative = objective(kind, {**parameters, name: minus})[0]
        answer[index] = (positive - negative) / 2e-6
    return answer


def run_checks() -> dict:
    """Check gradients and projection identities; raise on any failed check."""
    parameters = example()
    results = []
    for kind in ("I", "M", "B", "P", "C"):
        _, gradients = objective(kind, parameters)
        for name, gradient in gradients.items():
            numeric = central_difference(kind, parameters, name)
            error = float(np.max(np.abs(numeric - gradient)))
            if error >= 1e-7:
                raise AssertionError((kind, name, error))
            results.append({"check": f"{kind}_{name}_gradient", "max_error": error})
    bank = (parameters["reference"] - parameters["generic"]).mean(0)
    projector = np.outer(bank, bank) / (bank @ bank)
    np.testing.assert_allclose(projector, projector.T, atol=1e-15)
    results.append({"check": "projection_symmetry", "passed": True})
    np.testing.assert_allclose(projector @ projector, projector, atol=1e-15)
    results.append({"check": "projection_idempotence", "passed": True})
    for scale in (2.5, -3.0):
        scaled = scale * bank
        np.testing.assert_allclose(
            np.outer(scaled, scaled) / (scaled @ scaled), projector, atol=1e-15
        )
    results.append({"check": "projection_direction_scale_invariance", "passed": True})
    passages = parameters["passages"]
    parallel = passages @ projector
    perpendicular = passages - parallel
    residual = passages - 0.5 * parallel
    np.testing.assert_allclose(residual, 0.5 * parallel + perpendicular, atol=1e-15)
    results.append(
        {"check": "projection_parallel_perpendicular_decomposition", "passed": True}
    )
    np.testing.assert_allclose(
        np.square(residual).sum(1),
        0.25 * np.square(parallel).sum(1) + np.square(perpendicular).sum(1),
        atol=1e-15,
    )
    results.append({"check": "projection_residual_squared_norm", "passed": True})
    return {
        "scope": "independent mathematical expressions in NumPy; CPU float64",
        "checks": len(results),
        "gradient_checks": sum("max_error" in r for r in results),
        "max_gradient_error": max(r.get("max_error", 0.0) for r in results),
        "finite_difference_step": 1e-6,
        "gradient_error_tolerance": 1e-7,
        "example_seed": 61026,
        "results": results,
    }


def main() -> None:
    """Print results and optionally save an explicitly requested JSON receipt."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    arguments = parser.parse_args()
    rendered = json.dumps(run_checks(), indent=2, allow_nan=False) + "\n"
    if arguments.output is not None:
        arguments.output.parent.mkdir(parents=True, exist_ok=True)
        arguments.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()
