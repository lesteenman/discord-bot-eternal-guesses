from loguru import logger

from eternal_guesses.authorization.command_authorizer import CommandAuthorizer
from eternal_guesses.discord_messaging import DiscordMessaging
from eternal_guesses.repositories.configs_repository import ConfigsRepository
from eternal_guesses.util.message_provider import MessageProvider
from eternal_guesses.model.discord.discord_event import DiscordEvent
from eternal_guesses.model.discord_response import DiscordResponse


class AdminRoute:
    def __init__(self, message_provider: MessageProvider, configs_repository: ConfigsRepository,
                 command_authorizer: CommandAuthorizer, discord_messaging: DiscordMessaging):
        self.command_authorizer = command_authorizer
        self.message_provider = message_provider
        self.configs_repository = configs_repository
        self.discord_messaging = discord_messaging

    async def info(self, event: DiscordEvent) -> DiscordResponse:
        logger.debug("Getting info")

        await self.command_authorizer.authorize_admin_call(event)

        guild_config = self.configs_repository.get(guild_id=event.guild_id)

        message = self.message_provider.channel_admin_info(guild_config=guild_config)
        await self.discord_messaging.send_temp_message(text=message,
                                                       channel_id=event.channel_id)

        return DiscordResponse.acknowledge_with_source()

    async def add_management_channel(self, event: DiscordEvent) -> DiscordResponse:
        await self.command_authorizer.authorize_admin_call(event)

        guild_config = self.configs_repository.get(guild_id=event.guild_id)

        channel = event.command.options['channel']
        if channel in guild_config.management_channels:
            message = self.message_provider.error_duplicate_management_channel(channel)
            await self.discord_messaging.send_temp_message(text=message,
                                                           channel_id=event.channel_id)
            return DiscordResponse.acknowledge_with_source()

        guild_config.management_channels.append(channel)
        self.configs_repository.save(guild_config)

        # TODO: MessageProvider
        await self.discord_messaging.send_temp_message(text=f"Added new management channel: <#{channel}>",
                                                       channel_id=event.channel_id)
        return DiscordResponse.acknowledge_with_source()

    async def remove_management_channel(self, event: DiscordEvent) -> DiscordResponse:
        await self.command_authorizer.authorize_admin_call(event)

        guild_config = self.configs_repository.get(guild_id=event.guild_id)

        channel = event.command.options['channel']
        if channel not in guild_config.management_channels:
            # TODO: MessageProvider
            await self.discord_messaging.send_temp_message(text=f"Channel <#{channel}> was not a management channel.",
                                                           channel_id=event.channel_id)
            return DiscordResponse.acknowledge_with_source()

        guild_config.management_channels.remove(channel)
        self.configs_repository.save(guild_config)

        # TODO: MessageProvider
        await self.discord_messaging.send_temp_message(text=f"Removed management channel: <#{channel}>",
                                                       channel_id=event.channel_id)
        return DiscordResponse.acknowledge_with_source()

    async def add_management_role(self, event: DiscordEvent) -> DiscordResponse:
        await self.command_authorizer.authorize_admin_call(event)

        guild_config = self.configs_repository.get(guild_id=event.guild_id)

        role = event.command.options['role']
        if role in guild_config.management_roles:
            # TODO: MessageProvider
            await self.discord_messaging.send_temp_message(text=f"Role <@&{role}> is already a management role.",
                                                           channel_id=event.channel_id)
            return DiscordResponse.acknowledge_with_source()

        guild_config.management_roles.append(role)
        self.configs_repository.save(guild_config)

        # TODO: MessageProvider
        await self.discord_messaging.send_temp_message(text=f"Added new management role: <@&{role}>",
                                                       channel_id=event.channel_id)
        return DiscordResponse.acknowledge_with_source()

    async def remove_management_role(self, event: DiscordEvent) -> DiscordResponse:
        await self.command_authorizer.authorize_admin_call(event)

        guild_config = self.configs_repository.get(guild_id=event.guild_id)

        role = event.command.options['role']
        if role not in guild_config.management_roles:
            # TODO: MessageProvider
            await self.discord_messaging.send_temp_message(text=f"role <@&{role}> is not a management role.",
                                                           channel_id=event.channel_id)

            return DiscordResponse.acknowledge_with_source()

        guild_config.management_roles.remove(role)
        self.configs_repository.save(guild_config)

        # TODO: MessageProvider
        await self.discord_messaging.send_temp_message(text=f"Removed management role: <@&{role}>",
                                                       channel_id=event.channel_id)

        return DiscordResponse.acknowledge_with_source()
