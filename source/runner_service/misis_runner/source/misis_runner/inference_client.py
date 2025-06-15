import requests
import cv2
import logging


class InferenceClient:
    def __init__(self, base_url: str):
        self.base_url = base_url

    def predict(self, frame) -> list:
        try:
            _, img_encoded = cv2.imencode('.jpg', frame)
            response = requests.post(
                f"{self.base_url}/predict",
                files={'image': ('frame.jpg', img_encoded.tobytes(), 'image/jpeg')},
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            self._logger().error(f"Prediction request failed: {e}")
            return []

    def _logger(self):
        return logging.getLogger(__name__)
