import json
import logging
from confluent_kafka import Producer
from datetime import datetime
from uuid import UUID


class HeartbeatSender:
    def __init__(self, bootstrap_servers: str, topic: str = 'heartbeats'):
        self.producer = Producer({'bootstrap.servers': bootstrap_servers})
        self.topic = topic

    def send_heartbeat(self, scenario_id: UUID):
        try:
            message = {
                "scenario_id": str(scenario_id),
                "timestamp": datetime.utcnow().isoformat()
            }
            self.producer.produce(self.topic, json.dumps(message).encode('utf-8'))
            self.producer.flush()
            self._logger().debug(f"Heartbeat sent for scenario {scenario_id}")
        except Exception as e:
            self._logger().error(f"Failed to send heartbeat: {e}")

    def _logger(self):
        return logging.getLogger(__name__)
