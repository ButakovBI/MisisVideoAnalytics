import setuptools

PACKAGE_NAME = 'misis_builder'
VERSION = '1.0.1'
AUTHOR = 'ButakovBI'


setuptools.setup(
    name=PACKAGE_NAME,
    version=VERSION,
    author=AUTHOR,
    description='Misis Builder',
    packages=setuptools.find_packages(where='source'),
    package_dir={'': 'source'},
    entry_points={'console_scripts': [f'misis-build-run={PACKAGE_NAME}.main:main']},
)
