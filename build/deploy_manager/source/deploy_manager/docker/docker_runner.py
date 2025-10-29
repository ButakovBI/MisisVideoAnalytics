import logging
import subprocess


class DockerRunner:
    @staticmethod
    def run_container(self, image: str):
        cmd = ['docker', 'run', '--rm', image]
        self._execute_cmd(cmd)

    def _execute_cmd(self, cmd: list[str]):
        try:
            subprocess.check_call(cmd)
        except Exception as ex:
            msg = f"Error while run {cmd}: {ex}"
            self._logger.error(msg)
            raise RuntimeError(msg)

    @property
    def _logger(self) -> logging.Logger:
        return logging.getLogger()
