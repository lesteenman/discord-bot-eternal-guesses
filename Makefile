test:
	cd discord_app && poetry run flake8 --config ../.flake8 ./tests ./eternal_guesses ../error_parser_function
	cd discord_app && poetry run pytest
