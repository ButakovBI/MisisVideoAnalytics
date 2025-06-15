from pydantic import BaseModel


class ScenarioStatusResponse(BaseModel):
    status: str
