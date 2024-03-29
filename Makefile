DISCORD_APP_DIR=discord_app
ERROR_PARSER_DIR=error_parser_function
INFRA_DIR=infra

autopep:
	python -m autopep8 --recursive --in-place --aggressive discord_app/eternal_guesses
	python -m autopep8 --recursive --in-place --aggressive discord_app/tests
	python -m autopep8 --recursive --in-place --aggressive error_parser_function/
	python -m autopep8 --recursive --in-place --aggressive infra/app.py
	python -m autopep8 --recursive --in-place --aggressive infra/infra/

quality:
	cd ${DISCORD_APP_DIR} && poetry run flake8 --config ../.flake8 ./tests ./eternal_guesses ../error_parser_function ../infra

test: quality
	cd ${DISCORD_APP_DIR} && poetry run pytest

build:
	cd ${DISCORD_APP_DIR} && serverless package
	cd ${ERROR_PARSER_DIR} && serverless package

deploy:
	cd ${INFRA_DIR} && poetry run cdk deploy

all: test build deploy
