import asyncio
from typing import cast

import pytest
from adaptcrm_worker.config import Environment, Settings
from adaptcrm_worker.runtime import WorkerRunner, serve_worker
from temporalio.client import Client


class FakeWorker:
    def __init__(self, task_queue: str) -> None:
        self.task_queue = task_queue
        self.started = asyncio.Event()
        self.stopped = asyncio.Event()
        self.run_cancelled = asyncio.Event()
        self.shutdown_calls = 0

    async def run(self) -> None:
        self.started.set()
        try:
            await self.stopped.wait()
        except asyncio.CancelledError:
            self.run_cancelled.set()
            raise

    async def shutdown(self) -> None:
        self.shutdown_calls += 1
        self.stopped.set()


@pytest.mark.asyncio
async def test_worker_starts_on_configured_queue_and_shuts_down_cleanly() -> None:
    settings = Settings.model_validate(
        {
            "APP_ENV": Environment.TEST,
            "TEMPORAL_ADDRESS": "localhost:7233",
            "TEMPORAL_NAMESPACE": "adaptcrm-test",
            "TEMPORAL_TASK_QUEUE": "adaptcrm-platform-test",
        },
    )
    client = object()
    worker = FakeWorker(settings.temporal_task_queue)
    connected_settings: list[Settings] = []
    registered_queues: list[str] = []

    async def connect(resolved_settings: Settings) -> Client:
        connected_settings.append(resolved_settings)
        return cast(Client, client)

    def build_worker(_client: Client, resolved_settings: Settings) -> WorkerRunner:
        assert _client is client
        registered_queues.append(resolved_settings.temporal_task_queue)
        return worker

    stop_event = asyncio.Event()
    process = asyncio.create_task(
        serve_worker(
            settings,
            stop_event,
            connect=connect,
            build_worker=build_worker,
        ),
    )

    await asyncio.wait_for(worker.started.wait(), timeout=1)
    stop_event.set()
    await asyncio.wait_for(process, timeout=1)

    assert connected_settings == [settings]
    assert registered_queues == ["adaptcrm-platform-test"]
    assert worker.shutdown_calls == 1


@pytest.mark.asyncio
async def test_worker_run_task_is_cleaned_up_when_shutdown_fails() -> None:
    settings = Settings.model_validate(
        {
            "APP_ENV": Environment.TEST,
            "TEMPORAL_ADDRESS": "localhost:7233",
            "TEMPORAL_NAMESPACE": "adaptcrm-test",
            "TEMPORAL_TASK_QUEUE": "adaptcrm-platform-test",
        },
    )
    worker = FakeWorker(settings.temporal_task_queue)

    async def connect(_settings: Settings) -> Client:
        return cast(Client, object())

    def build_worker(_client: Client, _settings: Settings) -> WorkerRunner:
        async def failing_shutdown() -> None:
            worker.shutdown_calls += 1
            raise RuntimeError("shutdown failed")

        worker.shutdown = failing_shutdown  # type: ignore[method-assign]
        return worker

    stop_event = asyncio.Event()
    process = asyncio.create_task(
        serve_worker(
            settings,
            stop_event,
            connect=connect,
            build_worker=build_worker,
        ),
    )
    await asyncio.wait_for(worker.started.wait(), timeout=1)

    stop_event.set()
    with pytest.raises(RuntimeError, match="shutdown failed"):
        await asyncio.wait_for(process, timeout=1)

    assert worker.run_cancelled.is_set()
