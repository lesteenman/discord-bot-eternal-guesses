#!/usr/bin/env bash
set -eou pipefail

PROJECT_ROOT="$(pwd)"
if [ ! -f "$PROJECT_ROOT/bin/deploy.sh" ]; then
    echo "this script should be run from the root of the project."
    exit 1
fi

DISCORD_APP_DIR="$PROJECT_ROOT/discord_app"

cd $DISCORD_APP_DIR
poetry run flake8 --config $PROJECT_ROOT/.flake8 ./tests ./eternal_guesses ../error_parser_function
poetry run pytest
