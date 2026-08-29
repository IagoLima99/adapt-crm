from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path
from typing import Any, Self, cast

import pytest
from adaptcrm_api.config import Settings
from adaptcrm_api.database import (
    Base,
    create_database_engine,
    create_session_factory,
    transaction_scope,
)
from alembic.config import Config
from alembic.script import ScriptDirectory
from sqlalchemy.ext.asyncio import AsyncEngine

PROJECT_ROOT = Path(__file__).parents[3]


def build_settings(**overrides: Any) -> Settings:
    values: dict[str, Any] = {
        "APP_ENV": "test",
        "DATABASE_URL": "postgresql+asyncpg://localhost/adaptcrm_test",
    }
    values.update(overrides)
    return Settings.model_validate(values)


def test_database_engine_uses_external_url_and_pool_settings(monkeypatch: Any) -> None:
    calls: dict[str, Any] = {}

    def fake_create_async_engine(url: str, **kwargs: Any) -> AsyncEngine:
        calls["url"] = url
        calls["kwargs"] = kwargs
        return cast(AsyncEngine, object())

    monkeypatch.setattr(
        "adaptcrm_api.database.create_async_engine",
        fake_create_async_engine,
    )

    create_database_engine(
        build_settings(
            DATABASE_POOL_SIZE=3,
            DATABASE_MAX_OVERFLOW=4,
            DATABASE_POOL_TIMEOUT=12,
        )
    )

    assert calls == {
        "url": "postgresql+asyncpg://localhost/adaptcrm_test",
        "kwargs": {
            "pool_pre_ping": True,
            "pool_size": 3,
            "max_overflow": 4,
            "pool_timeout": 12,
        },
    }


def test_session_factory_disables_expire_on_commit() -> None:
    engine = cast(
        AsyncEngine,
        object(),
    )

    factory = create_session_factory(engine)

    assert factory.kw["expire_on_commit"] is False


def test_alembic_points_to_empty_baseline() -> None:
    config = Config(str(PROJECT_ROOT / "apps" / "api" / "alembic.ini"))
    scripts = ScriptDirectory.from_config(config)

    assert scripts.get_current_head() == "0001_baseline"
    assert Base.metadata.tables == {}


class TransactionStub:
    def __init__(self) -> None:
        self.rollback_called = False

    def begin(self) -> Self:
        return self

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(self, *_: object) -> bool:
        return False

    async def rollback(self) -> None:
        self.rollback_called = True


@pytest.mark.asyncio
async def test_transaction_scope_rolls_back_on_failure() -> None:
    session = TransactionStub()

    with pytest.raises(RuntimeError, match="transaction failed"):
        async with transaction_scope(cast(Any, session)):
            raise RuntimeError("transaction failed")

    assert session.rollback_called is True


def test_alembic_generates_empty_database_upgrade_sql() -> None:
    environment = os.environ.copy()
    environment.update(
        {
            "APP_ENV": "test",
            "DATABASE_URL": "postgresql+asyncpg://localhost/adaptcrm_test",
        }
    )
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "alembic",
            "-c",
            "apps/api/alembic.ini",
            "upgrade",
            "head",
            "--sql",
        ],
        cwd=PROJECT_ROOT,
        env=environment,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert "CREATE TABLE alembic_version" in result.stdout
    assert "0001_baseline" in result.stdout
