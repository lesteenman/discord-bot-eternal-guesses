from typing import Dict, List


class Game:
    guild_id: str
    game_id: str
    guesses: Dict = {}
    channel_messages: List[int] = []
