import logging
from datetime import datetime
from uuid import UUID

from misis_orchestrator.models.scenario_state import ScenarioState
from misis_orchestrator.models.scenario import Scenario
from misis_orchestrator.app.state_machine import StateMachine
from misis_orchestrator.database.database import Database


class CommandHandler:
    def __init__(self, db: Database):
        self.db = db

    def complete_scenario(self, scenario_id: UUID):
        self.transition_state(scenario_id, ScenarioState.INACTIVE)
        self._logger().info(f"Scenario {scenario_id} is completed")

    def create_scenario(self, video_path: str) -> UUID:
        scenario = Scenario(video_path)
        self.db.save_scenario(scenario)
        self.transition_state(scenario.id, ScenarioState.IN_STARTUP_PROCESSING)
        self._logger().info(f"Scenario {scenario.id} is created")
        return scenario.id

    def start_scenario(self, scenario_id: UUID):
        self.transition_state(scenario_id, ScenarioState.IN_STARTUP_PROCESSING)
        self._logger().info(f"Scenario {scenario_id} is started")

    def stop_scenario(self, scenario_id: UUID):
        self.transition_state(scenario_id, ScenarioState.INIT_SHUTDOWN)
        self._logger().info(f"Scenario {scenario_id} is stopped")

    def transition_state(self, scenario_id: UUID, new_state: ScenarioState):
        scenario = self.db.get_scenario(scenario_id)
        if not scenario:
            self._logger().error(f"Scenario {scenario_id} not found")
            return

        if StateMachine.can_transition(scenario.state, new_state):
            old_state = scenario.state
            scenario.state = new_state
            scenario.updated_at = datetime.utcnow()
            self.db.save_scenario(scenario)
            self._logger().info(f"Scenario {scenario_id} transition: {old_state} -> {new_state}")
            return True
        else:
            self._logger().warning(f"Invalid transition: {scenario.state} -> {new_state}")
            return False

    def _logger(self):
        return logging.getLogger(__name__)
