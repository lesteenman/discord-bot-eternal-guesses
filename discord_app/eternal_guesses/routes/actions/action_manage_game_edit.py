import re

from eternal_guesses.app.component_ids import ComponentIds
from eternal_guesses.model.discord.discord_component import ActionRow, \
    DiscordComponent
from eternal_guesses.model.discord.discord_event import DiscordEvent
from eternal_guesses.model.discord.discord_response import DiscordResponse
from eternal_guesses.repositories.games_repository import GamesRepository
from eternal_guesses.routes.route import Route


class ActionManageGameEditRoute(Route):
    def __init__(
        self,
        # games_service: GamesService,
        games_repository: GamesRepository
    ):
        pass
        self.games_repository = games_repository
        # self.games_service = games_service

    def matches(self, event: DiscordEvent) -> bool:
        action = event.component_action
        if action is None:
            return False

        custom_id = action.component_custom_id
        return custom_id.startswith(
            ComponentIds.component_button_edit_game_prefix
        )

    async def call(self, event: DiscordEvent) -> DiscordResponse:
        guild_id = event.guild_id
        game_id = re.search(
            fr"{ComponentIds.component_button_edit_game_prefix}(.*)",
            event.component_action.component_custom_id
        ).group(1)

        game = self.games_repository.get(guild_id, game_id)

        edit_title_button_id = ComponentIds.button_edit_game_title_id(
            game_id
        )
        edit_min_guess_button_id = ComponentIds.button_edit_game_min_guess_id(
            game_id
        )
        edit_max_guess_button_id = ComponentIds.button_edit_game_max_guess_id(
            game_id
        )
        edit_desc_button_id = ComponentIds.button_edit_game_description_id(
            game_id
        )

        return DiscordResponse.ephemeral_channel_message(
            content=f""" What do you want to edit?

Title: {game.title or 'None'}
Min value: '{game.min_guess or 'None'}'
Max value: '{game.max_guess or 'None'}'
Description: {game.description or 'None'}
            """,
            action_rows=[
                ActionRow(
                    components=[
                        DiscordComponent.button(
                            custom_id=edit_title_button_id,
                            label="Edit title",
                        ),
                        DiscordComponent.button(
                            custom_id=edit_min_guess_button_id,
                            label="Edit min guess",
                        ),
                        DiscordComponent.button(
                            custom_id=edit_max_guess_button_id,
                            label="Edit max guess",
                        ),
                        DiscordComponent.button(
                            custom_id=edit_desc_button_id,
                            label="Edit description",
                        ),
                    ]
                )
            ]
        )
