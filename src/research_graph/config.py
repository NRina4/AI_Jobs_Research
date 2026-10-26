from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Настройки приложения."""

    model_config = SettingsConfigDict(
        env_prefix="RG_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    github_token: str | None = Field(default=None, repr=False)
    data_dir: Path = Path("data")
    log_level: str = "INFO"
    request_timeout: float = Field(default=30.0, gt=0, le=300)
    max_concurrency: int = Field(default=5, ge=1, le=50)


def get_settings() -> Settings:
    """Загрузить настройки приложения."""
    return Settings()
