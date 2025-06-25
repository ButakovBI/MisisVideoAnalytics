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
        self._is_running = False
        self.start_consumer = AIOKafkaConsumer(
            KafkaTopic.RUNNER_COMMANDS,
            bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
            group_id="runners_group",
            enable_auto_commit=False
        )
        self.stop_consumer = AIOKafkaConsumer(
            KafkaTopic.RUNNER_COMMANDS,
            bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS
        )

    async def start(self, start_handler, stop_handler):
        self._is_running = True
        await self.start_consumer.start()
        await self.stop_consumer.start()

        asyncio.create_task(self._consume_starts(start_handler))
        asyncio.create_task(self._consume_stops(stop_handler))

    async def _consume_starts(self, handler):
        async for msg in self.start_consumer:
            if not self._is_running:
                break
            try:
                data = json.loads(msg.value)
                if data.get("type") == "start":
                    if not all(k in data for k in ["scenario_id", "video_path"]):
                        raise ValueError("Invalud message format")
                    await handler(UUID(data["scenario_id"]), data["video_path"])
                    await self.start_consumer.commit()
            except json.JSONDecodeError:
                logger.error("[Runner] Consumer: invalid message format")
            except Exception as e:
                logger.error(f"[Runner] Consumer: start command processing failed: {str(e)}")

    async def _consume_stops(self, handler):
        async for msg in self.stop_consumer:
            if not self._is_running:
                break
            data = json.loads(msg.value)
            if data.get("type") == "stop":
                await handler(data["scenario_id"])

    async def stop(self):
        self._is_running = False
        await self.start_consumer.stop()
        await self.stop_consumer.stop()
