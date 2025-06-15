import logging
from datetime import datetime
from uuid import UUID

from misis_orchestrator.database.database import Database
from misis_orchestrator.models.prediction import Prediction


class EventHandler:
    def __init__(self, db: Database):
        self.db = db

    def handle_heartbeat(self, scenario_id: UUID, timestamp: datetime):
        self.db.save_heartbeat(scenario_id, timestamp)
        self._logger().debug(f"Heartbeat processed for scenario {scenario_id}")

    def handle_prediction(self, scenario_id: UUID, frame_number: int, boxes: list):
        prediction = Prediction(scenario_id, frame_number, boxes)
        self.db.save_prediction(prediction)
        self._logger().info(f"Prediction saved for scenario {scenario_id}, frame {frame_number}")

    def _logger(self):
        return logging.getLogger(__name__)
