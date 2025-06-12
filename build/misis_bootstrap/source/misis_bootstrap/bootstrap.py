import os
import json
import subprocess
from pathlib import Path
from typing import List


class Bootstrap:
    def __init__(self, wheel_dir: Path, root_dir: Path):
        self.wheel_dir = wheel_dir
        self.root_dir = root_dir
        if self.wheel_dir.exists():
            for f in self.wheel_dir.glob("*"):
                f.unlink()
        self.wheel_dir.mkdir(parents=True, exist_ok=True)

    def build_wheels(self, packages: List[str]):
        found_packages = self._find_packages()

        for name in packages:
            if name in found_packages:
                print(f"[bootstrap] Building package: {name}")
                subprocess.run([
                    "pip3", "wheel", "--no-deps",
                    "--wheel-dir", str(self.wheel_dir),
                    str(found_packages[name])
                ], check=True)
            else:
                raise RuntimeError(f"[bootstrap] Package not found: {name}")

    def _find_packages(self) -> dict:
        result = {}
        for root, _, files in os.walk(self.root_dir):
            root_path = Path(root)
            if "pyproject.toml" in files:
                lines = (root_path / "pyproject.toml").read_text(encoding="utf-8").splitlines()
                for line in lines:
                    if line.strip().startswith("name"):
                        name = line.split("=", 1)[1].strip().strip('"').strip("'")
                        result[name] = root_path
                        break
            if "setup.py" in files:
                result[root_path.name] = root_path
        return result

    def _load_versions(self, path: Path) -> dict:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        return {item["name"]: item["version"] for item in data}
