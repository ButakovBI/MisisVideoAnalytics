import json
import os
from confluent_kafka import Producer
import logging


class KafkaProducer:
    def __init__(self, bootstrap_servers: str):
        self.producer = Producer({'bootstrap.servers': bootstrap_servers})

    def send_scenario_command(self, command: dict):
        try:
            self.producer.produce(
                'scenario_commands',
                json.dumps(command).encode('utf-8')
            )
            self.producer.flush()
            self._logger().info(f"Sent scenario command: {command}")
        except Exception as e:
            self._logger().error(f"Failed to send Kafka message: {e}")
            raise

    def _logger(self):
        return logging.getLogger(__name__)


def get_kafka_producer() -> KafkaProducer:
    bootstrap_servers = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")
    return KafkaProducer(bootstrap_servers)
