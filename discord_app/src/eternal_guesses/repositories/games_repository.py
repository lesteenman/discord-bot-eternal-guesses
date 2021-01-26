from pprint import pprint
from typing import Optional, Dict

import boto3
from eternal_guesses.model.data.game import Game
from eternal_guesses.config import load_config


def make_game(guild_id: str, game_id: str, item: Dict):
    game = Game()

    game.guild_id = guild_id
    game.game_id = game_id
    game.guesses = item['guesses']

    return game


class GamesRepository:
    @staticmethod
    def get(guild_id: str, game_id: str) -> Optional[Game]:
        table = GamesRepository._get_table()

        response = table.get_item(Key={
            "pk": f"GUILD#{guild_id}",
            "sk": f"GAME#{game_id}",
        })
        pprint(response)

        if 'Item' not in response:
            return None

        item = response['Item']
        return make_game(guild_id, game_id, item)

    @staticmethod
    def put(guild_id: str, game: Game):
        assert game.game_id is not None

        table = GamesRepository._get_table()

        response = table.put_item(
            Item={
                "pk": f"GUILD#{guild_id}",
                "sk": f"GAME#{game.game_id}",
                "guesses": game.guesses,
            }
        )
        pprint(response)

    @staticmethod
    def _get_table():
        dynamodb = boto3.resource('dynamodb')
        config = load_config()
        table = dynamodb.Table(config.dynamodb_table_name)
        # table.load()
        return table
