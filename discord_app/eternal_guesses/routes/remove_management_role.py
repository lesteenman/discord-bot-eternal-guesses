from eternal_guesses.authorization.command_authorizer import CommandAuthorizer
from eternal_guesses.model.discord.discord_event import DiscordEvent
from eternal_guesses.model.discord_response import DiscordResponse
from eternal_guesses.repositories.configs_repository import ConfigsRepository
from eternal_guesses.routes.route import Route
from eternal_guesses.util.discord_messaging import DiscordMessaging
from eternal_guesses.util.message_provider import MessageProvider


class RemoveManagementRoleRoute(Route):
    def __init__(self,
                 message_provider: MessageProvider,
                 configs_repository: ConfigsRepository,
                 command_authorizer: CommandAuthorizer,
                 discord_messaging: DiscordMessaging):
        self.command_authorizer = command_authorizer
        self.message_provider = message_provider
        self.configs_repository = configs_repository
        self.discord_messaging = discord_messaging

    async def call(self, event: DiscordEvent) -> DiscordResponse:
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
