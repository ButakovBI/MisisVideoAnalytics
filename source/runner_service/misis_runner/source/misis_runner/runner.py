import asyncio
import logging
from uuid import UUID

from misis_runner.app.heartbeat_sender import HeartbeatSender
from misis_runner.kafka.consumer import Consumer
from misis_runner.app.video_processor import VideoProcessor
from misis_runner.app.config import settings


logger = logging.getLogger(__name__)


class Runner:
    def __init__(self):
        self.active_scenarios: dict[UUID, VideoProcessor] = {}
        self.consumer = Consumer()
        self.heartbeat_sender = HeartbeatSender()

    async def start(self):
        await self.consumer.start(
            start_handler=self.handle_start,
            stop_handler=self.handle_stop
        )
        await self.heartbeat_sender.start(
            get_active_scenarios=lambda: self.active_scenarios
        )

    async def handle_start(self, scenario_id: UUID, video_path: str):
        if len(self.active_scenarios) >= settings.MAX_CONCURRENT_SCENARIOS:
            return

        processor = VideoProcessor(scenario_id=scenario_id, video_path=video_path)
        self.active_scenarios[scenario_id] = processor

        async def frame_callback(frame):
            await asyncio.sleep(1)

        await processor.process(frame_callback=frame_callback)
        self.active_scenarios.pop(scenario_id, None)

    async def handle_stop(self, scenario_id: UUID):
        if scenario_id in self.active_scenarios:
            self.active_scenarios[scenario_id].stop()

    async def stop(self):
        await self.consumer.stop()
        await self.heartbeat_sender.stop()
