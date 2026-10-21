"""Record development error used to select training checkpoints."""

from viper.config import MetricConfig
from viper.metrics import MetricContext, metric


@metric(metric_id="development_mse", mode="stateless")
def development_mse(_context: MetricContext[MetricConfig], value: float) -> float:
    """Record one epoch's development MSE."""
    return value


@metric(metric_id="training_answer_ce", mode="stateless")
def training_answer_ce(_context: MetricContext[MetricConfig], value: float) -> float:
    """Record the answer loss for one training epoch."""
    return value


@metric(metric_id="development_answer_ce", mode="stateless")
def development_answer_ce(_context: MetricContext[MetricConfig], value: float) -> float:
    """Record teacher-forced answer loss on development captions."""
    return value
