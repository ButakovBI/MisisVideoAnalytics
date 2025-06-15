from pydantic import BaseModel


class ScenarioUpdateRequest(BaseModel):
    command: str
