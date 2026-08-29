from __future__ import annotations

import secrets
import time
from datetime import UTC, datetime
from decimal import Decimal
from typing import Annotated, Final, TypeAlias
from uuid import UUID

from sqlalchemy import DateTime, MetaData, Numeric, String, Uuid, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

NAMING_CONVENTION: Final[dict[str, str]] = {
    "ix": "ix_%(table_name)s_%(column_0_N_name)s",
    "uq": "uq_%(table_name)s_%(column_0_N_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_N_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}
MONEY_PRECISION: Final = 19
MONEY_SCALE: Final = 4


def new_uuid7() -> UUID:
    """Generate an RFC 9562 UUIDv7 using the Python standard library."""
    timestamp_ms = time.time_ns() // 1_000_000
    if timestamp_ms >= 1 << 48:
        raise OverflowError("Current Unix timestamp does not fit in UUIDv7.")

    random_value = secrets.randbits(74)
    random_a = random_value >> 62
    random_b = random_value & ((1 << 62) - 1)
    value = (
        (timestamp_ms << 80)
        | (0b0111 << 76)
        | (random_a << 64)
        | (0b10 << 62)
        | random_b
    )
    return UUID(int=value)


def utc_now() -> datetime:
    """Return an aware UTC timestamp for ORM-side defaults and updates."""
    return datetime.now(UTC)


ModelId: TypeAlias = Annotated[
    UUID,
    mapped_column(
        Uuid(as_uuid=True, native_uuid=True),
        primary_key=True,
        default=new_uuid7,
    ),
]
MoneyAmount: TypeAlias = Annotated[
    Decimal,
    mapped_column(Numeric(MONEY_PRECISION, MONEY_SCALE, asdecimal=True)),
]
CurrencyCode: TypeAlias = Annotated[str, mapped_column(String(3))]


class Base(DeclarativeBase):
    """Declarative root containing the canonical Alembic metadata."""

    metadata = MetaData(naming_convention=NAMING_CONVENTION)


class Model(Base):
    """Shared identity and audit timestamps for persisted domain entities."""

    __abstract__ = True

    id: Mapped[ModelId]
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        server_default=func.now(),
        onupdate=utc_now,
    )
