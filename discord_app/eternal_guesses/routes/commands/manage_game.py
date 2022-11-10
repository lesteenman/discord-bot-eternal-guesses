from eternal_guesses.model.discord.discord_component import ActionRow, \
    DiscordComponent
from eternal_guesses.model.discord.discord_event import DiscordEvent
from eternal_guesses.model.discord.discord_response import DiscordResponse, \
    ResponseType
from eternal_guesses.repositories.games_repository import GamesRepository
from eternal_guesses.routes.route import Route
from eternal_guesses.util.custom_id_generator import CustomIdGenerator
from eternal_guesses.util.message_provider import MessageProvider


class ManageGameRoute(Route):
    def __init__(
        self,
        message_provider: MessageProvider,
        games_repository: GamesRepository
    ):
        self.games_repository = games_repository
        self.message_provider = message_provider

    async def call(self, event: DiscordEvent) -> DiscordResponse:
        guild_id = event.guild_id
        game_id = event.command.options['game-id']
        game = self.games_repository.get(guild_id, game_id)

        response = DiscordResponse(
            response_type=ResponseType.CHANNEL_MESSAGE,
        )

        title = game.title if game.title is not None else game.game_id
        response.content = f"Managing game '{title}'. Created at {game.create_datetime}"

        response.is_ephemeral = True
        response.action_rows = [
            ActionRow(
                components=[
                    DiscordComponent.button(
                        custom_id=f"action-manage_game-close-{game_id}",
                        label="Close",
                    ),
                    DiscordComponent.button(
                        custom_id=CustomIdGenerator.trigger_post_game_action(game_id),
                        label="Post",
                    ),
                    DiscordComponent.button(
                        custom_id=f"action-manage_game-edit_guess-{game_id}",
                        label="Edit Guess",
                    ),
                    DiscordComponent.button(
                        custom_id=f"action-manage_game-delete_guess-{game_id}",
                        label="Delete Guess",
                    ),
                ]
            )
        ]

        return response