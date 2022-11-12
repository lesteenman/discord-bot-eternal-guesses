from eternal_guesses.model.discord.discord_component import ActionRow, \
    DiscordComponent, DiscordSelectOption
from eternal_guesses.model.discord.discord_event import DiscordEvent
from eternal_guesses.model.discord.discord_response import DiscordResponse
from eternal_guesses.repositories.games_repository import GamesRepository
from eternal_guesses.routes.route import Route
from eternal_guesses.util.component_ids import ComponentIds
from eternal_guesses.util.message_provider import MessageProvider


class ListGamesRoute(Route):
    def __init__(
        self,
        games_repository: GamesRepository,
        message_provider: MessageProvider
    ):
        self.games_repository = games_repository
        self.message_provider = message_provider

    @staticmethod
    def matches(event: DiscordEvent) -> bool:
        return (
            event.command is not None and
            event.command.command_name == 'list-games'
        )

    async def call(self, event: DiscordEvent) -> DiscordResponse:
        guild_id = event.guild_id

        all_games = self.games_repository.get_all(guild_id)

        if 'closed' in event.command.options:
            if event.command.options['closed']:
                closed_games = list(filter(lambda g: g.closed, all_games))
                message = self.message_provider.channel_manage_list_closed_games(
                    closed_games
                )
            else:
                open_games = list(filter(lambda g: not g.closed, all_games))
                message = self.message_provider.channel_manage_list_open_games(
                    open_games
                )
        else:
            message = self.message_provider.channel_manage_list_all_games(
                all_games
            )

        # TODO: Add a multi-selector to select a game to manage

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
                            ) for game in all_games
                        ]
                    )
                ]
            )
        ]

        return response
