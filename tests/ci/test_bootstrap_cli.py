from __future__ import annotations

import json
import os
import socket
import subprocess
import sys
import threading
import time
from collections.abc import Sequence
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import pytest

from scripts.repo import execute_command, run_commands, start_process, stop_processes

PROJECT_ROOT = Path(__file__).parents[2]
REPOSITORY_CLI = PROJECT_ROOT / "scripts" / "repo.py"


def run_cli(*arguments: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(REPOSITORY_CLI), *arguments],
        cwd=PROJECT_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )


def test_install_command_publishes_locked_dependency_steps() -> None:
    result = run_cli("install", "--dry-run")

    assert result.returncode == 0
    assert result.stdout.splitlines() == [
        "uv sync --locked --all-packages --dev",
        "npm ci",
    ]


def test_test_command_covers_python_and_web_suites() -> None:
    result = run_cli("test", "--dry-run")

    assert result.returncode == 0
    assert result.stdout.splitlines() == [
        "uv run pytest -q --basetemp .pytest-tmp",
        "npm run test --workspace @adaptcrm/web",
    ]


def test_lint_command_covers_all_static_quality_gates() -> None:
    result = run_cli("lint", "--dry-run")

    assert result.returncode == 0
    assert result.stdout.splitlines() == [
        "uv run ruff check .",
        "uv run ruff format --check .",
        "uv run mypy tests scripts apps",
        "uv run python scripts/check_architecture.py",
        "npm run lint --workspace @adaptcrm/web",
        "npm run typecheck --workspace @adaptcrm/web",
    ]


def test_build_command_creates_the_web_production_artifact() -> None:
    result = run_cli("build", "--dry-run")

    assert result.returncode == 0
    assert result.stdout.splitlines() == [
        "npm run build --workspace @adaptcrm/web",
    ]


def test_dev_command_publishes_all_processes_with_example_configuration() -> None:
    result = run_cli("dev", "--env-file", ".env.example", "--dry-run")

    assert result.returncode == 0
    assert result.stdout.splitlines() == [
        (
            "uv run --directory apps/api uvicorn "
            "adaptcrm_api.main:create_app --factory --host 127.0.0.1 --port 8000"
        ),
        "uv run --directory apps/worker python -m adaptcrm_worker",
        "npm run dev --workspace @adaptcrm/web",
    ]


def test_repository_task_propagates_the_first_failing_exit_code() -> None:
    executed: list[tuple[str, ...]] = []

    def execute(command: Sequence[str]) -> int:
        executed.append(tuple(command))
        return 23

    result = run_commands(
        (("uv", "run", "pytest"), ("npm", "run", "test")),
        dry_run=False,
        command_runner=execute,
    )

    assert result == 23
    assert executed == [("uv", "run", "pytest")]


def test_repository_task_resolves_the_platform_executable(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    executed: list[tuple[str, ...]] = []

    def run_process(
        command: Sequence[str], *, check: bool
    ) -> subprocess.CompletedProcess[str]:
        assert not check
        executed.append(tuple(command))
        return subprocess.CompletedProcess(command, 0)

    monkeypatch.setattr("shutil.which", lambda executable: f"resolved/{executable}")
    monkeypatch.setattr("scripts.repo.subprocess.run", run_process)

    assert execute_command(("npm", "ci")) == 0
    assert executed == [("resolved/npm", "ci")]


def test_smoke_command_validates_the_public_api_health_contract() -> None:
    class HealthHandler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:
            body = json.dumps(
                {
                    "status": "ok",
                    "service": "adaptcrm-api",
                    "environment": "local",
                }
            ).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, format: str, *args: object) -> None:
            del format, args

    with ThreadingHTTPServer(("127.0.0.1", 0), HealthHandler) as server:
        thread = threading.Thread(target=server.serve_forever)
        thread.start()
        try:
            host = server.server_name
            port = server.server_port
            result = run_cli("smoke", "--api-url", f"http://{host}:{port}")
        finally:
            server.shutdown()
            thread.join()

    assert result.returncode == 0
    assert result.stdout.strip() == "adaptcrm-api health ok (local)"


def test_smoke_command_reaches_api_through_the_web_origin() -> None:
    requested_paths: list[str] = []

    class WebProxyHandler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:
            requested_paths.append(self.path)
            body = json.dumps(
                {
                    "status": "ok",
                    "service": "adaptcrm-api",
                    "environment": "local",
                }
            ).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, format: str, *args: object) -> None:
            del format, args

    with ThreadingHTTPServer(("127.0.0.1", 0), WebProxyHandler) as server:
        thread = threading.Thread(target=server.serve_forever)
        thread.start()
        try:
            result = run_cli(
                "smoke",
                "--web-url",
                f"http://{server.server_name}:{server.server_port}",
            )
        finally:
            server.shutdown()
            thread.join()

    assert result.returncode == 0
    assert requested_paths == ["/api/health"]


def test_smoke_command_validates_real_api_startup() -> None:
    with socket.socket() as reservation:
        reservation.bind(("127.0.0.1", 0))
        port = reservation.getsockname()[1]
    environment = dict(os.environ)
    environment["APP_ENV"] = "local"
    environment["DATABASE_URL"] = (
        "postgresql+asyncpg://adaptcrm:adaptcrm@127.0.0.1:5432/adaptcrm"
    )
    process = start_process(
        (
            sys.executable,
            "-m",
            "uvicorn",
            "adaptcrm_api.main:create_app",
            "--factory",
            "--host",
            "127.0.0.1",
            "--port",
            str(port),
        ),
        cwd=PROJECT_ROOT / "apps" / "api",
        env=environment,
    )
    try:
        deadline = time.monotonic() + 10
        while time.monotonic() < deadline:
            result = run_cli(
                "smoke",
                "--api-url",
                f"http://127.0.0.1:{port}",
                "--timeout",
                "0.2",
            )
            if result.returncode == 0:
                break
            time.sleep(0.1)
        else:
            pytest.fail(f"API did not become healthy: {result.stderr}")
    finally:
        stop_processes((process,))

    assert result.stdout.strip() == "adaptcrm-api health ok (local)"


def test_dev_command_rejects_an_invalid_api_port(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.delenv("API_PORT", raising=False)
    env_file = tmp_path / ".env"
    env_file.write_text(
        (PROJECT_ROOT / ".env.example")
        .read_text(encoding="utf-8")
        .replace("API_PORT=8000", "API_PORT=invalid"),
        encoding="utf-8",
    )

    result = run_cli("dev", "--env-file", str(env_file), "--dry-run")

    assert result.returncode == 2
    assert result.stderr.strip() == "API_PORT must be an integer between 1 and 65535."
