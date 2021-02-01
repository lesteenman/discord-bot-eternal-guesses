#!/usr/bin/env bash
set -e

PROJECT_ROOT="$(pwd)"
if [ ! -f "$PROJECT_ROOT/bin/deploy.sh" ]; then
    echo "this script should be run from the root of the project."
    exit 1
fi

./bin/test.sh
./bin/build.sh
./bin/deploy.sh
