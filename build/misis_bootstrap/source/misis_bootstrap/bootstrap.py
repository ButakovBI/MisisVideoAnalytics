import os
import subprocess
from pathlib import Path
from typing import List


class Bootstrap:
    def __init__(self, wheel_dir: Path, root_dir: Path):
        self.wheel_dir = wheel_dir
        self.root_dir = root_dir
        self._clean_wheel_dir()

    def build_wheels(self, packages: List[str]):
        found_packages = self._find_packages()

        if "misis_bootstrap" in packages:
            self._build_package("misis_bootstrap", found_packages)
            packages.remove("misis_bootstrap")

        for name in packages:
            self._build_package(name, found_packages)

    def _build_package(self, name: str, found_packages: dict[str, Path]):
        if name not in found_packages:
            raise RuntimeError(f"[bootstrap] Package not found: {name}")

        print(f"[bootstrap] Building package: {name}")
        subprocess.run([
            "pip", "wheel",
            "--no-deps",
            "--no-build-isolation",
            "--wheel-dir", str(self.wheel_dir),
            str(found_packages[name])
        ], check=True)

    def _clean_wheel_dir(self):
        if self.wheel_dir.exists():
            for f in self.wheel_dir.glob("*"):
                f.unlink()
        self.wheel_dir.mkdir(parents=True, exist_ok=True)

    def _find_packages(self) -> dict:
        result = {}
        for root, _, files in os.walk(self.root_dir):
            root_path = Path(root)
            if "pyproject.toml" in files or "setup.py" in files:
                result[root_path.name] = root_path
        return result
