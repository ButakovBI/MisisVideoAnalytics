import logging
from uuid import UUID

from sqlalchemy.exc import NoResultFound

from misis_orchestrator.kafka.producer import Producer
from misis_orchestrator.models.constants.command_type import CommandType
from misis_orchestrator.models.constants.kafka_topic import KafkaTopic
from misis_orchestrator.models.constants.scenario_status import ScenarioStatus
from misis_orchestrator.models.scenario_command import ScenarioCommand
from misis_orchestrator.scenario_db_manager import ScenarioDBManager

logger = logging.getLogger(__name__)


class OrchestratorService:
    def __init__(self, session_factory):
        self.session_factory = session_factory
        self.producer = Producer()
        self.scenario_manager = ScenarioDBManager(session_factory)

    async def start(self):
        await self.producer.start()

    async def process_command(self, command: ScenarioCommand):
        if command.type == CommandType.START:
            await self._process_start_command(command)
        elif command.type == CommandType.STOP:
            await self._process_stop_command(command)

    async def _process_start_command(self, command: ScenarioCommand):
        async for session in self.session_factory():
            try:
                async with session.begin():
                    current_status = await self.scenario_manager.get_status(command.scenario_id, session=session)
                    if current_status not in [ScenarioStatus.INIT_STARTUP, ScenarioStatus.INACTIVE]:
                        logger.warning(f"Ignore start for {command.scenario_id}, status: {current_status}")
                        return

                    await self.scenario_manager.update_status(
                        command.scenario_id,
                        ScenarioStatus.IN_STARTUP_PROCESSING,
                        session=session
                    )

                    await self.producer.send(
                        KafkaTopic.RUNNER_COMMANDS.value,
                        value={
                            "type": "start",
                            "scenario_id": str(command.scenario_id),
                            "video_path": command.video_path
                        }
                    )

                    await self.scenario_manager.create_outbox_event(
                        scenario_id=command.scenario_id,
                        event_type=ScenarioStatus.IN_STARTUP_PROCESSING,
                        payload={"video_path": command.video_path},
                        session=session,
                    )

                    await self.scenario_manager.create_heartbeat(
                        scenario_id=command.scenario_id,
                        session=session,
                    )
            except Exception as e:
                logger.error(f"Error processing command: {e}")
                raise

    async def _process_stop_command(self, command: ScenarioCommand):
        async with self.session_factory() as session:
            async with session.begin():
                await self.scenario_manager.update_status(
                    command.scenario_id,
                    ScenarioStatus.IN_SHUTDOWN_PROCESSING,
                    session=session
                )

                await self.producer.send(
                    KafkaTopic.RUNNER_COMMANDS.value,
                    value={
                        "type": "stop",
                        "scenario_id": str(command.scenario_id)
                    }
                )

                await self.scenario_manager.create_outbox_event(
                    scenario_id=command.scenario_id,
                    event_type=ScenarioStatus.IN_SHUTDOWN_PROCESSING,
                    payload={"status": ScenarioStatus.IN_SHUTDOWN_PROCESSING},
                    session=session,
                )

                await self.scenario_manager.delete_heartbeat(
                    scenario_id=command.scenario_id,
                    session=session,
                )

    async def restart_scenario(self, scenario_id: UUID):
        async with self.session_factory() as session:
            try:
                video_path = await self.scenario_manager.get_video_path(scenario_id, session=session)
            except NoResultFound:
                logger.error(f"Scenario {scenario_id} not found")
                return
            await self.scenario_manager.update_status(
                scenario_id=scenario_id,
                status=ScenarioStatus.IN_STARTUP_PROCESSING,
                session=session
            )

            await self.producer.send(
                KafkaTopic.RUNNER_COMMANDS.value,
                value={
                    "type": "start",
                    "scenario_id": str(scenario_id),
                    "video_path": video_path,
                    "is_restart": True,
                }
            )

            await self.scenario_manager.create_outbox_event(
                scenario_id=scenario_id,
                event_type=ScenarioStatus.IN_STARTUP_PROCESSING,
                payload={"video_path": video_path, "is_restart": True},
                session=session,
            )

    async def stop(self):
        await self.producer.stop()
