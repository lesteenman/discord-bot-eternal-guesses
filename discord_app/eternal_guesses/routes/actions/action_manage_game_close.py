import re

from eternal_guesses.app.component_ids import ComponentIds
from eternal_guesses.model.discord.discord_event import DiscordEvent
from eternal_guesses.model.discord.discord_response import DiscordResponse
from eternal_guesses.repositories.games_repository import GamesRepository
from eternal_guesses.routes.route import Route
from eternal_guesses.services.games_service import GamesService


class ActionManageGameCloseRoute(Route):
    def __init__(
        self,
        games_service: GamesService,
        games_repository: GamesRepository
    ):
        self.games_repository = games_repository
        self.games_service = games_service

    @staticmethod
    def matches(event: DiscordEvent) -> bool:
        action = event.component_action
        if action is None:
            return False

        custom_id = action.component_custom_id
        return custom_id.startswith(
            ComponentIds.component_button_close_game_prefix
        )

    async def call(self, event: DiscordEvent) -> DiscordResponse:
        guild_id = event.guild_id
        game_id = re.search(
            fr"{ComponentIds.component_button_close_game_prefix}(.*)",
            event.component_action.component_custom_id
        ).group(1)
        await self.games_service.close(
            guild_id=guild_id,
            game_id=game_id,
        )

        return DiscordResponse.ephemeral_channel_message(
            content=f"Game {game_id} has been closed."
        )
