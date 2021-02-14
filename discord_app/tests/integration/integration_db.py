from typing import List

import boto3
from boto3.dynamodb.table import TableResource

from eternal_guesses.config import load_config
from eternal_guesses.model.data.game import Game

app_config = load_config()


def find_games() -> List[Game]:
    table = _get_table()

    response = table.scan()
    print(response)

    return None


def _get_table() -> TableResource:
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(app_config.dynamodb_table_name)
    return table
