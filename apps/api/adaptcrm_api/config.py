from enum import StrEnum

from pydantic import Field, PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class Environment(StrEnum):
    LOCAL = "local"
    TEST = "test"
    STAGING = "staging"
    PRODUCTION = "production"


class Settings(BaseSettings):
    """Process configuration loaded exclusively from external inputs."""

    model_config = SettingsConfigDict(
        case_sensitive=True,
        extra="ignore",
        frozen=True,
    )

    environment: Environment = Field(validation_alias="APP_ENV")
    database_url: PostgresDsn = Field(validation_alias="DATABASE_URL")


def load_settings() -> Settings:
    # BaseSettings resolves required constructor fields from process environment.
    return Settings()  # type: ignore[call-arg]
