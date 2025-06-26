import logging
from uuid import UUID, uuid4

from fastapi import HTTPException, UploadFile, status
from misis_scenario_api.app.config import settings
from misis_scenario_api.database.tables.outbox import Outbox
from misis_scenario_api.database.tables.scenario import Scenario
from misis_scenario_api.kafka.producer import Producer
from misis_scenario_api.models.bounding_box import BoundingBox
from misis_scenario_api.models.constants.command_type import CommandType
from misis_scenario_api.models.constants.scenario_status import ScenarioStatus
from misis_scenario_api.models.prediction_response import PredictionResponse
from misis_scenario_api.models.scenario_status_response import \
    ScenarioStatusResponse
from misis_scenario_api.s3.s3_client import S3Client
from sqlalchemy import insert, select, update
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)


class ScenarioService:
    def __init__(self, db: AsyncSession | None, producer: Producer | None, s3_client: S3Client | None):
        self.db = db
        self.producer = producer
        self.s3_client = s3_client

    async def create_scenario(self, video: UploadFile) -> ScenarioStatusResponse:
        logger.info("[Create] Create scenario for video %s", {video.filename})
        scenario_id = uuid4()
        s3_video_path = f"scenarios/{scenario_id}/{video.filename}"
        await self.s3_client.upload_video(
            bucket=settings.S3_VIDEOS_BUCKET,
            s3_link=s3_video_path,
            video_bytes=await video.read(),
        )
        logger.debug("[Create] Video uploaded to s3: %s", s3_video_path)

        async with self.db.begin() as transaction:
            logger.debug("[Create] Inserting scenario %s", scenario_id)
            await self.db.execute(
                insert(Scenario).values(
                    id=scenario_id,
                    status=ScenarioStatus.INIT_STARTUP,
                    video_path=s3_video_path
                )
            )
            logger.debug("[Create] Inserting scenario %s to outbox", scenario_id)

            await self.db.execute(
                insert(Outbox).values(
                    id=uuid4(),
                    scenario_id=scenario_id,
                    event_type=ScenarioStatus.INIT_STARTUP,
                    payload={"video_path": s3_video_path}
                )
            )

            await transaction.commit()
            logger.info("[Create] Transaction committed for %s", scenario_id)

        return ScenarioStatusResponse(
            scenario_id=scenario_id,
            status=ScenarioStatus.INIT_STARTUP
        )

    async def update_scenario(self, scenario_id: UUID, command: CommandType) -> ScenarioStatusResponse:
        logger.info("[Update] Update scenario %s with command %s", scenario_id, command.value)

        try:
            async with self.db.begin() as transaction:
                scenario = await self.db.execute(
                    select(Scenario).where(Scenario.id == scenario_id)
                )
                scenario = scenario.scalar_one_or_none()

                if not scenario:
                    logger.error("[Update] Scenario %s not found", scenario_id)
                    raise NoResultFound("[Update] Scenario not found")

                current_status = scenario.status
                new_status = None
                event_type = None
                payload = {}

                if command == CommandType.START:
                    if current_status in [
                        ScenarioStatus.INIT_STARTUP,
                        ScenarioStatus.IN_STARTUP_PROCESSING,
                        ScenarioStatus.ACTIVE
                    ]:
                        logger.info("[Update] Scenario %s already started or starting", scenario_id)
                        return ScenarioStatusResponse(
                            scenario_id=scenario_id,
                            status=current_status
                        )
                    elif current_status in [
                        ScenarioStatus.IN_SHUTDOWN_PROCESSING,
                        ScenarioStatus.INIT_SHUTDOWN
                    ]:
                        raise ValueError("[Update] Cannot start while shutting down")
                    elif current_status in [ScenarioStatus.INACTIVE]:
                        new_status = ScenarioStatus.INIT_STARTUP
                        event_type = ScenarioStatus.INIT_STARTUP
                        payload = {"video_path": scenario.video_path}

                elif command == CommandType.STOP:
                    if current_status in [
                        ScenarioStatus.INIT_SHUTDOWN,
                        ScenarioStatus.IN_SHUTDOWN_PROCESSING,
                        ScenarioStatus.INACTIVE
                    ]:
                        logger.info("[Update] Scenario %s already stopped or stopping", scenario_id)
                        return ScenarioStatusResponse(
                            scenario_id=scenario_id,
                            status=current_status
                        )
                    elif current_status in [
                        ScenarioStatus.INIT_STARTUP,
                        ScenarioStatus.IN_STARTUP_PROCESSING,
                        ScenarioStatus.ACTIVE
                    ]:
                        new_status = ScenarioStatus.INIT_SHUTDOWN
                        event_type = ScenarioStatus.INIT_SHUTDOWN

                if new_status is None:
                    raise ValueError(f"Invalid command '{command}' for current status '{current_status}'")

                await self.db.execute(
                    update(Scenario)
                    .where(Scenario.id == scenario_id)
                    .values(status=new_status)
                )

                outbox_id = uuid4()
                await self.db.execute(
                    insert(Outbox).values(
                        id=outbox_id,
                        scenario_id=scenario_id,
                        event_type=event_type,
                        payload=payload
                    )
                )

                await transaction.commit()
                logger.info("[Update] Scenario %s status updated to %s", scenario_id, new_status)

            return ScenarioStatusResponse(
                scenario_id=scenario_id,
                status=new_status
            )

        except NoResultFound as e:
            logger.warning("[Update] Scenario not found: %s", scenario_id)
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        except ValueError as e:
            logger.warning("[Update] Invalid operation: %s", str(e))
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    async def get_scenario_status(self, scenario_id: UUID) -> ScenarioStatusResponse:
        logger.info("[Status] Getting status for scenario %s", scenario_id)

        try:
            result = await self.db.execute(
                select(Scenario)
                .where(Scenario.id == scenario_id)
            )
            scenario = result.scalar_one_or_none()

            if not scenario:
                logger.warning("[Status] Scenario not found: %s", scenario_id)
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Scenario not found"
                )

            logger.debug("[Status] get status for %s: %s", scenario_id, scenario.status)
            return ScenarioStatusResponse(
                scenario_id=scenario_id,
                status=scenario.status
            )

        except Exception as e:
            logger.error("[Status] Failed to get status for %s: %s", scenario_id, str(e))
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get scenario status: {str(e)}"
            )

    async def get_predictions(self, scenario_id: UUID) -> list[PredictionResponse]:
        logger.info("[Prediction] Getting predictions for scenario %s", scenario_id)

        try:
            scenario_exists = await self.db.execute(
                select(Scenario.id)
                .where(Scenario.id == scenario_id)
            )
            if not scenario_exists.scalar_one_or_none():
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Scenario not found"
                )

            predictions = await self.s3_client.get_predictions(scenario_id=scenario_id)

            logger.debug(f"[Prediction] Found {len(predictions)} predictions for {scenario_id}")
            return [
                PredictionResponse(
                    scenario_id=scenario_id,
                    predictions=[
                        BoundingBox(**box) for box in pred["predictions"]
                    ]
                )
                for pred in predictions
            ]

        except HTTPException:
            raise
        except Exception as e:
            logger.error("[Prediction] Failed to get predictions for %s: %s", scenario_id, str(e))
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get predictions: {str(e)}"
            )
