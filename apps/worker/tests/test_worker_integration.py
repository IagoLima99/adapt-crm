import asyncio
import os

import pytest
from adaptcrm_worker.config import Settings
from adaptcrm_worker.runtime import build_temporal_worker, serve_worker
from temporalio.client import Client
from temporalio.testing import WorkflowEnvironment
from temporalio.worker import Worker

pytestmark = [
    pytest.mark.asyncio,
    pytest.mark.integration,
    pytest.mark.skipif(
        os.getenv("RUN_TEMPORAL_INTEGRATION") != "1",
        reason="set RUN_TEMPORAL_INTEGRATION=1 to start the Temporal dev server",
    ),
]


async def test_real_worker_starts_and_shuts_down_against_local_temporal() -> None:
    async with await WorkflowEnvironment.start_local(
        namespace="adaptcrm-test",
    ) as environment:
        settings = Settings.model_validate(
            {
                "APP_ENV": "test",
                "TEMPORAL_ADDRESS": (
                    environment.client.service_client.config.target_host
                ),
                "TEMPORAL_NAMESPACE": environment.client.namespace,
                "TEMPORAL_TASK_QUEUE": "adaptcrm-platform-test",
            },
        )
        workers: list[Worker] = []

        def capture_worker(client: Client, resolved_settings: Settings) -> Worker:
            worker = build_temporal_worker(client, resolved_settings)
            workers.append(worker)
            return worker

        stop_event = asyncio.Event()
        process = asyncio.create_task(
            serve_worker(settings, stop_event, build_worker=capture_worker),
        )

        async def wait_until_running() -> None:
            while not workers or not workers[0].is_running:
                await asyncio.sleep(0.01)

        await asyncio.wait_for(wait_until_running(), timeout=5)
        assert workers[0].task_queue == "adaptcrm-platform-test"

        stop_event.set()
        await asyncio.wait_for(process, timeout=5)

        assert workers[0].is_shutdown
