from pathlib import Path

import pytest
from pydantic import ValidationError

from research_graph.config import Settings, get_settings


def test_default_settings() -> None:
    settings = Settings()

    assert settings.github_token is None
    assert settings.data_dir == Path("data")
    assert settings.log_level == "INFO"
    assert settings.request_timeout == 30.0
    assert settings.max_concurrency == 5


def test_settings_from_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("RG_DATA_DIR", "custom_data")
    monkeypatch.setenv("RG_LOG_LEVEL", "DEBUG")
    monkeypatch.setenv("RG_REQUEST_TIMEOUT", "15.5")
    monkeypatch.setenv("RG_MAX_CONCURRENCY", "10")

    settings = get_settings()

    assert settings.data_dir == Path("custom_data")
    assert settings.log_level == "DEBUG"
    assert settings.request_timeout == 15.5
    assert settings.max_concurrency == 10


def test_invalid_timeout() -> None:
    with pytest.raises(ValidationError):
        Settings(request_timeout=0)


def test_invalid_concurrency() -> None:
    with pytest.raises(ValidationError):
        Settings(max_concurrency=0)


def test_github_token_is_hidden_from_repr() -> None:
    settings = Settings(github_token="secret-test-token")

    assert "secret-test-token" not in repr(settings)
