import asyncio
import logging

from sqlalchemy import select, update
from sqlalchemy.exc import OperationalError

from misis_orchestrator.models.constants.scenario_status import ScenarioStatus
from misis_orchestrator.database.tables.outbox import Outbox
from misis_orchestrator.kafka.producer import Producer
from misis_orchestrator.models.constants.kafka_topic import KafkaTopic

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class OutboxWorker:
    BATCH_SIZE = 100
    RETRY_INTERVAL = 5

    def __init__(self, session_factory):
        self.session_factory = session_factory
        self.producer = Producer()
        self.running = False

    async def start(self):
        self.running = True
        await self.producer.start()
        while self.running:
            try:
                await self._process_outbox()
                await asyncio.sleep(1)
            except Exception as e:
                logger.error(f"[Orchestrator Outbox] Outbox worker error: {str(e)}")
                await asyncio.sleep(5)

    async def stop(self):
        self.running = False
        await self.producer.stop()

    async def _process_outbox(self):
        while self.running:
            try:
                async for session in self.session_factory():
                    async with session.begin():
                        result = await session.execute(
                            select(Outbox)
                            .where(Outbox.processed == False)  # noqa E712
                            .order_by(Outbox.created_at)
                            .limit(self.BATCH_SIZE)
                            .with_for_update(skip_locked=True)
                        )
                        events = result.scalars().all()

                        processed_events = []
                        for event in events:
                            payload = event.payload or {}
                            try:
                                command_type = None
                                if event.event_type == ScenarioStatus.INIT_STARTUP.value:
                                    command_type = "start"
                                elif event.event_type == ScenarioStatus.INIT_SHUTDOWN.value:
                                    command_type = "stop"
                                message = {
                                    "type": command_type,
                                    "scenario_id": str(event.scenario_id),
                                    "video_path": payload.get("video_path"),
                                }
                                if command_type == "start":
                                    message["resume_from_frame"] = payload.get("resume_from_frame", 0)
                                await self.producer.send(
                                    KafkaTopic.RUNNER_COMMANDS.value,
                                    value=message
                                )
                                processed_events.append(event.id)
                                logger.info("[Orch Outbox] Get event")
                            except Exception as e:
                                logger.error(f"[Orch Outbox] Failed to send outbox event {event.id}: {str(e)}")

                        if processed_events:
                            await session.execute(
                                update(Outbox)
                                .where(Outbox.id.in_(processed_events))
                                .values(processed=True)
                            )
                        await session.commit()
                        logger.info("[Orch Outbox] Transaction success")

                await asyncio.sleep(1)
            except OperationalError:
                await asyncio.sleep(self.RETRY_INTERVAL)
            except Exception as e:
                logger.error(f"[Orch Outbox] Outbox processing failed: {str(e)}")
                await asyncio.sleep(self.RETRY_INTERVAL)
