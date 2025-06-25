import setuptools

PACKAGE_NAME = 'misis_inference'
VERSION = '2.0.1'
AUTHOR = 'ButakovBI'

REQUIRES = [
    "fastapi",
    "httpx",
    "pydantic",
    "pydantic_settings",
    "python-multipart",
    "ultralytics",
    "uvicorn[standard]",
]

setuptools.setup(
    name=PACKAGE_NAME,
    version=VERSION,
    author=AUTHOR,
    description='Misis Inference',
    packages=setuptools.find_packages(where='source'),
    package_dir={'': 'source'},
    install_requires=REQUIRES
)
