import asyncio
import logging
from datetime import datetime

from sqlalchemy import select, update
from sqlalchemy.exc import OperationalError

from misis_orchestrator.database.tables.outbox import Outbox
from misis_orchestrator.kafka.producer import Producer

logger = logging.getLogger(__name__)


class OutboxWorker:
    def __init__(self, db_session):
        self.db_session = db_session
        self.producer = Producer()
        self.running = False

    async def start(self):
        self.running = True
        await self.producer.producer.start()

        while self.running:
            try:
                await self._process_outbox()
                await asyncio.sleep(1)
            except Exception as e:
                logger.error(f"[Orchestrator] Outbox worker error: {str(e)}")
                await asyncio.sleep(5)

    async def stop(self):
        self.running = False
        await self.producer.producer.stop()

    async def _process_outbox(self):
        async with self.db_session.begin() as transaction:
            try:
                result = await self.db_session.execute(
                    select(Outbox)
                    .where(Outbox.processed == False)  # noqa E712
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
                            event.event_type,
                            {
                                "scenario_id": str(event.scenario_id),
                                "payload": event.payload,
                                "event_id": str(event.id),
                                "timestamp": datetime.utcnow().isoformat()
                            }
                        )

                        await self.db_session.execute(
                            update(Outbox)
                            .where(Outbox.id == event.id)
                            .values(processed=True)
                        )
                        logger.info(f"[Orchestrator] Processed outbox event {event.id}")

                    except Exception as e:
                        logger.error(f"[Orchestrator] Failed to process outbox event {event.id}: {str(e)}")
                        continue

                await transaction.commit()

            except OperationalError as e:
                logger.warning(f"[Orchestrator] Database operation failed: {str(e)}")
                await transaction.rollback()
