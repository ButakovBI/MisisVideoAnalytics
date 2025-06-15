import abc
from datetime import datetime
from uuid import UUID


class HeartbeatStorage(abc.ABC):
    @abc.abstractmethod
    def update_heartbeat(self, scenario_id: UUID, timestamp: datetime):
        pass

    @abc.abstractmethod
    def get_last_heartbeat(self, scenario_id: UUID) -> datetime:
        pass

    @abc.abstractmethod
    def get_active_scenarios(self):
        pass
