from datetime import datetime
from typing import Dict, List, Optional


class ChannelMessage:
    channel_id: int
    message_id: int

    def __init__(self, channel_id: int, message_id: int):
        self.channel_id = channel_id
        self.message_id = message_id


class Game:
    guild_id: int
    game_id: str
    created_by: int
    create_datetime: datetime
    close_datetime: Optional[datetime]
    closed: bool
    guesses: Dict = {}
    channel_messages: List[ChannelMessage] = []
