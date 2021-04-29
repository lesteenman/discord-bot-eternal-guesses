from datetime import datetime
from typing import Optional, Mapping, List

from eternal_guesses.model.data.channel_message import ChannelMessage
from eternal_guesses.model.data.game_guess import GameGuess


class Game:
    def __init__(self, guild_id: int = None, game_id: str = None, created_by: int = None, closed: bool = None,
                 guesses: Mapping[int, GameGuess] = None, channel_messages: List[ChannelMessage] = None,
                 create_datetime: datetime = None, close_datetime: Optional[datetime] = None, title: str = None,
                 description: str = None, min_guess: int = None, max_guess: int = None):
        self.guild_id = guild_id
        self.game_id = game_id
        self.title = title
        self.description = description

        self.created_by = created_by
        self.create_datetime = create_datetime
        self.close_datetime = close_datetime
        self.closed = closed
        self.guesses = guesses
        self.channel_messages = channel_messages

        self.min_guess = min_guess
        self.max_guess = max_guess

        if channel_messages is None:
            self.channel_messages = []

        if guesses is None:
            self.guesses = {}

    def is_numeric(self):
        return self.min_guess is not None or self.max_guess is not None
