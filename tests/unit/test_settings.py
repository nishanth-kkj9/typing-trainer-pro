from pathlib import Path
from unittest.mock import patch

import pytest
from pydantic import ValidationError

from typing_trainer.config.settings import AppSettings, load_settings, save_settings


class TestAppSettings:
    def test_defaults(self):
        s = AppSettings()
        assert s.difficulty == "medium"
        assert s.mode == "beginner"
        assert s.theme == "dark"
        assert s.timer_seconds == 60
        assert s.sound_enabled is True
        assert s.sound_volume == 0.5

    def test_invalid_difficulty(self):
        with pytest.raises(ValidationError):
            AppSettings(difficulty="expert")

    def test_invalid_timer_out_of_range(self):
        with pytest.raises(ValidationError):
            AppSettings(timer_seconds=10)

    def test_invalid_volume_out_of_range(self):
        with pytest.raises(ValidationError):
            AppSettings(sound_volume=1.5)

    def test_env_override(self, monkeypatch):
        monkeypatch.setenv("TYPING_DIFFICULTY", "hard")
        monkeypatch.setenv("TYPING_THEME", "light")
        s = AppSettings()
        assert s.difficulty == "hard"
        assert s.theme == "light"


class TestLoadSave:
    def test_load_returns_defaults_when_file_missing(self, tmp_path: Path):
        with patch(
            "typing_trainer.config.settings.config_path",
            return_value=tmp_path / "settings.toml",
        ):
            s = load_settings()
            assert s.difficulty == "medium"

    def test_roundtrip(self, tmp_path: Path):
        toml = tmp_path / "settings.toml"
        with patch(
            "typing_trainer.config.settings.config_path",
            return_value=toml,
        ):
            original = AppSettings(difficulty="hard", theme="light")
            save_settings(original)
            assert toml.exists()

            loaded = load_settings()
            assert loaded.difficulty == "hard"
            assert loaded.theme == "light"

    def test_load_handles_partial_toml(self, tmp_path: Path):
        toml = tmp_path / "settings.toml"
        toml.write_text('difficulty = "easy"\n', encoding="utf-8")
        with patch(
            "typing_trainer.config.settings.config_path",
            return_value=toml,
        ):
            s = load_settings()
            assert s.difficulty == "easy"
            assert s.theme == "dark"

    def test_save_none_last_user_id(self, tmp_path: Path):
        toml = tmp_path / "settings.toml"
        with patch(
            "typing_trainer.config.settings.config_path",
            return_value=toml,
        ):
            s = AppSettings(last_user_id=None)
            save_settings(s)
            content = toml.read_text(encoding="utf-8")
            assert "last_user_id = 0" in content
