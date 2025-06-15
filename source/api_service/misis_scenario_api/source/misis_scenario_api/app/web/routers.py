from fastapi import APIRouter, Depends
from uuid import UUID

from misis_scenario_api.app.command_handler import ScenarioCommandHandler
from misis_scenario_api.app.query_handler import ScenarioQueryHandler
from misis_scenario_api.kafka.kafka_producer import get_kafka_producer
from misis_scenario_api.models.predictions_response import PredictionsResponse
from misis_scenario_api.models.scenario_status_response import ScenarioStatusResponse
from misis_scenario_api.models.scenario_create_request import ScenarioCreateRequest
from misis_scenario_api.models.scenario_update_request import ScenarioUpdateRequest
from misis_scenario_api.orchestrator_client import get_orchestrator_client

router = APIRouter()


def get_command_handler() -> ScenarioCommandHandler:
    return ScenarioCommandHandler(get_kafka_producer())


def get_query_handler() -> ScenarioQueryHandler:
    return ScenarioQueryHandler(get_orchestrator_client())


@router.post("/scenario/", response_model=ScenarioStatusResponse, status_code=201)
async def create_scenario(
    request: ScenarioCreateRequest,
    handler: ScenarioCommandHandler = Depends(get_command_handler)
):
    scenario_id = handler.create_scenario(request)
    return {"status": "init_startup", "scenario_id": scenario_id}


@router.post("/scenario/{scenario_id}/", status_code=202)
async def update_scenario(
    scenario_id: str,
    request: ScenarioUpdateRequest,
    handler: ScenarioCommandHandler = Depends(get_command_handler)
):
    handler.update_scenario(scenario_id, request)
    return {"status": "command_accepted"}


@router.get("/scenario/{scenario_id}/", response_model=ScenarioStatusResponse)
async def get_scenario_status(
    scenario_id: UUID,
    handler: ScenarioQueryHandler = Depends(get_query_handler)
):
    return handler.get_status(scenario_id)


@router.get("/prediction/{scenario_id}/", response_model=PredictionsResponse)
async def get_predictions(
    scenario_id: UUID,
    handler: ScenarioQueryHandler = Depends(get_query_handler)
):
    return handler.get_predictions(scenario_id)
