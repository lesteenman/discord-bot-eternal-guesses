from typing import Optional

from loguru import logger

from eternal_guesses.app.game_post_manager import GamePostManager
from eternal_guesses.exceptions import GameNotFoundError
from eternal_guesses.model.data.channel_message import ChannelMessage
from eternal_guesses.repositories.games_repository import GamesRepository


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

    async def reopen(self, guild_id: int, game_id: str):
        game = self.games_repository.get(guild_id, game_id)
        game.closed = False
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

    def list(self, guild_id: int, include_closed: bool):
        all_games = self.games_repository.get_all(guild_id)

        if include_closed:
            return all_games
        else:
            return list(filter(lambda g: not g.closed, all_games))

    async def edit_title(self, guild_id: int, game_id: str, new_title: str):
        game = self.games_repository.get(guild_id, game_id)
        game.title = new_title
        self.games_repository.save(game)

        await self.game_post_manager.update(game)

    async def edit_min_guess(
        self,
        guild_id: int,
        game_id: str,
        new_minimum: str
    ):
        game = self.games_repository.get(guild_id, game_id)
        game.min_guess = new_minimum
        self.games_repository.save(game)

        await self.game_post_manager.update(game)

    async def edit_max_guess(
        self,
        guild_id: int,
        game_id: str,
        new_maximum: str
    ):
        game = self.games_repository.get(guild_id, game_id)
        game.max_guess = new_maximum
        self.games_repository.save(game)

        await self.game_post_manager.update(game)

    async def edit_description(
        self,
        guild_id: int,
        game_id: str,
        new_description: str
    ):
        game = self.games_repository.get(guild_id, game_id)
        game.description = new_description
        self.games_repository.save(game)

        await self.game_post_manager.update(game)
