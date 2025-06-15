import os
import httpx
import logging
from uuid import UUID

from misis_scenario_api.models.predictions_response import PredictionsResponse
from misis_scenario_api.models.scenario_status_response import ScenarioStatusResponse


class OrchestratorClient:
    def __init__(self, base_url: str):
        self.base_url = base_url

    def get_scenario_status(self, scenario_id: UUID) -> ScenarioStatusResponse:
        try:
            with httpx.Client() as client:
                response = client.get(f"{self.base_url}/scenario/{scenario_id}")
                response.raise_for_status()
                return ScenarioStatusResponse(**response.json())
        except httpx.RequestError as e:
            self._logger().error(f"Request to orchestrator failed: {e}")
            raise

    def get_predictions(self, scenario_id: UUID) -> PredictionsResponse:
        try:
            with httpx.Client() as client:
                response = client.get(f"{self.base_url}/prediction/{scenario_id}")
                response.raise_for_status()
                return PredictionsResponse(**response.json())
        except httpx.RequestError as e:
            self._logger().error(f"Request to orchestrator failed: {e}")
            raise

    def _logger(self):
        return logging.getLogger(__name__)


def get_orchestrator_client() -> OrchestratorClient:
    base_url = os.getenv("ORCHESTRATOR_URL", "http://orchestrator:8000")
    return OrchestratorClient(base_url)
