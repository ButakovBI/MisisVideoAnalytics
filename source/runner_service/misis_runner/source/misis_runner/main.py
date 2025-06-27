import asyncio
import logging

from misis_runner.runner import Runner

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


async def main():
    runner = Runner()
    try:
        await runner.start()
        while True:
            await asyncio.sleep(3600)
    except KeyboardInterrupt:
        logger.info("[Runner] Received exit signal")
    finally:
        await runner.stop()
        logger.info("[Runner] Runner shutdown complete")


if __name__ == "__main__":
    asyncio.run(main())
