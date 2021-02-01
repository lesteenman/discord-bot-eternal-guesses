#!/usr/bin/env bash
set -e

cd discord_app/
poetry run flake8 --config=../.flake8
poetry run pytest
