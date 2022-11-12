import re

from eternal_guesses.model.discord.discord_component import DiscordComponent, \
    ComponentType
from eternal_guesses.model.discord.discord_event import DiscordEvent
from eternal_guesses.model.discord.discord_response import DiscordResponse
from eternal_guesses.repositories.games_repository import GamesRepository
from eternal_guesses.routes.route import Route
from eternal_guesses.util.component_ids import ComponentIds
from eternal_guesses.util.message_provider import MessageProvider


# Triggered by clicking the 'guess' button on a game.
# Shows a modal to enter the guess in.
class ActionGameGuessRoute(Route):
    def __init__(
        self,
        message_provider: MessageProvider,
        games_repository: GamesRepository
    ):
        self.games_repository = games_repository
        self.message_provider = message_provider

    @staticmethod
    def matches(event: DiscordEvent) -> bool:
        return (
            event.component_action is not None and
            event.component_action.component_type == ComponentType.BUTTON and
            event.component_action.component_custom_id.startswith(
                ComponentIds.component_button_guess_prefix
            )
        )

    async def call(self, event: DiscordEvent) -> DiscordResponse:
        component_action = event.component_action
        game_id = re.search(
            fr"{ComponentIds.component_button_guess_prefix}(.*)",
            component_action.component_custom_id
        ).group(1)

        game = self.games_repository.get(
            guild_id=event.guild_id,
            game_id=game_id
        )

        user_id = event.member.user_id
        if game.guesses.get(user_id) is not None:
            error_message = self.message_provider.error_duplicate_guess(game_id)
            return DiscordResponse.ephemeral_channel_message(error_message)

        return DiscordResponse.modal(
            custom_id=ComponentIds.submit_guess_modal_id(game_id),
            title=self.message_provider.modal_title_place_guess(game),
            components=[
                DiscordComponent.text_input(
                    custom_id=ComponentIds.submit_guess_input_value,
                    label=self.message_provider.modal_input_label_guess_value(
                        game
                    )
                )
            ]
        )
