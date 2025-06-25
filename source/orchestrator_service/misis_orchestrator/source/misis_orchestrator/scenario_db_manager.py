from uuid import UUID

from sqlalchemy import insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from misis_orchestrator.database.tables.outbox import Outbox
from misis_orchestrator.database.tables.scenario import Scenario
from misis_orchestrator.models.constants.scenario_status import ScenarioStatus


class ScenarioDBManager:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_outbox_event(self, scenario_id: UUID, event_type: str, payload: dict):
        await self.session.execute(
            insert(Outbox).values(
                scenario_id=scenario_id,
                event_type=event_type,
                payload=payload,
                processed=False,
            )
        )

    async def get_video_path(self, scenario_id: UUID) -> str:
        res = await self.session.execute(
            select(Scenario.video_path)
            .where(Scenario.id == scenario_id)
        )
        return res.scalar_one()

    async def mark_outbox_processed(self, outbox_id: UUID):
        await self.session.execute(
            update(Outbox)
            .where(Outbox.id == outbox_id)
            .values(processed=True)
        )

    async def update_status(self, scenario_id: UUID, status: ScenarioStatus):
        await self.session.execute(
            update(Scenario)
            .where(Scenario.id == scenario_id)
            .values(status=status)
        )
