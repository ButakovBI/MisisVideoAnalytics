import threading
import cv2
import time
import logging
from uuid import UUID

from misis_runner.models.video_processing_task import VideoProcessingTask
from misis_runner.inference_client import InferenceClient
from misis_runner.kafka.kafka_service import KafkaService


class VideoProcessor:
    def __init__(self, inference_client: InferenceClient, kafka_service: KafkaService):
        self.inference_client = inference_client
        self.kafka_service = kafka_service

    def process_video(self, task: VideoProcessingTask):
        heartbeat_thread = threading.Thread(
            target=self._send_heartbeats,
            args=(task.scenario_id,),
            daemon=True
        )
        heartbeat_thread.start()

        try:
            cap = cv2.VideoCapture(task.video_path)
            if not cap.isOpened():
                self._logger().error(f"Failed to open video: {task.video_path}")
                return

            frame_number = 0
            frame_interval = 5

            while task.active and cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break

                if frame_number % frame_interval != 0:
                    frame_number += 1
                    continue

                frame = cv2.resize(frame, (640, 480))
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                predictions = self.inference_client.predict(frame)

                self.kafka_service.publish_prediction(
                    task.scenario_id,
                    frame_number,
                    predictions
                )

                frame_number += 1
                time.sleep(0.033)

        except Exception as e:
            self._logger().error(f"Video processing failed for {task.scenario_id}: {e}")
        finally:
            cap.release()
            self.kafka_service.publish_complete(task.scenario_id)
            self._logger().info(f"Completed processing for scenario {task.scenario_id}")

    def _send_heartbeats(self, scenario_id: UUID):
        while True:
            try:
                self.kafka_service.publish_heartbeat(scenario_id)
                time.sleep(1)
            except Exception as e:
                self._logger().error(f"Heartbeat send error for {scenario_id}: {e}")
                time.sleep(1)

    def _logger(self):
        return logging.getLogger(__name__)
