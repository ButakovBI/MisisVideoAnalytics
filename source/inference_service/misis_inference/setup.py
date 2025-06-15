import setuptools

from misis_bootstrap.package_manager import PackageManager

PACKAGE_NAME = 'misis_inference'
VERSION = '1.0.0'
AUTHOR = 'ButakovBI'

REQUIRES = [
    "fastapi",
    "httpx",
    "opencv-python-headless",
    "numpy",
    "pydantic",
    "uvicorn[standard]",
    "python-multipart"
]

setuptools.setup(
    name=PACKAGE_NAME,
    version=VERSION,
    author=AUTHOR,
    description='Misis Inference',
    packages=setuptools.find_packages(where='source'),
    package_dir={'': 'source'},
    install_requires=PackageManager.get_versioned_packages(REQUIRES)
)
