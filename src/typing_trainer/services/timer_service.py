"""
TimerService
------------
Countdown timer backed by QElapsedTimer so the displayed remaining time
does not accumulate drift from QTimer's 1000 ms tick latency.

QTimer fires the "wake-up" tick at ~250 ms intervals; the authoritative
time source is QElapsedTimer which reads the system clock directly.
"""

from PySide6.QtCore import QTimer, QObject, Signal, QElapsedTimer


class TimerService(QObject):
    """Countdown timer for typing sessions."""

    time_updated    = Signal(int)    # remaining seconds (for UI display)
    elapsed_updated = Signal(float)  # elapsed seconds  (for WPM calculation)
    timer_finished  = Signal()

    def __init__(self, duration_seconds: int = 60, parent=None) -> None:
        super().__init__(parent)
        self.duration  = duration_seconds
        self.remaining = duration_seconds

        self._elapsed_timer        = QElapsedTimer()
        self._elapsed_ms_at_pause  = 0  # accumulated ms from previous runs

        self._tick_timer = QTimer(self)
        self._tick_timer.setInterval(250)   # 4 Hz — smooth display, low CPU
        self._tick_timer.timeout.connect(self._tick)

    # ── Public API ─────────────────────────────────────────────────────────

    def start(self) -> None:
        if self.remaining <= 0:
            self.reset()
        self._elapsed_timer.start()
        self._tick_timer.start()

    def stop(self) -> None:
        if self._tick_timer.isActive():
            self._elapsed_ms_at_pause += self._elapsed_timer.elapsed()
        self._tick_timer.stop()

    def reset(self) -> None:
        self._tick_timer.stop()
        self._elapsed_ms_at_pause = 0
        self.remaining = self.duration
        self.time_updated.emit(self.remaining)
        self.elapsed_updated.emit(0.0)

    def is_running(self) -> bool:
        return self._tick_timer.isActive()

    def elapsed_seconds(self) -> float:
        """Wall-clock seconds since last reset (pauses excluded)."""
        total_ms = self._elapsed_ms_at_pause
        if self._tick_timer.isActive():
            total_ms += self._elapsed_timer.elapsed()
        return total_ms / 1000.0

    # ── Internal ───────────────────────────────────────────────────────────

    def _tick(self) -> None:
        elapsed_s    = self.elapsed_seconds()
        new_remaining = max(0, self.duration - int(elapsed_s))

        if new_remaining != self.remaining:
            self.remaining = new_remaining
            self.time_updated.emit(self.remaining)

        self.elapsed_updated.emit(elapsed_s)

        if self.remaining <= 0:
            self._tick_timer.stop()
            self.timer_finished.emit()
