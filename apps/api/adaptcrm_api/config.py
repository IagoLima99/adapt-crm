from enum import StrEnum

from pydantic import Field, NonNegativeInt, PositiveInt, PostgresDsn
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
    database_pool_size: PositiveInt = Field(
        default=5,
        validation_alias="DATABASE_POOL_SIZE",
    )
    database_max_overflow: NonNegativeInt = Field(
        default=10,
        validation_alias="DATABASE_MAX_OVERFLOW",
    )
    database_pool_timeout: PositiveInt = Field(
        default=30,
        validation_alias="DATABASE_POOL_TIMEOUT",
    )


def load_settings() -> Settings:
    # BaseSettings resolves required constructor fields from process environment.
    return Settings()  # type: ignore[call-arg]
