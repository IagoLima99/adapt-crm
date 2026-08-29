from __future__ import annotations

import os
import socket
import subprocess
import sys
import time
from collections.abc import Mapping, Sequence
from pathlib import Path

import pytest

from scripts.repo import Process, start_process, stop_processes, supervise_processes


class FakeProcess:
    def __init__(self, return_code: int | None) -> None:
        self.return_code = return_code
        self.terminated = False
        self.killed = False

    def poll(self) -> int | None:
        return self.return_code

    def terminate(self) -> None:
        self.terminated = True
        self.return_code = 0

    def wait(self, timeout: float | None = None) -> int:
        assert timeout is not None
        assert self.return_code is not None
        return self.return_code

    def kill(self) -> None:
        self.killed = True
        self.return_code = -1


def test_dev_supervisor_stops_siblings_when_a_service_fails() -> None:
    started: dict[str, FakeProcess] = {}

    def start_process(
        command: Sequence[str], *, cwd: Path, env: Mapping[str, str]
    ) -> Process:
        del cwd, env
        process = FakeProcess(7 if command[0] == "worker" else None)
        started[command[0]] = process
        return process

    result = supervise_processes(
        (("api",), ("worker",), ("web",)),
        environment={},
        process_factory=start_process,
        poll_interval=0,
    )

    assert result == 7
    assert started.keys() == {"api", "worker", "web"}
    assert started["api"].terminated
    assert started["web"].terminated
    assert not any(process.killed for process in started.values())


def test_dev_supervisor_cleans_started_services_when_startup_fails() -> None:
    api = FakeProcess(None)

    def start_process(
        command: Sequence[str], *, cwd: Path, env: Mapping[str, str]
    ) -> Process:
        del cwd, env
        if command[0] == "worker":
            raise OSError("worker executable is unavailable")
        return api

    with pytest.raises(OSError, match="worker executable is unavailable"):
        supervise_processes(
            (("api",), ("worker",), ("web",)),
            environment={},
            process_factory=start_process,
            poll_interval=0,
        )

    assert api.terminated
    assert not api.killed


def test_dev_process_resolves_the_platform_executable(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    started: list[tuple[str, ...]] = []
    process = FakeProcess(None)

    def popen(
        command: Sequence[str],
        *,
        cwd: Path,
        env: Mapping[str, str],
        **options: object,
    ) -> Process:
        assert cwd == tmp_path
        assert env == {"APP_ENV": "local"}
        expected_option = (
            {"creationflags": getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0)}
            if os.name == "nt"
            else {"start_new_session": True}
        )
        assert options == expected_option
        started.append(tuple(command))
        return process

    monkeypatch.setattr("shutil.which", lambda executable: f"resolved/{executable}")
    monkeypatch.setattr("scripts.repo.subprocess.Popen", popen)

    managed = start_process(
        ("npm", "run", "dev"), cwd=tmp_path, env={"APP_ENV": "local"}
    )

    assert managed.poll() is None
    assert started == [("resolved/npm", "run", "dev")]


def test_dev_supervisor_stops_all_services_on_requested_shutdown() -> None:
    class InterruptingProcess(FakeProcess):
        interrupted = False

        def poll(self) -> int | None:
            if not self.interrupted:
                self.interrupted = True
                raise KeyboardInterrupt
            return super().poll()

    processes = [InterruptingProcess(None), FakeProcess(None), FakeProcess(None)]

    def start_process(
        command: Sequence[str], *, cwd: Path, env: Mapping[str, str]
    ) -> Process:
        del command, cwd, env
        return processes.pop(0)

    started = processes.copy()
    result = supervise_processes(
        (("api",), ("worker",), ("web",)),
        environment={},
        process_factory=start_process,
        poll_interval=0,
    )

    assert result == 130
    assert all(process.terminated for process in started)


def test_dev_supervisor_stops_a_real_descendant_process(tmp_path: Path) -> None:
    child_script = tmp_path / "child.py"
    child_script.write_text(
        """
import socket
import sys
import time
from pathlib import Path

port = int(sys.argv[1])
ready_file = Path(sys.argv[2])
with socket.socket() as server:
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(("127.0.0.1", port))
    server.listen()
    ready_file.write_text("ready", encoding="utf-8")
    time.sleep(60)
""".strip(),
        encoding="utf-8",
    )
    parent_script = tmp_path / "parent.py"
    parent_script.write_text(
        """
import subprocess
import sys
import time

subprocess.Popen([sys.executable, sys.argv[1], sys.argv[2], sys.argv[3]])
time.sleep(60)
""".strip(),
        encoding="utf-8",
    )
    with socket.socket() as reservation:
        reservation.bind(("127.0.0.1", 0))
        port = reservation.getsockname()[1]
    ready_file = tmp_path / "ready"
    process = start_process(
        (
            sys.executable,
            str(parent_script),
            str(child_script),
            str(port),
            str(ready_file),
        ),
        cwd=tmp_path,
        env=dict(os.environ),
    )
    try:
        deadline = time.monotonic() + 5
        while not ready_file.exists() and time.monotonic() < deadline:
            time.sleep(0.05)
        assert ready_file.exists()

        stop_processes((process,))

        deadline = time.monotonic() + 5
        while time.monotonic() < deadline:
            with socket.socket() as client:
                if client.connect_ex(("127.0.0.1", port)) != 0:
                    break
            time.sleep(0.05)
        else:
            pytest.fail("descendant process kept its listening socket after shutdown")
    finally:
        if process.poll() is None:
            process.kill()
