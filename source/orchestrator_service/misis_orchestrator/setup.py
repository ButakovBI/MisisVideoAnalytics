import setuptools

from misis_bootstrap.package_manager import PackageManager

PACKAGE_NAME = 'misis_orchestrator'
VERSION = '1.0.1'
AUTHOR = 'ButakovBI'

REQUIRES = [
    "confluent_kafka",
    "fastapi",
    "httpx",
    "psycopg2-binary",
    "pydantic",
    "sqlalchemy",
    "uvicorn",

    "misis_healthcheck"
]

setuptools.setup(
    name=PACKAGE_NAME,
    version=VERSION,
    author=AUTHOR,
    description='Misis Orchestrator',
    packages=setuptools.find_packages(where='source'),
    package_dir={'': 'source'},
    install_requires=PackageManager.get_versioned_packages(REQUIRES),
)
