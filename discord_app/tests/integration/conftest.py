import opnieuw
import pytest
from pynamodb.exceptions import TableError

from eternal_guesses.repositories.dynamodb_models import EternalGuessesTable

REGION = "eu-west-1"
TABLE_NAME = "eternal-guesses-test"
HOST = "http://127.0.0.1:8000"
ACCESS_KEY_ID = "LOCAL"


# @pytest.fixture(scope="session", autouse=True)
# def start_dynamodb_container():
#     docker_client = docker.from_env()
#     dynamodb_container = docker_client.containers.run('amazon/dynamodb-local', ports={8000: 8000}, detach=True,
#                                                       auto_remove=True)
#
#     yield
#
#     dynamodb_container.stop()


@opnieuw.retry(retry_on_exceptions=TableError, max_calls_total=10, retry_window_after_first_call_in_seconds=5)
def _create_table():
    EternalGuessesTable.Meta.table_name = TABLE_NAME
    EternalGuessesTable.Meta.host = HOST
    EternalGuessesTable.Meta.region = REGION
    EternalGuessesTable.Meta.aws_access_key_id = ACCESS_KEY_ID
    EternalGuessesTable.Meta.aws_secret_access_key = "ANY"
    EternalGuessesTable.create_table(read_capacity_units=1, write_capacity_units=1, wait=True)


@opnieuw.retry(retry_on_exceptions=TableError, max_calls_total=10, retry_window_after_first_call_in_seconds=5)
def _delete_table():
    EternalGuessesTable.delete_table()


@pytest.fixture(autouse=True)
def create_test_database():
    _create_table()

    yield

    _delete_table()
