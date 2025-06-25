import asyncio
from datetime import datetime, timedelta
from uuid import UUID

from sqlalchemy import delete, func, insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from misis_orchestrator.app.config import settings
from misis_orchestrator.database.tables.heartbeat import HeartbeatModel


class Watchdog:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def update_heartbeat(self, scenario_id: UUID):
        async with self.db_session.begin():
            await self.db_session.execute(
                insert(HeartbeatModel)
                .values(scenario_id=scenario_id, last_timestamp=func.now())
                .on_conflict_do_update(
                    index_elements=['scenario_id'],
                    set_={'last_timestamp': func.now()}
                )
            )

    async def check_timeouts(self):
        while True:
            timeout = timedelta(seconds=settings.HEARTBEAT_TIMEOUT)
            t = datetime.utcnow() - timeout

            result = await self.db_session.execute(
                select(HeartbeatModel.scenario_id)
                .where(HeartbeatModel.last_timestamp < t)
            )
            timed_out = result.scalars().all()

            for scenario_id in timed_out:
                yield scenario_id
                await self.db_session.execute(
                    delete(HeartbeatModel)
                    .where(HeartbeatModel.scenario_id == scenario_id)
                )

            await asyncio.sleep(settings.HEARTBEAT_CHECK_INTERVAL)
