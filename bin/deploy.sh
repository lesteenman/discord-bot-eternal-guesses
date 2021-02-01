#!/usr/bin/env bash
set -e

PROJECT_ROOT="$(pwd)"
if [ ! -f "$PROJECT_ROOT/bin/deploy.sh" ]; then
    echo "this script should be run from the root of the project."
    exit 1
fi

INFRA_DIR="$PROJECT_ROOT/infra"
DISCORD_APP_DIR="$PROJECT_ROOT/discord_app"

# Tox and flake8 checking
cd $DISCORD_APP_DIR
poetry run flake8 --config $PROJECT_ROOT/.flake8
poetry run pytest

# Package using a Python container to be cross-platform
cd $DISCORD_APP_DIR
serverless package

cd "error_parser_function"
mkdir -p dist/
zip dist/error_parser_function.zip parser.py

# Deploy
cd "$INFRA_DIR"
cdk deploy
