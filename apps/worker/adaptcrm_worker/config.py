from enum import StrEnum
from typing import Annotated

from pydantic import Field, StringConstraints
from pydantic_settings import BaseSettings, SettingsConfigDict


class Environment(StrEnum):
    LOCAL = "local"
    TEST = "test"
    STAGING = "staging"
    PRODUCTION = "production"


NonBlankString = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]


class Settings(BaseSettings):
    """Worker process configuration loaded from external inputs."""

    model_config = SettingsConfigDict(
        case_sensitive=True,
        extra="ignore",
        frozen=True,
    )

    environment: Environment = Field(validation_alias="APP_ENV")
    temporal_address: NonBlankString = Field(
        validation_alias="TEMPORAL_ADDRESS",
    )
    temporal_namespace: NonBlankString = Field(
        validation_alias="TEMPORAL_NAMESPACE",
    )
    temporal_task_queue: NonBlankString = Field(
        validation_alias="TEMPORAL_TASK_QUEUE",
    )


def load_settings() -> Settings:
    # BaseSettings resolves required constructor fields from process environment.
    return Settings()  # type: ignore[call-arg]
