import uuid

from misis_scenario_api.models.scenario_create_request import ScenarioCreateRequest
from misis_scenario_api.models.scenario_update_request import ScenarioUpdateRequest
from misis_scenario_api.kafka.kafka_producer import KafkaProducer


class ScenarioCommandHandler:
    def __init__(self, producer: KafkaProducer):
        self.producer = producer

    def create_scenario(self, request: ScenarioCreateRequest) -> str:
        scenario_id = str(uuid.uuid4())
        self.producer.send_scenario_command({
            "scenario_id": scenario_id,
            "command": "create",
            "video_path": request.video_path
        })
        return scenario_id

    def update_scenario(self, scenario_id: str, request: ScenarioUpdateRequest):
        self.producer.send_scenario_command({
            "scenario_id": scenario_id,
            "command": request.command
        })
