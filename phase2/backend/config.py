from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator
from typing import List, Union
import os


class DatabaseSettings(BaseSettings):
    """Database configuration loaded from environment variables."""

    model_config = SettingsConfigDict(env_prefix="")

    database_url: str = "sqlite:///./test.db"
    pool_size: int = 5
    max_overflow: int = 10
    pool_timeout: int = 30
    pool_recycle: int = 3600
    pool_pre_ping: bool = True


class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="",
        extra="ignore"
    )

    port: int = 8000
    log_level: str = "DEBUG"
    database_url: str = "sqlite:///./test.db"
    _cors_origins_str: str = os.getenv("CORS_ORIGINS", "*")

    @property
    def cors_origins(self) -> List[str]:
        return [origin.strip() for origin in self._cors_origins_str.split(",")]


# Global settings instance
settings = Settings()
