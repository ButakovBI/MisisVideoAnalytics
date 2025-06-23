from pydantic import BaseModel
from uuid import UUID
from datetime import datetime


class Scenario(BaseModel):
    id: UUID
    video_path: str
    state: str
    created_at: datetime
    updated_at: datetime
