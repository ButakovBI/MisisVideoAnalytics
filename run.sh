#!/bin/bash

set -e

export REPO_ROOT=$(pwd)

rm -rf "$REPO_ROOT/build/whl"
mkdir -p "$REPO_ROOT/build/whl"

echo "Installing bootstrap..."
pip3 install -e "$REPO_ROOT/build/misis_bootstrap"

echo "Building packages..."
misis-bootstrap

echo "Verifying wheels..."
if [ -z "$(ls -A "$REPO_ROOT/build/whl")" ]; then
    echo "Error: No wheels built!"
    exit 1
fi

echo "Bootstrap completed successfully"

if [[ "$1" == "--test" ]]; then
    python3 $REPO_ROOT/build/docker/build_all.py --test
else
    python3 $REPO_ROOT/build/docker/build_all.py
fi
