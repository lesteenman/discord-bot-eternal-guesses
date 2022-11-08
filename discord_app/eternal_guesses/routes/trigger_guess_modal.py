import re

from eternal_guesses.model.discord.discord_component import DiscordComponent
from eternal_guesses.model.discord.discord_event import DiscordEvent
from eternal_guesses.model.discord.discord_response import DiscordResponse
from eternal_guesses.repositories.games_repository import GamesRepository
from eternal_guesses.routes.route import Route
from eternal_guesses.util.message_provider import MessageProvider


class TriggerGuessModalRoute(Route):
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
            r"button_trigger_guess_modal_(.*)",
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
                    custom_id=f"modal_input_guess_value_{game_id}",
                    label=self.message_provider.modal_input_label_guess_value(
                        game
                    )
                )
            ]
        )
        # Create modal with id 'modal_submit_guess_$GAME_ID'
        # And text input 'modal_input_guess_value_$GAME_ID'
