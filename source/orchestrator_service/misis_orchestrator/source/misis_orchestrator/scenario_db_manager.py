from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import update, insert
from uuid import UUID

from misis_orchestrator.database.tables.scenario import Scenario
from misis_orchestrator.database.tables.outbox import Outbox
from misis_orchestrator.models.constants.scenario_status import ScenarioStatus


class ScenarioDBManager:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def update_status(self, scenario_id: UUID, status: ScenarioStatus):
        await self.session.execute(
            update(Scenario)
            .where(Scenario.id == scenario_id)
            .values(status=status)
        )

    async def create_outbox_event(self, scenario_id: UUID, event_type: str, payload: dict):
        await self.session.execute(
            insert(Outbox).values(
                scenario_id=scenario_id,
                event_type=event_type,
                payload=payload,
            )
        )

    async def mark_outbox_processed(self, outbox_id: UUID):
        await self.session.execute(
            update(Outbox)
            .where(Outbox.id == outbox_id)
            .values(processed=True)
        )
