import pytest
from adaptcrm_worker.config import Environment, load_settings
from pydantic import ValidationError


def test_settings_load_required_typed_temporal_configuration(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("APP_ENV", "test")
    monkeypatch.setenv("TEMPORAL_ADDRESS", "localhost:7233")
    monkeypatch.setenv("TEMPORAL_NAMESPACE", "adaptcrm-test")
    monkeypatch.setenv("TEMPORAL_TASK_QUEUE", "adaptcrm-platform-test")

    settings = load_settings()

    assert settings.environment is Environment.TEST
    assert settings.temporal_address == "localhost:7233"
    assert settings.temporal_namespace == "adaptcrm-test"
    assert settings.temporal_task_queue == "adaptcrm-platform-test"


def test_settings_reject_missing_required_configuration(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    for variable in (
        "APP_ENV",
        "TEMPORAL_ADDRESS",
        "TEMPORAL_NAMESPACE",
        "TEMPORAL_TASK_QUEUE",
    ):
        monkeypatch.delenv(variable, raising=False)

    with pytest.raises(ValidationError) as error:
        load_settings()

    missing_fields = {item["loc"] for item in error.value.errors()}
    assert missing_fields == {
        ("APP_ENV",),
        ("TEMPORAL_ADDRESS",),
        ("TEMPORAL_NAMESPACE",),
        ("TEMPORAL_TASK_QUEUE",),
    }


def test_settings_reject_blank_temporal_values(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("APP_ENV", "test")
    monkeypatch.setenv("TEMPORAL_ADDRESS", "localhost:7233")
    monkeypatch.setenv("TEMPORAL_NAMESPACE", "adaptcrm-test")
    monkeypatch.setenv("TEMPORAL_TASK_QUEUE", "   ")

    with pytest.raises(ValidationError):
        load_settings()
