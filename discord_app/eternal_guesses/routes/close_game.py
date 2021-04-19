from eternal_guesses.model.discord.discord_event import DiscordEvent
from eternal_guesses.model.discord.discord_response import DiscordResponse
from eternal_guesses.repositories.games_repository import GamesRepository
from eternal_guesses.routes.route import Route
from eternal_guesses.util.discord_messaging import DiscordMessaging
from eternal_guesses.util.message_provider import MessageProvider


class CloseGameRoute(Route):
    def __init__(self,
                 games_repository: GamesRepository,
                 discord_messaging: DiscordMessaging,
                 message_provider: MessageProvider):
        self.games_repository = games_repository
        self.discord_messaging = discord_messaging
        self.message_provider = message_provider

    async def call(self, event: DiscordEvent) -> DiscordResponse:
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
            embed = self.message_provider.game_post_embed(game)
            await self.discord_messaging.update_channel_message(message.channel_id, message.message_id, embed=embed)

        game_closed_message = self.message_provider.game_closed(game)
        return DiscordResponse.ephemeral_channel_message(game_closed_message)
