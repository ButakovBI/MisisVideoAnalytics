import setuptools

PACKAGE_NAME = 'misis_bootstrap'
VERSION = '1.0.0'
AUTHOR = 'ButakovBI'

setuptools.setup(
    name=PACKAGE_NAME,
    version=VERSION,
    author=AUTHOR,
    description='Misis Bootstrap',
    packages=setuptools.find_packages(where='source'),
    package_dir={'': 'source'},
    entry_points={'console_scripts': [f'misis-bootstrap={PACKAGE_NAME}.main:main']},
)
