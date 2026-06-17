from typing_trainer.exceptions import (
    ConfigError,
    DatabaseError,
    LessonError,
    SessionError,
    TypingTrainerError,
)


class TestExceptions:
    def test_hierarchy(self):
        assert issubclass(DatabaseError, TypingTrainerError)
        assert issubclass(ConfigError, TypingTrainerError)
        assert issubclass(SessionError, TypingTrainerError)
        assert issubclass(LessonError, TypingTrainerError)

    def test_instantiation(self):
        exc = DatabaseError("connection failed")
        assert str(exc) == "connection failed"

    def test_catch_base(self):
        with __import__("pytest").raises(TypingTrainerError):
            raise ConfigError("bad config")
