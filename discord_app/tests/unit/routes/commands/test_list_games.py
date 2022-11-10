import typing
from unittest.mock import MagicMock

import pytest

from eternal_guesses.model.data.game import Game
from eternal_guesses.model.discord.discord_command import DiscordCommand
from eternal_guesses.model.discord.discord_event import DiscordEvent
from eternal_guesses.model.discord.discord_member import DiscordMember
from eternal_guesses.routes.commands.list_games import ListGamesRoute
from eternal_guesses.util.message_provider import MessageProvider
from tests.fakes import FakeGamesRepository

pytestmark = pytest.mark.asyncio


async def test_list_all_without_closed_option():
    # Given
    list_games_message = "message listing all games, open and closed"
    message_provider = MagicMock(MessageProvider)
    message_provider.channel_manage_list_all_games.return_value = list_games_message

    open_game = Game(closed=False)
    closed_game = Game(closed=True)
    games_repository = FakeGamesRepository([open_game, closed_game])

    route = ListGamesRoute(
        games_repository=games_repository,
        message_provider=message_provider,
    )

    # When
    event = _make_event(
        options={}
    )
    response = await route.call(event)

    # Then
    message_provider.channel_manage_list_all_games.assert_called()
    used_games = message_provider.channel_manage_list_all_games.call_args.args[0]
    assert closed_game in used_games
    assert open_game in used_games

    assert response.is_ephemeral
    assert response.content == list_games_message


async def test_list_all_closed_games():
    # Given
    guild_id = 100

    # We have one open and one closed game
    open_game = Game(closed=False)
    closed_game = Game(closed=True)
    games_repository = FakeGamesRepository([open_game, closed_game])

    # And we have a mock message provider
    list_games_message = "message listing all games, open and closed"
    message_provider = MagicMock(MessageProvider)
    message_provider.channel_manage_list_closed_games.return_value = list_games_message

    route = ListGamesRoute(
        games_repository=games_repository,
        message_provider=message_provider,
    )

    # When we list only the closed games
    event = _make_event(guild_id=guild_id, options={
        'closed': True
    })
    response = await route.call(event)

    # Then: a message is sent based on only the closed games
    message_provider.channel_manage_list_closed_games.assert_called()
    used_games = message_provider.channel_manage_list_closed_games.call_args.args[0]
    assert closed_game in used_games
    assert open_game not in used_games

    assert response.is_ephemeral
    assert response.content == list_games_message


async def test_list_all_open_games():
    # Given
    guild_id = 100

    # We have one open and one closed game
    open_game = Game(closed=False)
    closed_game = Game(closed=True)
    games_repository = FakeGamesRepository([open_game, closed_game])

    # And we have a mock message provider
    list_games_message = "message listing all games, open and closed"
    message_provider = MagicMock(MessageProvider)
    message_provider.channel_manage_list_open_games.return_value = list_games_message

    route = ListGamesRoute(
        games_repository=games_repository,
        message_provider=message_provider,
    )

    # When we list only the open games
    event = _make_event(guild_id=guild_id, options={
        'closed': False
    })
    response = await route.call(event)

    # Then: a message is sent based on only the open games
    message_provider.channel_manage_list_open_games.assert_called()
    used_games = message_provider.channel_manage_list_open_games.call_args.args[0]
    assert closed_game not in used_games
    assert open_game in used_games

    assert response.is_ephemeral
    assert response.content == list_games_message


def _make_event(guild_id: int = -1,
                options: typing.Dict = None,
                discord_member: DiscordMember = None,
                channel_id: int = -1):
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
