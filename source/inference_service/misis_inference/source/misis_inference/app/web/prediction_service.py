import time
from fastapi import UploadFile
import io
from PIL import Image
import logging

from ultralytics import YOLO

from misis_inference.models.prediction_response import PredictionResponse

logger = logging.getLogger(__name__)


class PredictionService:
    def __init__(self):
        self.model = YOLO('yolov8n.pt')

    async def predict(self, file: UploadFile) -> PredictionResponse:
        logger.info("[Inference predict] Do prediction for frame %s", file.filename)
        bytes = await file.read()
        image = Image.open(io.BytesIO(bytes)).convert("RGB")

        try:
            results = self.model.predict(source=image)
            predictions = []

            for res in results:
                for box in res.boxes:
                    pred = {
                        "x1": float(box.xyxy[0][0]),
                        "y1": float(box.xyxy[0][1]),
                        "x2": float(box.xyxy[0][2]),
                        "y2": float(box.xyxy[0][3]),
                        "class_name": res.names[int(box.cls[0])],
                        "confidence": float(box.conf[0]),
                    }
                    predictions.append(pred)
            time.sleep(1)
            logger.error(f"Prediction done for frame {file.filename}")
            return predictions
        except Exception as e:
            logger.error(f"Prediction failed: {str(e)}")
            raise
