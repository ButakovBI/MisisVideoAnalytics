import uuid
from datetime import datetime

from misis_orchestrator.models.scenario_state import ScenarioState


class Scenario:
    def __init__(self, video_path: str):
        self.id = uuid.uuid4()
        self.video_path = video_path
        self.state = ScenarioState.INIT_STARTUP
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
