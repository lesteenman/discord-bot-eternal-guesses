from pprint import pprint
from unittest.mock import MagicMock

import pytest

from eternal_guesses.discord_messaging import DiscordMessaging
from eternal_guesses.errors import DiscordEventDisallowedError
from eternal_guesses.model.data.game import Game, ChannelMessage
from eternal_guesses.model.discord_event import DiscordEvent, DiscordCommand, CommandType
from eternal_guesses.model.discord_member import DiscordMember
from eternal_guesses.model.discord_response import ResponseType
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

    formatted_message = "mock formatted message"
    message_provider = MagicMock(MessageProvider)
    message_provider.channel_list_game_guesses.return_value = formatted_message
    game = Game(guild_id=guild_id, game_id=game_id)

    games_repository = FakeGamesRepository([game])
    discord_messaging = FakeDiscordMessaging()
    command_authorizer = FakeCommandAuthorizer(passes=True)

    event = DiscordEvent(
        command_type=CommandType.COMMAND,
        guild_id=guild_id,
        channel_id=channel_id,
        command=DiscordCommand(
            command_id="-1",
            command_name="manage",
            subcommand_name="post",
            options={
                'game-id': game_id,
                'channel': channel_id,
            }
        ),
        member=DiscordMember()
    )

    # When
    manage_route = ManageRoute(games_repository=games_repository, discord_messaging=discord_messaging,
                               message_provider=message_provider, command_authorizer=command_authorizer)
    await manage_route.post(event)

    # Then
    message_provider.channel_list_game_guesses.assert_called_with(game)
    assert {'channel_id': channel_id, 'text': formatted_message} in discord_messaging.sent_channel_messages

    saved_game = games_repository.get(guild_id, game_id)
    assert len(saved_game.channel_messages) == 1


async def test_post_without_channel_uses_event_channel():
    # Given
    guild_id = 1001
    game_id = 'game-1'
    event_channel_id = 50001

    formatted_message = "mock formatted message"
    message_provider = MagicMock(MessageProvider)
    message_provider.channel_list_game_guesses.return_value = formatted_message
    game = Game(guild_id=guild_id, game_id=game_id)

    games_repository = FakeGamesRepository([game])
    discord_messaging = FakeDiscordMessaging()
    command_authorizer = FakeCommandAuthorizer(passes=True)

    event = DiscordEvent(
        command_type=CommandType.COMMAND,
        guild_id=guild_id,
        channel_id=event_channel_id,
        command=DiscordCommand(
            command_id="-1",
            command_name="manage",
            subcommand_name="post",
            options={
                'game-id': game_id,
            }
        ),
        member=DiscordMember()
    )

    # When
    manage_route = ManageRoute(games_repository=games_repository, discord_messaging=discord_messaging,
                               message_provider=message_provider, command_authorizer=command_authorizer)
    await manage_route.post(event)

    # Then
    message_provider.channel_list_game_guesses.assert_called_with(game)
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

    command_authorizer = FakeCommandAuthorizer(passes=True)

    event = DiscordEvent(
        command_type=CommandType.COMMAND,
        guild_id=guild_id,
        channel_id=channel_id,
        member=DiscordMember(),
        command=DiscordCommand(
            command_id="-1",
            command_name="manage",
            subcommand_name="post",
            options={
                'game-id': game_id,
                'channel': channel_id,
            }
        )
    )

    # When
    manage_route = ManageRoute(games_repository=games_repository, discord_messaging=discord_messaging,
                               message_provider=MessageProvider(), command_authorizer=command_authorizer)
    await manage_route.post(event)

    # Then
    updated_game = games_repository.get(guild_id, game_id)
    assert updated_game.channel_messages is not None

    pprint(updated_game.channel_messages)
    pprint(ChannelMessage(channel_id, new_message_id))
    assert any(channel_message.channel_id == channel_id and channel_message.message_id == new_message_id
               for channel_message in updated_game.channel_messages)


async def test_post_invalid_game_id_sends_dm_error():
    # Given
    guild_id = 1001
    game_id = 'game-1'
    channel_id = 50001

    games_repository = FakeGamesRepository([])
    discord_messaging = FakeDiscordMessaging()
    command_authorizer = FakeCommandAuthorizer(passes=True)

    formatted_error = "mock formatted error"
    message_provider = MagicMock(MessageProvider)
    message_provider.dm_error_game_not_found.return_value = formatted_error

    discord_member = DiscordMember()

    event = DiscordEvent(
        command_type=CommandType.COMMAND,
        guild_id=guild_id,
        channel_id=channel_id,
        command=DiscordCommand(
            command_id="-1",
            command_name="manage",
            subcommand_name="post",
            options={
                'game-id': game_id,
                'channel': channel_id,
            }
        ),
        member=discord_member
    )

    # When
    manage_route = ManageRoute(games_repository=games_repository, discord_messaging=discord_messaging,
                               message_provider=message_provider, command_authorizer=command_authorizer)
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

    event = DiscordEvent(
        command_type=CommandType.COMMAND,
        guild_id=guild_id,
        command=DiscordCommand(
            command_id="-1",
            command_name="manage",
            subcommand_name="list",
            options={}
        ),
        member=DiscordMember(roles=[role_id])
    )

    open_game = Game(closed=False)
    closed_game = Game(closed=True)

    games_repository = FakeGamesRepository([open_game, closed_game])

    command_authorizer = FakeCommandAuthorizer(passes=True)

    # When
    manage_route = ManageRoute(games_repository=games_repository, discord_messaging=FakeDiscordMessaging(),
                               message_provider=message_provider, command_authorizer=command_authorizer)
    discord_response = await manage_route.list_games(event)

    # Then
    message_provider.channel_manage_list_all_games.assert_called()
    used_games = message_provider.channel_manage_list_all_games.call_args.args[0]
    assert closed_game in used_games
    assert open_game in used_games

    assert discord_response.response_type == ResponseType.CHANNEL_MESSAGE
    assert discord_response.content == list_games_message


async def test_list_all_closed_games():
    # Given
    guild_id = 100
    role_id = 500

    list_games_message = "message listing all games, open and closed"
    message_provider = MagicMock(MessageProvider)
    message_provider.channel_manage_list_closed_games.return_value = list_games_message

    event = DiscordEvent(
        command_type=CommandType.COMMAND,
        guild_id=guild_id,
        command=DiscordCommand(
            command_id="-1",
            command_name="manage",
            subcommand_name="list",
            options={
                'closed': True
            }
        ),
        member=DiscordMember(roles=[role_id])
    )

    open_game = Game(closed=False)
    closed_game = Game(closed=True)

    games_repository = FakeGamesRepository([open_game, closed_game])

    command_authorizer = FakeCommandAuthorizer(passes=True)

    # When
    manage_route = ManageRoute(games_repository=games_repository, discord_messaging=FakeDiscordMessaging(),
                               message_provider=message_provider, command_authorizer=command_authorizer)
    discord_response = await manage_route.list_games(event)

    # Then
    message_provider.channel_manage_list_closed_games.assert_called()
    used_games = message_provider.channel_manage_list_closed_games.call_args.args[0]
    assert closed_game in used_games
    assert open_game not in used_games

    assert discord_response.response_type == ResponseType.CHANNEL_MESSAGE
    assert discord_response.content == list_games_message


async def test_list_all_open_games():
    # Given
    guild_id = 100
    role_id = 500

    list_games_message = "message listing all games, open and closed"
    message_provider = MagicMock(MessageProvider)
    message_provider.channel_manage_list_open_games.return_value = list_games_message

    event = DiscordEvent(
        command_type=CommandType.COMMAND,
        guild_id=guild_id,
        command=DiscordCommand(
            command_id="-1",
            command_name="manage",
            subcommand_name="list",
            options={
                'closed': False
            }
        ),
        member=DiscordMember(roles=[role_id])
    )

    open_game = Game(closed=False)
    closed_game = Game(closed=True)
    games_repository = FakeGamesRepository([open_game, closed_game])

    command_authorizer = FakeCommandAuthorizer(passes=True)

    # When
    manage_route = ManageRoute(games_repository=games_repository, discord_messaging=FakeDiscordMessaging(),
                               message_provider=message_provider, command_authorizer=command_authorizer)
    discord_response = await manage_route.list_games(event)

    # Then
    message_provider.channel_manage_list_open_games.assert_called()
    used_games = message_provider.channel_manage_list_open_games.call_args.args[0]
    assert closed_game not in used_games
    assert open_game in used_games

    assert discord_response.response_type == ResponseType.CHANNEL_MESSAGE
    assert discord_response.content == list_games_message


async def test_post_disallowed():
    # Given
    event_channel = 101
    event_role = 201

    member = DiscordMember(roles=[event_role])

    event = DiscordEvent(
        command_type=CommandType.COMMAND,
        guild_id=-1,
        command=DiscordCommand(
            command_id="-1",
            command_name="manage",
            subcommand_name="post"
        ),
        member=member,
        channel_id=event_channel
    )

    command_authorizer = FakeCommandAuthorizer(passes=False)

    manage_route = ManageRoute(games_repository=GamesRepository(), discord_messaging=DiscordMessaging(),
                               message_provider=MessageProvider(), command_authorizer=command_authorizer)

    # Then
    try:
        await manage_route.post(event)
        assert False
    except DiscordEventDisallowedError:
        pass


async def test_list_disallowed():
    # Given
    command_authorizer = FakeCommandAuthorizer(passes=False)

    event = DiscordEvent(
        command_type=CommandType.COMMAND,
        guild_id=-1,
        command=DiscordCommand(
            command_id="-1",
            command_name="manage",
            subcommand_name="list"
        ),
        member=DiscordMember(),
        channel_id=101
    )

    manage_route = ManageRoute(
        command_authorizer=command_authorizer,
        games_repository=GamesRepository(),
        discord_messaging=DiscordMessaging(),
        message_provider=MessageProvider()
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

    event = DiscordEvent(
        command_type=CommandType.COMMAND,
        guild_id=-1,
        command=DiscordCommand(
            command_id="-1",
            command_name="manage",
            subcommand_name="close"
        ),
        member=DiscordMember(),
        channel_id=101
    )

    manage_route = ManageRoute(games_repository=GamesRepository(), discord_messaging=DiscordMessaging(),
                               message_provider=MessageProvider(), command_authorizer=command_authorizer)

    # Then
    try:
        await manage_route.close(event)
        assert False
    except DiscordEventDisallowedError:
        pass
