import logging
from uuid import UUID

from sqlalchemy import func, insert, select, update
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from misis_orchestrator.database.tables.scenario import Scenario
from misis_orchestrator.database.tables.heartbeat import Heartbeat
from misis_orchestrator.models.constants.command_type import CommandType
from misis_orchestrator.models.constants.scenario_status import ScenarioStatus
from misis_orchestrator.models.scenario_command import ScenarioCommand
from misis_orchestrator.scenario_db_manager import ScenarioDBManager

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class OrchestratorService:
    def __init__(self, session_factory: AsyncSession):
        self.session_factory = session_factory
        self.scenario_manager = ScenarioDBManager(session_factory)

    async def process_command(self, command: ScenarioCommand):
        if command.type == CommandType.START.value:
            await self._process_start_command(command)
        elif command.type == CommandType.STOP.value:
            await self._process_stop_command(command)

    async def _process_start_command(self, command: ScenarioCommand):
        async for session in self.session_factory():
            try:
                async with session.begin():
                    current_status = await self.scenario_manager.get_status(command.scenario_id, session=session)
                    if current_status not in [ScenarioStatus.INIT_STARTUP.value, ScenarioStatus.INACTIVE.value]:
                        logger.info(f"[Orch] Ignore start for {command.scenario_id}, status: {current_status}")
                        return

                    await self.scenario_manager.update_status(
                        command.scenario_id,
                        ScenarioStatus.IN_STARTUP_PROCESSING,
                        session=session
                    )

                    await self.scenario_manager.create_outbox_event(
                        scenario_id=command.scenario_id,
                        event_type=ScenarioStatus.IN_STARTUP_PROCESSING.value,
                        payload={"video_path": command.video_path},
                        session=session,
                    )

                    await self.scenario_manager.create_heartbeat(
                        scenario_id=command.scenario_id,
                        last_frame=0,
                        session=session,
                    )
                    logger.info("[Orchestrator] Command start success")
            except Exception as e:
                logger.error(f"[Orchestrator] Error start command: {e}")
                raise

    async def _process_stop_command(self, command: ScenarioCommand):
        async for session in self.session_factory():
            try:
                async with session.begin():
                    current_status = await self.scenario_manager.get_status(command.scenario_id, session=session)
                    if current_status in [ScenarioStatus.IN_SHUTDOWN_PROCESSING.value, ScenarioStatus.INACTIVE.value]:
                        logger.warning(f"Ignore stop for {command.scenario_id}, status: {current_status}")
                        return
                    await self.scenario_manager.update_status(
                        command.scenario_id,
                        ScenarioStatus.IN_SHUTDOWN_PROCESSING,
                        session=session
                    )

                    await self.scenario_manager.create_outbox_event(
                        scenario_id=command.scenario_id,
                        event_type=ScenarioStatus.IN_SHUTDOWN_PROCESSING.value,
                        payload={"status": ScenarioStatus.IN_SHUTDOWN_PROCESSING.value},
                        session=session,
                    )

                    await self.scenario_manager.delete_heartbeat(
                        scenario_id=command.scenario_id,
                        session=session,
                    )

                    logger.info("[Orchestrator] Command stop success")
            except Exception as e:
                logger.error(f"[Orchestrator] Error stop command: {e}")
                raise

    async def restart_scenario(self, scenario_id: UUID, session: AsyncSession):
        current_status = await self.scenario_manager.get_status(scenario_id, session=session)
        if current_status != ScenarioStatus.ACTIVE.value:
            logger.warning(f"[Orchestrator] Skipping restart for non-active scenario {scenario_id}")
            return
        try:
            video_path = await self.scenario_manager.get_video_path(scenario_id, session=session)
        except NoResultFound:
            logger.error(f"Scenario {scenario_id} not found")
            return
        try:
            await session.execute(
                update(Heartbeat)
                .where(Heartbeat.scenario_id == scenario_id)
                .values(is_active=False)
            )

            result = await session.execute(
                select(Heartbeat.last_frame)
                .where(Heartbeat.scenario_id == scenario_id)
            )
            last_frame = result.scalar_one_or_none() or 0

            await self.scenario_manager.update_status(
                scenario_id=scenario_id,
                status=ScenarioStatus.IN_STARTUP_PROCESSING,
                session=session
            )

            await self.scenario_manager.create_outbox_event(
                scenario_id=scenario_id,
                event_type=ScenarioStatus.IN_STARTUP_PROCESSING.value,
                payload={"video_path": video_path,
                         "resume_from_frame": last_frame},
                session=session,
            )

            await self.scenario_manager.create_heartbeat(
                scenario_id=scenario_id,
                last_frame=last_frame,
                session=session,
            )
            logger.info("[Orchestrator] Restart scenario success")
        except Exception as e:
            logger.error(f"[Orchestrator] Error restart scenario: {e}")
            raise

    async def update_heartbeat(self, scenario_id: UUID, runner_id: str, last_frame: int):
        try:
            async for session in self.session_factory():
                scenario_status = await session.execute(
                    select(Scenario.status)
                    .where(Scenario.id == scenario_id)
                )

                if scenario_status.scalar_one_or_none() != ScenarioStatus.ACTIVE.value:
                    logger.warning(f"Heartbeat rejected for stopped scenario: {scenario_id}")
                    return
                await session.execute(
                    insert(Heartbeat)
                    .values(
                        scenario_id=scenario_id,
                        runner_id=runner_id,
                        last_timestamp=func.now(),
                        last_frame=last_frame,
                        is_active=True
                    )
                    .on_conflict_do_update(
                        index_elements=['scenario_id'],
                        set_={
                            'runner_id': runner_id,
                            'last_timestamp': func.now(),
                            'last_frame': last_frame,
                            'is_active': True
                        }
                    )
                )
                logger.info("[Orchestrator] Update heartbeat success")
        except Exception as e:
            logger.error(f"[Watchdog] Update heartbeat error: {str(e)}")

    async def stop(self):
        await self.producer.stop()
