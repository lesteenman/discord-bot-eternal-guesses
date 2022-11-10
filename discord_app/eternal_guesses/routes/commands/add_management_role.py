from eternal_guesses.model.discord.discord_event import DiscordEvent
from eternal_guesses.model.discord.discord_response import DiscordResponse
from eternal_guesses.repositories.configs_repository import ConfigsRepository
from eternal_guesses.routes.route import Route
from eternal_guesses.util.message_provider import MessageProvider


class AddManagementRoleRoute(Route):
    def __init__(
        self,
        message_provider: MessageProvider,
        configs_repository: ConfigsRepository
    ):
        self.message_provider = message_provider
        self.configs_repository = configs_repository

    async def call(self, event: DiscordEvent) -> DiscordResponse:
        guild_config = self.configs_repository.get(guild_id=event.guild_id)

        role = int(event.command.options['role'])
        if role in guild_config.management_roles:
            text = self.message_provider.add_duplicate_management_role(role)
            return DiscordResponse.ephemeral_channel_message(text)

        guild_config.management_roles.append(role)
        self.configs_repository.save(guild_config)

        text = self.message_provider.added_management_role(role)
        return DiscordResponse.ephemeral_channel_message(text)
