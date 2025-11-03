import os
from enum import StrEnum
from pathlib import Path

PROJECT_ROOT = Path(os.environ['REPO_ROOT']).resolve()

BUILD_DIR = 'build'
DOCKER_DIR = 'docker'
DOCKERFILE = 'dockerfile'
ERROR = 'Error'
LIBS = 'LIBS'
SERVICES_SECTION = 'services'

DEFAULT_IMAGES_CONF_PATH = PROJECT_ROOT / BUILD_DIR / DOCKER_DIR / 'images_configuration.json'
DEFAULT_COMPOSE_PATH = PROJECT_ROOT / BUILD_DIR / DOCKER_DIR / 'docker_compose.yml'


class DeployMode(StrEnum):
    PROD = 'prod'
    TEST = 'test'


class ServicesType(StrEnum):
    PROD_SERVICES = 'prod_services'
    TEST_SERVICES = 'test_services'
