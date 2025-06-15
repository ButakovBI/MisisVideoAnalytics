from sqlalchemy import Column, DateTime, Enum, String, text
from sqlalchemy.dialects.postgresql import UUID

from misis_orchestrator.models.scenario_state import ScenarioState
from misis_orchestrator.database.base import Base


class ScenarioModel(Base):
    __tablename__ = 'scenario'
    id = Column(UUID, primary_key=True)
    video_path = Column(String, nullable=False)
    state = Column(Enum(ScenarioState), nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=text('now()'))
    updated_at = Column(DateTime, nullable=False, server_default=text('now()'), onupdate=text('now()'))
