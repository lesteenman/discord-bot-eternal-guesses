from datetime import datetime
from typing import Optional, Mapping, List

from eternal_guesses.model.data.game_guess import GameGuess


class ChannelMessage:
    channel_id: int
    message_id: int

    def __init__(self, channel_id: int, message_id: int):
        self.channel_id = channel_id
        self.message_id = message_id


class Game:
    def __init__(self, guild_id: int = None, game_id: str = None, created_by: int = None, closed: bool = None,
                 guesses: Mapping[int, GameGuess] = None, channel_messages: List[ChannelMessage] = None,
                 create_datetime: datetime = None, close_datetime: Optional[datetime] = None):
        self.guild_id = guild_id
        self.game_id = game_id
        self.created_by = created_by
        self.create_datetime = create_datetime
        self.close_datetime = close_datetime
        self.closed = closed
        self.guesses = guesses
        self.channel_messages = channel_messages

        if channel_messages is None:
            self.channel_messages = []

        if guesses is None:
            self.guesses = {}
