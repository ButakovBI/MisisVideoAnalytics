from datetime import datetime
import json
from uuid import UUID

from aiokafka import AIOKafkaConsumer

from misis_orchestrator.models.heartbeat import Heartbeat
from misis_orchestrator.models.constants.command_type import CommandType
from misis_orchestrator.models.scenario_command import ScenarioCommand
from misis_orchestrator.models.constants.kafka_topic import KafkaTopic
from misis_orchestrator.app.config import settings


class Consumer:
    def __init__(self, producer):
        self.producer = producer
        self.commands_consumer = AIOKafkaConsumer(
            KafkaTopic.SCENARIO_EVENTS,
            bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
            group_id="orchestrator_group",
            value_deserializer=lambda v: json.loads(v.decode('utf-8')),
        )
        self.heartbeats_consumer = AIOKafkaConsumer(
            KafkaTopic.HEARTBEATS,
            bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
            value_deserializer=lambda v: json.loads(v.decode())
        )

    async def start(self):
        await self.commands_consumer.start()
        await self.heartbeats_consumer.start()

    async def consume_commands(self):
        async for msg in self.commands_consumer:
            data = msg.value
            event_type = data.get("event_type")
            if event_type == "init_startup":
                yield ScenarioCommand(
                    scenario_id=UUID(data["scenario_id"]),
                    type=CommandType.START,
                    video_path=data.get("video_path"),
                )
            elif event_type == "init_shutdown":
                yield ScenarioCommand(
                    scenario_id=UUID(data["scenario_id"]),
                    type=CommandType.STOP,
                    video_path=data.get("video_path"),
                )

    async def consume_heartbeats(self):
        async for msg in self.commands_consumer:
            data = msg.value
            yield Heartbeat(
                scenario_id=UUID(data["scenario_id"]),
                runner_id=data["runner_id"],
                last_frame=data["last_frame"],
                timestamp=datetime.fromtimestamp(data["timestamp"])
            )

    async def stop(self):
        await self.commands_consumer.stop()
        await self.heartbeats_consumer.stop()
