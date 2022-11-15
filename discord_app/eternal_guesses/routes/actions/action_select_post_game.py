import re

from loguru import logger

from eternal_guesses.model.discord.discord_event import DiscordEvent
from eternal_guesses.model.discord.discord_response import DiscordResponse
from eternal_guesses.routes.route import Route
from eternal_guesses.services.games_service import GamesService
from eternal_guesses.app.component_ids import ComponentIds
from eternal_guesses.app.message_provider import MessageProvider


class ActionSelectPostGameRoute(Route):
    def __init__(
        self,
        message_provider: MessageProvider,
        games_service: GamesService
    ):
        self.games_service = games_service
        self.message_provider = message_provider

    @staticmethod
    def matches(event: DiscordEvent) -> bool:
        action = event.component_action
        if action is None:
            return False

        custom_id = action.component_custom_id
        return custom_id.startswith(
            ComponentIds.selector_post_game_prefix
        )

    async def call(self, event: DiscordEvent) -> DiscordResponse:
        custom_id = event.component_action.component_custom_id
        game_id = re.search(
            fr"{ComponentIds.selector_post_game_prefix}(.*)",
            custom_id
        ).group(1)

        channel_id = int(event.component_action.values[0])

        logger.info(f"guild {event.guild_id}, user {event.member.user_id}, "
                    f"posting game {game_id} to channel {channel_id}")

        await self.games_service.post(
            guild_id=event.guild_id,
            game_id=game_id,
            channel_id=channel_id,
        )

        return DiscordResponse.ephemeral_channel_message(
            self.message_provider.game_post_created_message()
        )
