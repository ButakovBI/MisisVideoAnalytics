from sqlalchemy import Column, DateTime, Integer, JSON, text
from sqlalchemy.dialects.postgresql import UUID

from misis_orchestrator.database.base import Base


class PredictionModel(Base):
    __tablename__ = 'prediction'
    id = Column(Integer, primary_key=True, autoincrement=True)
    scenario_id = Column(UUID, nullable=False)
    frame_number = Column(Integer, nullable=False)
    boxes = Column(JSON, nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=text('now()'))
