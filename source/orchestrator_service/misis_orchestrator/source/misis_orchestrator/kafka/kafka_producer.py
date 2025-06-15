import json
import logging
from confluent_kafka import Producer


class KafkaProducer:
    def __init__(self, bootstrap_servers: str):
        self.producer = Producer({'bootstrap.servers': bootstrap_servers})

    def send_scenario_event(self, event: dict):
        try:
            self.producer.produce(
                'scenario_events',
                json.dumps(event).encode('utf-8')
            )
            self.producer.flush()
            self._logger().info(f"Sent scenario event: {event}")
        except Exception as e:
            self._logger().error(f"Failed to send Kafka message: {e}")
            raise

    def _logger(self):
        return logging.getLogger(__name__)
