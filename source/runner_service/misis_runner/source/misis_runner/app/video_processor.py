import logging
import os
from uuid import UUID

import cv2

from misis_runner.inference_client import InferenceClient
from misis_runner.s3.s3_client import S3Client

FRAME_SKIP = 10
SIZE = (640, 480)

logger = logging.getLogger(__name__)


class VideoProcessor:
    def __init__(
        self,
        scenario_id: UUID,
        s3_video_key: str,
        s3_client: S3Client,
        inference_client: InferenceClient
    ):
        self.scenario_id = scenario_id
        self.s3_video_key = s3_video_key
        self.s3_client = s3_client
        self.inference_client = inference_client
        self._break_flag = False
        self.last_processed_frame = 0
        self.processed_frames = 0
        self.temp_video_path = None

    async def process(self):
        cap = None
        try:
            self.temp_video_path = await self.s3_client.download_video(self.s3_video_key)

            cap = cv2.VideoCapture(self.temp_video_path)
            if not cap.isOpened():
                raise ValueError(f"Failed to open video {self.temp_video_path}")

            while not self._break_flag:
                ret, frame = cap.read()
                self.last_processed_frame += 1

                if not ret or (self.last_processed_frame % FRAME_SKIP != 0):
                    continue
                try:
                    processed_frame = self._preprocess(frame)
                    predictions = await self._process_frame(processed_frame)
                    await self._save_predicitons(predictions)
                    self.processed_frames += 1
                except Exception as e:
                    logger.error(f"[Runner] Frame processing failed {str(e)}")
        except Exception as e:
            logger.error(f"[Runner] Video processing failed: {str(e)}")
        finally:
            if cap:
                cap.release()
            if self.temp_video_path and os.path.exists(self.temp_video_path):
                os.unlink(self.temp_video_path)
            logger.info(f"[Runner] Completed. Scenario {self.scenario_id}. Processed {self.processed_frames} frames")

    def stop(self):
        self._break_flag = True

    def _preprocess(self, frame):
        if frame is None:
            raise ValueError("Empty frame received")
        return cv2.resize(frame, SIZE) / 255.0

    async def _process_frame(self, frame) -> list:
        try:
            _, img_bytes = cv2.imencode('.jpg', frame)
            return await self.inference_client.predict_frame(
                frame_bytes=img_bytes.tobytes(),
                scenario_id=self.scenario_id,
                frame_number=self.last_processed_frame
            )
        except Exception as e:
            logger.error(f"[Runner] Video processor: frame processing failed: {str(e)}")
            return []

    async def _save_predictions(self, predictions: list):
        if not predictions:
            return

        try:
            await self.s3_client.save_predictions(
                scenario_id=self.scenario_id,
                frame_number=self.last_processed_frame,
                predictions=predictions
            )
            logger.debug(f"[Runner] Saved predictions for frame {self.last_processed_frame}")
        except Exception as e:
            logger.error(f"[Runner] Failed to save predictions: {str(e)}")
