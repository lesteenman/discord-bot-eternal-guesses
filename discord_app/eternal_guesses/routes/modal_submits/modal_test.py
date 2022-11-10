from eternal_guesses.model.discord.discord_component import DiscordComponent
from eternal_guesses.model.discord.discord_event import DiscordEvent
from eternal_guesses.model.discord.discord_response import DiscordResponse
from eternal_guesses.routes.route import Route


class ModalTestRoute(Route):
    async def call(self, event: DiscordEvent) -> DiscordResponse:
        return DiscordResponse.modal(
            custom_id="test",
            title="This is a test",
            components=[
                DiscordComponent.text_input(
                    custom_id="test_input",
                    label="Test Input",
                    paragraph=False,
                )
            ]
        )
