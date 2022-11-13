import re

from eternal_guesses.model.discord.discord_component import ActionRow, \
    DiscordComponent, ComponentType
from eternal_guesses.model.discord.discord_event import DiscordEvent
from eternal_guesses.model.discord.discord_response import DiscordResponse
from eternal_guesses.routes.route import Route
from eternal_guesses.app.component_ids import ComponentIds


class ActionManageGamePostRoute(Route):
    @staticmethod
    def matches(event: DiscordEvent) -> bool:
        return (
            event.component_action is not None and
            event.component_action.component_type == ComponentType.BUTTON and
            event.component_action.component_custom_id.startswith(
                ComponentIds.component_button_post_game_prefix
            )
        )

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
                    DiscordComponent.text_channel_select(
                        placeholder="select channel",
                        custom_id=ComponentIds.selector_post_game_id(
                            game_id
                        )
                    )
                ]
            )
        ]

        return response
