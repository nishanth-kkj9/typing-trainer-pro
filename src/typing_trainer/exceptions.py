"""Custom exceptions for Typing Trainer Pro."""


class TypingTrainerError(Exception):
    """Base exception for all application errors."""


class DatabaseError(TypingTrainerError):
    """Database operation failed."""


class ConfigError(TypingTrainerError):
    """Configuration loading/saving failed."""


class SessionError(TypingTrainerError):
    """Typing session error."""


class LessonError(TypingTrainerError):
    """Lesson loading/validation error."""
