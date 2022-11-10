import re

from eternal_guesses.model.discord.discord_event import DiscordEvent
from eternal_guesses.model.discord.discord_response import DiscordResponse
from eternal_guesses.repositories.games_repository import GamesRepository
from eternal_guesses.routes.route import Route
from eternal_guesses.util.game_post_manager import GamePostManager
from eternal_guesses.util.message_provider import MessageProvider


class ActionSelectDeleteGuessRoute(Route):
    def __init__(
        self,
        games_repository: GamesRepository,
        message_provider: MessageProvider,
        game_post_manager: GamePostManager
    ):
        self.game_post_manager = game_post_manager
        self.message_provider = message_provider
        self.games_repository = games_repository

    async def call(self, event: DiscordEvent) -> DiscordResponse:
        guild_id = event.guild_id

        custom_id = event.component_action.component_custom_id
        game_id = re.search(
            r"select-edit_guess-(.*)",
            custom_id
        ).group(1)

        member_id = int(event.component_action.values[0])

        game = self.games_repository.get(guild_id=guild_id, game_id=game_id)

        if game is None:
            error_game_not_found = self.message_provider.error_game_not_found(
                game_id
            )
            return DiscordResponse.ephemeral_channel_message(
                error_game_not_found
            )

        if member_id not in game.guesses:
            error_guess_not_found = self.message_provider.error_guess_not_found(
                game_id,
                member_id
            )
            return DiscordResponse.ephemeral_channel_message(
                error_guess_not_found
            )

        del game.guesses[member]

        self.games_repository.save(game)

        await self.game_post_manager.update(game)

        guess_deleted_message = self.message_provider.guess_deleted()
        return DiscordResponse.ephemeral_channel_message(guess_deleted_message)
