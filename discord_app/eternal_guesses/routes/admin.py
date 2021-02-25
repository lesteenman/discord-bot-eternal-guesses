from eternal_guesses.authorization.command_authorizer import CommandAuthorizer
from eternal_guesses.repositories.configs_repository import ConfigsRepository
from eternal_guesses.util.message_provider import MessageProvider
from eternal_guesses.model.discord_event import DiscordEvent
from eternal_guesses.model.discord_response import DiscordResponse


class AdminRoute:
    def __init__(self, message_provider: MessageProvider, configs_repository: ConfigsRepository,
                 command_authorizer: CommandAuthorizer):
        self.command_authorizer = command_authorizer
        self.message_provider = message_provider
        self.configs_repository = configs_repository

    async def info(self, event: DiscordEvent) -> DiscordResponse:
        guild_config = self.configs_repository.get(guild_id=event.guild_id)
        message = self.message_provider.channel_admin_info(config=guild_config)
        return DiscordResponse.channel_message_with_source(message=message)

    async def add_management_channel(self, event: DiscordEvent) -> DiscordResponse:
        return DiscordResponse.channel_message_with_source("TODO: Unimplemented admin.add-management-channel")

    async def remove_management_channel(self, event: DiscordEvent) -> DiscordResponse:
        return DiscordResponse.channel_message_with_source("TODO: Unimplemented admin.remove-management-channel")

    async def add_management_role(self, event: DiscordEvent) -> DiscordResponse:
        return DiscordResponse.channel_message_with_source("TODO: Unimplemented admin.add-management-role")

    async def remove_management_role(self, event: DiscordEvent) -> DiscordResponse:
        return DiscordResponse.channel_message_with_source("TODO: Unimplemented admin.remove-management-role")
