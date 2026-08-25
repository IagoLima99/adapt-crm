from typing import Literal

from fastapi import APIRouter, Request
from pydantic import BaseModel

from adaptcrm_api.config import Environment, Settings

router = APIRouter(tags=["health"])


class HealthResponse(BaseModel):
    status: Literal["ok"] = "ok"
    service: Literal["adaptcrm-api"] = "adaptcrm-api"
    environment: Environment


@router.get("/health", response_model=HealthResponse)
async def health(request: Request) -> HealthResponse:
    settings: Settings = request.app.state.settings
    return HealthResponse(environment=settings.environment)
