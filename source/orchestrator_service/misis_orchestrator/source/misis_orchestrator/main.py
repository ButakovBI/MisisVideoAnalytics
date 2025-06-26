import asyncio
import logging

from misis_orchestrator.database.database import get_db_session, engine
from misis_orchestrator.database.base import Base
from misis_orchestrator.health.watchdog import Watchdog
from misis_orchestrator.kafka.consumer import Consumer
from misis_orchestrator.orchestrator_service import OrchestratorService
from misis_orchestrator.outbox.outbox_worker import OutboxWorker

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_factory = get_db_session
    orchestrator = OrchestratorService(session_factory)
    consumers = Consumer()
    watchdog = Watchdog(session_factory, orchestrator)
    outbox_worker = OutboxWorker(session_factory)

    await orchestrator.start()
    await consumers.start()

    tasks = [
        asyncio.create_task(outbox_worker.start()),
        asyncio.create_task(process_heartbeats(consumers, watchdog)),
        asyncio.create_task(handle_timeouts(watchdog, orchestrator)),
        asyncio.create_task(process_commands(consumers, orchestrator))
    ]

    try:
        await asyncio.gather(*tasks)
    finally:
        await shutdown(consumers, orchestrator, outbox_worker, watchdog)


async def process_heartbeats(consumers: Consumer, watchdog: Watchdog):
    try:
        async for heartbeat in consumers.consume_heartbeats():
            try:
                await watchdog.update_heartbeat(heartbeat.scenario_id, heartbeat.last_frame)
                logger.debug(f"Heartbeat received: {heartbeat.scenario_id}")
            except Exception as e:
                logger.error(f"Heartbeat update failed: {str(e)}")
    except Exception as e:
        logger.error(f"Heartbeat processing failed: {str(e)}")


async def handle_timeouts(watchdog: Watchdog, orchestrator: OrchestratorService):
    try:
        async for scenario_id in watchdog.check_timeouts():
            logger.warning(f"Heartbeat timeout for {scenario_id}, restarting")
            try:
                await orchestrator.restart_scenario(scenario_id)
            except Exception as e:
                logger.error(f"Failed to restart scenario: {str(e)}")
    except Exception as e:
        logger.error(f"Timeout handler failed: {str(e)}")


async def process_commands(consumers: Consumer, orchestrator: OrchestratorService):
    try:
        async for command in consumers.consume_commands():
            try:
                await orchestrator.process_command(command)
            except Exception as e:
                logger.error(f"Command processing failed: {str(e)}")
    except Exception as e:
        logger.error(f"Command processing failed: {str(e)}")


async def shutdown(consumers, orchestrator, outbox_worker, watchdog):
    watchdog.running = False
    consumers.running = False
    outbox_worker.running = False

    await consumers.stop()
    await orchestrator.stop()
    await outbox_worker.stop()

    logger.info("Orchestrator shutdown complete")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
