import asyncio
import logging
from datetime import datetime

from misis_scenario_api.database.database import get_db_session
from misis_scenario_api.database.tables.outbox import Outbox
from misis_scenario_api.kafka.producer import Producer
from misis_scenario_api.models.constants.kafka_topic import KafkaTopic
from sqlalchemy import select, update
from sqlalchemy.exc import OperationalError

logger = logging.getLogger(__name__)


class OutboxWorker:
    def __init__(self, producer: Producer):
        self.producer = producer
        self.running = False

    async def start(self):
        self.running = True
        while self.running:
            try:
                await self._process_outbox()
                await asyncio.sleep(1)
            except Exception as e:
                logger.error(f"[API] Outbox worker error: {str(e)}")
                await asyncio.sleep(5)

    async def stop(self):
        self.running = False

    async def _process_outbox(self):
        async for session in get_db_session():
            try:
                result = await session.execute(
                    select(Outbox)
                    .where(Outbox.processed == False)  # noqa: E712
                    .order_by(Outbox.created_at)
                    .limit(100)
                    .with_for_update(skip_locked=True)
                )
                events = result.scalars().all()

                if not events:
                    return

                for event in events:
                    try:
                        await self.producer.send(
                            KafkaTopic.SCENARIO_EVENTS,
                            {
                                "event_type": event.event_type,
                                "scenario_id": str(event.scenario_id),
                                "payload": event.payload,
                                "event_id": str(event.id),
                                "timestamp": datetime.utcnow().isoformat()
                            }
                        )

                        await session.execute(
                            update(Outbox)
                            .where(Outbox.id == event.id)
                            .values(processed=True)
                        )
                        await session.commit()
                        logger.info(f"[API] Processed outbox event {event.id}")

                    except Exception as e:
                        logger.error(f"[API] Failed to process outbox event {event.id}: {str(e)}")
                        await session.rollback()
                        continue

            except OperationalError as e:
                logger.warning(f"[API] Database operation failed: {str(e)}")
                await session.rollback()
                raise
