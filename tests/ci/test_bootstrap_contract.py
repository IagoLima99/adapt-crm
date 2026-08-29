from __future__ import annotations

from pathlib import Path

from adaptcrm_api.config import Settings as ApiSettings
from adaptcrm_worker.config import Settings as WorkerSettings

PROJECT_ROOT = Path(__file__).parents[2]


def test_root_readme_publishes_the_repository_bootstrap_commands() -> None:
    readme = (PROJECT_ROOT / "README.md").read_text(encoding="utf-8")

    for command in (
        "python scripts/repo.py install",
        "python scripts/repo.py dev",
        "python scripts/repo.py test",
        "python scripts/repo.py lint",
        "python scripts/repo.py build",
        "python scripts/repo.py smoke",
    ):
        assert f"`{command}`" in readme

    assert "PostgreSQL" in readme
    assert "Temporal" in readme
    assert "EL-25" in readme


def test_environment_example_covers_process_and_bootstrap_configuration() -> None:
    entries = {
        line.split("=", 1)[0].strip(): line.split("=", 1)[1].strip()
        for line in (PROJECT_ROOT / ".env.example")
        .read_text(encoding="utf-8")
        .splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    }
    process_aliases = {
        field.validation_alias
        for settings in (ApiSettings, WorkerSettings)
        for field in settings.model_fields.values()
    }

    assert process_aliases <= entries.keys()
    assert entries.keys() == {
        "APP_ENV",
        "API_HOST",
        "API_PORT",
        "DATABASE_URL",
        "TEMPORAL_ADDRESS",
        "TEMPORAL_NAMESPACE",
        "TEMPORAL_TASK_QUEUE",
        "VITE_API_BASE_URL",
    }
    assert all(entries.values())

    gitignore = (PROJECT_ROOT / ".gitignore").read_text(encoding="utf-8")
    assert gitignore.splitlines()[:3] == [".env", ".env.*", "!.env.example"]
