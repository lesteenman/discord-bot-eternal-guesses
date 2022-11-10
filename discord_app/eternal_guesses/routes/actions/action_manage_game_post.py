import re

from eternal_guesses.model.discord.discord_component import ActionRow, \
    DiscordComponent
from eternal_guesses.model.discord.discord_event import DiscordEvent
from eternal_guesses.model.discord.discord_response import DiscordResponse
from eternal_guesses.routes.route import Route
from eternal_guesses.util.component_ids import ComponentIds


class ActionManageGamePostRoute(Route):
    async def call(self, event: DiscordEvent) -> DiscordResponse:
        custom_id = event.component_action.component_custom_id
        game_id = re.search(
            ComponentIds.component_button_post_game_regex,
            custom_id
        ).group(1)

        response = DiscordResponse.channel_message()
        response.is_ephemeral = True
        response.action_rows = [
            ActionRow(
                components=[
                    DiscordComponent.channel_select(
                        placeholder="select guess",
                        custom_id=f"select-post_game-{game_id}",
                    )
                ]
            )
        ]

        return response
