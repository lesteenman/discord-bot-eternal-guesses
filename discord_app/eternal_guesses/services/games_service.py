from typing import Optional

from loguru import logger

from eternal_guesses.exceptions import GameNotFoundError
from eternal_guesses.model.data.channel_message import ChannelMessage
from eternal_guesses.repositories.games_repository import GamesRepository
from eternal_guesses.util.game_post_manager import GamePostManager


class GamesService:
    def __init__(
        self,
        games_repository: GamesRepository,
        game_post_manager: GamePostManager,
    ):
        self.game_post_manager = game_post_manager
        self.games_repository = games_repository

    async def close(self, guild_id: int, game_id: str):
        game = self.games_repository.get(guild_id, game_id)
        game.closed = True
        self.games_repository.save(game)
        await self.game_post_manager.update(game)

    async def post(
        self,
        guild_id: int,
        game_id: str,
        channel_id: Optional[int]
    ):
        logger.debug(
            f"posting a game's info. guild_id={guild_id}, game_id={game_id}"
        )

        game = self.games_repository.get(guild_id, game_id)
        if game is None:
            raise GameNotFoundError()

        message_id = await self.game_post_manager.post(game, channel_id)

        if game.channel_messages is None:
            game.channel_messages = []

        game.channel_messages.append(ChannelMessage(channel_id, message_id))
        self.games_repository.save(game)
