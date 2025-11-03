import logging

from deploy_manager.common.subprocess_executor import SubprocessExecutor
from deploy_manager.constants import DOCKERFILE, LIBS, PROJECT_ROOT


class DockerBuilder:
    def __init__(self, executor: SubprocessExecutor):
        self._executor = executor

    def build_image(self, config_data: dict, image_name: str) -> None:
        dockerfile_path = PROJECT_ROOT / config_data[DOCKERFILE]
        cmd = ['docker', 'build', '-f', str(dockerfile_path), '-t', image_name]

        added_libs = ' '.join(config_data.get(LIBS, []))
        if added_libs:
            cmd += ['--build-arg', f'{LIBS}={added_libs}']

        cmd.append(str(PROJECT_ROOT))
        self._logger.info(f'Building image {image_name}...')
        error_context = f'Error while building image {image_name}'
        self._executor.execute_cmd(cmd, error_context)

    @property
    def _logger(self) -> logging.Logger:
        return logging.getLogger(__name__)
