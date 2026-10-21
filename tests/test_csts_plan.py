"""Validate identifiers before spending GPU time on development trials."""

from pydantic import TypeAdapter
from viper.ids import VariantId

from csts_pilot.run import trial_name


def test_learning_rate_trial_identifiers_are_valid():
    validator = TypeAdapter(VariantId)
    for label in ("conditioned", "without_question"):
        for rate in (1e-5, 3e-5):
            name = trial_name(label, rate)
            assert validator.validate_python(name) == name
