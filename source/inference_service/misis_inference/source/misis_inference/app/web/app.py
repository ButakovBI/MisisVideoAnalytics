from fastapi import FastAPI, UploadFile, File
import numpy as np
import cv2

from misis_inference.app.prediction_service import PredictionService


app = FastAPI(title="MISIS Inference Service")
prediction_service = PredictionService()


@app.post("/predict")
async def predict(image: UploadFile = File(...)):
    try:
        contents = await image.read()
        nparr = np.frombuffer(contents, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        return prediction_service.predict(img)
    except Exception as e:
        return {"error": str(e)}
