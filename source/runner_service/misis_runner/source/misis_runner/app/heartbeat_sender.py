import asyncio

from misis_runner.kafka.producer import Producer
from misis_runner.app.config import settings


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
            for scenario_id, processor in get_active_scenarios().items():
                await self.producer.send_heartbeat(
                    scenario_id=scenario_id,
                    last_frame=processor.last_processed_frame
                )
                await asyncio.sleep(settings.HEARTBEAT_INTERVAL)

    async def stop(self):
        self._running = False
        await self.producer.producer.stop()
