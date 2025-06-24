import asyncio
import threading
from datetime import datetime, timedelta
from uuid import UUID


from misis_orchestrator.app.config import settings


class Watchdog(threading.Thread):
    def __init__(self):
        self.active_scenarios: dict[UUID, datetime] = {}

    def update_heartbeat(self, scenario_id: UUID):
        self.active_scenarios[scenario_id] = datetime.now()

    async def check_timeouts(self):
        while True:
            now = datetime.now()
            timeout = timedelta(seconds=settings.HEARTBEAT_TIMEOUT)
            timed_out = [
                scenario_id for scenario_id, last_seen in self.active_scenarios.items
                if (now - last_seen) > timeout
            ]

            for scenario_id in timed_out:
                yield scenario_id
                del self.active_scenarios[scenario_id]

            await asyncio.sleep(10)
