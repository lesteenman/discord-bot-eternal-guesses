import re
import typing
from abc import ABC

from loguru import logger

from eternal_guesses.app.component_ids import ComponentIds
from eternal_guesses.model.discord.discord_event import DiscordEvent
from eternal_guesses.model.discord.discord_response import DiscordResponse
from eternal_guesses.routes.route import Route
from eternal_guesses.services.games_service import GamesService


class SubmitEditGameRoute(Route, ABC):
    def __init__(
        self,
        games_service: GamesService,
        modal_prefix: str,
        input_id: str,
        game_update_func: typing.Callable[
            [int, str, str], typing.Awaitable[typing.Any]],
        is_numeric: bool,
    ):
        self.is_numeric = is_numeric
        self.games_helper = games_service
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
        if self.is_numeric:
            new_value = int(new_value)

        logger.info(f"guild_id={event.guild_id}, user {event.member.user_id} "
                    f"editing game, field {self.input_id}, new value is"
                    f"{new_value}")

        await self.game_update_func(event.guild_id, game_id, new_value)

        return DiscordResponse.ephemeral_channel_message(
            content="Game edited."
        )


class SubmitEditGameTitleRoute(SubmitEditGameRoute):
    def __init__(self, games_service: GamesService):
        super().__init__(
            games_service=games_service,
            modal_prefix=ComponentIds.edit_game_title_modal_prefix,
            input_id=ComponentIds.edit_game_title_input,
            game_update_func=games_service.edit_title,
            is_numeric=False,
        )


class SubmitEditGameMinGuessRoute(SubmitEditGameRoute):
    def __init__(self, games_service: GamesService):
        super().__init__(
            games_service=games_service,
            modal_prefix=ComponentIds.edit_game_min_guess_modal_prefix,
            input_id=ComponentIds.edit_game_min_guess_input,
            game_update_func=games_service.edit_min_guess,
            is_numeric=True,
        )


class SubmitEditGameMaxGuessRoute(SubmitEditGameRoute):
    def __init__(self, games_service: GamesService):
        super().__init__(
            games_service=games_service,
            modal_prefix=ComponentIds.edit_game_max_guess_modal_prefix,
            input_id=ComponentIds.edit_game_max_guess_input,
            game_update_func=games_service.edit_max_guess,
            is_numeric=True,
        )


class SubmitEditGameDescriptionRoute(SubmitEditGameRoute):
    def __init__(self, games_service: GamesService):
        super().__init__(
            games_service=games_service,
            modal_prefix=ComponentIds.edit_game_description_modal_prefix,
            input_id=ComponentIds.edit_game_description_input,
            game_update_func=games_service.edit_description,
            is_numeric=False,
        )
