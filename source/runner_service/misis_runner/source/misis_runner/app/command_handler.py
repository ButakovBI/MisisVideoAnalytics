import threading
import logging
from uuid import UUID

from misis_runner.models.video_processing_task import VideoProcessingTask
from misis_runner.kafka.kafka_service import KafkaService
from misis_runner.app.video_processor import VideoProcessor


class CommandHandler:
    def __init__(self, video_processor: VideoProcessor, kafka_service: KafkaService):
        self.video_processor = video_processor
        self.kafka_service = kafka_service
        self.active_tasks = {}
        self.lock = threading.Lock()

    def handle_start_command(self, scenario_id: UUID, video_path: str):
        with self.lock:
            if scenario_id in self.active_tasks:
                self._logger().warning(f"Scenario {scenario_id} is already active")
                return

            task = VideoProcessingTask(scenario_id, video_path)
            self.active_tasks[scenario_id] = task

            thread = threading.Thread(
                target=self.video_processor.process_video,
                args=(task,),
                daemon=True
            )
            thread.start()
            self._logger().info(f"Started processing for scenario {scenario_id}")

    def handle_stop_command(self, scenario_id: UUID):
        with self.lock:
            if scenario_id in self.active_tasks:
                self.active_tasks[scenario_id].active = False
                self._logger().info(f"Stopping scenario {scenario_id}")

    def _logger(self):
        return logging.getLogger(__name__)
