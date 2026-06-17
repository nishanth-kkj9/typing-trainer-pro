import pytest
from PySide6.QtCore import QTimer

from typing_trainer.services.timer_service import TimerService


@pytest.fixture
def timer_service():
    svc = TimerService(duration_seconds=60)
    svc.reset()
    return svc


class TestTimerService:
    def test_initial_state(self, timer_service):
        assert timer_service.remaining == 60
        assert not timer_service.is_running()

    def test_reset(self, timer_service, qtbot):
        timer_service.start()
        qtbot.wait(50)
        timer_service.reset()
        assert timer_service.remaining == 60
        assert not timer_service.is_running()

    def test_custom_duration(self):
        svc = TimerService(duration_seconds=30)
        svc.reset()
        assert svc.duration == 30
        assert svc.remaining == 30

    def test_start_stop(self, timer_service, qtbot):
        timer_service.start()
        qtbot.wait(50)
        assert timer_service.is_running()
        timer_service.stop()
        assert not timer_service.is_running()

    def test_stop_when_not_running(self, timer_service):
        timer_service.stop()
        assert not timer_service.is_running()

    def test_double_start(self, timer_service, qtbot):
        timer_service.start()
        timer_service.start()
        qtbot.wait(50)
        assert timer_service.is_running()
        timer_service.stop()

    def test_elapsed_seconds_after_reset(self, timer_service):
        assert timer_service.elapsed_seconds() == 0.0

    def test_elapsed_increases(self, timer_service, qtbot):
        timer_service.start()
        QTimer.singleShot(500, timer_service.stop)
        with qtbot.wait_signal(timer_service.elapsed_updated, timeout=1000):
            pass
        elapsed = timer_service.elapsed_seconds()
        assert 0.2 <= elapsed <= 0.8

    def test_time_updated_signal(self, timer_service, qtbot):
        timer_service.duration = 1
        timer_service.reset()
        timer_service.time_updated.connect(lambda s: setattr(self, "_time", s))
        timer_service.start()
        with qtbot.wait_signal(timer_service.time_updated, timeout=2000):
            pass
        timer_service.stop()

    def test_timer_finished_signal(self, qtbot):
        svc = TimerService(duration_seconds=1)
        svc.reset()
        with qtbot.wait_signal(svc.timer_finished, timeout=3000):
            svc.start()
