from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from adaptcrm_api.config import Settings, load_settings
from adaptcrm_api.database import create_database_engine, create_session_factory
from adaptcrm_api.health import router as health_router


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    try:
        yield
    finally:
        await app.state.db_engine.dispose()


def create_app(settings: Settings | None = None) -> FastAPI:
    """Build the API and fail fast when required process config is absent."""
    resolved_settings = settings if settings is not None else load_settings()
    db_engine = create_database_engine(resolved_settings)
    app = FastAPI(
        title="AdaptCRM API",
        version="0.1.0",
        lifespan=lifespan,
    )
    app.state.settings = resolved_settings
    app.state.db_engine = db_engine
    app.state.db_session_factory = create_session_factory(db_engine)
    app.include_router(health_router)
    return app
