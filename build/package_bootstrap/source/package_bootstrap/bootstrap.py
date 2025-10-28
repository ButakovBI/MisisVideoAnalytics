import logging
import subprocess
from pathlib import Path

from package_bootstrap.constants import BOOTSTRAP_NAME
from package_bootstrap.package_manager import PackageManager


class Bootstrap:

    def __init__(self, wheel_dir: Path, root_dir: Path):
        self.wheel_dir = wheel_dir
        self.root_dir = root_dir
        self._clean_wheel_dir()

    def build_wheels(self, packages: list[str]) -> None:
        packages = set(packages)
        found_packages = PackageManager.discover_local_packages(self.root_dir)

        if BOOTSTRAP_NAME in packages:
            self._build_package(BOOTSTRAP_NAME, found_packages)
            packages.remove(BOOTSTRAP_NAME)

        for name in packages:
            self._build_package(name, found_packages)

    def _build_package(self, name: str, found_packages: dict[str, Path]) -> None:
        if name not in found_packages:
            raise RuntimeError(f"[{BOOTSTRAP_NAME}] Package not found: {name}")

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
            raise RuntimeError(f"[{BOOTSTRAP_NAME}] Build failed for {name}")

    def _clean_wheel_dir(self) -> None:
        if self.wheel_dir.exists():
            for f in self.wheel_dir.glob("*"):
                f.unlink()
        self.wheel_dir.mkdir(parents=True, exist_ok=True)

    @property
    def _logger(self) -> logging.Logger:
        return logging.getLogger(name=BOOTSTRAP_NAME)
