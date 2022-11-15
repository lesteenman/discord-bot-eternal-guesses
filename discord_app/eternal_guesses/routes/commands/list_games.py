from eternal_guesses.app.component_ids import ComponentIds
from eternal_guesses.app.message_provider import MessageProvider
from eternal_guesses.model.discord.discord_component import ActionRow, \
    DiscordComponent, DiscordSelectOption
from eternal_guesses.model.discord.discord_event import DiscordEvent
from eternal_guesses.model.discord.discord_response import DiscordResponse
from eternal_guesses.routes.route import Route
from eternal_guesses.services.games_service import GamesService


class ListGamesRoute(Route):
    def __init__(
        self,
        message_provider: MessageProvider,
        games_service: GamesService,
    ):
        self.games_service = games_service
        self.message_provider = message_provider

    @staticmethod
    def matches(event: DiscordEvent) -> bool:
        return (
            event.command is not None and
            event.command.command_name == 'list-games'
        )

    async def call(self, event: DiscordEvent) -> DiscordResponse:
        guild_id = event.guild_id

        include_closed = False
        if 'include-closed' in event.command.options:
            include_closed = event.command.options['include-closed']

        games = self.games_service.list(
            guild_id=guild_id,
            include_closed=include_closed
        )

        lines = []
        for game in games:
            line = f"- {game.game_id}"
            if game.closed:
                line = f"{line} (closed)"

            lines.append(line)

        if include_closed:
            message = "All games:\n"
        else:
            message = "All open games:\n"

        message = message + "\n".join(sorted(lines))

        response = DiscordResponse.ephemeral_channel_message(message)
        response.action_rows = [
            ActionRow(
                components=[
                    DiscordComponent.string_select(
                        placeholder="Manage Game",
                        custom_id=ComponentIds.component_select_game_to_manage,
                        options=[
                            DiscordSelectOption(
                                label=game.game_id,
                                value=game.game_id,
                                description=None,
                            ) for game in games
                        ]
                    )
                ]
            )
        ]

        return response
