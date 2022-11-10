import re

from eternal_guesses.model.discord.discord_component import DiscordComponent
from eternal_guesses.model.discord.discord_event import DiscordEvent
from eternal_guesses.model.discord.discord_response import DiscordResponse
from eternal_guesses.repositories.games_repository import GamesRepository
from eternal_guesses.routes.route import Route
from eternal_guesses.util.custom_id_generator import CustomIdGenerator
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

    async def call(self, event: DiscordEvent) -> DiscordResponse:
        component_action = event.component_action
        game_id = re.search(
            CustomIdGenerator.trigger_guess_modal_action_game_id_regex,
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
            custom_id=f"modal_submit_guess_{game_id}",
            title=self.message_provider.modal_title_place_guess(game),
            components=[
                DiscordComponent.text_input(
                    custom_id=CustomIdGenerator.guess_modal_input_guess,
                    label=self.message_provider.modal_input_label_guess_value(
                        game
                    )
                )
            ]
        )
