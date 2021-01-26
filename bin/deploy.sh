#!/usr/bin/env bash
set -e

PROJECT_ROOT="$(pwd)"
if [ ! -f "$PROJECT_ROOT/bin/deploy.sh" ]; then
    echo "this script should be run from the root of the project."
    exit 1
fi

INFRA_DIR="$PROJECT_ROOT/infra"
DISCORD_APP_DIR="$PROJECT_ROOT/discord_app"

# Tox tests
cd $DISCORD_APP_DIR
tox

# Package using a Python container to be cross-platform
cd $PROJECT_ROOT
docker run \
    --rm \
    --workdir=/discord_app \
    -v "$DISCORD_APP_DIR":/discord_app \
    python:3.8-buster \
    python setup.py ldist

# Deploy
cd "$INFRA_DIR"
cdk deploy
