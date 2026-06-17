"""
StatsTracker
------------
Aggregates typing events and emits real-time stats via Qt signals.

Single update() method avoids the double-recalculate bug present in
earlier versions where update_time() and update_input() each triggered
a full recalculation independently.
"""

from PySide6.QtCore import QObject, Signal

from typing_trainer.core.typing_engine import CharStatus, TypingEngine
from typing_trainer.core.stats_calculator import StatsCalculator


class StatsTracker(QObject):
    """Real-time stats aggregator for a single typing session."""

    # Emitted only when values change — avoids redundant UI redraws.
    stats_changed = Signal(dict)   # {'wpm', 'accuracy', 'errors', 'correct', 'total_typed'}

    def __init__(self, target_text: str, parent=None) -> None:
        super().__init__(parent)
        self.engine     = TypingEngine(target_text)
        self.calculator = StatsCalculator()

        self._elapsed_seconds: float = 0.0
        self._user_input:      str   = ""
        self._last_stats:      dict  = {}

    # ── Public API ─────────────────────────────────────────────────────────

    def update(self, user_input: str, elapsed_seconds: float) -> None:
        """Combined update — avoids double recalculation."""
        self._user_input       = user_input
        self._elapsed_seconds  = elapsed_seconds
        self._recalculate()

    def update_time(self, elapsed_seconds: float) -> None:
        """Update elapsed time only (called from timer tick)."""
        self._elapsed_seconds = elapsed_seconds
        self._recalculate()

    def update_input(self, user_input: str) -> None:
        """Update input only (called on each keystroke)."""
        self._user_input = user_input
        self._recalculate()

    # ── Internal ───────────────────────────────────────────────────────────

    def _recalculate(self) -> None:
        statuses, _ = self.engine.compare(self._user_input)
        correct     = sum(1 for s in statuses if s == CharStatus.CORRECT)
        errors      = self.calculator.count_errors(statuses)
        total_typed = correct + errors

        stats = {
            "wpm":        round(self.calculator.calculate_wpm(correct, self._elapsed_seconds), 1),
            "accuracy":   round(self.calculator.calculate_accuracy(correct, total_typed), 1),
            "errors":     errors,
            "correct":    correct,
            "total_typed": total_typed,
        }
        if stats != self._last_stats:
            self._last_stats = stats.copy()
            self.stats_changed.emit(stats)
