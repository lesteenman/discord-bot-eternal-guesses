from eternal_guesses.authorization.command_authorizer import CommandAuthorizer
from eternal_guesses.model.discord.discord_event import DiscordEvent
from eternal_guesses.model.discord_response import DiscordResponse
from eternal_guesses.repositories.games_repository import GamesRepository
from eternal_guesses.routes.route import Route
from eternal_guesses.util.discord_messaging import DiscordMessaging
from eternal_guesses.util.message_provider import MessageProvider


class CloseGameRoute(Route):
    def __init__(self,
                 command_authorizer: CommandAuthorizer,
                 games_repository: GamesRepository,
                 discord_messaging: DiscordMessaging,
                 message_provider: MessageProvider):
        self.command_authorizer = command_authorizer
        self.games_repository = games_repository
        self.discord_messaging = discord_messaging
        self.message_provider = message_provider

    async def call(self, event: DiscordEvent) -> DiscordResponse:
        await self.command_authorizer.authorize_management_call(event)

        guild_id = event.guild_id
        game_id = event.command.options['game-id']

        game = self.games_repository.get(guild_id, game_id)
        game.closed = True
        self.games_repository.save(game)

        await self.discord_messaging.send_channel_message(
            text=f"Game '{game_id} has now been closed for new guesses.",
            channel_id=event.channel_id,
        )

        for message in game.channel_messages:
            text = self.message_provider.game_managed_channel_message(game)
            await self.discord_messaging.update_channel_message(message.channel_id, message.message_id, text)

        return DiscordResponse.acknowledge()
