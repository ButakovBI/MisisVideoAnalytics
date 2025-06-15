from pydantic import BaseModel


class PredictionsResponse(BaseModel):
    predictions: list
