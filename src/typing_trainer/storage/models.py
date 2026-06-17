from datetime import datetime

from sqlmodel import Field, SQLModel


class User(SQLModel, table=True):
    __tablename__ = "users"

    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(max_length=100)
    created_at: datetime = Field(default_factory=datetime.now)
    preferences_json: str = Field(default="{}")


class TrainingSession(SQLModel, table=True):
    __tablename__ = "sessions"

    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    started_at: datetime = Field(default_factory=datetime.now)
    ended_at: datetime | None = Field(default=None)
    duration_seconds: float = Field(default=0.0)
    target_text_hash: str = Field(max_length=64, default="")
    difficulty: str = Field(max_length=16)
    mode: str = Field(max_length=16)
    wpm: float = Field(default=0.0)
    accuracy: float = Field(default=100.0)
    errors: int = Field(default=0)
    correct: int = Field(default=0)
    xp_earned: int = Field(default=0)


class KeyStat(SQLModel, table=True):
    __tablename__ = "key_stats"

    id: int | None = Field(default=None, primary_key=True)
    session_id: int = Field(foreign_key="sessions.id", index=True)
    key_char: str = Field(max_length=4)
    correct_count: int = Field(default=0)
    error_count: int = Field(default=0)
    avg_latency_ms: float = Field(default=0.0)
