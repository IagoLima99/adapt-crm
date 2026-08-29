from __future__ import annotations

import argparse
import json
import os
import shutil
import signal
import subprocess
import sys
import time
from collections.abc import Callable, Sequence
from pathlib import Path
from typing import Protocol, TypeAlias
from urllib.error import URLError
from urllib.parse import urlparse
from urllib.request import urlopen

INSTALL_COMMANDS: tuple[tuple[str, ...], ...] = (
    ("uv", "sync", "--locked", "--all-packages", "--dev"),
    ("npm", "ci"),
)
TEST_COMMANDS: tuple[tuple[str, ...], ...] = (
    ("uv", "run", "pytest", "-q"),
    ("npm", "run", "test", "--workspace", "@adaptcrm/web"),
)
LINT_COMMANDS: tuple[tuple[str, ...], ...] = (
    ("uv", "run", "ruff", "check", "."),
    ("uv", "run", "ruff", "format", "--check", "."),
    ("uv", "run", "mypy", "tests", "scripts", "apps"),
    ("uv", "run", "python", "scripts/check_architecture.py"),
    ("npm", "run", "lint", "--workspace", "@adaptcrm/web"),
    ("npm", "run", "typecheck", "--workspace", "@adaptcrm/web"),
)
BUILD_COMMANDS: tuple[tuple[str, ...], ...] = (
    ("npm", "run", "build", "--workspace", "@adaptcrm/web"),
)
REQUIRED_DEV_VARIABLES = (
    "APP_ENV",
    "DATABASE_URL",
    "TEMPORAL_ADDRESS",
    "TEMPORAL_NAMESPACE",
    "TEMPORAL_TASK_QUEUE",
    "VITE_API_BASE_URL",
)
CommandRunner: TypeAlias = Callable[[Sequence[str]], int]


class Process(Protocol):
    def poll(self) -> int | None: ...

    def terminate(self) -> None: ...

    def wait(self, timeout: float | None = None) -> int: ...

    def kill(self) -> None: ...


class ProcessFactory(Protocol):
    def __call__(
        self,
        command: Sequence[str],
        *,
        cwd: Path,
        env: dict[str, str],
    ) -> Process: ...


class ProcessTree:
    """Own a subprocess group so wrappers cannot orphan development services."""

    def __init__(self, process: subprocess.Popen[bytes]) -> None:
        self._process = process

    def poll(self) -> int | None:
        return self._process.poll()

    def _signal_tree(self, *, force: bool) -> None:
        if os.name == "nt":
            if not force:
                try:
                    self._process.send_signal(  # type: ignore[attr-defined]
                        signal.CTRL_BREAK_EVENT  # type: ignore[attr-defined]
                    )
                except OSError:
                    pass
                return

            subprocess.run(
                ["taskkill", "/PID", str(self._process.pid), "/T", "/F"],
                check=False,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            if self._process.poll() is None:
                self._process.kill()
            return

        try:
            os.killpg(  # type: ignore[attr-defined]
                self._process.pid,
                signal.SIGKILL  # type: ignore[attr-defined]
                if force
                else signal.SIGTERM,
            )
        except ProcessLookupError:
            pass

    def terminate(self) -> None:
        self._signal_tree(force=False)

    def wait(self, timeout: float | None = None) -> int:
        return self._process.wait(timeout=timeout)

    def kill(self) -> None:
        self._signal_tree(force=True)


def format_command(command: Sequence[str]) -> str:
    return " ".join(command)


def execute_command(command: Sequence[str]) -> int:
    executable = shutil.which(command[0])
    if executable is None:
        print(f"Required executable not found: {command[0]}", file=sys.stderr)
        return 127
    resolved_command = (executable, *command[1:])
    return subprocess.run(resolved_command, check=False).returncode


def run_commands(
    commands: Sequence[Sequence[str]],
    *,
    dry_run: bool,
    command_runner: CommandRunner = execute_command,
) -> int:
    for command in commands:
        if dry_run:
            print(format_command(command))
            continue

        return_code = command_runner(command)
        if return_code != 0:
            return return_code

    return 0


def load_environment(path: Path) -> dict[str, str]:
    if not path.is_file():
        raise ValueError(f"Environment file not found: {path}")

    environment = dict(os.environ)
    for line_number, raw_line in enumerate(
        path.read_text(encoding="utf-8").splitlines(), start=1
    ):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            raise ValueError(f"Invalid environment entry at {path}:{line_number}")
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip()
        if not key:
            raise ValueError(f"Invalid environment entry at {path}:{line_number}")
        if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
            value = value[1:-1]
        environment.setdefault(key, value)

    missing = [key for key in REQUIRED_DEV_VARIABLES if not environment.get(key)]
    if missing:
        raise ValueError(
            "Missing required development variables: " + ", ".join(missing)
        )
    return environment


def build_dev_commands(environment: dict[str, str]) -> tuple[tuple[str, ...], ...]:
    host = environment.get("API_HOST", "127.0.0.1")
    port = environment.get("API_PORT", "8000")
    try:
        port_number = int(port)
    except ValueError as error:
        raise ValueError("API_PORT must be an integer between 1 and 65535.") from error
    if not 1 <= port_number <= 65535:
        raise ValueError("API_PORT must be an integer between 1 and 65535.")
    return (
        (
            "uv",
            "run",
            "--directory",
            "apps/api",
            "uvicorn",
            "adaptcrm_api.main:create_app",
            "--factory",
            "--host",
            host,
            "--port",
            port,
        ),
        (
            "uv",
            "run",
            "--directory",
            "apps/worker",
            "python",
            "-m",
            "adaptcrm_worker",
        ),
        ("npm", "run", "dev", "--workspace", "@adaptcrm/web"),
    )


def start_process(command: Sequence[str], *, cwd: Path, env: dict[str, str]) -> Process:
    executable = shutil.which(command[0])
    if executable is None:
        raise FileNotFoundError(f"Required executable not found: {command[0]}")
    resolved_command = (executable, *command[1:])
    if os.name == "nt":
        process = subprocess.Popen(
            resolved_command,
            cwd=cwd,
            env=env,
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP,
        )
    else:
        process = subprocess.Popen(
            resolved_command,
            cwd=cwd,
            env=env,
            start_new_session=True,
        )
    return ProcessTree(process)


def stop_processes(processes: Sequence[Process]) -> None:
    for process in processes:
        process.terminate()
    for process in processes:
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=5)


def supervise_processes(
    commands: Sequence[Sequence[str]],
    *,
    environment: dict[str, str],
    process_factory: ProcessFactory = start_process,
    poll_interval: float = 0.1,
) -> int:
    processes: list[Process] = []
    try:
        for command in commands:
            processes.append(process_factory(command, cwd=Path.cwd(), env=environment))
    except BaseException:
        stop_processes(processes)
        raise
    try:
        while True:
            for process in processes:
                return_code = process.poll()
                if return_code is not None:
                    stop_processes(processes)
                    return return_code if return_code != 0 else 1
            time.sleep(poll_interval)
    except KeyboardInterrupt:
        stop_processes(processes)
        return 130


def check_api_health(api_url: str, *, timeout: float) -> str:
    parsed_url = urlparse(api_url)
    if parsed_url.scheme not in {"http", "https"} or not parsed_url.netloc:
        raise ValueError("API URL must be an absolute HTTP(S) URL.")

    health_url = f"{api_url.rstrip('/')}/health"
    with urlopen(health_url, timeout=timeout) as response:
        if response.status != 200:
            raise ValueError(f"API health returned HTTP {response.status}.")
        payload: object = json.load(response)

    if not isinstance(payload, dict):
        raise TypeError("API health returned a non-object response.")
    if payload.get("status") != "ok" or payload.get("service") != "adaptcrm-api":
        raise ValueError("API health response does not match the AdaptCRM contract.")
    environment = payload.get("environment")
    if not isinstance(environment, str) or not environment:
        raise ValueError("API health response is missing the environment.")
    return f"adaptcrm-api health ok ({environment})"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run AdaptCRM repository tasks from one cross-platform entrypoint."
    )
    subparsers = parser.add_subparsers(dest="task", required=True)
    install_parser = subparsers.add_parser(
        "install", help="Install locked Python and Node.js dependencies."
    )
    install_parser.add_argument("--dry-run", action="store_true")
    test_parser = subparsers.add_parser("test", help="Run Python and web test suites.")
    test_parser.add_argument("--dry-run", action="store_true")
    lint_parser = subparsers.add_parser(
        "lint", help="Run all static quality and architecture gates."
    )
    lint_parser.add_argument("--dry-run", action="store_true")
    build_parser = subparsers.add_parser("build", help="Build production artifacts.")
    build_parser.add_argument("--dry-run", action="store_true")
    dev_parser = subparsers.add_parser(
        "dev", help="Start API, worker, and web development processes."
    )
    dev_parser.add_argument("--env-file", type=Path, default=Path(".env"))
    dev_parser.add_argument("--dry-run", action="store_true")
    smoke_parser = subparsers.add_parser(
        "smoke", help="Validate API health directly or through the web dev proxy."
    )
    smoke_target = smoke_parser.add_mutually_exclusive_group()
    smoke_target.add_argument(
        "--api-url",
        help="Call the API origin directly instead of the web development proxy.",
    )
    smoke_target.add_argument(
        "--web-url",
        help="Web origin whose /api proxy should reach the API.",
    )
    smoke_parser.add_argument("--timeout", type=float, default=5.0)
    return parser


def main(arguments: Sequence[str] | None = None) -> int:
    parsed = build_parser().parse_args(arguments)
    if parsed.task == "install":
        return run_commands(INSTALL_COMMANDS, dry_run=parsed.dry_run)
    if parsed.task == "test":
        return run_commands(TEST_COMMANDS, dry_run=parsed.dry_run)
    if parsed.task == "lint":
        return run_commands(LINT_COMMANDS, dry_run=parsed.dry_run)
    if parsed.task == "build":
        return run_commands(BUILD_COMMANDS, dry_run=parsed.dry_run)
    if parsed.task == "dev":
        try:
            environment = load_environment(parsed.env_file)
            commands = build_dev_commands(environment)
        except ValueError as error:
            print(error, file=sys.stderr)
            return 2
        if parsed.dry_run:
            return run_commands(commands, dry_run=True)
        return supervise_processes(commands, environment=environment)
    if parsed.task == "smoke":
        health_base_url = parsed.api_url or (
            f"{(parsed.web_url or 'http://localhost:5173').rstrip('/')}/api"
        )
        try:
            print(check_api_health(health_base_url, timeout=parsed.timeout))
        except (
            OSError,
            URLError,
            TypeError,
            ValueError,
            json.JSONDecodeError,
        ) as error:
            print(f"Smoke failed: {error}", file=sys.stderr)
            return 1
        return 0
    raise AssertionError(f"Unhandled repository task: {parsed.task}")


if __name__ == "__main__":
    raise SystemExit(main())
