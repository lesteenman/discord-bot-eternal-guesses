import typing
from unittest.mock import MagicMock, Mock

import pytest

from eternal_guesses.app.message_provider import MessageProvider
from eternal_guesses.model.data.game import Game
from eternal_guesses.model.discord.discord_command import DiscordCommand
from eternal_guesses.model.discord.discord_event import DiscordEvent
from eternal_guesses.model.discord.discord_member import DiscordMember
from eternal_guesses.routes.commands.list_games import ListGamesRoute
from eternal_guesses.services.games_service import GamesService
from tests.fakes import FakeGamesRepository

pytestmark = pytest.mark.asyncio


async def test_list_all_without_closed_option():
    # Given
    list_games_message = "message listing all games, open and closed"
    message_provider = MagicMock(MessageProvider)
    message_provider.channel_manage_list_all_games.return_value = list_games_message

    open_game = Game(game_id="open-game", closed=False)
    closed_game = Game(game_id="closed-game", closed=True)
    games_repository = FakeGamesRepository([open_game, closed_game])

    route = ListGamesRoute(
        games_service=GamesService(
            games_repository=games_repository,
            game_post_manager=Mock(),
        ),
        message_provider=message_provider,
    )

    # When
    event = _make_event(
        options={}
    )
    response = await route.call(event)

    # Then
    assert response.is_ephemeral
    assert open_game.game_id in response.content
    assert closed_game.game_id not in response.content


async def test_list_all_games_including_closed():
    # Given
    guild_id = 100

    # We have one open and one closed game
    open_game = Game(game_id="open-game", closed=False)
    closed_game = Game(game_id="closed-game", closed=True)
    games_repository = FakeGamesRepository([open_game, closed_game])

    # And we have a mock message provider
    list_games_message = "message listing all games, open and closed"
    message_provider = MagicMock(MessageProvider)
    message_provider.channel_manage_list_closed_games.return_value = list_games_message

    route = ListGamesRoute(
        games_service=GamesService(
            games_repository=games_repository,
            game_post_manager=Mock(),
        ),
        message_provider=message_provider,
    )

    # When we list only the closed games
    event = _make_event(
        guild_id=guild_id, options={
            'include-closed': True
        }
    )
    response = await route.call(event)

    # Then: a message is sent based on only the closed games
    assert response.is_ephemeral
    assert closed_game.game_id in response.content
    assert open_game.game_id in response.content


def _make_event(
    guild_id: int = -1,
    options: typing.Dict = None,
    discord_member: DiscordMember = None,
    channel_id: int = -1
):
    if options is None:
        options = {}

    if discord_member is None:
        discord_member = DiscordMember()

    return DiscordEvent(
        guild_id=guild_id,
        channel_id=channel_id,
        command=DiscordCommand(
            command_name="manage",
            subcommand_name="list-games",
            options=options,
        ),
        member=discord_member
    )
