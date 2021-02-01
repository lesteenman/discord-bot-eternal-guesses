import logging
import re
from datetime import datetime
from pprint import pformat
from typing import Optional, Dict, List

import boto3
from boto3.dynamodb.conditions import Key
from eternal_guesses.config import load_config
from eternal_guesses.model.data.game import Game, ChannelMessage
from eternal_guesses.model.data.game_guess import GameGuess

log = logging.getLogger(__name__)

SK_REGEX = r"GAME#(.*)"


def make_game(guild_id: int, item: Dict):
    game = Game()

    game.guild_id = guild_id
    game.game_id = re.match(SK_REGEX, item.get('sk')).group(1)
    game.created_by = item.get('created_by')
    game.closed = item.get('closed', False)
    game.create_datetime = datetime.fromisoformat(item.get('create_datetime'))

    if 'close_datetime' in item:
        game.close_datetime = datetime.fromisoformat(
            item.get('close_datetime'))
    else:
        game.close_datetime = None

    game_guesses = {}
    for user_id, guess_dict in item.get('guesses', {}).items():
        game_guess = GameGuess()
        game_guess.user_id = user_id
        game_guess.nickname = guess_dict['nickname']
        game_guess.guess = guess_dict['guess']
        game_guess.datetime = datetime.fromisoformat(guess_dict['datetime'])
        game_guesses[user_id] = game_guess

    game.guesses = game_guesses

    channel_messages = []
    for channel_message in item.get('channel_messages', []):
        channel_messages.append(
            ChannelMessage(
                channel_message['channel_id'],
                channel_message['message_id']))

    game.channel_messages = channel_messages

    return game


class GamesRepository:
    @staticmethod
    def get(guild_id: int, game_id: str) -> Optional[Game]:
        table = GamesRepository._get_table()

        key = {
            "pk": f"GUILD#{guild_id}",
            "sk": f"GAME#{game_id}",
        }

        log.debug(f"getting item, key={key}")

        response = table.get_item(Key=key)

        if log.isEnabledFor(logging.DEBUG):
            log.debug(f"table.get_item response: {pformat(response)}")

        if 'Item' not in response:
            return None

        item = response['Item']
        return make_game(guild_id, item)

    @staticmethod
    def get_all(guild_id: int) -> List[Game]:
        table = GamesRepository._get_table()

        key_condition_expression = Key('pk').eq(f"GUILD#{guild_id}") & \
            Key('sk').begins_with("GAME#")

        log.debug(f"getting item, key={key_condition_expression}")

        response = table.query(
            KeyConditionExpression=key_condition_expression
        )

        if log.isEnabledFor(logging.DEBUG):
            log.debug(f"table.get_item response: {pformat(response)}")

        games = list(make_game(guild_id, item)
                     for item in response.get('Items', []))

        return games

    @staticmethod
    def save(guild_id: int, game: Game):
        assert game.game_id is not None

        table = GamesRepository._get_table()

        item = {
            "pk": f"GUILD#{guild_id}",
            "sk": f"GAME#{game.game_id}",
            "create_datetime": game.create_datetime.isoformat(),
            "created_by": game.created_by,
            "closed": game.closed,
            "guesses": {user_id: {
                'user_id': game_guess.user_id,
                'nickname': game_guess.nickname,
                'guess': game_guess.guess,
                'datetime': game_guess.datetime.isoformat(),
            } for (user_id, game_guess) in game.guesses.items()},
            "channel_messages": list({'message_id': message.message_id, 'channel_id': message.channel_id}
                                     for message in game.channel_messages),
        }

        log.debug(f"saving item, item={item}")

        response = table.put_item(
            Item=item
        )

        if log.isEnabledFor(logging.DEBUG):
            log.debug(f"table.put_item response: {pformat(response)}")

    @staticmethod
    def _get_table():
        dynamodb = boto3.resource('dynamodb')
        config = load_config()
        table = dynamodb.Table(config.dynamodb_table_name)
        return table
