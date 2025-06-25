import asyncio
import logging

from misis_orchestrator.database.database import async_session
from misis_orchestrator.health.watchdog import Watchdog
from misis_orchestrator.kafka.consumer import Consumer
from misis_orchestrator.orchestrator_service import OrchestratorService
from misis_orchestrator.outbox.outbox_worker import OutboxWorker

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def main():
    async with async_session() as session:
        orchestrator = OrchestratorService(db_session=session)
        consumers = Consumer()
        watchdog = Watchdog(db_session=session)
        outbox_worker = OutboxWorker(db_session=session)

        await orchestrator.start()
        await consumers.start()
        worker_task = asyncio.create_task(outbox_worker.start())

        asyncio.create_task(process_heartbeats(consumers, watchdog))
        asyncio.create_task(handle_timeouts(watchdog, orchestrator))

        async for command in consumers.consume_commands():
            try:
                await orchestrator.process_command(command)
            except Exception as e:
                logger.error(f"[Orchestrator] Command processing failed: {str(e)}")

        await consumers.stop()
        await orchestrator.stop()
        outbox_worker.stop()
        await worker_task


async def process_heartbeats(consumers: Consumer, watchdog: Watchdog):
    async for heartbeat in consumers.consume_heartbeats():
        await watchdog.update_heartbeat(heartbeat.scenario_id)
        logger.debug(f"[Orchestrator] Heartbeat received: {heartbeat}")


async def handle_timeouts(watchdog, orchestrator):
    async for scenario_id in watchdog.check_timeouts():
        logger.warning(f"[Orchestrator] Heartbeat timeout for scenario {scenario_id}, restarting")
        try:
            await orchestrator.restart_scenario(scenario_id)
        except Exception as e:
            logger.error(f"[Orchestrator] Failed to restart scenario {scenario_id}: {str(e)}")


if __name__ == "__main__":
    asyncio.run(main())
