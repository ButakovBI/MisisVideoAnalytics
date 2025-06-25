from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from misis_orchestrator.kafka.producer import Producer
from misis_orchestrator.models.constants.command_type import CommandType
from misis_orchestrator.models.constants.kafka_topic import KafkaTopic
from misis_orchestrator.models.constants.scenario_status import ScenarioStatus
from misis_orchestrator.models.scenario_command import ScenarioCommand
from misis_orchestrator.scenario_db_manager import ScenarioDBManager


class OrchestratorService:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session
        self.producer = Producer()
        self.scenario_manager = ScenarioDBManager(db_session)

    async def start(self):
        await self.producer.start()

    async def process_command(self, command: ScenarioCommand):
        async with self.db_session.begin():
            if command.type == CommandType.START:
                await self._process_start_command(command)
            elif command.type == CommandType.STOP:
                await self._process_stop_command(command)

    async def _process_start_command(self, command: ScenarioCommand):
        await self.scenario_manager.update_status(
            command.scenario_id,
            ScenarioStatus.IN_STARTUP_PROCESSING
        )

        await self.producer.send(
            KafkaTopic.RUNNER_COMMANDS,
            value={
                "type": "start",
                "scenario_id": str(command.scenario_id),
                "video_path": command.video_path
            }
        )

        await self.scenario_manager.create_outbox_event(
            scenario_id=command.scenario_id,
            event_type="status_update",
            payload={"status": ScenarioStatus.IN_STARTUP_PROCESSING}
        )

    async def _process_stop_command(self, command: ScenarioCommand):
        await self.scenario_manager.update_status(
            command.scenario_id,
            ScenarioStatus.IN_SHUTDOWN_PROCESSING
        )

        await self.producer.send(
            KafkaTopic.RUNNER_COMMANDS,
            value={
                "type": "stop",
                "scenario_id": str(command.scenario_id)
            }
        )

        await self.scenario_manager.create_outbox_event(
            scenario_id=command.scenario_id,
            event_type="status_update",
            payload={"status": ScenarioStatus.IN_SHUTDOWN_PROCESSING}
        )

    async def update_scenario_status(self, scenario_id: UUID, status: ScenarioStatus):
        async with self.db_session.begin():
            await self.scenario_manager.update_status(scenario_id=scenario_id, status=status)

            await self.scenario_manager.create_outbox_event(
                scenario_id=scenario_id,
                event_type="status_update",
                payload={"status": status}
            )

    async def restart_scenario(self, scenario_id: UUID):
        async with self.db_session.begin():
            video_path = await self.scenario_manager.get_video_path(scenario_id)

            await self.scenario_manager.update_status(
                scenario_id=scenario_id,
                status=ScenarioStatus.IN_STARTUP_PROCESSING,
            )

            await self.producer.send(
                topic=KafkaTopic.RUNNER_COMMANDS,
                value={
                    "type": "start",
                    "scenario_id": str(scenario_id),
                    "video_path": video_path,
                    "is_restart": True,
                }
            )

            await self.scenario_manager.create_outbox_event(
                scenario_id=scenario_id,
                event_type="status_update",
                payload={"status": ScenarioStatus.IN_STARTUP_PROCESSING},
            )

    async def stop(self):
        await self.producer.stop()
