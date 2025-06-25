import asyncio
import logging

from misis_runner.app.config import settings
from misis_runner.kafka.producer import Producer

logger = logging.getLogger(__name__)


class HeartbeatSender:
    def __init__(self):
        self.producer = Producer()
        self._running = False

    async def start(self, get_active_scenarios):
        self._running = True
        await self.producer.producer.start()
        asyncio.create_task(self._send_loop(get_active_scenarios))

    async def _send_loop(self, get_active_scenarios):
        while self._running:
            try:
                for scenario_id, processor in get_active_scenarios().items():
                    try:
                        await self.producer.send_heartbeat(
                            scenario_id=scenario_id,
                            last_frame=processor.last_processed_frame
                        )
                    except Exception as e:
                        logger.error(f"[Runner] Heartbeat send failed: {str(e)}")
                    await asyncio.sleep(settings.HEARTBEAT_INTERVAL)
            except Exception as e:
                logger.error(f"[Runner] Heartbeat loop error: {str(e)}")
                await asyncio.sleep(5)

    async def stop(self):
        self._running = False
        await self.producer.producer.stop()
