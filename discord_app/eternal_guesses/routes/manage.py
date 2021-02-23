import logging

from eternal_guesses import message_formatter
from eternal_guesses.discord_messaging import DiscordMessaging
from eternal_guesses.errors import DiscordEventDisallowedError
from eternal_guesses.model.data.game import ChannelMessage
from eternal_guesses.model.discord_event import DiscordEvent
from eternal_guesses.model.discord_response import DiscordResponse
from eternal_guesses.repositories.configs_repository import ConfigsRepository
from eternal_guesses.repositories.games_repository import GamesRepository

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


class ManageRoute:
    def __init__(self, games_repository: GamesRepository, discord_messaging: DiscordMessaging,
                 configs_repository: ConfigsRepository):
        self.games_repository = games_repository
        self.discord_messaging = discord_messaging
        self.configs_repository = configs_repository

    async def post(self, event: DiscordEvent) -> DiscordResponse:
        await self._assert_caller_rights(event)

        guild_id = event.guild_id
        game_id = event.command.options['game-id']

        if 'channel' in event.command.options:
            channel_id = event.command.options['channel']
        else:
            channel_id = event.channel_id

        game = self.games_repository.get(guild_id, game_id)
        if game is None:
            message = message_formatter.dm_error_game_not_found(game_id)
            await self.discord_messaging.send_dm(event.member, message)
        else:
            message = message_formatter.channel_list_game_guesses(game)
            message_id = await self.discord_messaging.create_channel_message(channel_id, message)

            if game.channel_messages is None:
                game.channel_messages = []

            game.channel_messages.append(ChannelMessage(channel_id, message_id))
            self.games_repository.save(game)

        return DiscordResponse.acknowledge()

    async def list_games(self, event: DiscordEvent) -> DiscordResponse:
        await self._assert_caller_rights(event)

        guild_id = event.guild_id

        all_games = self.games_repository.get_all(guild_id)

        if 'closed' in event.command.options:
            if event.command.options['closed']:
                closed_games = list(filter(lambda g: g.closed, all_games))
                message = message_formatter.channel_manage_list_closed_games(
                    closed_games)
            else:
                open_games = list(filter(lambda g: not g.closed, all_games))
                message = message_formatter.channel_manage_list_open_games(
                    open_games)
        else:
            message = message_formatter.channel_manage_list_all_games(all_games)

        return DiscordResponse.channel_message(message)

    async def close(self, event: DiscordEvent) -> DiscordResponse:
        await self._assert_caller_rights(event)

        return DiscordResponse.channel_message_with_source("TODO: Unimplemented manage.close")

    async def _assert_caller_rights(self, event: DiscordEvent):
        guild_id = event.guild_id
        guild_config = self.configs_repository.get(guild_id=guild_id)

        log.debug(f"channel check: checking if {event.channel_id} is in {guild_config.management_channels}")
        if event.channel_id in guild_config.management_channels:
            return

        log.debug(f"roles check: checking if any of {event.member.roles} is in {guild_config.management_roles}")
        for role in event.member.roles:
            if role in guild_config.management_roles:
                return

        raise DiscordEventDisallowedError("the user has no management role and the request was not done from a management channel.")
