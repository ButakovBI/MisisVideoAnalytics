import argparse
from pathlib import Path

from misis_builder.build_runner import BuildRunner


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--config',
                        default='build/docker/images_configuration.json',
                        help='Path to JSON config')
    parser.add_argument('--test', action='store_true',
                        help='Build test images and run all tests')
    args = parser.parse_args()

    BuildRunner(Path(args.config)).execute(args.test)
