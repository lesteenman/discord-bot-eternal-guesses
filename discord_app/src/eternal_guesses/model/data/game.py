from typing import Dict, List


class ChannelMessage:
    channel_id: int
    message_id: int

    def __init__(self, channel_id: int, message_id: int):
        self.channel_id = channel_id
        self.message_id = message_id


class Game:
    guild_id: str
    game_id: str
    guesses: Dict = {}
    channel_messages: List[ChannelMessage] = []
