import logging
from datetime import datetime
from uuid import UUID
from misis_healthcheck.abstract_storage import HeartbeatStorage


class HeartbeatProcessor:
    def __init__(self, storage: HeartbeatStorage):
        self.storage = storage

    def process_heartbeat(self, scenario_id: UUID, timestamp: datetime):
        self.storage.update_heartbeat(scenario_id, timestamp)
        self._logger().debug(f"Heartbeat processed for scenario {scenario_id}")

    def _logger(self):
        return logging.getLogger(__name__)
