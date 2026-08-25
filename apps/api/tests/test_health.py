import pytest
from adaptcrm_api.config import Environment, Settings
from adaptcrm_api.main import create_app
from httpx import ASGITransport, AsyncClient


def test_app_factory_loads_external_configuration(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("APP_ENV", "test")
    monkeypatch.setenv("DATABASE_URL", "postgresql+asyncpg://localhost/adaptcrm_test")

    app = create_app()

    assert app.state.settings.environment is Environment.TEST


@pytest.mark.asyncio
async def test_health_endpoint_smoke() -> None:
    settings = Settings.model_validate(
        {
            "APP_ENV": "test",
            "DATABASE_URL": "postgresql+asyncpg://localhost/adaptcrm_test",
        }
    )

    async with AsyncClient(
        transport=ASGITransport(app=create_app(settings)),
        base_url="http://testserver",
    ) as client:
        response = await client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "adaptcrm-api",
        "environment": Environment.TEST.value,
    }
