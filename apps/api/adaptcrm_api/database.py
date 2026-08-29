from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import Request
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from adaptcrm_api.config import Settings


class Base(DeclarativeBase):
    """Declarative root for all API models and Alembic metadata."""


def create_database_engine(settings: Settings) -> AsyncEngine:
    """Create the async PostgreSQL engine from external configuration."""
    return create_async_engine(
        str(settings.database_url),
        pool_pre_ping=True,
        pool_size=settings.database_pool_size,
        max_overflow=settings.database_max_overflow,
        pool_timeout=settings.database_pool_timeout,
    )


def create_session_factory(
    engine: AsyncEngine,
) -> async_sessionmaker[AsyncSession]:
    """Create sessions that keep transaction boundaries explicit to callers."""
    return async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )


async def get_db_session(request: Request) -> AsyncIterator[AsyncSession]:
    """Yield one request-scoped session and close it after the request."""
    session_factory: async_sessionmaker[AsyncSession] = (
        request.app.state.db_session_factory
    )
    async with session_factory() as session:
        yield session


@asynccontextmanager
async def transaction_scope(session: AsyncSession) -> AsyncIterator[AsyncSession]:
    """Commit on success and explicitly roll back when work fails."""
    try:
        async with session.begin():
            yield session
    except BaseException:
        await session.rollback()
        raise
