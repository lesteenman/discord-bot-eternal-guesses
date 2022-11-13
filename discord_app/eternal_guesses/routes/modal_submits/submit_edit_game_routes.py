import re
import typing
from abc import ABC

from eternal_guesses.app.component_ids import ComponentIds
from eternal_guesses.model.discord.discord_event import DiscordEvent
from eternal_guesses.model.discord.discord_response import DiscordResponse
from eternal_guesses.routes.route import Route
from eternal_guesses.services.games_service import GamesService


class SubmitEditGameRoute(Route, ABC):
    def __init__(
        self,
        games_helper: GamesService,
        modal_prefix: str,
        input_id: str,
        game_update_func: typing.Callable[
            [int, str, str], typing.Awaitable[typing.Any]]
    ):
        self.games_helper = games_helper
        self.modal_prefix = modal_prefix
        self.input_id = input_id
        self.game_update_func = game_update_func

    def matches(self, event: DiscordEvent) -> bool:
        modal = event.modal_submit
        if modal is None:
            return False

        return modal.modal_custom_id.startswith(self.modal_prefix)

    async def call(self, event: DiscordEvent) -> DiscordResponse:
        game_id = re.search(
            fr"{self.modal_prefix}(.*)",
            event.modal_submit.modal_custom_id,
        ).group(1)

        new_value = event.modal_submit.inputs[self.input_id]

        await self.game_update_func(event.guild_id, game_id, new_value)

        return DiscordResponse.ephemeral_channel_message(
            content="Game edited."
        )


class SubmitEditGameTitleRoute(SubmitEditGameRoute):
    def __init__(self, games_service: GamesService):
        super().__init__(
            games_service,
            ComponentIds.edit_game_title_modal_prefix,
            ComponentIds.edit_game_title_input,
            games_service.edit_title
        )


class SubmitEditGameMinGuessRoute(SubmitEditGameRoute):
    def __init__(self, games_service: GamesService):
        super().__init__(
            games_service,
            ComponentIds.edit_game_min_guess_modal_prefix,
            ComponentIds.edit_game_min_guess_input,
            games_service.edit_min_guess
        )


class SubmitEditGameMaxGuessRoute(SubmitEditGameRoute):
    def __init__(self, games_service: GamesService):
        super().__init__(
            games_service,
            ComponentIds.edit_game_max_guess_modal_prefix,
            ComponentIds.edit_game_max_guess_input,
            games_service.edit_max_guess
        )


class SubmitEditGameDescriptionRoute(SubmitEditGameRoute):
    def __init__(self, games_service: GamesService):
        super().__init__(
            games_service,
            ComponentIds.edit_game_description_modal_prefix,
            ComponentIds.edit_game_description_input,
            games_service.edit_description
        )
