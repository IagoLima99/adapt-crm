import asyncio

from adaptcrm_worker.config import load_settings
from adaptcrm_worker.runtime import serve_worker


async def run() -> None:
    await serve_worker(load_settings(), asyncio.Event())


def main() -> None:
    try:
        asyncio.run(run())
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
