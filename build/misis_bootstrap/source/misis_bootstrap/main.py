import os
from misis_bootstrap.bootstrap import Bootstrap
from pathlib import Path
import json


def main():
    PROJECT_ROOT = Path(os.environ['REPO_ROOT']).resolve()
    config_path = PROJECT_ROOT / "build" / "docker" / "images_configuration.json"
    wheel_dir = PROJECT_ROOT / "build" / "whl"

    config = json.loads(config_path.read_text(encoding='utf-8'))

    all_packages = set()
    for service in config.values():
        all_packages.update(service.get("LIBS", []))

    misis_packages = [pkg for pkg in all_packages if pkg.startswith("misis_")]

    bootstrap = Bootstrap(wheel_dir, PROJECT_ROOT)
    bootstrap.build_wheels(misis_packages)
