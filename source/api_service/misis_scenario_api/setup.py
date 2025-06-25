import setuptools

PACKAGE_NAME = 'misis_scenario_api'
VERSION = '2.2.0'
AUTHOR = 'ButakovBI'

REQUIRES = [
    "aioboto3",
    "aiokafka",
    "fastapi",
    "httpx",
    "pydantic",
    "uvicorn[standard]"
]

setuptools.setup(
    name=PACKAGE_NAME,
    version=VERSION,
    author=AUTHOR,
    description='Misis Scenario API',
    packages=setuptools.find_packages(where='source'),
    package_dir={'': 'source'},
    install_requires=REQUIRES
)
