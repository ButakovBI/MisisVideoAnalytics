import asyncio
import logging
import time
from uuid import UUID

from misis_runner.app.config import settings
from misis_runner.app.heartbeat_sender import HeartbeatSender
from misis_runner.app.video_processor import VideoProcessor
from misis_runner.inference_client import InferenceClient
from misis_runner.kafka.consumer import Consumer
from misis_runner.s3.s3_client import S3Client

logger = logging.getLogger(__name__)


class Runner:
    def __init__(self):
        self.active_scenarios: dict[UUID, VideoProcessor] = {}
        self.consumer = Consumer()
        self.heartbeat_sender = HeartbeatSender()
        self.s3_client = S3Client()
        self.inference_client = InferenceClient(
            base_url=settings.INFERENCE_SERVICE_URL
        )

    async def start(self):
        await self.consumer.start(
            start_handler=self.handle_start,
            stop_handler=self.handle_stop
        )
        await self.heartbeat_sender.start(
            get_active_scenarios=lambda: self.active_scenarios
        )

    async def handle_start(self, scenario_id: UUID, s3_video_key: str):
        try:
            if scenario_id in self.active_scenarios:
                logger.warning(f"[Runner] Scenario already runnign {scenario_id}")
            if len(self.active_scenarios) >= settings.MAX_CONCURRENT_SCENARIOS:
                logger.info(f"[Runner] Reached max scenarios limit, rejecting {scenario_id}")
                return

            logger.info(f"[Runner] Starting scenario {scenario_id}")
            processor = VideoProcessor(
                scenario_id=scenario_id,
                s3_video_key=s3_video_key,
                s3_client=self.s3_client,
                inference_client=self.inference_client,
            )
            self.active_scenarios[scenario_id] = processor
            asyncio.create_task(self._run_processor(processor))

        except Exception as e:
            logger.error(f"[Runner] Failed to start scenario {scenario_id}: {str(e)}")
            self.active_scenarios.pop(scenario_id, None)

    async def handle_stop(self, scenario_id: UUID):
        if scenario_id in self.active_scenarios:
            self.active_scenarios[scenario_id].stop()

    async def stop(self):
        logger.info("[Runner] Stopping runner...")
        for processor in self.active_scenarios.values():
            processor.stop()
        await self.consumer.stop()
        await self.heartbeat_sender.stop()
        logger.info("[Runner] Runner stopped")

    async def _run_processor(self, processor: VideoProcessor):
        start_time = time.time()
        try:
            await processor.process()
            logger.info(f"Scenario {processor.scenario_id} completed in {time.time() - start_time}s")
        finally:
            self.active_scenarios.pop(processor.scenario_id, None)
