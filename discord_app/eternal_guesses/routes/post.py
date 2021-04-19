from loguru import logger

from eternal_guesses.authorization.command_authorizer import CommandAuthorizer
from eternal_guesses.model.data.channel_message import ChannelMessage
from eternal_guesses.model.discord.discord_event import DiscordEvent
from eternal_guesses.model.discord_response import DiscordResponse
from eternal_guesses.repositories.games_repository import GamesRepository
from eternal_guesses.routes.route import Route
from eternal_guesses.util.discord_messaging import DiscordMessaging
from eternal_guesses.util.message_provider import MessageProvider


class PostRoute(Route):
    def __init__(self,
                 command_authorizer: CommandAuthorizer,
                 games_repository: GamesRepository,
                 message_provider: MessageProvider,
                 discord_messaging: DiscordMessaging):
        self.command_authorizer = command_authorizer
        self.discord_messaging = discord_messaging
        self.message_provider = message_provider
        self.games_repository = games_repository

    async def call(self, event: DiscordEvent) -> DiscordResponse:
        await self.command_authorizer.authorize_management_call(event)

        guild_id = event.guild_id
        game_id = event.command.options['game-id']

        logger.debug(f"posting a game's info. guild_id={guild_id}, game_id={game_id}")

        if 'channel' in event.command.options:
            channel_id = int(event.command.options['channel'])
        else:
            channel_id = int(event.channel_id)

        game = self.games_repository.get(guild_id, game_id)
        if game is None:
            message = self.message_provider.manage_error_game_not_found(game_id)
            await self.discord_messaging.send_channel_message(channel_id=event.channel_id, text=message)
        else:
            message = self.message_provider.game_managed_channel_message(game)
            message_id = await self.discord_messaging.send_channel_message(channel_id, message)

            if game.channel_messages is None:
                game.channel_messages = []

            game.channel_messages.append(ChannelMessage(channel_id, message_id))
            self.games_repository.save(game)

        return DiscordResponse.acknowledge()
