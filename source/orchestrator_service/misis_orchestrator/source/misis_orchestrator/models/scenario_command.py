from uuid import UUID

from pydantic import BaseModel

from misis_orchestrator.models.constants.command_type import CommandType


class ScenarioCommand(BaseModel):
    scenario_id: UUID
    type: CommandType
    video_path: str | None = None
