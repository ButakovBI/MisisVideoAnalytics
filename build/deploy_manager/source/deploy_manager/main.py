import argparse

from misis_builder.build_runner import BuildRunner


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--test', action='store_true',
                        help='Build test images and run all tests')
    args = parser.parse_args()

    BuildRunner().execute(args.test)
