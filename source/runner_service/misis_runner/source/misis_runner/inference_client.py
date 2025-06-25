import logging
from uuid import UUID

import cv2
import httpx

from misis_runner.models.bounding_box import BoundingBox

logger = logging.getLogger(__name__)


class InferenceClient:
    def __init__(self, base_url: str):
        self.client = httpx.AsyncClient(base_url=base_url)

    async def predict_frame(self, frame, scenario_id: UUID) -> list[BoundingBox]:
        try:
            _, img_bytes = cv2.imencode('.jpg', frame)
            files = {'file': ('frame.jpg', img_bytes.tobytes())}

            response = await self.client.post(
                "/predict",
                files=files,
                params={"scenario_id": str(scenario_id)}
            )
            response.raise_for_status()
            return response.json()["predictions"]
        except Exception as e:
            logger.error(f"Inference request failed: {str(e)}")
            raise
