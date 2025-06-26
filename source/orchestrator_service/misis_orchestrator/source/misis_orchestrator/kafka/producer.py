import json

from aiokafka import AIOKafkaProducer

from misis_orchestrator.app.config import settings


class Producer:
    def __init__(self):
        self.producer = AIOKafkaProducer(
            bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            acks='all',
            enable_idempotence=True,
        )

    async def send(self, topic: str, value: dict):
        await self.producer.send(topic, value=value)

    async def start(self):
        await self.producer.start()

    async def stop(self):
        await self.producer.stop()
