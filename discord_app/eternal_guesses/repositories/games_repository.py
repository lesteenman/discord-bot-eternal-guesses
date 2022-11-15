import json
import re
from abc import ABC
from datetime import datetime
from typing import Optional, List

from boto3.dynamodb.conditions import Key

from eternal_guesses.model.data.channel_message import ChannelMessage
from eternal_guesses.model.data.game import Game
from eternal_guesses.model.data.game_guess import GameGuess

PK_REGEX = r"GUILD#(.*)"
SK_REGEX = r"GAME#(.*)"


def _channel_message_from_model(message_model: dict):
    return ChannelMessage(
        channel_id=message_model['channel_id'],
        message_id=message_model['message_id']
    )


def _guess_from_model(guess_model):
    return GameGuess(
        user_id=guess_model['user_id'],
        guess=guess_model['guess'],
        nickname=guess_model['nickname'],
        timestamp=datetime.fromisoformat(guess_model['timestamp']),
    )


def _game_from_model(model: dict) -> Game:
    guild_id = int(re.match(PK_REGEX, model['pk']).group(1))
    game_id = re.match(SK_REGEX, model['sk']).group(1)

    create_datetime = None
    if 'create_datetime' in model:
        create_datetime = datetime.fromisoformat(model['create_datetime'])

    close_datetime = None
    if 'close_datetime' in model:
        close_datetime = datetime.fromisoformat(model['close_datetime'])

    closed = model.get('closed', False) or False
    title = model.get('title', '') or ''
    description = model.get('description', '') or ''
    min_guess = model.get('min_guess' or None)
    max_guess = model.get('max_guess' or None)

    channel_messages = []
    if 'channel_messages' in model:
        channel_messages = list(
            _channel_message_from_model(message_model) for message_model in
            model['channel_messages']
        )

    guesses = {}
    if 'guesses' in model:
        for (user_id, guess_model) in json.loads(model['guesses']).items():
            guesses[int(user_id)] = _guess_from_model(guess_model)

    return Game(
        guild_id=guild_id,
        game_id=game_id,
        title=title,
        description=description,
        min_guess=min_guess,
        max_guess=max_guess,
        created_by=model['created_by'],
        create_datetime=create_datetime,
        close_datetime=close_datetime,
        closed=closed,
        channel_messages=channel_messages,
        guesses=guesses,
    )


def _hash_key(guild_id: int):
    return f"GUILD#{guild_id}"


def _range_key(game_id: str):
    return f"GAME#{game_id}"


class GamesRepository(ABC):
    def get(self, guild_id: int, game_id: str) -> Optional[Game]:
        pass

    def get_all(self, guild_id: int) -> List[Game]:
        pass

    def save(self, game: Game):
        pass


class GamesRepositoryImpl(GamesRepository):
    def __init__(self, eternal_guesses_table):
        self.table = eternal_guesses_table

    def get(self, guild_id: int, game_id: str) -> Optional[Game]:
        result = self.table.get_item(
            Key={
                'pk': _hash_key(guild_id),
                'sk': _range_key(game_id),
            },
        )

        if 'Item' not in result:
            return None

        return _game_from_model(result['Item'])

    def get_all(self, guild_id: int) -> List[Game]:
        games = []

        query_results = self.table.query(
            KeyConditionExpression=(
                Key('pk').eq(_hash_key(guild_id)) &
                Key('sk').begins_with('GAME#')
            )
        )

        if 'Items' not in query_results:
            return []

        for game_model in query_results['Items']:
            games.append(_game_from_model(game_model))

        return games

    def save(self, game: Game):
        assert game.game_id is not None

        model = {
            'pk': _hash_key(game.guild_id),
            'sk': _range_key(game.game_id),
            'created_by': int(game.created_by),
            'closed': game.closed
        }

        if game.title:
            model['title'] = game.title

        if game.description:
            model['description'] = game.description

        if game.min_guess:
            model['min_guess'] = game.min_guess

        if game.max_guess:
            model['max_guess'] = game.max_guess

        if game.create_datetime is not None:
            model['create_datetime'] = game.create_datetime.isoformat()

        if game.close_datetime is not None:
            model['close_datetime'] = game.close_datetime.isoformat()

        if game.guesses is not None:
            model['guesses'] = json.dumps(self._guesses(game))

        if game.channel_messages is not None:
            channel_messages = []
            for message in game.channel_messages:
                channel_messages.append(
                    {
                        'message_id': message.message_id,
                        'channel_id': message.channel_id
                    }
                )
            model['channel_messages'] = channel_messages

        self.table.put_item(
            Item=model,
        )

    def _guesses(self, game):
        guesses = {}

        for user_id, game_guess in game.guesses.items():
            guesses[user_id] = {
                'user_id': game_guess.user_id,
                'nickname': game_guess.nickname,
                'guess': game_guess.guess,
                'timestamp': game_guess.timestamp.isoformat(),
            }

        return guesses
