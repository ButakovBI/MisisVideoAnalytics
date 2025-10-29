import logging
import subprocess


class DockerComposeRunner:
    down_command = 'down'
    up_command = 'up'
    def __init__(self, compose_file: str):
        self._base_cmd = ['docker-compose', '-f', compose_file]

    def down_compose(self) -> None:
        cmd = self._base_cmd + [self.down_command]
        self._execute_cmd(cmd)

    def up_compose(self, daemon: bool = True) -> None:
        cmd = self._base_cmd + [self.up_command]
        if daemon:
            cmd.append('-d')
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
