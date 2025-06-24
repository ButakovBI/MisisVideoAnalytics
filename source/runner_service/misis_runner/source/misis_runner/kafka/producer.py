import json
import time
from uuid import UUID

from aiokafka import AIOKafkaProducer

from misis_runner.app.config import settings
from misis_runner.models.constants.kafka_topic import KafkaTopic


class Producer:
    def __init__(self):
        self.producer = AIOKafkaProducer(
            bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
            value_serializer=lambda v: json.dumps(v).encode()
        )

    async def send_heartbeat(self, scenario_id: UUID, last_frame):
        await self.producer.send(
            KafkaTopic.HEARTBEATS,
            value={
                "scenario_id": str(scenario_id),
                "runner_id": settings.RUNNER_ID,
                "last_frame": last_frame,
                "timestamp": int(time.time())
            }
        )
