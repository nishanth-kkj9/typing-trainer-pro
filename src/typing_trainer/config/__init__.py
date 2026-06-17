"""Configuration management — persistent user settings backed by TOML."""
from typing_trainer.config.settings import AppSettings, load_settings, save_settings

__all__ = ["AppSettings", "load_settings", "save_settings"]
