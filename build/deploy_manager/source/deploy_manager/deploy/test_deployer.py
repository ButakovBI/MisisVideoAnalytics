from deploy_manager.common.subprocess_executor import SubprocessExecutor
from deploy_manager.docker.docker_builder import DockerBuilder
from deploy_manager.constants import SERVICES_SECTION, DeployMode, ServicesType
from deploy_manager.deploy.deployer_abstract import Deployer
from deploy_manager.docker.docker_compose_runner import DockerComposeRunner


class TestDeployer(Deployer):
    def __init__(self,
                 config_data: dict,
                 dc_runner: DockerComposeRunner,
                 executor: SubprocessExecutor,):
        super().__init__(config_data, dc_runner=dc_runner, executor=executor)

    def deploy(self) -> None:
        config_services = self.config_data[SERVICES_SECTION]
        test_services = config_services[ServicesType.TEST_SERVICES.value]

        builder = DockerBuilder(self._executor)

        for service_name, service_conf in test_services.items():
            image_name = f"{DeployMode.TEST.value}-{service_name}"
            builder.build_image(service_conf, image_name)

        self._logger.info("Test images build successfully")
