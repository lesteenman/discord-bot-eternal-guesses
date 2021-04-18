from loguru import logger

from eternal_guesses.authorization.command_authorizer import CommandAuthorizer
from eternal_guesses.repositories.configs_repository import ConfigsRepository
from eternal_guesses.util.discord_messaging import DiscordMessaging
from eternal_guesses.util.message_provider import MessageProvider
from eternal_guesses.model.discord.discord_event import DiscordEvent
from eternal_guesses.model.discord_response import DiscordResponse


class AdminRoute:
    def __init__(self,
                 message_provider: MessageProvider,
                 configs_repository: ConfigsRepository,
                 command_authorizer: CommandAuthorizer,
                 discord_messaging: DiscordMessaging):
        self.command_authorizer = command_authorizer
        self.message_provider = message_provider
        self.configs_repository = configs_repository
        self.discord_messaging = discord_messaging

    async def info(self, event: DiscordEvent) -> DiscordResponse:
        logger.debug("Getting info")

        await self.command_authorizer.authorize_admin_call(event)

        guild_config = self.configs_repository.get(guild_id=event.guild_id)

        message = self.message_provider.channel_admin_info(guild_config=guild_config)
        await self.discord_messaging.send_channel_message(text=message,
                                                          channel_id=event.channel_id)

        return DiscordResponse.acknowledge()

    async def add_management_channel(self, event: DiscordEvent) -> DiscordResponse:
        await self.command_authorizer.authorize_admin_call(event)

        guild_config = self.configs_repository.get(guild_id=event.guild_id)

        channel = int(event.command.options['channel'])
        if channel in guild_config.management_channels:
            text = self.message_provider.error_duplicate_management_channel(channel)
            await self.discord_messaging.send_channel_message(text=text,
                                                              channel_id=event.channel_id)
            return DiscordResponse.acknowledge()

        guild_config.management_channels.append(channel)
        self.configs_repository.save(guild_config)

        text = self.message_provider.added_management_channel(channel)
        await self.discord_messaging.send_channel_message(text=text,
                                                          channel_id=event.channel_id)
        return DiscordResponse.acknowledge()

    async def remove_management_channel(self, event: DiscordEvent) -> DiscordResponse:
        await self.command_authorizer.authorize_admin_call(event)

        guild_config = self.configs_repository.get(guild_id=event.guild_id)

        channel = int(event.command.options['channel'])
        if channel not in guild_config.management_channels:
            text = self.message_provider.remove_invalid_management_channel(channel)
            await self.discord_messaging.send_channel_message(
                text=text,
                channel_id=event.channel_id)
            return DiscordResponse.acknowledge()

        guild_config.management_channels.remove(channel)
        self.configs_repository.save(guild_config)

        text = self.message_provider.removed_management_channel(channel)
        await self.discord_messaging.send_channel_message(text=text,
                                                          channel_id=event.channel_id)
        return DiscordResponse.acknowledge()

    async def add_management_role(self, event: DiscordEvent) -> DiscordResponse:
        await self.command_authorizer.authorize_admin_call(event)

        guild_config = self.configs_repository.get(guild_id=event.guild_id)

        role = int(event.command.options['role'])
        if role in guild_config.management_roles:
            text = self.message_provider.add_duplicate_management_role(role)
            await self.discord_messaging.send_channel_message(text=text,
                                                              channel_id=event.channel_id)
            return DiscordResponse.acknowledge()

        guild_config.management_roles.append(role)
        self.configs_repository.save(guild_config)

        text = self.message_provider.added_management_role(role)
        await self.discord_messaging.send_channel_message(text=text,
                                                          channel_id=event.channel_id)
        return DiscordResponse.acknowledge()

    async def remove_management_role(self, event: DiscordEvent) -> DiscordResponse:
        await self.command_authorizer.authorize_admin_call(event)

        guild_config = self.configs_repository.get(guild_id=event.guild_id)

        role = int(event.command.options['role'])
        if role not in guild_config.management_roles:
            text = self.message_provider.remove_invalid_management_role(role)
            await self.discord_messaging.send_channel_message(text=text,
                                                              channel_id=event.channel_id)

            return DiscordResponse.acknowledge()

        guild_config.management_roles.remove(role)
        self.configs_repository.save(guild_config)

        text = self.message_provider.admin_removed_management_role(role=role)
        await self.discord_messaging.send_channel_message(text=text,
                                                          channel_id=event.channel_id)

        return DiscordResponse.acknowledge()
