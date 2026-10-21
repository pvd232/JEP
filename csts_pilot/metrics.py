"""Record development error used to select training checkpoints."""

from viper.config import MetricConfig
from viper.metrics import MetricContext, metric


@metric(metric_id="development_mse", mode="stateless")
def development_mse(_context: MetricContext[MetricConfig], value: float) -> float:
    """Record one epoch's development MSE."""
    return value
