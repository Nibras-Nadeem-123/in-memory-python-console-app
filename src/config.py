"""Configuration and logging setup for the console application."""

import logging
import os
from typing import Any, Dict


def setup_logging(level: str = "INFO") -> None:
    """Configure Python logging module with structured format.

    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR)
    """
    numeric_level = getattr(logging, level.upper(), logging.INFO)

    logging.basicConfig(
        level=numeric_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    logger = logging.getLogger(__name__)
    logger.info(f"Logging configured at {level.upper()} level")


def get_default_config() -> Dict[str, Any]:
    """Get default configuration values.

    Returns:
        Dictionary with default configuration settings
    """
    return {
        "log_level": "INFO",
        "max_memory_mb": 200,
        "max_session_objects": 10000,
        "enable_debug_mode": False,
        "startup_message": True,
        "confirm_destructive_ops": True,
    }


def load_config(filepath: str | None = None) -> Dict[str, Any]:
    """Load configuration from environment variables or file.

    Args:
        filepath: Optional path to configuration file (reserved for future use)

    Returns:
        Configuration dictionary with values from environment or defaults
    """
    config = get_default_config()

    # Override from environment variables
    if "LOG_LEVEL" in os.environ:
        config["log_level"] = os.environ["LOG_LEVEL"]

    if "MAX_MEMORY_MB" in os.environ:
        try:
            config["max_memory_mb"] = int(os.environ["MAX_MEMORY_MB"])
        except ValueError:
            pass  # Keep default if invalid

    if "MAX_SESSION_OBJECTS" in os.environ:
        try:
            config["max_session_objects"] = int(os.environ["MAX_SESSION_OBJECTS"])
        except ValueError:
            pass

    if "ENABLE_DEBUG_MODE" in os.environ:
        config["enable_debug_mode"] = os.environ["ENABLE_DEBUG_MODE"].lower() in ("true", "1", "yes")

    return config
