#!/bin/bash

set -e

export REPO_ROOT=$(pwd)

rm -rf "$REPO_ROOT/build/whl"
mkdir -p "$REPO_ROOT/build/whl"

echo "Installing bootstrap..."
pip3 install "$REPO_ROOT/build/misis_bootstrap"

echo "Building packages..."
misis-bootstrap

echo "Verifying wheels..."
if [ -z "$(ls -A "$REPO_ROOT/build/whl")" ]; then
    echo "Error: No wheels built!"
    exit 1
fi

echo "Installing builder..."
pip3 install "$REPO_ROOT"/build/whl/misis_builder-*.whl

if [[ "$1" == "--test" ]]; then
    misis-build-run --test
else
    misis-build-run
fi