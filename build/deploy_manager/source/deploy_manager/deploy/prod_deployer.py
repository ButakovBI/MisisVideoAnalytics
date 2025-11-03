from deploy_manager.common.subprocess_executor import SubprocessExecutor
from deploy_manager.docker.docker_builder import DockerBuilder
from deploy_manager.constants import SERVICES_SECTION, DeployMode, ServicesType
from deploy_manager.deploy.deployer_abstract import Deployer, DockerComposeRunner


class ProdDeployer(Deployer):
    def __init__(self,
                 config_data: dict,
                 dc_runner: DockerComposeRunner,
                 executor: SubprocessExecutor,):
        super().__init__(config_data, dc_runner=dc_runner, executor=executor)

    def deploy(self) -> None:
        config_services = self.config_data[SERVICES_SECTION]
        prod_services = config_services[ServicesType.PROD_SERVICES.value]

        builder = DockerBuilder(self._executor)
        self._logger.info("Deploying production services...")

        for service_name, service_conf in prod_services.items():
            image_name = f"{DeployMode.PROD.value}-{service_name}"
            builder.build_image(service_conf, image_name)

        self._dc_runner.up_compose(daemon=True)

        self._logger.info("Production services deployed successfully")
