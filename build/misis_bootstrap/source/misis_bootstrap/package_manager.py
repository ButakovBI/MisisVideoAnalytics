import json
import os
from pathlib import Path

DEFAULT_VERSIONS_PATH = Path(os.environ['REPO_ROOT']).resolve() / "build" / "misis_bootstrap" / "versions.json"


class PackageManager:
    _versions: dict[str, str] | None = None

    @classmethod
    def get_version(cls, name: str, versions_file: Path | None = None):
        cls._load_versions(versions_file)
        return cls._versions.get(name)

    @classmethod
    def get_versioned_packages(cls, names: list[str], versions_file: Path | None = None) -> list[str]:
        cls._load_versions(versions_file)
        res = []
        for name in names:
            if name in cls._versions:
                res.append(f"{name}=={cls._versions[name]}")
            else:
                res.append(name)
        return res

    @classmethod
    def get_local_packages(cls, versions_file: Path | None = None, prefix: str = 'misis_') -> list[str]:
        cls._load_versions(versions_file)
        return [name for name in cls._versions if name.startswith(prefix)]

    @classmethod
    def _load_versions(cls, versions_file: Path | None = None) -> None:
        if cls._versions is not None:
            return
        path = versions_file or DEFAULT_VERSIONS_PATH
        with path.open(encoding='utf-8') as f:
            raw = json.load(f)
        cls._versions = {item['name']: item['version'] for item in raw}
