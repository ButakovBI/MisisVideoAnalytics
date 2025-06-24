from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from misis_orchestrator.models.constants.kafka_topic import KafkaTopic
from misis_orchestrator.models.scenario_command import ScenarioCommand
from misis_orchestrator.models.constants.command_type import CommandType
from misis_orchestrator.scenario_db_manager import ScenarioDBManager
from misis_orchestrator.kafka.producer import Producer
from misis_orchestrator.models.constants.scenario_status import ScenarioStatus


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

        await self.scenario_manager.create_outbox_event(
            command.scenario_id,
            "scenario_started",
            {"video_path": command.video_path}
        )

        await self.producer.send(
            KafkaTopic.RUNNER_COMMANDS,
            value={
                "type": "start",
                "scenario_id": str(command.scenario_id),
                "video_path": command.video_path
            }
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

    async def restart_scenario(self, scenario_id: UUID):
        async with self.db_session.begin():
            await self.scenario_manager.update_status(
                scenario_id=scenario_id,
                status=ScenarioStatus.IN_STARTUP_PROCESSING,
            )

            await self.producer.send(
                KafkaTopic.RUNNER_COMMANDS,
                value={
                    "type": "start",
                    "scenario_id": str(scenario_id),
                    "is_restart": True
                }
            )

    async def stop(self):
        await self.producer.stop()
