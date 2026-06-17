from pathlib import Path
from typing import Literal

import tomli_w
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

Difficulty = Literal["easy", "medium", "hard"]
Mode = Literal["beginner", "intermediate", "advanced"]
Theme = Literal["dark", "light", "high_contrast"]


class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="TYPING_",
        env_nested_delimiter="__",
        extra="ignore",
    )

    difficulty: Difficulty = Field(default="medium")
    mode: Mode = Field(default="beginner")
    theme: Theme = Field(default="dark")
    timer_seconds: int = Field(default=60, ge=15, le=300)
    sound_enabled: bool = Field(default=True)
    sound_volume: float = Field(default=0.5, ge=0.0, le=1.0)
    animation_speed: float = Field(default=1.0, ge=0.1, le=3.0)
    auto_next: bool = Field(default=True)
    show_finger_legend: bool = Field(default=True)

    last_user_id: int | None = Field(default=None)


def config_path() -> Path:
    base = Path.home() / ".config" / "typing-trainer-pro"
    base.mkdir(parents=True, exist_ok=True)
    return base / "settings.toml"


def load_settings() -> AppSettings:
    path = config_path()
    if path.exists():
        import tomllib
        data = tomllib.loads(path.read_text(encoding="utf-8"))
        return AppSettings(**data)
    return AppSettings()


def save_settings(settings: AppSettings) -> None:
    path = config_path()
    data = settings.model_dump()
    for k, v in data.items():
        if v is None:
            data[k] = 0
    path.write_text(tomli_w.dumps(data), encoding="utf-8")
