import asyncio
import json

from aiokafka import AIOKafkaConsumer

from misis_runner.kafka.producer import settings
from misis_runner.models.constants.kafka_topic import KafkaTopic


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
            data = json.loads(msg.value)
            if data.get("type") == "start":
                await handler(data["scenario_id"], data["video_path"])
                await self.start_consumer.commit()

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
