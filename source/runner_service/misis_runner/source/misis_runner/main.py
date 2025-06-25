import asyncio

from misis_runner.runner import Runner


async def main():
    runner = Runner()
    await runner.start()
    while True:
        await asyncio.sleep(1)


if __name__ == "__main__":
    asyncio.run(main())
