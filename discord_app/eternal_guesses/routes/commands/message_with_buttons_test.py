from eternal_guesses.model.discord.discord_component import ActionRow, \
    DiscordComponent, ButtonStyle
from eternal_guesses.model.discord.discord_event import DiscordEvent
from eternal_guesses.model.discord.discord_response import DiscordResponse
from eternal_guesses.routes.route import Route


class MessageWithButtonsRoute(Route):
    async def call(self, event: DiscordEvent) -> DiscordResponse:
        response = DiscordResponse.channel_message()
        response.is_ephemeral = False
        response.content = "This is a demonstration message - with buttons!"
        response.action_rows = [
            ActionRow(
                components=[
                    DiscordComponent.button(
                        custom_id="test_button_primary",
                        label="Primary",
                        style=ButtonStyle.PRIMARY
                    ),
                    DiscordComponent.button(
                        custom_id="test_button_secondary",
                        label="Secondary",
                        style=ButtonStyle.SECONDARY
                    ),
                    DiscordComponent.button(
                        custom_id="test_button_success",
                        label="SuCcEsS!",
                        style=ButtonStyle.PRIMARY
                    ),
                    DiscordComponent.button(
                        custom_id="test_button_danger",
                        label="DANGER",
                        style=ButtonStyle.PRIMARY
                    ),
                ]
            )
        ]

        return response
        #
        #     custom_id="test",
        #     title="This is a test",
        #     components=[
        #         DiscordComponent.text_input(
        #             custom_id="test_input",
        #             label="Test Input",
        #             paragraph=False,
        #         )
        #     ]
        # )
