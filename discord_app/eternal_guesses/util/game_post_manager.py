from abc import ABC

import discord
from loguru import logger

from eternal_guesses.model.data.game import Game
from eternal_guesses.repositories.games_repository import GamesRepository
from eternal_guesses.util.discord_messaging import DiscordMessaging
from eternal_guesses.util.message_provider import MessageProvider


class GamePostManager(ABC):
    async def post(self, game: Game):
        raise NotImplementedError()

    async def update(self, game: Game):
        raise NotImplementedError()


class GamePostManagerImpl(GamePostManager):
    def __init__(self, games_repository: GamesRepository, message_provider: MessageProvider,
                 discord_messaging: DiscordMessaging):
        self.discord_messaging = discord_messaging
        self.games_repository = games_repository
        self.message_provider = message_provider

    async def post(self, game: Game):
        pass

    async def update(self, game: Game):
        logger.info(f"updating {len(game.channel_messages)} channel messages for {game.game_id}")
        if game.channel_messages is not None:
            new_embed = self.message_provider.game_post_embed(game)
            for channel_message in game.channel_messages:
                logger.debug(f"sending update to channel message, channel_id={channel_message.channel_id}, "
                             f"message_id={channel_message.message_id}, message='{new_embed}'")

                try:
                    await self.discord_messaging.update_channel_message(channel_message.channel_id,
                                                                        channel_message.message_id,
                                                                        embed=new_embed)
                except discord.NotFound:
                    game.channel_messages.remove(channel_message)
                    self.games_repository.save(game)
