from fastapi import APIRouter, Depends, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from misis_scenario_api.app.web.scenario_service import ScenarioService
from misis_scenario_api.database.database import get_db_session
from misis_scenario_api.s3.s3_client import S3Client
from misis_scenario_api.kafka.producer import Producer
from misis_scenario_api.models.scenario_status_response import ScenarioStatusResponse

router = APIRouter()


@router.post(
    "/scenario/",
    response_model=ScenarioStatusResponse,
    status_code=status.HTTP_202_ACCEPTED
)
async def create_scenario(
    video: UploadFile,
    db: AsyncSession = Depends(get_db_session),
    producer: Producer = Depends(),
    s3_client: S3Client = Depends()
):
    try:
        service = ScenarioService(db=db, producer=producer, s3_client=s3_client)
        res = await service.create_scenario(video=video)
        return res
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error: {e}. Try to restart scenario"
        )


# @router.post(
#     "/scenario/{scenario_id}/",
#     response_model=ScenarioStatusResponse,
#     status_code=status.HTTP_202_ACCEPTED
# )
# async def update_scenario(
#     scenario_id: UUID,
#     request: ScenarioUpdateRequest,
#     handler: ScenarioCommandHandler = Depends(get_command_handler)
# ):
#     try:
#         status = handler.update_scenario(scenario_id, request.command)
#         return status
#     except ValueError as e:
#         raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=str(e))


# @router.get(
#     "/scenario/{scenario_id}/",
#     response_model=ScenarioStatusResponse
# )
# async def get_scenario_status(
#     scenario_id: UUID,
#     handler: ScenarioQueryHandler = Depends(get_query_handler)
# ):
#     return await handler.get_status(scenario_id)


# @router.get(
#     "/prediction/{scenario_id}/",
#     response_model=PredictionsResponse
# )
# async def get_predictions(
#     scenario_id: UUID,
#     handler: ScenarioQueryHandler = Depends(get_query_handler)
# ):
#     return await handler.get_predictions(scenario_id)
