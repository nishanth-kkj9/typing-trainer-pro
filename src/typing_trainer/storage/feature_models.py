"""
Feature Models for Typing Trainer Pro
======================================
Database models for daily goals, achievements, custom word lists, and streaks.
Separated to avoid circular imports with database.py
"""

from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


# ─────────────────────────────────────────────────────────────────────────────
#  Models - Database tables for features
# ─────────────────────────────────────────────────────────────────────────────

class DailyGoal(SQLModel, table=True):
    """Daily typing practice goals"""
    __tablename__ = "daily_goals"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id")
    date: str  # ISO format YYYY-MM-DD
    target_wpm: int = 60
    target_accuracy: float = 90.0
    target_duration_minutes: int = 10
    achieved_wpm: Optional[float] = None
    achieved_accuracy: Optional[float] = None
    actual_duration_minutes: Optional[float] = None
    completed: bool = False


class Achievement(SQLModel, table=True):
    """Achievement/badge system"""
    __tablename__ = "achievements"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id")
    badge_id: str  # e.g., "first_session", "speed_demon", "perfectionist"
    name: str
    description: str
    unlocked_at: datetime
    icon: str = "🏆"


class CustomWordList(SQLModel, table=True):
    """User-customized word lists"""
    __tablename__ = "custom_word_lists"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id")
    name: str
    words: str  # JSON array or comma-separated
    created_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = True


class Streak(SQLModel, table=True):
    """Daily practice streak tracking"""
    __tablename__ = "streaks"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id")
    current_streak: int = 0
    longest_streak: int = 0
    last_practice_date: Optional[str] = None
    total_practice_days: int = 0
