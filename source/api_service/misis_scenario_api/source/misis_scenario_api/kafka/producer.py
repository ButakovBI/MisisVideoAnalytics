import json

from aiokafka import AIOKafkaProducer
from misis_scenario_api.app.config import settings


class Producer:
    def __init__(self):
        self.producer = AIOKafkaProducer(
            bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            acks='all'
        )

    async def send(self, topic: str, value: dict):
        await self.producer.send_and_wait(topic, value=value)
