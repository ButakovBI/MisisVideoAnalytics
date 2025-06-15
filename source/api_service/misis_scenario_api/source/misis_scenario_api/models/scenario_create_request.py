from pydantic import BaseModel


class ScenarioCreateRequest(BaseModel):
    video_path: str
