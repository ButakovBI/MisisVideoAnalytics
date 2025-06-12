import setuptools

PACKAGE_NAME = 'misis_api'
VERSION = '1.0.1'
AUTHOR = 'ButakovBI'

setuptools.setup(
    name=PACKAGE_NAME,
    version=VERSION,
    author=AUTHOR,
    description='Misis Backend API',
    packages=setuptools.find_packages(where='source'),
    package_dir={'': 'source'},
    include_package_data=True,
    package_data={'': ['data/*']},
    entry_points={'console_scripts': [f'misis-bootstrap={PACKAGE_NAME}.main:main']},
)
