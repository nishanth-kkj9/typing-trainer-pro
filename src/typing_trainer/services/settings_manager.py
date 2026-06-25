"""
services/settings_manager.py — Reactive settings manager
========================================================
Singleton service wrapping AppSettings with Qt signals for live UI updates.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from PySide6.QtCore import QObject, Signal

from typing_trainer.config.settings import (
    AppSettings,
    Difficulty,
    Mode,
    Theme,
    config_path,
    load_settings,
    save_settings,
)


class SettingsManager(QObject):
    """Reactive settings manager with auto-save and change notifications."""

    settings_changed = Signal(str, object)  # (key, new_value)
    theme_changed = Signal(str)  # theme name

    _instance: SettingsManager | None = None

    def __new__(cls) -> SettingsManager:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        if hasattr(self, "_initialized"):
            return
        super().__init__()
        self._settings = load_settings()
        self._initialized = True

    @property
    def settings(self) -> AppSettings:
        return self._settings

    def get(self, key: str) -> Any:
        return getattr(self._settings, key)

    def update(self, **kwargs: Any) -> None:
        """Update settings and auto-save. Emits signals for changed values."""
        changed = False
        for key, value in kwargs.items():
            if hasattr(self._settings, key):
                old = getattr(self._settings, key)
                if old != value:
                    setattr(self._settings, key, value)
                    self.settings_changed.emit(key, value)
                    if key == "theme":
                        self.theme_changed.emit(value)
                    changed = True
        if changed:
            self._save()

    def _save(self) -> None:
        save_settings(self._settings)

    # Convenience typed accessors
    @property
    def difficulty(self) -> Difficulty:
        return self._settings.difficulty

    @difficulty.setter
    def difficulty(self, value: Difficulty) -> None:
        self.update(difficulty=value)

    @property
    def mode(self) -> Mode:
        return self._settings.mode

    @mode.setter
    def mode(self, value: Mode) -> None:
        self.update(mode=value)

    @property
    def theme(self) -> Theme:
        return self._settings.theme

    @theme.setter
    def theme(self, value: Theme) -> None:
        self.update(theme=value)

    @property
    def timer_seconds(self) -> int:
        return self._settings.timer_seconds

    @timer_seconds.setter
    def timer_seconds(self, value: int) -> None:
        self.update(timer_seconds=value)

    @property
    def sound_enabled(self) -> bool:
        return self._settings.sound_enabled

    @sound_enabled.setter
    def sound_enabled(self, value: bool) -> None:
        self.update(sound_enabled=value)

    @property
    def sound_volume(self) -> float:
        return self._settings.sound_volume

    @sound_volume.setter
    def sound_volume(self, value: float) -> None:
        self.update(sound_volume=value)

    @property
    def animation_speed(self) -> float:
        return self._settings.animation_speed

    @animation_speed.setter
    def animation_speed(self, value: float) -> None:
        self.update(animation_speed=value)

    @property
    def auto_next(self) -> bool:
        return self._settings.auto_next

    @auto_next.setter
    def auto_next(self, value: bool) -> None:
        self.update(auto_next=value)

    @property
    def show_finger_legend(self) -> bool:
        return self._settings.show_finger_legend

    @show_finger_legend.setter
    def show_finger_legend(self, value: bool) -> None:
        self.update(show_finger_legend=value)

    @property
    def minimize_to_tray(self) -> bool:
        return getattr(self._settings, "minimize_to_tray", True)

    @minimize_to_tray.setter
    def minimize_to_tray(self, value: bool) -> None:
        self.update(minimize_to_tray=value)


def get_settings_manager() -> SettingsManager:
    return SettingsManager()