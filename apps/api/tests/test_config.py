import pytest
from adaptcrm_api.config import Environment, load_settings
from pydantic import ValidationError


def test_settings_load_required_typed_environment(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("APP_ENV", "test")
    monkeypatch.setenv("DATABASE_URL", "postgresql+asyncpg://localhost/adaptcrm_test")

    settings = load_settings()

    assert settings.environment is Environment.TEST
    assert str(settings.database_url) == "postgresql+asyncpg://localhost/adaptcrm_test"


def test_settings_reject_missing_required_configuration(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("APP_ENV", raising=False)
    monkeypatch.delenv("DATABASE_URL", raising=False)

    with pytest.raises(ValidationError) as error:
        load_settings()

    missing_fields = {item["loc"] for item in error.value.errors()}
    assert missing_fields == {("APP_ENV",), ("DATABASE_URL",)}


def test_settings_reject_unknown_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("APP_ENV", "invalid")
    monkeypatch.setenv("DATABASE_URL", "postgresql+asyncpg://localhost/adaptcrm_test")

    with pytest.raises(ValidationError):
        load_settings()
