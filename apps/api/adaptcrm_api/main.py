from fastapi import FastAPI

from adaptcrm_api.config import Settings, load_settings
from adaptcrm_api.health import router as health_router


def create_app(settings: Settings | None = None) -> FastAPI:
    """Build the API and fail fast when required process config is absent."""
    resolved_settings = settings if settings is not None else load_settings()
    app = FastAPI(
        title="AdaptCRM API",
        version="0.1.0",
    )
    app.state.settings = resolved_settings
    app.include_router(health_router)
    return app
