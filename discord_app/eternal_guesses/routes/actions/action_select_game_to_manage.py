from eternal_guesses.model.discord.discord_component import ActionRow, \
    DiscordComponent
from eternal_guesses.model.discord.discord_event import DiscordEvent
from eternal_guesses.model.discord.discord_response import DiscordResponse
from eternal_guesses.repositories.games_repository import GamesRepository
from eternal_guesses.routes.route import Route
from eternal_guesses.util.component_ids import ComponentIds


class ActionSelectGameToManageRoute(Route):
    def __init__(self, games_repository: GamesRepository):
        self.games_repository = games_repository

    @staticmethod
    def matches(event: DiscordEvent) -> bool:
        action = event.component_action
        return (
            action is not None and
            action.component_custom_id == ComponentIds.component_select_game_to_manage
        )

    async def call(self, event: DiscordEvent) -> DiscordResponse:
        guild_id = event.guild_id
        game_id = event.component_action.values[0]
        game = self.games_repository.get(guild_id, game_id)

        title = game.title if game.title is not None else game.game_id

        response = DiscordResponse.ephemeral_channel_message(
            content=f"Managing game '{title}'. Created at {game.create_datetime}",
        )

        response.action_rows = [
            ActionRow(
                components=[
                    DiscordComponent.button(
                        custom_id=ComponentIds.component_button_close_game_id(
                            game_id
                        ),
                        label="Close",
                    ),
                    DiscordComponent.button(
                        custom_id=ComponentIds.component_button_post_game_id(
                            game_id
                        ),
                        label="Post",
                    ),
                    DiscordComponent.button(
                        custom_id=ComponentIds.component_button_edit_game_id(
                            game_id
                        ),
                        label="Edit Game",
                    ),
                    DiscordComponent.button(
                        custom_id=ComponentIds.component_button_edit_guess_id(
                            game_id
                        ),
                        label="Edit Guess",
                    ),
                    DiscordComponent.button(
                        custom_id=ComponentIds.component_button_delete_guess_id(
                            game_id
                        ),
                        label="Delete Guess",
                    ),
                ]
            )
        ]

        return response
