"""Stop after a declared sequence of validation checks without improvement."""

import math
from dataclasses import dataclass


@dataclass
class ValidationPatience:
    """Track validation Spearman separately from checkpoint selection."""

    patience: int | None = 5
    min_delta: float = 0.0
    best_score: float = -math.inf
    stale_epochs: int = 0

    def __post_init__(self) -> None:
        """Reject unusable patience counts and nonfinite thresholds."""
        if self.patience is not None and self.patience < 1:
            raise ValueError("Patience must be a positive epoch count or None.")
        if not math.isfinite(self.min_delta) or self.min_delta < 0:
            raise ValueError("min_delta must be finite and nonnegative.")

    def observe(self, score: float) -> bool:
        """Reset on sufficient improvement; return whether patience is exhausted."""
        if not math.isfinite(score):
            raise ValueError("Validation Spearman must be finite.")
        if score > self.best_score + self.min_delta:
            self.best_score = score
            self.stale_epochs = 0
        else:
            self.stale_epochs += 1
        return self.patience is not None and self.stale_epochs >= self.patience
