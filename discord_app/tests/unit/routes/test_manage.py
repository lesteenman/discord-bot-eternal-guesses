from typing import Dict
from unittest.mock import MagicMock

import pytest

from eternal_guesses.discord_messaging import DiscordMessaging
from eternal_guesses.errors import DiscordEventDisallowedError
from eternal_guesses.model.data.game import Game
from eternal_guesses.model.discord.discord_event import DiscordEvent, DiscordCommand, CommandType
from eternal_guesses.model.discord.discord_member import DiscordMember
from eternal_guesses.repositories.games_repository import GamesRepository
from eternal_guesses.routes.manage import ManageRoute
from eternal_guesses.util.message_provider import MessageProvider
from tests.fakes import FakeDiscordMessaging, FakeGamesRepository, FakeCommandAuthorizer

pytestmark = pytest.mark.asyncio


async def test_post_creates_channel_message():
    # Given
    guild_id = 1001
    game_id = 'game-1'
    channel_id = 50001

    # We have a game
    game = Game(guild_id=guild_id, game_id=game_id)
    games_repository = FakeGamesRepository([game])

    # And we have a mock message provider
    formatted_message = "mock formatted message"
    message_provider = MagicMock(MessageProvider)
    message_provider.channel_list_game_guesses.return_value = formatted_message

    discord_messaging = FakeDiscordMessaging()
    manage_route = ManageRoute(
        games_repository=games_repository,
        discord_messaging=discord_messaging,
        message_provider=message_provider,
        command_authorizer=FakeCommandAuthorizer(passes=True)
    )

    # When we post a channel message for our game with an explicit channel
    event = _make_event(guild_id=guild_id, options={
        'game-id': game_id,
        'channel': channel_id,
    })
    await manage_route.post(event)

    # Then a message is posted based on that game
    message_provider.channel_list_game_guesses.assert_called_with(game)

    # And it is sent in the given channel
    assert {'channel_id': channel_id, 'text': formatted_message} in discord_messaging.sent_channel_messages

    # And the channel id is saved in the game
    saved_game = games_repository.get(guild_id, game_id)
    assert len(saved_game.channel_messages) == 1


async def test_post_without_channel_uses_event_channel():
    # Given
    guild_id = 1001
    game_id = 'game-1'
    event_channel_id = 50001

    # We have a game
    game = Game(guild_id=guild_id, game_id=game_id)
    games_repository = FakeGamesRepository([game])

    formatted_message = "mock formatted message"
    message_provider = MagicMock(MessageProvider)
    message_provider.channel_list_game_guesses.return_value = formatted_message

    discord_messaging = FakeDiscordMessaging()

    manage_route = ManageRoute(
        games_repository=games_repository,
        discord_messaging=discord_messaging,
        message_provider=message_provider,
        command_authorizer=FakeCommandAuthorizer(passes=True)
    )

    # When we post a channel message without an explicit target channel
    event = DiscordEvent(
        command_type=CommandType.COMMAND,
        guild_id=guild_id,
        channel_id=event_channel_id,
        command=DiscordCommand(
            command_id=-1,
            command_name="manage",
            subcommand_name="post",
            options={
                'game-id': game_id,
            }
        ),
        member=DiscordMember()
    )
    await manage_route.post(event)

    # Then a message is posted based on that game
    message_provider.channel_list_game_guesses.assert_called_with(game)

    # And it is posted in the channel we sent this command from
    assert {'channel_id': event_channel_id, 'text': formatted_message} in discord_messaging.sent_channel_messages


async def test_post_saves_message_id_to_game():
    # Given
    guild_id = 1001
    game_id = 'game-1'
    channel_id = 50001

    new_message_id = 1000
    discord_messaging = FakeDiscordMessaging()
    discord_messaging.created_channel_message_id = 1000

    game = Game(guild_id=guild_id, game_id=game_id)
    games_repository = FakeGamesRepository([game])

    manage_route = ManageRoute(
        games_repository=games_repository,
        discord_messaging=discord_messaging,
        message_provider=MessageProvider(),
        command_authorizer=FakeCommandAuthorizer(passes=True)
    )

    # When
    event = _make_event(guild_id=guild_id, options={
        'game-id': game_id,
        'channel': channel_id,
    })
    await manage_route.post(event)

    # Then
    updated_game = games_repository.get(guild_id, game_id)
    assert updated_game.channel_messages is not None

    assert any(channel_message.channel_id == channel_id and channel_message.message_id == new_message_id
               for channel_message in updated_game.channel_messages)


async def test_post_invalid_game_id_sends_dm_error():
    # Given
    guild_id = 1001
    game_id = 'game-1'
    channel_id = 50001

    # We have no games
    games_repository = FakeGamesRepository([])
    discord_messaging = FakeDiscordMessaging()

    formatted_error = "mock formatted error"
    message_provider = MagicMock(MessageProvider)
    message_provider.dm_error_game_not_found.return_value = formatted_error

    manage_route = ManageRoute(
        games_repository=games_repository,
        discord_messaging=discord_messaging,
        message_provider=message_provider,
        command_authorizer=FakeCommandAuthorizer(passes=True)
    )

    discord_member = DiscordMember()

    # When
    event = _make_event(
        guild_id=guild_id,
        discord_member=discord_member,
        options={
            'game-id': game_id,
            'channel': channel_id,
        }
    )
    await manage_route.post(event)

    # Then
    message_provider.dm_error_game_not_found.assert_called_with(game_id)
    assert {'member': discord_member, 'text': formatted_error} in discord_messaging.sent_dms
    assert len(discord_messaging.sent_channel_messages) == 0


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


async def test_post_disallowed():
    # Given
    event_channel = 101
    event_role = 201

    member = DiscordMember(roles=[event_role])

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
            subcommand_name="post"
        ),
        member=member,
        channel_id=event_channel
    )

    # Then
    try:
        await manage_route.post(event)
        assert False
    except DiscordEventDisallowedError:
        pass


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


def _make_event(guild_id: int = -1, options: Dict = None, discord_member: DiscordMember = None):
    if options is None:
        options = {}

    if discord_member is None:
        discord_member = DiscordMember()

    return DiscordEvent(
        command_type=CommandType.COMMAND,
        guild_id=guild_id,
        command=DiscordCommand(
            command_id=-1,
            command_name="manage",
            subcommand_name="does-not-matter",
            options=options,
        ),
        member=discord_member
    )
