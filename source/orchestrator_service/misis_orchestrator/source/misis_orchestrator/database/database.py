
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import logging

from misis_orchestrator.database.base import Base
from misis_orchestrator.database.tables.heartbeat import HeartbeatModel
from misis_orchestrator.database.tables.prediction import PredictionModel
from misis_orchestrator.database.tables.scenario import ScenarioModel


class Database:
    def __init__(self, connection_string: str):
        self.engine = create_engine(connection_string)
        self.Session = sessionmaker(bind=self.engine)
        Base.metadata.create_all(self.engine)
        self._logger().info("Database initialized")

    def get_heartbeat(self, scenario_id):
        with self.Session() as session:
            return session.query(HeartbeatModel).filter_by(scenario_id=scenario_id).first()

    def get_scenario(self, scenario_id):
        with self.Session() as session:
            model = session.query(ScenarioModel).filter_by(id=scenario_id).first()
            return model

    def get_active_scenarios(self, states):
        with self.Session() as session:
            return session.query(ScenarioModel).filter(ScenarioModel.state.in_(states)).all()

    def save_heartbeat(self, heartbeat):
        with self.Session() as session:
            model = session.query(HeartbeatModel).filter_by(scenario_id=heartbeat.scenario_id).first()
            if not model:
                model = HeartbeatModel(
                    scenario_id=heartbeat.scenario_id,
                    last_timestamp=heartbeat.last_timestamp
                )
                session.add(model)
            else:
                model.last_timestamp = heartbeat.last_timestamp
            session.commit()

    def save_scenario(self, scenario):
        with self.Session() as session:
            model = session.query(ScenarioModel).filter_by(id=scenario.id).first()
            if not model:
                model = ScenarioModel(
                    id=scenario.id,
                    video_path=scenario.video_path,
                    state=scenario.state,
                    created_at=scenario.created_at,
                    updated_at=scenario.updated_at
                )
                session.add(model)
            else:
                model.state = scenario.state
                model.updated_at = scenario.updated_at
            session.commit()

    def save_prediction(self, prediction):
        with self.Session() as session:
            model = PredictionModel(
                scenario_id=prediction.scenario_id,
                frame_number=prediction.frame_number,
                boxes=prediction.boxes,
                created_at=prediction.created_at
            )
            session.add(model)
            session.commit()

    def get_predictions(self, scenario_id):
        with self.Session() as session:
            return session.query(PredictionModel).filter_by(scenario_id=scenario_id).all()

    def _logger(self):
        return logging.getLogger(__name__)
