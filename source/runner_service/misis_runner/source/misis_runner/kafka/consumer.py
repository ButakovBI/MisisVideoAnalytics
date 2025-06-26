import asyncio
import json
import logging
from uuid import UUID

from aiokafka import AIOKafkaConsumer

from misis_runner.app.config import settings
from misis_runner.models.constants.kafka_topic import KafkaTopic

logger = logging.getLogger(__name__)


class Consumer:
    def __init__(self):
        self._running = False
        self.start_consumer = AIOKafkaConsumer(
            KafkaTopic.RUNNER_COMMANDS.value,
            bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
            group_id="runners_group",
            enable_auto_commit=False,
            max_poll_interval_ms=settings.KAFKA_MAX_POLL_INTERVAL_MS,
            session_timeout_ms=60000,
        )
        self.stop_consumer = AIOKafkaConsumer(
            KafkaTopic.RUNNER_COMMANDS.value,
            bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
            auto_offset_reset='latest',
        )

    async def start(self, start_handler, stop_handler):
        self._running = True
        await self.start_consumer.start()
        await self.stop_consumer.start()

        asyncio.create_task(self._consume_starts(start_handler))
        asyncio.create_task(self._consume_stops(stop_handler))

    async def _consume_starts(self, handler):
        while self._running:
            try:
                async for msg in self.start_consumer:
                    if not self._running:
                        break

                    data = json.loads(msg.value)

                    if data.get("type") == "start" and "scenario_id" in data and "video_path" in data:
                        scenario_id = UUID(data["scenario_id"])
                        try:
                            await handler(scenario_id, data["video_path"])
                            await self.start_consumer.commit()
                        except Exception as e:
                            logger.error(f"Failed to start scenario: {str(e)}")
                    else:
                        logger.warning("[Runner] Invalid start message format")
            except Exception as e:
                logger.error(f"[Runner] Start command processing failed: {str(e)}")
                await asyncio.sleep(1)

    async def _consume_stops(self, handler):
        while self._running:
            try:
                msg = await self.stop_consumer.getone()
                data = json.loads(msg.value)
                if data.get("type") == "stop":
                    await handler(UUID(data["scenario_id"]))
            except Exception as e:
                logger.error(f"[Runner] Stop command processing failed: {str(e)}")
                await asyncio.sleep(1)

    async def stop(self):
        self._running = False
        await self.start_consumer.stop()
        await self.stop_consumer.stop()
