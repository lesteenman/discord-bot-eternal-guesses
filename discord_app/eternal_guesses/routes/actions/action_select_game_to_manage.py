from eternal_guesses.app.component_ids import ComponentIds
from eternal_guesses.model.data.game import Game
from eternal_guesses.model.discord.discord_component import ActionRow, \
    DiscordComponent
from eternal_guesses.model.discord.discord_event import DiscordEvent
from eternal_guesses.model.discord.discord_response import DiscordResponse
from eternal_guesses.repositories.games_repository import GamesRepository
from eternal_guesses.routes.route import Route


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

        response = DiscordResponse.ephemeral_channel_message(
            content=f"What would you like to do with game '{game.game_id}'?",
        )

        response.action_rows = [
            ActionRow(
                components=self.get_components(game)
            )
        ]

        return response

    @staticmethod
    def get_components(game: Game):
        components = [
            DiscordComponent.button(
                custom_id=ComponentIds.component_button_post_game_id(
                    game.game_id
                ),
                label="Post",
            ),
        ]

        if game.closed:
            components.append(
                DiscordComponent.button(
                    custom_id=ComponentIds.component_button_reopen_game_id(
                        game.game_id
                    ),
                    label="Reopen",
                ),
            )
        else:
            components.append(
                DiscordComponent.button(
                    custom_id=ComponentIds.component_button_close_game_id(
                        game.game_id
                    ),
                    label="Close",
                ),
            )

            components.append(
                DiscordComponent.button(
                    custom_id=ComponentIds.component_button_edit_game_id(
                        game.game_id
                    ),
                    label="Edit Game",
                ),
            )

            components.append(
                DiscordComponent.button(
                    custom_id=ComponentIds.component_button_edit_guess_id(
                        game.game_id
                    ),
                    label="Edit Guess",
                ),
            )

            components.append(
                DiscordComponent.button(
                    custom_id=ComponentIds.component_button_delete_guess_id(
                        game.game_id
                    ),
                    label="Delete Guess",
                ),
            )

        return components
