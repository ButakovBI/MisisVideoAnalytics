import asyncio
import logging
from datetime import datetime, timedelta
from uuid import UUID

from sqlalchemy import delete, func, insert, select

from misis_orchestrator.app.config import settings
from misis_orchestrator.database.tables.heartbeat import HeartbeatModel
from misis_orchestrator.database.tables.scenario import Scenario
from misis_orchestrator.models.constants.scenario_status import ScenarioStatus
from misis_orchestrator.orchestrator_service import OrchestratorService

logger = logging.getLogger(__name__)


class Watchdog:
    def __init__(self, session_factory, orchestrator: OrchestratorService):
        self.session_factory = session_factory
        self.orchestrator = orchestrator
        self.running = True

    async def update_heartbeat(self, scenario_id: UUID, last_frame: int):
        async with self.session_factory() as session:
            async with session.begin():
                await session.execute(
                    insert(HeartbeatModel)
                    .values(scenario_id=scenario_id,
                            last_timestamp=func.now(),
                            last_frame=last_frame)
                    .on_conflict_do_update(
                        index_elements=['scenario_id'],
                        set_={'last_timestamp': func.now(),
                              'last_frame': last_frame}
                    )
                )

    async def check_timeouts(self):
        while self.running:
            try:
                async with self.session_factory() as session:
                    async with session.begin():
                        timeout = timedelta(seconds=settings.HEARTBEAT_TIMEOUT)
                        t = datetime.utcnow() - timeout

                        result = await session.execute(
                            select(HeartbeatModel.scenario_id)
                            .where(HeartbeatModel.last_timestamp < t)
                        )
                        timed_out = result.scalars().all()

                        for scenario_id in timed_out:
                            logger.warning(f"[Watchdog] Heartbeat timeout for {scenario_id}, restarting")
                            try:
                                current_status = await self.get_scenario_status(scenario_id)
                                if current_status != ScenarioStatus.ACTIVE:
                                    logger.debug(
                                        f"[Watchdog] Skipping restart for {scenario_id}, status: {current_status}"
                                    )
                                    continue

                                await self.orchestrator.restart_scenario(scenario_id)

                                await session.execute(
                                    delete(HeartbeatModel)
                                    .where(HeartbeatModel.scenario_id == scenario_id)
                                )
                            except Exception as e:
                                logger.error(f"[Watchdog] Failed to restart scenario: {str(e)}")
                await asyncio.sleep(settings.HEARTBEAT_CHECK_INTERVAL)
            except Exception as e:
                logger.error(f"[Watchdog] Watchdog error: {str(e)}")
                await asyncio.sleep(5)

    async def get_scenario_status(self, scenario_id: UUID) -> str:
        async with self.session_factory() as session:
            result = await session.execute(
                select(Scenario.status)
                .where(Scenario.id == scenario_id)
            )
            return result.scalar_one_or_none()
