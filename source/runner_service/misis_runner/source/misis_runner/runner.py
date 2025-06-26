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
        self.processing_semaphore = asyncio.Semaphore(settings.MAX_CONCURRENT_PROCESSORS)

    async def start(self):
        await self.heartbeat_sender.producer.start()
        await self.consumer.start(
            start_handler=self.handle_start,
            stop_handler=self.handle_stop
        )
        await self.heartbeat_sender.start(
            get_active_scenarios=lambda: self.active_scenarios
        )

    async def handle_start(self, scenario_id: UUID, s3_video_key: str):
        if scenario_id in self.active_scenarios:
            logger.warning(f"[Runner] Scenario already runnign {scenario_id}")
            await self.handle_stop(scenario_id)
            await asyncio.sleep(0.1)
        if len(self.active_scenarios) >= settings.MAX_CONCURRENT_SCENARIOS:
            logger.info(f"[Runner] Reached max scenarios limit, rejecting {scenario_id}")
            return
        try:
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
        processor = self.active_scenarios.pop(scenario_id, None)
        if processor:
            processor.stop()

    async def stop(self):
        logger.info("[Runner] Stopping runner...")
        await self.heartbeat_sender.stop()
        await self.consumer.stop()
        await self.inference_client.close()
        for processor in self.active_scenarios.values():
            processor.stop()
        self.active_scenarios.clear()
        logger.info("[Runner] Runner stopped")

    async def _run_processor(self, processor: VideoProcessor):
        start_time = time.time()
        try:
            async with self.processing_semaphore:
                await processor.process()
            logger.info(f"Scenario {processor.scenario_id} completed in {time.time() - start_time}s")
        except Exception as e:
            logger.error(f"Scenario processing failed: {str(e)}")
        finally:
            if processor.scenario_id in self.active_scenarios:
                del self.active_scenarios[processor.scenario_id]
