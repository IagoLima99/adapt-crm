from __future__ import annotations

import os
import subprocess
import sys
from datetime import UTC
from decimal import Decimal
from pathlib import Path
from typing import Any, Self, cast
from uuid import RFC_4122, UUID

import pytest
from adaptcrm_api.config import Settings
from adaptcrm_api.database import (
    create_database_engine,
    create_session_factory,
    transaction_scope,
)
from adaptcrm_api.models import (
    NAMING_CONVENTION,
    Base,
    CurrencyCode,
    Model,
    MoneyAmount,
    new_uuid7,
    utc_now,
)
from alembic.config import Config
from alembic.script import ScriptDirectory
from sqlalchemy import (
    CheckConstraint,
    Column,
    ForeignKey,
    Index,
    MetaData,
    String,
    Table,
    UniqueConstraint,
)
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy.orm import Mapped
from sqlalchemy.sql.sqltypes import DateTime, Numeric, Uuid

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


def test_uuid7_matches_rfc_layout(monkeypatch: Any) -> None:
    timestamp_ms = 1_645_557_742_000
    random_a = 0xCC3
    random_b = 0x18C4DC0C0C07398F
    random_bits = (random_a << 62) | random_b
    monkeypatch.setattr(
        "adaptcrm_api.models.time.time_ns",
        lambda: timestamp_ms * 1_000_000,
    )
    monkeypatch.setattr(
        "adaptcrm_api.models.secrets.randbits",
        lambda bit_count: random_bits if bit_count == 74 else 0,
    )

    identifier = new_uuid7()

    assert identifier == UUID("017f22e2-79b0-7cc3-98c4-dc0c0c07398f")
    assert identifier.version == 7
    assert identifier.variant == RFC_4122


def test_model_conventions_define_ids_utc_timestamps_and_money() -> None:
    class ExampleModel(Model):
        __tablename__ = "_test_model_conventions"

        amount: Mapped[MoneyAmount]
        currency: Mapped[CurrencyCode]

    table = cast(Table, ExampleModel.__table__)
    try:
        columns = table.c

        assert isinstance(columns.id.type, Uuid)
        assert columns.id.type.native_uuid is True
        assert columns.id.type.as_uuid is True
        assert columns.id.primary_key is True

        assert isinstance(columns.created_at.type, DateTime)
        assert columns.created_at.type.timezone is True
        assert columns.created_at.server_default is not None
        assert isinstance(columns.updated_at.type, DateTime)
        assert columns.updated_at.type.timezone is True
        assert columns.updated_at.server_default is not None
        assert columns.updated_at.onupdate is not None

        assert isinstance(columns.amount.type, Numeric)
        assert columns.amount.type.precision == 19
        assert columns.amount.type.scale == 4
        assert columns.amount.type.asdecimal is True
        assert columns.amount.type.python_type is Decimal
        assert isinstance(columns.currency.type, String)
        assert columns.currency.type.length == 3
    finally:
        Base.metadata.remove(table)

    now = utc_now()
    assert now.tzinfo is UTC


def test_constraint_and_index_names_are_deterministic() -> None:
    metadata = MetaData(naming_convention=NAMING_CONVENTION)
    accounts = Table(
        "accounts",
        metadata,
        Column("id", Uuid(), primary_key=True),
        Column("code", String(20)),
        UniqueConstraint("code"),
    )
    entries = Table(
        "entries",
        metadata,
        Column("id", Uuid(), primary_key=True),
        Column("account_id", Uuid(), ForeignKey("accounts.id"), index=True),
        Column("amount", Numeric(19, 4)),
        CheckConstraint("amount >= 0", name="amount_non_negative"),
    )

    account_unique = next(
        constraint
        for constraint in accounts.constraints
        if isinstance(constraint, UniqueConstraint)
    )
    entry_check = next(
        constraint
        for constraint in entries.constraints
        if isinstance(constraint, CheckConstraint)
    )
    entry_index = next(iter(entries.indexes))
    entry_foreign_key = next(iter(entries.foreign_key_constraints))

    assert accounts.primary_key.name == "pk_accounts"
    assert account_unique.name == "uq_accounts_code"
    assert entry_check.name == "ck_entries_amount_non_negative"
    assert entry_foreign_key.name == "fk_entries_account_id_accounts"
    assert isinstance(entry_index, Index)
    assert entry_index.name == "ix_entries_account_id"


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
