import asyncio
from collections.abc import Awaitable, Callable
from contextlib import suppress
from typing import Protocol

from temporalio import activity
from temporalio.client import Client
from temporalio.worker import Worker

from adaptcrm_worker.config import Settings


class WorkerRunner(Protocol):
    async def run(self) -> None: ...

    async def shutdown(self) -> None: ...


ClientConnector = Callable[[Settings], Awaitable[Client]]
WorkerBuilder = Callable[[Client, Settings], WorkerRunner]


@activity.defn(name="adaptcrm.worker.bootstrap")
async def bootstrap_activity() -> None:
    """Provide the technical registration required by an empty worker."""


async def connect_temporal(settings: Settings) -> Client:
    return await Client.connect(
        settings.temporal_address,
        namespace=settings.temporal_namespace,
    )


def build_temporal_worker(client: Client, settings: Settings) -> Worker:
    return Worker(
        client,
        task_queue=settings.temporal_task_queue,
        activities=[bootstrap_activity],
    )


async def shutdown_worker(
    worker: WorkerRunner,
    run_task: asyncio.Task[None],
) -> None:
    try:
        await worker.shutdown()
    except BaseException:
        run_task.cancel()
        with suppress(asyncio.CancelledError):
            await run_task
        raise

    await run_task


async def serve_worker(
    settings: Settings,
    stop_event: asyncio.Event,
    *,
    connect: ClientConnector = connect_temporal,
    build_worker: WorkerBuilder = build_temporal_worker,
) -> None:
    """Run the Temporal worker until stopped or until it fails."""

    client = await connect(settings)
    worker = build_worker(client, settings)
    run_task = asyncio.create_task(worker.run(), name="adaptcrm-temporal-worker")
    stop_task = asyncio.create_task(stop_event.wait(), name="adaptcrm-worker-stop")

    try:
        completed, _ = await asyncio.wait(
            {run_task, stop_task},
            return_when=asyncio.FIRST_COMPLETED,
        )
        if stop_task in completed and not run_task.done():
            await shutdown_worker(worker, run_task)
        else:
            await run_task
    except asyncio.CancelledError:
        if not run_task.done():
            await shutdown_worker(worker, run_task)
        raise
    finally:
        stop_task.cancel()
        with suppress(asyncio.CancelledError):
            await stop_task
