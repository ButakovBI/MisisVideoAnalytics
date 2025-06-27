import asyncio
import json
import logging
from uuid import UUID

from aiokafka import AIOKafkaConsumer, ConsumerStoppedError

from misis_orchestrator.app.config import settings
from misis_orchestrator.models.constants.command_type import CommandType
from misis_orchestrator.models.constants.kafka_topic import KafkaTopic
from misis_orchestrator.models.constants.scenario_status import ScenarioStatus
from misis_orchestrator.models.heartbeat import Heartbeat
from misis_orchestrator.models.scenario_command import ScenarioCommand

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class Consumer:
    def __init__(self):
        self.running = True
        self.commands_consumer = AIOKafkaConsumer(
            KafkaTopic.SCENARIO_EVENTS.value,
            bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
            group_id="orchestrator_group",
            value_deserializer=lambda v: json.loads(v.decode('utf-8')),
        )
        self.heartbeats_consumer = AIOKafkaConsumer(
            KafkaTopic.HEARTBEATS.value,
            bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
            value_deserializer=lambda v: json.loads(v.decode())
        )

    async def start(self):
        await self.commands_consumer.start()
        await self.heartbeats_consumer.start()

    async def consume_commands(self):
        while self.running:
            try:
                msg = await self.commands_consumer.getone()
                if msg:
                    logger.info("[Orchestrator] Consumer get msg")
                    data = msg.value
                    event_type = data.get("event_type")
                    if event_type in [ScenarioStatus.INIT_STARTUP.value, ScenarioStatus.INIT_SHUTDOWN.value]:
                        payload = data.get("payload", {})
                        yield ScenarioCommand(
                            scenario_id=UUID(data["scenario_id"]),
                            type=CommandType.START.value if event_type == ScenarioStatus.INIT_STARTUP.value else CommandType.STOP.value,
                            video_path=data.get("payload", {}).get("video_path"),
                            resume_from_frame=payload.get("resume_from_frame", 0)
                        )
            except ConsumerStoppedError:
                break
            except Exception as e:
                logger.error(f"[Orchestrator] Command consumer error: {str(e)}")
                await asyncio.sleep(1)

    async def consume_heartbeats(self):
        while self.running:
            try:
                msg = await self.heartbeats_consumer.getone()
                if msg:
                    logger.info("[Orchestrator] Consumer get heartbeat")
                    data = msg.value
                    yield Heartbeat(
                        scenario_id=UUID(data["scenario_id"]),
                        runner_id=data["runner_id"],
                        last_frame=data["last_frame"],
                        timestamp=data["timestamp"]
                    )
            except ConsumerStoppedError:
                break
            except Exception as e:
                logger.error(f"[Orchestrator] Heartbeat consumer error: {str(e)}")
                await asyncio.sleep(1)

    async def stop(self):
        self.running = False
        await self.commands_consumer.stop()
        await self.heartbeats_consumer.stop()
