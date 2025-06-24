import asyncio
import logging
from misis_orchestrator.database.database import async_session
from misis_orchestrator.kafka.consumer import Consumer
from misis_orchestrator.health.watchdog import Watchdog
from misis_orchestrator.orchestrator_service import OrchestratorService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def main():
    async with async_session() as session:
        orchestrator = OrchestratorService(session)
        consumers = Consumer()
        watchdog = Watchdog()

        await orchestrator.start()
        await consumers.start()

        asyncio.create_task(watchdog.process_heartbeats(consumers, watchdog))
        asyncio.create_task(handle_timeouts(watchdog, orchestrator))

        async for command in consumers.consume_commands():
            try:
                await orchestrator.process_command(command)
            except Exception as e:
                logger.error(f"Command processing failed: {str(e)}")


async def process_heartbeats(consumers: Consumer, watchdog: Watchdog):
    async for heartbeat in consumers.consume_heartbeats():
        watchdog.update_heartbeat(heartbeat.scenario_id)
        logger.debug(f"Heartbeat received: {heartbeat}")


async def handle_timeouts(watchdog, orchestrator):
    async for scenario_id in watchdog.check_timeouts():
        logger.warning(f"Heartbeat timeout for scenario {scenario_id}, restarting")
        try:
            await orchestrator.restart_scenario(scenario_id)
        except Exception as e:
            logger.error(f"Failed to restart scenario {scenario_id}: {str(e)}")


if __name__ == "__main__":
    asyncio.run(main())
