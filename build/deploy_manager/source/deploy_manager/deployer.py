import json
import logging
from pathlib import Path

from deploy_manager.docker.docker_runner import DockerRunner
from deploy_manager.docker.docker_builder import DockerBuilder
from deploy_manager.docker.docker_compose_runner import DockerComposeRunner
from deploy_manager.constants import SERVICES_SECTION, DeployMode, ServicesType


class Deployer:
    def __init__(self, compose_file: Path, config: Path, mode: DeployMode):
        self.mode = mode
        with open(config, 'r') as f:
            self.config_data = json.load(f)
        self.dc_runner = DockerComposeRunner(str(compose_file))

    def deploy(self):
        config_services = self.config_data[SERVICES_SECTION]
        prefix = self.mode.value

        if self.mode == DeployMode.TEST:
            test_services = config_services[ServicesType.TEST_SERVICES]
            for service in test_services:
                image_name = f"{prefix}-{service}"
                image_builder = DockerBuilder(test_services[service])
                image_builder.build_image(image_name)
                image_builder = DockerBuilder(test_services[service])
                DockerRunner.run_container(image_name)
        elif self.mode == DeployMode.PROD:
            prod_services = config_services[ServicesType.PROD_SERVICES]
            for service in prod_services:
                image_name = f"{prefix}-{service}"
                image_builder = DockerBuilder(prod_services[service])
                image_builder.build_image(image_name)
            self._logger.info("Deploying production services...")
            self.dc_runner.up_compose(daemon=True)
            self._logger.info("Production services deployed successfully")

    @property
    def _logger(self) -> logging.Logger:
        return logging.getLogger()
