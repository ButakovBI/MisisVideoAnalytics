import asyncio
import logging
from uuid import UUID

from misis_runner.app.config import settings
from misis_runner.kafka.producer import Producer

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class HeartbeatSender:
    def __init__(self):
        self.producer = Producer()
        self._running = False

    async def start(self, get_active_scenarios):
        self._running = True
        await self.producer.start()
        asyncio.create_task(self._send_loop(get_active_scenarios))

    async def _send_loop(self, get_active_scenarios):
        while self._running:
            try:
                active_scenarios = [
                    (scenario_id, processor)
                    for scenario_id, processor in get_active_scenarios().items()
                    if not processor.is_stopping
                ]
                tasks = [
                    self._send_single_heartbeat(scenario_id, processor)
                    for scenario_id, processor in active_scenarios
                ]
                if tasks:
                    await asyncio.gather(*tasks, return_exceptions=True)
                    logger.info("[Runner] Heartbeat sender: starting tasks")

                await asyncio.sleep(settings.HEARTBEAT_INTERVAL)
            except Exception as e:
                logger.error(f"[Runner] Heartbeat loop error: {str(e)}")
                await asyncio.sleep(5)

    async def _send_single_heartbeat(self, scenario_id: UUID, processor):
        try:
            if processor.is_stopping:
                return
            await self.producer.send_heartbeat(
                scenario_id=scenario_id,
                last_frame=processor.last_processed_frame
            )
            logger.info("[Runner] Heartbeat sender: sent heartbeat")
        except Exception as e:
            logger.error(f"[Runner] Heartbeat send failed for {scenario_id}: {str(e)}")

    async def stop(self):
        self._running = False
        await self.producer.producer.stop()
