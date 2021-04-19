from eternal_guesses.authorization.command_authorizer import CommandAuthorizer
from eternal_guesses.model.discord.discord_event import DiscordEvent
from eternal_guesses.model.discord_response import DiscordResponse
from eternal_guesses.repositories.games_repository import GamesRepository
from eternal_guesses.routes.route import Route
from eternal_guesses.util.discord_messaging import DiscordMessaging
from eternal_guesses.util.message_provider import MessageProvider


class ListGamesRoute(Route):
    def __init__(self,
                 games_repository: GamesRepository,
                 discord_messaging: DiscordMessaging,
                 message_provider: MessageProvider,
                 command_authorizer: CommandAuthorizer):
        self.games_repository = games_repository
        self.discord_messaging = discord_messaging
        self.message_provider = message_provider
        self.command_authorizer = command_authorizer

    async def call(self, event: DiscordEvent) -> DiscordResponse:
        await self.command_authorizer.authorize_management_call(event)

        guild_id = event.guild_id

        all_games = self.games_repository.get_all(guild_id)

        if 'closed' in event.command.options:
            if event.command.options['closed']:
                closed_games = list(filter(lambda g: g.closed, all_games))
                message = self.message_provider.channel_manage_list_closed_games(
                    closed_games)
            else:
                open_games = list(filter(lambda g: not g.closed, all_games))
                message = self.message_provider.channel_manage_list_open_games(
                    open_games)
        else:
            message = self.message_provider.channel_manage_list_all_games(all_games)

        await self.discord_messaging.send_channel_message(channel_id=event.channel_id, text=message)

        return DiscordResponse.acknowledge()
