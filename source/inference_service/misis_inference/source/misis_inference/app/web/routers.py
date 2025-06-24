
import logging
from fastapi import APIRouter, HTTPException, UploadFile, status

from misis_inference.app.web.prediction_service import PredictionService
from misis_inference.models.prediction_response import PredictionResponse

router = APIRouter()

logger = logging.getLogger(__name__)


@router.post(
    "/predict",
    response_model=PredictionResponse
)
async def predict(file: UploadFile):
    try:
        return await PredictionService().predict(file)
    except Exception as e:
        logger.error("Prediction of file %s failed: %s", file, str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing frame: {str(e)}. try again"
        )
