import json
import logging
from confluent_kafka import Producer

from misis_healthcheck.heartbeat.heartbeat_sender import HeartbeatSender


class KafkaService:
    def __init__(self, bootstrap_servers: str):
        self.producer = Producer({'bootstrap.servers': bootstrap_servers})
        self.heartbeat_sender = HeartbeatSender(bootstrap_servers)

    def publish_complete(self, scenario_id):
        message = {
            "scenario_id": str(scenario_id),
            "command": "complete"
        }
        self._publish('scenario_commands', message)

    def publish_heartbeat(self, scenario_id):
        self.heartbeat_sender.send_heartbeat(scenario_id)

    def publish_prediction(self, scenario_id, frame_number, boxes):
        message = {
            "scenario_id": str(scenario_id),
            "frame_number": frame_number,
            "boxes": boxes
        }
        self._publish('predictions', message)

    def _publish(self, topic, message):
        try:
            self.producer.produce(topic, json.dumps(message).encode('utf-8'))
            self.producer.flush()
            self._logger().debug(f"Published to {topic}: {message}")
        except Exception as e:
            self._logger().error(f"Failed to publish to {topic}: {e}")

    def _logger(self):
        return logging.getLogger(__name__)
