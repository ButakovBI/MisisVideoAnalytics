from uuid import UUID

from misis_scenario_api.models.predictions_response import PredictionsResponse
from misis_scenario_api.models.scenario_status_response import ScenarioStatusResponse
from misis_scenario_api.orchestrator_client import OrchestratorClient


class ScenarioQueryHandler:
    def __init__(self, client: OrchestratorClient):
        self.client = client

    def get_status(self, scenario_id: UUID) -> ScenarioStatusResponse:
        return self.client.get_scenario_status(scenario_id)

    def get_predictions(self, scenario_id: UUID) -> PredictionsResponse:
        return self.client.get_predictions(scenario_id)
