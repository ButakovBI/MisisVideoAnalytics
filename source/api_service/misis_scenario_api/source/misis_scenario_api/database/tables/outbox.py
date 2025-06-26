import datetime

from misis_scenario_api.database.base import Base
from sqlalchemy import JSON, Boolean, Column, DateTime, String
from sqlalchemy.dialects.postgresql import UUID


class Outbox(Base):
    __tablename__ = "outbox_scenario"

    id = Column(UUID(as_uuid=True), primary_key=True)
    scenario_id = Column(UUID(as_uuid=True), nullable=True)
    event_type = Column(String(50), nullable=False)
    payload = Column(JSON, nullable=False)
    processed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
