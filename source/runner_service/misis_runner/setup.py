import setuptools

from misis_bootstrap.package_manager import PackageManager

PACKAGE_NAME = 'misis_runner'
VERSION = '1.0.0'
AUTHOR = 'ButakovBI'

REQUIRES = [
    'opencv-python-headless',
    'requests',
    'confluent-kafka',

    "misis_healthcheck"
]

setuptools.setup(
    name=PACKAGE_NAME,
    version=VERSION,
    author=AUTHOR,
    description='Misis Runner',
    packages=setuptools.find_packages(where='source'),
    package_dir={'': 'source'},
    install_requires=PackageManager.get_versioned_packages(REQUIRES),
)
