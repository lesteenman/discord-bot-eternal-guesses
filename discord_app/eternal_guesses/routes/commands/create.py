from eternal_guesses.model.discord.discord_component import DiscordComponent
from eternal_guesses.model.discord.discord_event import DiscordEvent
from eternal_guesses.model.discord.discord_response import DiscordResponse
from eternal_guesses.repositories.games_repository import GamesRepository
from eternal_guesses.routes.route import Route
from eternal_guesses.app.discord_messaging import DiscordMessaging
from eternal_guesses.app.message_provider import MessageProvider


class CreateRoute(Route):
    def __init__(
        self,
        games_repository: GamesRepository,
        discord_messaging: DiscordMessaging,
        message_provider: MessageProvider
    ):
        self.discord_messaging = discord_messaging
        self.games_repository = games_repository
        self.message_provider = message_provider

    @staticmethod
    def matches(event: DiscordEvent) -> bool:
        return (
            event.command is not None and
            event.command.command_name == 'create-game'
        )

    async def call(self, event: DiscordEvent) -> DiscordResponse:
        return DiscordResponse.modal(
            custom_id="modal_create_game",
            title="Create new game",
            components=[
                DiscordComponent.text_input(
                    custom_id="modal_create_game_id",
                    label="Game Identifier",
                ),
                DiscordComponent.text_input(
                    custom_id="modal_create_game_title",
                    label="Game Title",
                ),
                DiscordComponent.text_input(
                    custom_id="modal_create_game_description",
                    label="Description",
                    paragraph=True,
                ),
                DiscordComponent.text_input(
                    custom_id="modal_create_game_min_value",
                    label="Min guess (optional)",
                    required=False,
                ),
                DiscordComponent.text_input(
                    custom_id="modal_create_game_max_value",
                    label="Max guess (optional)",
                    required=False,
                ),
            ]
        )
