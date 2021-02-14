import json
import logging
import re
from datetime import datetime
from typing import Optional, List

from pynamodb.exceptions import DoesNotExist

from eternal_guesses.model.data.game import Game, ChannelMessage
from eternal_guesses.model.data.game_guess import GameGuess
from eternal_guesses.repositories.dynamodb_models import EternalGuessesTable, ChannelMessageMap

log = logging.getLogger(__name__)

PK_REGEX = r"GUILD#(.*)"
SK_REGEX = r"GAME#(.*)"


def _channel_message_from_model(message_model: ChannelMessageMap):
    return ChannelMessage(
        channel_id=message_model.channel_id,
        message_id=message_model.message_id
    )


def _guess_from_model(guess_model):
    return GameGuess(
        user_id=guess_model['user_id'],
        guess=guess_model['guess'],
        nickname=guess_model['nickname'],
        timestamp=datetime.fromisoformat(guess_model['timestamp']),
    )


def _game_from_model(model: EternalGuessesTable) -> Game:
    print(f"Model = {model}")
    guild_id = int(re.match(PK_REGEX, model.pk).group(1))
    game_id = re.match(SK_REGEX, model.sk).group(1)

    create_datetime = None
    if model.create_datetime is not None:
        create_datetime = datetime.fromisoformat(model.create_datetime)

    close_datetime = None
    if model.close_datetime is not None:
        close_datetime = datetime.fromisoformat(model.close_datetime)

    closed = False
    if model.closed is not None:
        closed = model.closed

    channel_messages = []
    if model.channel_messages is not None:
        channel_messages = list(_channel_message_from_model(message_model) for message_model in model.channel_messages)

    guesses = {}
    if model.guesses is not None:
        for (user_id, guess_model) in json.loads(model.guesses).items():
            guesses[int(user_id)] = _guess_from_model(guess_model)

    return Game(
        guild_id=guild_id,
        game_id=game_id,
        created_by=model.created_by,
        create_datetime=create_datetime,
        close_datetime=close_datetime,
        closed=closed,
        channel_messages=channel_messages,
        guesses=guesses
    )


def _hash_key(guild_id: int):
    return f"GUILD#{guild_id}"


def _range_key(game_id: str):
    return f"GAME#{game_id}"


class GamesRepository:
    def __init__(self, table_name: str, host: str = None):
        self.table = EternalGuessesTable
        self.table.Meta.table_name = table_name
        if host is not None:
            self.table.Meta.host = host

    def get(self, guild_id: int, game_id: str) -> Optional[Game]:
        try:
            result = self.table.get(_hash_key(guild_id), _range_key(game_id))
        except DoesNotExist:
            return None

        return _game_from_model(result)

    def get_all(self, guild_id: int) -> List[Game]:
        games = []

        for game_model in self.table.query(_hash_key(guild_id)):
            games.append(_game_from_model(game_model))

        return games

    def save(self, game: Game):
        assert game.game_id is not None

        model = self.table(_hash_key(game.guild_id), _range_key(game.game_id))

        model.created_by = game.created_by
        model.closed = game.closed

        if game.create_datetime is not None:
            model.create_datetime = game.create_datetime.isoformat()

        if game.close_datetime is not None:
            model.close_datetime = game.close_datetime.isoformat()

        if game.guesses is not None:
            guesses = {}
            for user_id, game_guess in game.guesses.items():
                guesses[user_id] = {
                    'user_id': game_guess.user_id,
                    'nickname': game_guess.nickname,
                    'guess': game_guess.guess,
                    'timestamp': game_guess.timestamp.isoformat(),
                }
            model.guesses = json.dumps(guesses)

        if game.channel_messages is not None:
            channel_messages = []
            for message in game.channel_messages:
                channel_messages.append({'message_id': message.message_id, 'channel_id': message.channel_id})
            model.channel_messages = channel_messages

        model.save()

        # table = GamesRepository._get_table()
        #
        # item = {
        #     "pk": f"GUILD#{guild_id}",
        #     "sk": f"GAME#{game.game_id}",
        #     "create_datetime": game.create_datetime.isoformat(),
        #     "created_by": game.created_by,
        #     "closed": game.closed,
        #     "guesses": {user_id: {
        #         'user_id': game_guess.user_id,
        #         'nickname': game_guess.nickname,
        #         'guess': game_guess.guess,
        #         'datetime': game_guess.datetime.isoformat(),
        #     } for (user_id, game_guess) in game.guesses.items()},
        #     "channel_messages": list({'message_id': message.message_id, 'channel_id': message.channel_id}
        #                              for message in game.channel_messages),
        # }
        #
        # log.debug(f"saving item, item={item}")
        #
        # response = table.put_item(
        #     Item=item
        # )
        #
        # if log.isEnabledFor(logging.DEBUG):
        #     log.debug(f"table.put_item response: {pformat(response)}")

