#!/usr/bin/env bash
set -e

export PYTHONPATH="$PYTHONPATH:./discord_app/eternal_guesses"

pytest discord_app/
flake8 discord_app/
