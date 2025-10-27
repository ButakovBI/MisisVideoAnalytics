import logging
import os
import subprocess
from pathlib import Path

from misis_bootstrap.constants import BOOTSTRAP_NAME


class Bootstrap:
    PYPROJECT_FILE = 'pyproject.toml'
    SETUP_FILE = 'setup.py'

    def __init__(self, wheel_dir: Path, root_dir: Path):
        self.wheel_dir = wheel_dir
        self.root_dir = root_dir
        self._clean_wheel_dir()

    def build_wheels(self, packages: list[str]) -> None:
        packages = set(packages)
        found_packages = self._find_packages()

        if BOOTSTRAP_NAME in packages:
            self._build_package(BOOTSTRAP_NAME, found_packages)
            packages.remove(BOOTSTRAP_NAME)

        for name in packages:
            self._build_package(name, found_packages)

    def _build_package(self, name: str, found_packages: dict[str, Path]) -> None:
        if name not in found_packages:
            raise RuntimeError(f"[bootstrap] Package not found: {name}")

        self._logger.info(f"Building package: {name}")

        try:
            subprocess.run([
                "pip3", "wheel",
                "--no-deps",
                "--no-build-isolation",
                "--wheel-dir", str(self.wheel_dir),
                str(found_packages[name])
            ], check=True)
            self._logger.info(f"Built wheel for {name}")
        except Exception as e:
            self._logger.error(f"Failed to build wheel for {name}: {e}")
            raise RuntimeError(f"[bootstrap] Build failed for {name}")

    def _clean_wheel_dir(self) -> None:
        if self.wheel_dir.exists():
            for f in self.wheel_dir.glob("*"):
                f.unlink()
        self.wheel_dir.mkdir(parents=True, exist_ok=True)

    def _find_packages(self) -> dict[str, Path]:
        result = {}
        for root, _, files in os.walk(self.root_dir):
            root_path = Path(root)
            if self.PYPROJECT_FILE in files and self.SETUP_FILE in files:
                result[root_path.name] = root_path
        return result

    @property
    def _logger(self) -> logging.Logger:
        return logging.getLogger(name=BOOTSTRAP_NAME)
