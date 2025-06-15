from misis_healthcheck.abstract_storage import HeartbeatStorage
from misis_orchestrator.database.database import Database
from misis_orchestrator.models.scenario_state import ScenarioState


class DatabaseHealthStorage(HeartbeatStorage):
    def __init__(self, db: Database):
        self.db = db

    def update_heartbeat(self, scenario_id, timestamp):
        self.db.save_heartbeat(scenario_id, timestamp)

    def get_last_heartbeat(self, scenario_id):
        return self.db.get_heartbeat(scenario_id)

    def get_active_scenarios(self):
        active_states = [
            ScenarioState.IN_STARTUP_PROCESSING,
            ScenarioState.ACTIVE,
            ScenarioState.IN_SHUTDOWN_PROCESSING
        ]
        return self.db.get_active_scenarios(active_states)
