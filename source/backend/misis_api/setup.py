import setuptools

from misis_bootstrap.package_manager import PackageManager

PACKAGE_NAME = 'misis_api'
VERSION = '1.0.1'
AUTHOR = 'ButakovBI'

REQUIRES = [
    "fastapi",
    "uvicorn"
]

setuptools.setup(
    name=PACKAGE_NAME,
    version=VERSION,
    author=AUTHOR,
    description='Misis Backend API',
    packages=setuptools.find_packages(where='source'),
    package_dir={'': 'source'},
    install_requires=PackageManager.get_versioned_packages(REQUIRES)
)
