from uuid import UUID
from pydantic import BaseModel

from misis_inference.models.bounding_box import BoundingBox


class PredictionResponse(BaseModel):
    scenario_id: UUID
    predictions: list[BoundingBox]
