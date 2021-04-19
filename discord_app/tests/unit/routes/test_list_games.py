import typing
from unittest.mock import MagicMock

import pytest

from eternal_guesses.model.data.game import Game
from eternal_guesses.model.discord.discord_command import DiscordCommand
from eternal_guesses.model.discord.discord_event import DiscordEvent
from eternal_guesses.model.discord.discord_member import DiscordMember
from eternal_guesses.model.error.discord_event_disallowed_error import DiscordEventDisallowedError
from eternal_guesses.repositories.games_repository import GamesRepository
from eternal_guesses.routes.list_games import ListGamesRoute
from eternal_guesses.util.discord_messaging import DiscordMessaging
from eternal_guesses.util.message_provider import MessageProvider
from tests.fakes import FakeGamesRepository, FakeDiscordMessaging, FakeCommandAuthorizer

pytestmark = pytest.mark.asyncio


async def test_list_all_without_closed_option():
    # Given
    list_games_message = "message listing all games, open and closed"
    message_provider = MagicMock(MessageProvider)
    message_provider.channel_manage_list_all_games.return_value = list_games_message

    open_game = Game(closed=False)
    closed_game = Game(closed=True)
    games_repository = FakeGamesRepository([open_game, closed_game])

    discord_messaging = FakeDiscordMessaging()
    command_authorizer = FakeCommandAuthorizer(management=True)

    route = ListGamesRoute(
        games_repository=games_repository,
        discord_messaging=discord_messaging,
        message_provider=message_provider,
        command_authorizer=command_authorizer,
    )

    # When
    event = _make_event(
        options={}
    )
    await route.call(event)

    # Then
    message_provider.channel_manage_list_all_games.assert_called()
    used_games = message_provider.channel_manage_list_all_games.call_args.args[0]
    assert closed_game in used_games
    assert open_game in used_games

    assert len(discord_messaging.sent_channel_messages) == 1
    sent_message = discord_messaging.sent_channel_messages[0]

    assert sent_message['text'] == list_games_message


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

    discord_messaging = FakeDiscordMessaging()
    route = ListGamesRoute(
        games_repository=games_repository,
        discord_messaging=discord_messaging,
        message_provider=message_provider,
        command_authorizer=FakeCommandAuthorizer(management=True)
    )

    # When we list only the closed games
    event = _make_event(guild_id=guild_id, options={
        'closed': True
    })
    await route.call(event)

    # Then: a message is sent based on only the closed games
    message_provider.channel_manage_list_closed_games.assert_called()
    used_games = message_provider.channel_manage_list_closed_games.call_args.args[0]
    assert closed_game in used_games
    assert open_game not in used_games

    assert len(discord_messaging.sent_channel_messages)
    sent_game = discord_messaging.sent_channel_messages[0]
    assert sent_game['text'] == list_games_message


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

    discord_messaging = FakeDiscordMessaging()
    route = ListGamesRoute(
        games_repository=games_repository,
        discord_messaging=discord_messaging,
        message_provider=message_provider,
        command_authorizer=FakeCommandAuthorizer(management=True)
    )

    # When we list only the open games
    event = _make_event(guild_id=guild_id, options={
        'closed': False
    })
    await route.call(event)

    # Then: a message is sent based on only the open games
    message_provider.channel_manage_list_open_games.assert_called()
    used_games = message_provider.channel_manage_list_open_games.call_args.args[0]
    assert closed_game not in used_games
    assert open_game in used_games

    assert len(discord_messaging.sent_channel_messages) == 1
    sent_message = discord_messaging.sent_channel_messages[0]
    assert sent_message['text'] == list_games_message


async def test_list_disallowed():
    # Given
    command_authorizer = FakeCommandAuthorizer(management=False)

    route = ListGamesRoute(
        command_authorizer=command_authorizer,
        games_repository=GamesRepository(),
        discord_messaging=DiscordMessaging(),
        message_provider=MessageProvider()
    )

    # When
    try:
        event = _make_event()
        await route.call(event)
        assert False
    # Then
    except DiscordEventDisallowedError:
        pass


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
