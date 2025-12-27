"""Unit tests for config module."""

import logging
import os
from typing import Any, Dict

import pytest

from src.config import get_default_config, load_config, setup_logging


class TestSetupLogging:
    """Tests for setup_logging function."""

    def test_setup_logging_info_level(self, caplog: pytest.LogCaptureFixture) -> None:
        """Test logging setup with INFO level."""
        with caplog.at_level(logging.INFO):
            setup_logging("INFO")
            assert "Logging configured at INFO level" in caplog.text

    def test_setup_logging_debug_level(self, caplog: pytest.LogCaptureFixture) -> None:
        """Test logging setup with DEBUG level."""
        with caplog.at_level(logging.DEBUG):
            setup_logging("DEBUG")
            assert "Logging configured at DEBUG level" in caplog.text

    def test_setup_logging_invalid_level_defaults_to_info(self, caplog: pytest.LogCaptureFixture) -> None:
        """Test that invalid log level defaults to INFO."""
        with caplog.at_level(logging.INFO):
            setup_logging("INVALID")
            # Should not crash, defaults to INFO
            assert "Logging configured" in caplog.text


class TestGetDefaultConfig:
    """Tests for get_default_config function."""

    def test_returns_dict(self) -> None:
        """Test that function returns a dictionary."""
        config = get_default_config()
        assert isinstance(config, dict)

    def test_contains_required_keys(self) -> None:
        """Test that default config contains all required keys."""
        config = get_default_config()
        required_keys = {
            "log_level",
            "max_memory_mb",
            "max_session_objects",
            "enable_debug_mode",
            "startup_message",
            "confirm_destructive_ops",
        }
        assert set(config.keys()) == required_keys

    def test_default_values(self) -> None:
        """Test that default configuration values are correct."""
        config = get_default_config()
        assert config["log_level"] == "INFO"
        assert config["max_memory_mb"] == 200
        assert config["max_session_objects"] == 10000
        assert config["enable_debug_mode"] is False
        assert config["startup_message"] is True
        assert config["confirm_destructive_ops"] is True


class TestLoadConfig:
    """Tests for load_config function."""

    def test_load_config_no_env_vars(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test loading config without environment variables uses defaults."""
        # Clear environment variables
        for key in ["LOG_LEVEL", "MAX_MEMORY_MB", "MAX_SESSION_OBJECTS", "ENABLE_DEBUG_MODE"]:
            monkeypatch.delenv(key, raising=False)

        config = load_config()
        assert config == get_default_config()

    def test_load_config_with_log_level_env(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test that LOG_LEVEL environment variable overrides default."""
        monkeypatch.setenv("LOG_LEVEL", "DEBUG")
        config = load_config()
        assert config["log_level"] == "DEBUG"

    def test_load_config_with_max_memory_env(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test that MAX_MEMORY_MB environment variable overrides default."""
        monkeypatch.setenv("MAX_MEMORY_MB", "100")
        config = load_config()
        assert config["max_memory_mb"] == 100

    def test_load_config_with_invalid_memory_value(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test that invalid MAX_MEMORY_MB value keeps default."""
        monkeypatch.setenv("MAX_MEMORY_MB", "invalid")
        config = load_config()
        assert config["max_memory_mb"] == 200  # Default value

    def test_load_config_with_debug_mode_true(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test that ENABLE_DEBUG_MODE=true enables debug mode."""
        monkeypatch.setenv("ENABLE_DEBUG_MODE", "true")
        config = load_config()
        assert config["enable_debug_mode"] is True

    def test_load_config_with_debug_mode_false(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test that ENABLE_DEBUG_MODE=false disables debug mode."""
        monkeypatch.setenv("ENABLE_DEBUG_MODE", "false")
        config = load_config()
        assert config["enable_debug_mode"] is False

    def test_load_config_with_multiple_env_vars(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test loading config with multiple environment variables set."""
        monkeypatch.setenv("LOG_LEVEL", "WARNING")
        monkeypatch.setenv("MAX_MEMORY_MB", "300")
        monkeypatch.setenv("MAX_SESSION_OBJECTS", "5000")
        monkeypatch.setenv("ENABLE_DEBUG_MODE", "1")

        config = load_config()
        assert config["log_level"] == "WARNING"
        assert config["max_memory_mb"] == 300
        assert config["max_session_objects"] == 5000
        assert config["enable_debug_mode"] is True

    def test_load_config_filepath_parameter_ignored(self) -> None:
        """Test that filepath parameter is accepted but not yet used."""
        config = load_config(filepath="/some/path/config.json")
        # Should return defaults since file loading not yet implemented
        assert isinstance(config, dict)
