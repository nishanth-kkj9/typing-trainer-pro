"""
StatsCalculator
---------------
Pure-Python WPM / accuracy / error formulas.  No state — all methods are
@staticmethod so callers can use them without instantiation.
"""

from typing import List
from typing_trainer.core.typing_engine import CharStatus


class StatsCalculator:
    """Calculate WPM, accuracy, and error count."""

    @staticmethod
    def calculate_wpm(correct_chars: int, elapsed_seconds: float) -> float:
        """
        Standard WPM formula: (correct_chars / 5) / elapsed_minutes.
        Returns 0.0 if elapsed_seconds ≤ 0 (avoids division by zero).
        """
        if elapsed_seconds <= 0:
            return 0.0
        return (correct_chars / 5.0) / (elapsed_seconds / 60.0)

    @staticmethod
    def calculate_accuracy(correct_chars: int, total_typed: int) -> float:
        """Return accuracy as a percentage in [0, 100]. 100% when nothing typed."""
        if total_typed == 0:
            return 100.0
        return (correct_chars / total_typed) * 100.0

    @staticmethod
    def count_errors(statuses: List[CharStatus]) -> int:
        """Count characters marked INCORRECT."""
        return sum(1 for s in statuses if s == CharStatus.INCORRECT)
