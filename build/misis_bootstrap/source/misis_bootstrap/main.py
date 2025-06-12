import os
from pathlib import Path

from misis_bootstrap.package_manager import PackageManager
from misis_bootstrap.bootstrap import Bootstrap

PROJECT_ROOT = Path(os.environ['REPO_ROOT']).resolve()


def main():
    wheel_dir = PROJECT_ROOT / "build" / "whl"

    local_packages = PackageManager.get_local_packages()

    bootstrap = Bootstrap(wheel_dir, PROJECT_ROOT)
    bootstrap.build_wheels(local_packages)
