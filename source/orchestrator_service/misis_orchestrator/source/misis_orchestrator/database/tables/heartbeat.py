from sqlalchemy import Column, DateTime
from sqlalchemy.dialects.postgresql import UUID

from misis_orchestrator.database.base import Base


class HeartbeatModel(Base):
    __tablename__ = 'heartbeat'
    scenario_id = Column(UUID, primary_key=True)
    last_timestamp = Column(DateTime, nullable=False)
