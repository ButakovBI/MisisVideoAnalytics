import random
import logging
import numpy as np


class PredictionService:
    def predict(self, image: np.ndarray) -> list:
        try:
            height, width = image.shape[:2]
            boxes = []

            for _ in range(random.randint(1, 5)):
                x_min = random.randint(0, width - 100)
                y_min = random.randint(0, height - 100)
                x_max = x_min + random.randint(50, 100)
                y_max = y_min + random.randint(50, 100)
                class_name = random.choice(["person", "car", "dog", "cat", "bird"])
                confidence = round(random.uniform(0.5, 0.99), 2)

                boxes.append({
                    "x_min": x_min,
                    "y_min": y_min,
                    "x_max": x_max,
                    "y_max": y_max,
                    "class_name": class_name,
                    "confidence": confidence
                })

            return boxes
        except Exception as e:
            self._logger().error(f"Prediction failed: {e}")
            return []

    def _logger(self):
        return logging.getLogger(__name__)
