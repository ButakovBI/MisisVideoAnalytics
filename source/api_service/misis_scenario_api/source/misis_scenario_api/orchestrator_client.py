import os
import httpx
from uuid import UUID

from misis_scenario_api.models.predictions_response import PredictionsResponse
from misis_scenario_api.models.scenario_status_response import ScenarioStatusResponse


class OrchestratorClient:
    def __init__(self, base_url: str):
        self._base_url = base_url
        self._client = httpx.AsyncClient(base_url=base_url, timeout=5)

    async def get_scenario_status(self, scenario_id: UUID) -> ScenarioStatusResponse:
        resp = await self._client.get(f"/scenario/{scenario_id}")
        resp.raise_for_status()
        data = resp.json()
        return ScenarioStatusResponse(**data)

    async def get_predictions(self, scenario_id: UUID) -> PredictionsResponse:
        resp = await self._client.get(f"/prediction/{scenario_id}")
        resp.raise_for_status()
        data = resp.json()
        return PredictionsResponse(**data)

    async def close(self):
        await self._client.aclose()


def get_orchestrator_client() -> OrchestratorClient:
    url = os.getenv("ORCHESTRATOR_URL", "http://orchestrator:8001")
    return OrchestratorClient(url)
