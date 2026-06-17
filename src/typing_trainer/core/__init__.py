"""Core package — pure-Python logic, no Qt dependencies."""
from typing_trainer.core.typing_engine import TypingEngine, CharStatus
from typing_trainer.core.stats_calculator import StatsCalculator
from typing_trainer.core.sentence_generator import SentenceGenerator

__all__ = ["TypingEngine", "CharStatus", "StatsCalculator", "SentenceGenerator"]
