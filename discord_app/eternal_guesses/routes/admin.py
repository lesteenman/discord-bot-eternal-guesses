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
        await self.command_authorizer.authorize_admin_call(event)

        guild_config = self.configs_repository.get(guild_id=event.guild_id)
        message = self.message_provider.channel_admin_info(config=guild_config)
        return DiscordResponse.channel_message_with_source(message=message)

    async def add_management_channel(self, event: DiscordEvent) -> DiscordResponse:
        await self.command_authorizer.authorize_admin_call(event)

        guild_config = self.configs_repository.get(guild_id=event.guild_id)

        channel = event.command.options['channel']
        if channel in guild_config.management_channels:
            return DiscordResponse.channel_message_with_source(f"<#{channel}> is already a management "
                                                               f"channel.")

        guild_config.management_channels.append(channel)
        self.configs_repository.save(guild_config)

        return DiscordResponse.channel_message_with_source(f"Added new management channel: <#{channel}>")

    async def remove_management_channel(self, event: DiscordEvent) -> DiscordResponse:
        await self.command_authorizer.authorize_admin_call(event)

        guild_config = self.configs_repository.get(guild_id=event.guild_id)

        channel = event.command.options['channel']
        if channel not in guild_config.management_channels:
            return DiscordResponse.channel_message_with_source(f"Channel <#{channel}> was not a management "
                                                               f"channel.")

        guild_config.management_channels.remove(channel)
        self.configs_repository.save(guild_config)

        return DiscordResponse.channel_message_with_source(f"Removed management channel: <#{channel}>")

    async def add_management_role(self, event: DiscordEvent) -> DiscordResponse:
        await self.command_authorizer.authorize_admin_call(event)

        guild_config = self.configs_repository.get(guild_id=event.guild_id)

        role = event.command.options['role']
        if role in guild_config.management_roles:
            return DiscordResponse.channel_message_with_source(f"Role <@&{role}> is already a management role.")

        guild_config.management_roles.append(role)
        self.configs_repository.save(guild_config)

        return DiscordResponse.channel_message_with_source(f"Added new management role: <@&{role}>")

    async def remove_management_role(self, event: DiscordEvent) -> DiscordResponse:
        await self.command_authorizer.authorize_admin_call(event)

        guild_config = self.configs_repository.get(guild_id=event.guild_id)

        role = event.command.options['role']
        if role not in guild_config.management_roles:
            return DiscordResponse.channel_message_with_source(f"role <@&{role}> is not a management role.")

        guild_config.management_roles.remove(role)
        self.configs_repository.save(guild_config)

        return DiscordResponse.channel_message_with_source(f"Removed management role: <@&{role}>")
