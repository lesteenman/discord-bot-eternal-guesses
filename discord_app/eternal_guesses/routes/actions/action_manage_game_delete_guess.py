import re

import discord

from eternal_guesses.model.discord.discord_component import ComponentType, \
    ActionRow, DiscordComponent, DiscordSelectOption
from eternal_guesses.model.discord.discord_event import DiscordEvent
from eternal_guesses.model.discord.discord_response import DiscordResponse, \
    ResponseType
from eternal_guesses.repositories.games_repository import GamesRepository
from eternal_guesses.routes.route import Route
from eternal_guesses.app.component_ids import ComponentIds
from eternal_guesses.app.message_provider import MessageProvider


class ActionManageGameDeleteGuessRoute(Route):
    def __init__(
        self,
        message_provider: MessageProvider,
        games_repository: GamesRepository,
    ):
        self.games_repository = games_repository
        self.message_provider = message_provider

    @staticmethod
    def matches(event: DiscordEvent) -> bool:
        return (
            event.component_action is not None and
            event.component_action.component_type == ComponentType.BUTTON and
            event.component_action.component_custom_id.startswith(
                ComponentIds.component_button_delete_guess_prefix
            )
        )

    async def call(self, event: DiscordEvent) -> DiscordResponse:
        guild_id = event.guild_id

        custom_id = event.component_action.component_custom_id
        game_id = re.search(
            fr"{ComponentIds.component_button_delete_guess_prefix}(.*)",
            custom_id
        ).group(1)

        game = self.games_repository.get(guild_id, game_id)

        response = DiscordResponse(
            response_type=ResponseType.CHANNEL_MESSAGE,
        )

        guess_list = []
        for user_id, guess in _sorted_guesses(game):
            guess_list.append(f"<@{user_id}> ({user_id}) -> {guess.guess}")

        guesses_string = "\n".join(guess_list)
        response.embed = discord.Embed(
            description=f"Which guess would you like to delete for game {game_id}?\n\n{guesses_string}"
        )

        response.is_ephemeral = True
        response.action_rows = [
            ActionRow(
                components=[
                    DiscordComponent.string_select(
                        placeholder="delete guess",
                        custom_id=ComponentIds.component_select_delete_guess_id(
                            game_id
                        ),
                        options=[
                            DiscordSelectOption(
                                label=f"{u} -> {g.guess}",
                                value=u,
                                description=None,
                            ) for u, g in _sorted_guesses(game)
                        ]
                    )
                ]
            )
        ]

        return response


def _sorted_guesses(game):
    if game.is_numeric():
        return sorted(game.guesses.items(), key=lambda i: int(i[1].guess))
    else:
        return sorted(game.guesses.items(), key=lambda i: i[1].guess)
