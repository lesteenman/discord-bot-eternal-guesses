from typing import Dict
from unittest.mock import MagicMock

import pytest

from eternal_guesses.discord_messaging import DiscordMessaging
from eternal_guesses.errors import DiscordEventDisallowedError
from eternal_guesses.model.data.game import Game
from eternal_guesses.model.data.channel_message import ChannelMessage
from eternal_guesses.model.discord.discord_event import DiscordEvent, DiscordCommand, CommandType
from eternal_guesses.model.discord.discord_member import DiscordMember
from eternal_guesses.repositories.games_repository import GamesRepository
from eternal_guesses.routes.manage import ManageRoute
from eternal_guesses.util.message_provider import MessageProvider
from tests.fakes import FakeDiscordMessaging, FakeGamesRepository, FakeCommandAuthorizer, FakeMessageProvider

pytestmark = pytest.mark.asyncio


async def test_list_all_without_closed_option():
    # Given
    guild_id = 100
    role_id = 500

    list_games_message = "message listing all games, open and closed"
    message_provider = MagicMock(MessageProvider)
    message_provider.channel_manage_list_all_games.return_value = list_games_message

    open_game = Game(closed=False)
    closed_game = Game(closed=True)
    games_repository = FakeGamesRepository([open_game, closed_game])

    discord_messaging = FakeDiscordMessaging()
    command_authorizer = FakeCommandAuthorizer(passes=True)

    manage_route = ManageRoute(
        games_repository=games_repository,
        discord_messaging=discord_messaging,
        message_provider=message_provider,
        command_authorizer=command_authorizer,
    )

    # When
    event = DiscordEvent(
        command_type=CommandType.COMMAND,
        guild_id=guild_id,
        command=DiscordCommand(
            command_id=-1,
            command_name="manage",
            subcommand_name="list",
            options={}
        ),
        member=DiscordMember(roles=[role_id])
    )
    await manage_route.list_games(event)

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
    manage_route = ManageRoute(
        games_repository=games_repository,
        discord_messaging=discord_messaging,
        message_provider=message_provider,
        command_authorizer=FakeCommandAuthorizer(passes=True)
    )

    # When we list only the closed games
    event = _make_event(guild_id=guild_id, options={
        'closed': True
    })
    await manage_route.list_games(event)

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
    manage_route = ManageRoute(
        games_repository=games_repository,
        discord_messaging=discord_messaging,
        message_provider=message_provider,
        command_authorizer=FakeCommandAuthorizer(passes=True)
    )

    # When we list only the open games
    event = _make_event(guild_id=guild_id, options={
        'closed': False
    })
    await manage_route.list_games(event)

    # Then: a message is sent based on only the open games
    message_provider.channel_manage_list_open_games.assert_called()
    used_games = message_provider.channel_manage_list_open_games.call_args.args[0]
    assert closed_game not in used_games
    assert open_game in used_games

    assert len(discord_messaging.sent_channel_messages) == 1
    sent_message = discord_messaging.sent_channel_messages[0]
    assert sent_message['text'] == list_games_message


async def test_close():
    # Given
    guild_id = 1007
    game_id = 'game-id-1'

    # We have an open game
    game = Game(
        game_id=game_id,
        guild_id=guild_id,
        closed=False
    )
    games_repository = FakeGamesRepository([game])

    event = _make_event(
        guild_id=guild_id,
        options={
            'game-id': game.game_id,
        }
    )

    discord_messaging = FakeDiscordMessaging()
    manage_route = ManageRoute(
        games_repository=games_repository,
        discord_messaging=discord_messaging,
        message_provider=MessageProvider(),
        command_authorizer=FakeCommandAuthorizer(passes=True)
    )

    # When we close it
    await manage_route.close(event)

    # Then it should be closed
    saved_game = games_repository.get(guild_id, game.game_id)
    assert saved_game.closed


async def test_close_updates_channel_messages():
    guild_id = 1007
    game_id = 'game-id-1'

    # We have an open game with channel messages
    channel_message_1 = ChannelMessage(channel_id=1, message_id=10)
    channel_message_2 = ChannelMessage(channel_id=2, message_id=11)
    game = Game(
        game_id=game_id,
        guild_id=guild_id,
        closed=False,
        channel_messages=[channel_message_1, channel_message_2]
    )
    games_repository = FakeGamesRepository([game])

    discord_messaging = FakeDiscordMessaging()
    manage_route = ManageRoute(
        games_repository=games_repository,
        discord_messaging=discord_messaging,
        message_provider=FakeMessageProvider(),
        command_authorizer=FakeCommandAuthorizer(passes=True)
    )

    # When we close it
    event = _make_event(
        guild_id=guild_id,
        options={
            'game-id': game.game_id,
        }
    )
    await manage_route.close(event)

    # Then the channel messages are updated
    assert len(discord_messaging.updated_channel_messages) == 2

    assert any(
        map(lambda m: m['message_id'] == channel_message_1.message_id, discord_messaging.updated_channel_messages))

    assert any(
        map(lambda m: m['message_id'] == channel_message_2.message_id, discord_messaging.updated_channel_messages))


async def test_close_already_closed_game():
    # Given
    guild_id = 1007
    game_id = 'game-id-1'

    # We have a closed game
    game = Game(
        game_id=game_id,
        guild_id=guild_id,
        closed=True
    )
    games_repository = FakeGamesRepository([game])

    event = _make_event(
        guild_id=guild_id,
        options={
            'game-id': game.game_id,
        }
    )

    manage_route = ManageRoute(
        games_repository=games_repository,
        discord_messaging=FakeDiscordMessaging(),
        message_provider=MessageProvider(),
        command_authorizer=FakeCommandAuthorizer(passes=True)
    )

    # When we close it again
    await manage_route.close(event)

    # Then it should just still be closed
    saved_game = games_repository.get(guild_id, game.game_id)
    assert saved_game.closed


async def test_list_disallowed():
    # Given
    command_authorizer = FakeCommandAuthorizer(passes=False)

    manage_route = ManageRoute(
        command_authorizer=command_authorizer,
        games_repository=GamesRepository(),
        discord_messaging=DiscordMessaging(),
        message_provider=MessageProvider()
    )

    # When
    event = DiscordEvent(
        command_type=CommandType.COMMAND,
        guild_id=-1,
        command=DiscordCommand(
            command_id=-1,
            command_name="manage",
            subcommand_name="list"
        ),
        member=DiscordMember(),
        channel_id=101
    )

    # Then
    try:
        await manage_route.list_games(event)
        assert False
    except DiscordEventDisallowedError:
        pass


async def test_close_disallowed():
    # Given
    command_authorizer = FakeCommandAuthorizer(passes=False)

    manage_route = ManageRoute(games_repository=GamesRepository(), discord_messaging=DiscordMessaging(),
                               message_provider=MessageProvider(), command_authorizer=command_authorizer)

    # When
    event = DiscordEvent(
        command_type=CommandType.COMMAND,
        guild_id=-1,
        command=DiscordCommand(
            command_id=-1,
            command_name="manage",
            subcommand_name="close"
        ),
        member=DiscordMember(),
        channel_id=101
    )

    # Then
    try:
        await manage_route.close(event)
        assert False
    except DiscordEventDisallowedError:
        pass


def _make_event(guild_id: int = -1, options: Dict = None, discord_member: DiscordMember = None, channel_id: int = -1):
    if options is None:
        options = {}

    if discord_member is None:
        discord_member = DiscordMember()

    return DiscordEvent(
        command_type=CommandType.COMMAND,
        guild_id=guild_id,
        channel_id=channel_id,
        command=DiscordCommand(
            command_id=-1,
            command_name="manage",
            subcommand_name="does-not-matter",
            options=options,
        ),
        member=discord_member
    )
