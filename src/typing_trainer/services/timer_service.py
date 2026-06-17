from PySide6.QtCore import QElapsedTimer, QObject, QTimer, Signal


class TimerService(QObject):
    time_updated    = Signal(int)
    elapsed_updated = Signal(float)
    timer_finished  = Signal()
    timer_paused    = Signal()
    timer_resumed   = Signal()

    def __init__(self, duration_seconds: int = 60, parent=None) -> None:
        super().__init__(parent)
        self.duration  = duration_seconds
        self.remaining = duration_seconds
        self.minimum_duration = 1

        self._elapsed_timer       = QElapsedTimer()
        self._elapsed_ms_at_pause = 0
        self._paused              = False
        self._completion_callback = None

        self._tick_timer = QTimer(self)
        self._tick_timer.setInterval(250)
        self._tick_timer.timeout.connect(self._tick)

    def start(self) -> None:
        if self.duration < self.minimum_duration:
            self.duration = self.minimum_duration
        if self.remaining <= 0:
            self.reset()
        self._paused = False
        self._elapsed_timer.start()
        self._tick_timer.start()

    def stop(self) -> None:
        if self._tick_timer.isActive() and not self._paused:
            self._elapsed_ms_at_pause += self._elapsed_timer.elapsed()
        self._tick_timer.stop()
        self._paused = False

    def pause(self) -> None:
        if not self._tick_timer.isActive() or self._paused:
            return
        self._paused = True
        self._elapsed_ms_at_pause += self._elapsed_timer.elapsed()
        self._tick_timer.stop()
        self.timer_paused.emit()

    def resume(self) -> None:
        if not self._paused:
            return
        self._paused = False
        self._elapsed_timer.start()
        self._tick_timer.start()
        self.timer_resumed.emit()

    def reset(self) -> None:
        self._tick_timer.stop()
        self._elapsed_ms_at_pause = 0
        self.remaining = self.duration
        self._paused = False
        self.time_updated.emit(self.remaining)
        self.elapsed_updated.emit(0.0)

    def is_running(self) -> bool:
        return self._tick_timer.isActive() and not self._paused

    def is_paused(self) -> bool:
        return self._paused

    def elapsed_seconds(self) -> float:
        total_ms = self._elapsed_ms_at_pause
        if self._tick_timer.isActive() and not self._paused:
            total_ms += self._elapsed_timer.elapsed()
        return total_ms / 1000.0

    def set_on_completion(self, callback) -> None:
        self._completion_callback = callback

    def _tick(self) -> None:
        if self._paused:
            return
        elapsed_s    = self.elapsed_seconds()
        new_remaining = max(0, self.duration - int(elapsed_s))

        if new_remaining != self.remaining:
            self.remaining = new_remaining
            self.time_updated.emit(self.remaining)

        self.elapsed_updated.emit(elapsed_s)

        if self.remaining <= 0:
            self._tick_timer.stop()
            self.timer_finished.emit()
            if self._completion_callback:
                self._completion_callback()
