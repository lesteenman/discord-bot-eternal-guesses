import logging

from eternal_guesses.authorization.command_authorizer import CommandAuthorizer
from eternal_guesses.discord_messaging import DiscordMessaging
from eternal_guesses.model.data.game import ChannelMessage
from eternal_guesses.model.discord_event import DiscordEvent
from eternal_guesses.model.discord_response import DiscordResponse
from eternal_guesses.repositories.games_repository import GamesRepository
from eternal_guesses.util.message_provider import MessageProvider

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


class ManageRoute:
    def __init__(self, games_repository: GamesRepository, discord_messaging: DiscordMessaging,
                 message_provider: MessageProvider, command_authorizer: CommandAuthorizer):
        self.games_repository = games_repository
        self.discord_messaging = discord_messaging
        self.message_provider = message_provider
        self.command_authorizer = command_authorizer

    async def post(self, event: DiscordEvent) -> DiscordResponse:
        await self.command_authorizer.authorize_management_call(event)

        guild_id = event.guild_id
        game_id = event.command.options['game-id']

        if 'channel' in event.command.options:
            channel_id = event.command.options['channel']
        else:
            channel_id = event.channel_id

        game = self.games_repository.get(guild_id, game_id)
        if game is None:
            message = self.message_provider.dm_error_game_not_found(game_id)
            await self.discord_messaging.send_dm(event.member, message)
        else:
            message = self.message_provider.channel_list_game_guesses(game)
            message_id = await self.discord_messaging.create_channel_message(channel_id, message)

            if game.channel_messages is None:
                game.channel_messages = []

            game.channel_messages.append(ChannelMessage(channel_id, message_id))
            self.games_repository.save(game)

        return DiscordResponse.acknowledge()

    async def list_games(self, event: DiscordEvent) -> DiscordResponse:
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

        return DiscordResponse.channel_message(message)

    async def close(self, event: DiscordEvent) -> DiscordResponse:
        await self.command_authorizer.authorize_management_call(event)

        return DiscordResponse.channel_message_with_source("TODO: Unimplemented manage.close")
