import json
import logging
import time
from uuid import UUID

from aiokafka import AIOKafkaProducer

from misis_runner.app.config import settings
from misis_runner.models.constants.kafka_topic import KafkaTopic

logger = logging.getLogger(__name__)


class Producer:
    def __init__(self):
        self.producer = AIOKafkaProducer(
            bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
            value_serializer=lambda v: json.dumps(v).encode()
        )
        self.started = False

    async def start(self):
        if not self.started:
            await self.producer.start()
            self.started = True

    async def send_heartbeat(self, scenario_id: UUID, last_frame):
        try:
            if not self.started:
                await self.start()

            await self.producer.send(
                KafkaTopic.HEARTBEATS,
                value={
                    "scenario_id": str(scenario_id),
                    "runner_id": settings.RUNNER_ID,
                    "last_frame": last_frame,
                    "timestamp": int(time.time())
                }
            )
        except Exception as e:
            logger.error(f"[Runner] Heartbeat send failed: {str(e)}")
