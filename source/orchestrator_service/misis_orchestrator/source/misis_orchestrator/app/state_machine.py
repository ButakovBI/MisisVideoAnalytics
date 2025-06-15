from misis_orchestrator.models.scenario_state import ScenarioState


class StateMachine:
    VALID_TRANSITIONS = {
        ScenarioState.INIT_STARTUP: [ScenarioState.IN_STARTUP_PROCESSING],
        ScenarioState.IN_STARTUP_PROCESSING: [ScenarioState.ACTIVE, ScenarioState.INACTIVE],
        ScenarioState.ACTIVE: [ScenarioState.INIT_SHUTDOWN],
        ScenarioState.INIT_SHUTDOWN: [ScenarioState.IN_SHUTDOWN_PROCESSING],
        ScenarioState.IN_SHUTDOWN_PROCESSING: [ScenarioState.INACTIVE],
        ScenarioState.INACTIVE: [ScenarioState.INIT_STARTUP]
    }

    @classmethod
    def can_transition(cls, current_state: ScenarioState, new_state: ScenarioState) -> bool:
        return new_state in cls.VALID_TRANSITIONS.get(current_state, [])
