from eternal_guesses.model.discord.discord_event import DiscordEvent
from eternal_guesses.model.discord.discord_response import DiscordResponse
from eternal_guesses.repositories.configs_repository import ConfigsRepository
from eternal_guesses.routes.route import Route
from eternal_guesses.util.message_provider import MessageProvider


class RemoveManagementChannelRoute(Route):
    def __init__(self,
                 message_provider: MessageProvider,
                 configs_repository: ConfigsRepository):
        self.message_provider = message_provider
        self.configs_repository = configs_repository

    async def call(self, event: DiscordEvent) -> DiscordResponse:
        guild_config = self.configs_repository.get(guild_id=event.guild_id)

        channel = int(event.command.options['channel'])
        if channel not in guild_config.management_channels:
            text = self.message_provider.remove_invalid_management_channel(channel)
            return DiscordResponse.ephemeral_channel_message(text)

        guild_config.management_channels.remove(channel)
        self.configs_repository.save(guild_config)

        text = self.message_provider.removed_management_channel(channel)
        return DiscordResponse.ephemeral_channel_message(text)
