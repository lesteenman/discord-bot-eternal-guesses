from abc import ABC

from loguru import logger

from eternal_guesses.model.discord.discord_event import DiscordEvent
from eternal_guesses.model.error.discord_event_disallowed_error import DiscordEventDisallowedError
from eternal_guesses.repositories.configs_repository import ConfigsRepository


class CommandAuthorizer(ABC):
    async def authorize_management_call(self, event: DiscordEvent):
        pass

    async def authorize_admin_call(self, event: DiscordEvent):
        pass


class CommandAuthorizerImpl(CommandAuthorizer):
    def __init__(self, configs_repository: ConfigsRepository):
        self.configs_repository = configs_repository

    async def authorize_management_call(self, event: DiscordEvent):
        guild_id = event.guild_id
        guild_config = self.configs_repository.get(guild_id=guild_id)

        if event.member.is_admin:
            return

        logger.debug(f"channel check: checking if {event.channel_id} is in {guild_config.management_channels}")
        logger.debug(f"type of event.channel_id: {type(event.channel_id)}")
        for channel in guild_config.management_channels:
            logger.debug(f"type of guild_config.management_channels[]: {type(channel)}")
        if event.channel_id in guild_config.management_channels:
            return

        logger.debug(f"roles check: checking if any of {event.member.roles} is in {guild_config.management_roles}")
        for role in event.member.roles:
            logger.debug(f"type of event.member.roles[]: {type(role)}")
        for role in guild_config.management_roles:
            logger.debug(f"type of guild_config.management_roles[]: {type(role)}")
        for role in event.member.roles:
            if role in guild_config.management_roles:
                return

        raise DiscordEventDisallowedError("the user has no management role and the request was not done from a "
                                          "management channel.")

    async def authorize_admin_call(self, event):
        if event.member.is_admin:
            return

        raise DiscordEventDisallowedError("command only allowed by a member with admin permissions.")
