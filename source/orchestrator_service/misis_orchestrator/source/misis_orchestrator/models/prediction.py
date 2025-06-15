import uuid
from datetime import datetime


class Prediction:
    def __init__(self, scenario_id: uuid.UUID, frame_number: int, boxes: list):
        self.scenario_id = scenario_id
        self.frame_number = frame_number
        self.boxes = boxes
        self.created_at = datetime.utcnow()
