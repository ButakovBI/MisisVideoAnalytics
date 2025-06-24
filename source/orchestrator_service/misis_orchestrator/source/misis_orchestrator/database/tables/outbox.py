import datetime
from sqlalchemy import Boolean, Column, JSON, DateTime, String
from sqlalchemy.dialects.postgresql import UUID

from misis_orchestrator.database.database import Base


class Outbox(Base):
    __tablename__ = "outbox_scenario"

    id = Column(UUID(as_uuid=True), primary_key=True)
    scenario_id = Column(UUID(as_uuid=True), nullable=True)
    event_type = Column(String(50), nullable=False)
    payload = Column(JSON, nullable=False)
    processed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.timezone.utc)
