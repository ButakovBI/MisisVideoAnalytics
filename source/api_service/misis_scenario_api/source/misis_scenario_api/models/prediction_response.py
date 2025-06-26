from uuid import UUID

from misis_scenario_api.models.bounding_box import BoundingBox
from pydantic import BaseModel


class PredictionResponse(BaseModel):
    scenario_id: UUID
    predictions: list[BoundingBox]
