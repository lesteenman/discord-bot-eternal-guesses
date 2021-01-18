#!/usr/bin/env bash

PROJECT_ROOT="$(pwd)"
if [ ! -f "$PROJECT_ROOT/bin/deploy.sh" ]; then
    echo "this script should be run from the root of the project."
    exit 1
fi

INFRA_DIR="$PROJECT_ROOT/infra"
DISCORD_APP_DIR="$PROJECT_ROOT/discord_app"
DISCORD_APP_BUILD_DIR="$PROJECT_ROOT/discord_app/.build"

if [ -d "$DISCORD_APP_BUILD_DIR" ]; then
    rm -rf "$DISCORD_APP_BUILD_DIR"
fi
mkdir -p "$DISCORD_APP_BUILD_DIR"

#pip install -r "$DISCORD_APP_DIR/requirements.txt" --target "$DISCORD_APP_BUILD_DIR/package/"
docker container run --rm -v $(pwd)/discord_app/:/discord_app python:3.8-buster pip install -r /discord_app/requirements.txt --target /discord_app/.build/package

cd "$DISCORD_APP_BUILD_DIR/package"
zip -r "$DISCORD_APP_BUILD_DIR/deployment.zip" *

cd "$DISCORD_APP_DIR/eternal_guesses"
zip -r -g "$DISCORD_APP_BUILD_DIR/deployment.zip" *

cd "$INFRA_DIR"
cdk deploy
