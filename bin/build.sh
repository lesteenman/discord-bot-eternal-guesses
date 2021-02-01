#!/usr/bin/env bash
set -e

PROJECT_ROOT="$(pwd)"
if [ ! -f "$PROJECT_ROOT/bin/deploy.sh" ]; then
    echo "this script should be run from the root of the project."
    exit 1
fi

DISCORD_APP_DIR="$PROJECT_ROOT/discord_app"
ERROR_PARSER_DIR="$PROJECT_ROOT/error_parser_function"

# Package discord-app
cd $DISCORD_APP_DIR
serverless package

# Package error-parser
cd $ERROR_PARSER_DIR
serverless package
