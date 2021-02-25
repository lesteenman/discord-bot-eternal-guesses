import logging
from abc import ABC

from eternal_guesses.errors import DiscordEventDisallowedError
from eternal_guesses.model.discord_event import DiscordEvent
from eternal_guesses.repositories.configs_repository import ConfigsRepository

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


class CommandAuthorizer(ABC):
    async def authorize_management_call(self, event: DiscordEvent):
        pass


class CommandAuthorizerImpl(CommandAuthorizer):
    def __init__(self, configs_repository: ConfigsRepository):
        self.configs_repository = configs_repository

    async def authorize_management_call(self, event: DiscordEvent):
        guild_id = event.guild_id
        guild_config = self.configs_repository.get(guild_id=guild_id)

        log.debug(f"channel check: checking if {event.channel_id} is in {guild_config.management_channels}")
        if event.channel_id in guild_config.management_channels:
            return

        log.debug(f"roles check: checking if any of {event.member.roles} is in {guild_config.management_roles}")
        for role in event.member.roles:
            if role in guild_config.management_roles:
                return

        raise DiscordEventDisallowedError("the user has no management role and the request was not done from a "
                                          "management channel.")
