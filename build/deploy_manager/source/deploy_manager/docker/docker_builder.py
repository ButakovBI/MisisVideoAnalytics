import logging
import subprocess

from deploy_manager.constants import DOCKERFILE, LIBS, PROJECT_ROOT


class DockerBuilder:
    def __init__(self, config: dict):
        self._added_libs = ' '.join(config.get(LIBS))
        self._config_data = config

    def build_image(self, image_name: str) -> None:
        dockerfile_path = PROJECT_ROOT / self._config_data[DOCKERFILE]
        cmd = ['docker', 'build', '-f', str(dockerfile_path), '-t', image_name]

        if self._added_libs:
            cmd += ['--build-arg', f'{LIBS}={self._added_libs}']

        cmd.append(str(PROJECT_ROOT))
        self._logger.info(f'Building image {image_name}...')
        try:
            subprocess.check_call(cmd)
            self._logger.info(f'Image {image_name} built successfully')
        except Exception as ex:
            msg = f'Error while building image {image_name}: {ex}'
            self._logger.error(msg)
            raise RuntimeError(msg)

    @property
    def _logger(self) -> logging.Logger:
        return logging.getLogger()

