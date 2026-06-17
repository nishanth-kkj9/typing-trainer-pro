from typing_trainer.logging_setup import get_logger, setup_logging


class TestLogging:
    def test_setup_and_logger(self):
        setup_logging()
        log = get_logger("test_logging")
        assert log is not None
        assert log.name == "test_logging"

    def test_logger_returns_bound_logger(self):
        setup_logging()
        log = get_logger("my.module")
        assert hasattr(log, "info")
        assert hasattr(log, "error")
