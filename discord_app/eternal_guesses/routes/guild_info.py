from loguru import logger

from eternal_guesses.model.discord.discord_event import DiscordEvent
from eternal_guesses.model.discord.discord_response import DiscordResponse
from eternal_guesses.repositories.configs_repository import ConfigsRepository
from eternal_guesses.routes.route import Route
from eternal_guesses.util.message_provider import MessageProvider


class GuildInfoRoute(Route):
    def __init__(self,
                 message_provider: MessageProvider,
                 configs_repository: ConfigsRepository):
        self.message_provider = message_provider
        self.configs_repository = configs_repository

    async def call(self, event: DiscordEvent) -> DiscordResponse:
        logger.debug("Getting info")

        guild_config = self.configs_repository.get(guild_id=event.guild_id)

        message = self.message_provider.channel_admin_info(guild_config=guild_config)
        return DiscordResponse.ephemeral_channel_message(message)
