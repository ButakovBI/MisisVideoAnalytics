from typing import Literal
from pydantic import BaseModel


class ScenarioUpdateRequest(BaseModel):
    command: Literal['create', 'start', 'stop', 'restart']
