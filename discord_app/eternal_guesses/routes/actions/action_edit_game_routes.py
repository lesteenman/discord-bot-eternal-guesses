import re
from abc import ABC

from eternal_guesses.app.component_ids import ComponentIds
from eternal_guesses.model.discord.discord_component import ComponentType, \
    DiscordComponent
from eternal_guesses.model.discord.discord_event import DiscordEvent
from eternal_guesses.model.discord.discord_response import DiscordResponse
from eternal_guesses.routes.route import Route


class ActionEditGameRoute(Route, ABC):
    def __init__(
        self,
        prefix: str,
        input_id: str,
        is_paragraph: bool,
        name: str,
        modal_id_func
    ):
        self.modal_id_func = modal_id_func
        self.name = name
        self.prefix = prefix
        self.input_id = input_id
        self.is_paragraph = is_paragraph

    def matches(self, event: DiscordEvent) -> bool:
        action = event.component_action
        return (
            action is not None and
            action.component_type == ComponentType.BUTTON and
            action.component_custom_id.startswith(self.prefix)
        )

    async def call(self, event: DiscordEvent) -> DiscordResponse:
        game_id = re.search(
            fr"{self.prefix}(.*)",
            event.component_action.component_custom_id
        ).group(1)

        return DiscordResponse.modal(
            custom_id=self.modal_id_func(game_id=game_id),
            title=f"Edit {self.name}",
            components=[
                DiscordComponent.text_input(
                    custom_id=self.input_id,
                    label=f"New {self.name}"
                )
            ]
        )


class ActionEditGameTitleRoute(ActionEditGameRoute):
    def __init__(self):
        super().__init__(
            prefix=ComponentIds.button_edit_game_title_prefix,
            modal_id_func=ComponentIds.edit_game_title_modal_id,
            input_id=ComponentIds.edit_game_title_input,
            is_paragraph=False,
            name="title"
        )


class ActionEditGameMinGuessRoute(ActionEditGameRoute):
    def __init__(self):
        super().__init__(
            prefix=ComponentIds.button_edit_game_min_guess_prefix,
            modal_id_func=ComponentIds.edit_game_min_guess_modal_id,
            input_id=ComponentIds.edit_game_min_guess_input,
            is_paragraph=False,
            name="minimum guess"
        )


class ActionEditGameMaxGuessRoute(ActionEditGameRoute):
    def __init__(self):
        super().__init__(
            prefix=ComponentIds.button_edit_game_max_guess_prefix,
            modal_id_func=ComponentIds.edit_game_max_guess_modal_id,
            input_id=ComponentIds.edit_game_max_guess_input,
            is_paragraph=False,
            name="maximum guess"
        )


class ActionEditGameDescriptionRoute(ActionEditGameRoute):
    def __init__(self):
        super().__init__(
            prefix=ComponentIds.button_edit_game_description_prefix,
            modal_id_func=ComponentIds.edit_game_description_modal_id,
            input_id=ComponentIds.edit_game_description_input,
            is_paragraph=True,
            name="description"
        )
