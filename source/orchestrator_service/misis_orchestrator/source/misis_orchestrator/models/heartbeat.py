from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class Heartbeat(BaseModel):
    scenario_id: UUID
    runner_id: str
    last_frame: int
    timestamp: datetime
