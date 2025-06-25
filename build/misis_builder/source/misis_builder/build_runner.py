import json
import os
import subprocess
from pathlib import Path
from typing import List, Optional


class BuildRunner:
    def __init__(self, config_path: Path):
        self.config_path = config_path
        self.repo_root = Path(os.environ['REPO_ROOT']).resolve()

    def build_image(self, service: str, config: dict) -> str:
        dockerfile_path = self.repo_root / config['dockerfile']
        image = f"misis-{service}"
        cmd = ['docker', 'build', '-f', str(dockerfile_path), '-t', image]
        if 'LIBS' in config:
            cmd += ['--build-arg', f"LIBS={' '.join(config['LIBS'])}"]
        cmd.append(str(self.repo_root))
        print(f"Building image {image} (Dockerfile: {config['dockerfile']})…")
        subprocess.check_call(cmd)
        return image

    def execute(self, test_mode: bool = False):
        config = json.load(open(self.config_path))

        if test_mode:
            test_services = [service for service in config if service.startswith('test_')]
            for service in test_services:
                self.build_image(service, config[service])
            for service in test_services:
                conf = config[service]
                image = f"misis-{service}"
                if 'compose_file' in conf:
                    self.run_compose(self.repo_root / conf['compose_file'])
                else:
                    self.run_container(image, conf.get('cmd_override'))
        else:
            for service, conf in config.items():
                if not service.startswith('test_'):
                    self.build_image(service, conf)
            print("Deploying production services…")
            prod_compose = self.repo_root / 'build' / 'docker' / 'docker_compose.yml'
            subprocess.check_call(['docker-compose', '-f', str(prod_compose), 'up', '-d'])

    def run_compose(self, compose_file: Path):
        print(f"Up test stack '{compose_file.name}'…")
        subprocess.check_call([
            'docker-compose', '-f', str(compose_file),
            'up', '--abort-on-container-exit'
        ])
        print(f"Tearing down test stack '{compose_file.name}'…")
        subprocess.call([
            'docker-compose', '-f', str(compose_file),
            'down', '--volumes'
        ])

    def run_container(self, image: str, cmd_override: Optional[List[str]] = None):
        cmd = ['docker', 'run', '--rm', image]
        if cmd_override:
            cmd += cmd_override
            print(f"Running {image} with override: {' '.join(cmd_override)}…")
        else:
            print(f"Running {image}…")
        result = subprocess.run(cmd)
        if result.returncode not in (0, 5):
            raise subprocess.CalledProcessError(result.returncode, cmd)
