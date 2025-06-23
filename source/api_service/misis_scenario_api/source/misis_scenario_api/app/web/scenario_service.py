
from uuid import uuid4
from fastapi import UploadFile
from sqlalchemy import insert
from sqlalchemy.ext.asyncio import AsyncSession

from misis_scenario_api.models.constants.kafka_topics import KafkaTopics
from misis_scenario_api.database.tables.outbox import Outbox
from misis_scenario_api.models.constants.scenario_status import ScenarioStatus
from misis_scenario_api.s3.s3_client import S3Client
from misis_scenario_api.models.scenario_status_response import ScenarioStatusResponse
from misis_scenario_api.database.tables.scenario import Scenario
from misis_scenario_api.kafka.producer import Producer


class ScenarioService:
    def __init__(self, db: AsyncSession, producer: Producer, s3_client: S3Client):
        self.db = db
        self.producer = producer
        self.s3_client = s3_client

    async def create_scenario(self, video: UploadFile) -> ScenarioStatusResponse:
        scenario_id = uuid4()
        s3_video_path = f"scenarios/{scenario_id}/{video.filename}"
        await self.s3_client.upload_video(
            bucket="videos",
            s3_link=s3_video_path,
            video_bytes=await video.read(),
        )

        async with self.db.begin():
            await self.db.execute(
                insert(Scenario).values(
                    id=scenario_id,
                    status=ScenarioStatus.INIT_STARTUP,
                    video_path=s3_video_path
                )
            )

            await self.db.execute(
                insert(Outbox).values(
                    id=uuid4(),
                    scenario_id=scenario_id,
                    event_type=ScenarioStatus.INIT_STARTUP,
                    payload={"video_path": s3_video_path}
                )
            )

        await self.producer.send(
            KafkaTopics.SCENARIO_EVENTS.value,
            {
                "event_type": ScenarioStatus.INIT_STARTUP,
                "scenario_id": str(scenario_id),
                "video_path": s3_video_path
            }
        )

        return ScenarioStatusResponse(
            scenario_id=scenario_id,
            status=ScenarioStatus.INIT_STARTUP
        )
