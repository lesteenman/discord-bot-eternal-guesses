from pprint import pprint
from typing import List
from unittest.mock import patch, MagicMock

import pytest

from eternal_guesses.discord_messaging import DiscordMessaging
from eternal_guesses.errors import DiscordEventDisallowedError
from eternal_guesses.model.data.game import Game, ChannelMessage
from eternal_guesses.model.data.guild_config import GuildConfig
from eternal_guesses.model.discord_event import DiscordEvent, DiscordCommand, DiscordMember, CommandType
from eternal_guesses.model.discord_response import ResponseType
from eternal_guesses.repositories.configs_repository import ConfigsRepository
from eternal_guesses.repositories.games_repository import GamesRepository
from eternal_guesses.routes import manage
from eternal_guesses.routes.manage import ManageRoute
from tests.fakes import FakeDiscordMessaging

pytestmark = pytest.mark.asyncio


@patch.object(manage, 'message_formatter', autospec=True)
async def test_post_creates_channel_message(mock_message_formatter):
    # Given
    guild_id = 1001
    game_id = 'game-1'
    channel_id = 50001

    formatted_message = "mock formatted message"
    mock_message_formatter.channel_list_game_guesses.return_value = formatted_message

    game = Game()
    mock_games_repository = MagicMock(GamesRepository, autospec=True)
    mock_games_repository.get.return_value = game

    fake_discord_messaging = FakeDiscordMessaging()
    fake_configs_repository = FakeConfigsRepository(management_channels=[channel_id])

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
    manage_route = ManageRoute(games_repository=mock_games_repository, discord_messaging=fake_discord_messaging,
                               configs_repository=fake_configs_repository)
    await manage_route.post(event)

    # Then
    mock_games_repository.get.assert_called_with(guild_id, game_id)
    mock_message_formatter.channel_list_game_guesses.assert_called_with(game)
    assert {'channel_id': channel_id, 'text': formatted_message} in fake_discord_messaging.sent_channel_messages

    mock_games_repository.save.assert_called()
    saved_game = mock_games_repository.save.call_args.args[0]
    assert len(saved_game.channel_messages) == 1


@patch.object(manage, 'message_formatter', autospec=True)
async def test_post_without_channel_uses_event_channel(mock_message_formatter):
    # Given
    guild_id = 1001
    game_id = 'game-1'
    event_channel_id = 50001

    formatted_message = "mock formatted message"
    mock_message_formatter.channel_list_game_guesses.return_value = formatted_message

    game = Game()
    mock_games_repository = MagicMock(GamesRepository, autospec=True)
    mock_games_repository.get.return_value = game

    fake_discord_messaging = FakeDiscordMessaging()
    fake_configs_repository = FakeConfigsRepository(management_channels=[event_channel_id])

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
    manage_route = ManageRoute(games_repository=mock_games_repository, discord_messaging=fake_discord_messaging,
                               configs_repository=fake_configs_repository)
    await manage_route.post(event)

    # Then
    mock_games_repository.get.assert_called_with(guild_id, game_id)
    mock_message_formatter.channel_list_game_guesses.assert_called_with(game)
    assert {'channel_id': event_channel_id, 'text': formatted_message} in fake_discord_messaging.sent_channel_messages


async def test_post_saves_message_id_to_game():
    # Given
    guild_id = 1001
    game_id = 'game-1'
    channel_id = 50001

    new_message_id = 1000
    fake_discord_messaging = FakeDiscordMessaging()
    fake_discord_messaging.created_channel_message_id = 1000

    fake_configs_repository = FakeConfigsRepository(management_channels=[channel_id])

    game = Game()
    game.game_id = game_id

    mock_games_repository = MagicMock(GamesRepository, autospec=True)
    mock_games_repository.get.return_value = game

    event = DiscordEvent(
        command_type=CommandType.COMMAND,
        guild_id=guild_id,
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
    manage_route = ManageRoute(games_repository=mock_games_repository, discord_messaging=fake_discord_messaging,
                               configs_repository=fake_configs_repository)
    await manage_route.post(event)

    # Then
    mock_games_repository.save.assert_called()

    args = mock_games_repository.save.call_args.args
    updated_game = args[0]
    assert updated_game.channel_messages is not None

    pprint(updated_game.channel_messages)
    pprint(ChannelMessage(channel_id, new_message_id))
    assert any(channel_message.channel_id == channel_id and channel_message.message_id == new_message_id
               for channel_message in updated_game.channel_messages)


@patch.object(manage, 'message_formatter', autospec=True)
async def test_post_invalid_game_id_sends_dm_error(mock_message_formatter):
    # Given
    guild_id = 1001
    game_id = 'game-1'
    channel_id = 50001

    fake_discord_messaging = FakeDiscordMessaging()
    fake_configs_repository = FakeConfigsRepository(management_channels=[channel_id])

    formatted_error = "mock formatted error"
    mock_message_formatter.dm_error_game_not_found.return_value = formatted_error

    mock_games_repository = MagicMock(GamesRepository, autospec=True)
    mock_games_repository.get.return_value = None

    event = DiscordEvent(
        command_type=CommandType.COMMAND,
        guild_id=guild_id,
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
    manage_route = ManageRoute(games_repository=mock_games_repository, discord_messaging=fake_discord_messaging,
                               configs_repository=fake_configs_repository)
    await manage_route.post(event)

    # Then
    mock_message_formatter.dm_error_game_not_found.assert_called_with(game_id)
    assert {'member': (DiscordMember()), 'text': formatted_error} in fake_discord_messaging.sent_dms
    assert len(fake_discord_messaging.sent_channel_messages) == 0


@patch.object(manage, 'message_formatter', autospec=True)
async def test_list_all_without_closed_option(mock_message_formatter):
    # Given
    guild_id = 100
    role_id = 500

    list_games_message = "message listing all games, open and closed"
    mock_message_formatter.channel_manage_list_all_games.return_value = list_games_message

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

    open_game = Game()
    open_game.closed = False

    closed_game = Game()
    closed_game.closed = True

    games = [open_game, closed_game]
    mock_games_repository = MagicMock(GamesRepository, autospec=True)
    mock_games_repository.get_all.return_value = games

    fake_configs_repository = FakeConfigsRepository(management_roles=[role_id])

    # When
    manage_route = ManageRoute(games_repository=mock_games_repository, discord_messaging=FakeDiscordMessaging(),
                               configs_repository=fake_configs_repository)
    discord_response = await manage_route.list_games(event)

    # Then
    mock_message_formatter.channel_manage_list_all_games.assert_called()
    used_games = mock_message_formatter.channel_manage_list_all_games.call_args.args[0]
    assert closed_game in used_games
    assert open_game in used_games

    assert discord_response.type == ResponseType.CHANNEL_MESSAGE
    assert discord_response.content == list_games_message


@patch.object(manage, 'message_formatter', autospec=True)
async def test_list_all_closed_games(mock_message_formatter):
    # Given
    guild_id = 100
    role_id = 500

    list_games_message = "message listing all games, open and closed"
    mock_message_formatter.channel_manage_list_closed_games.return_value = list_games_message

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

    open_game = Game()
    open_game.closed = False

    closed_game = Game()
    closed_game.closed = True

    games = [open_game, closed_game]
    mock_games_repository = MagicMock(GamesRepository, autospec=True)
    mock_games_repository.get_all.return_value = games

    fake_configs_repository = FakeConfigsRepository(management_roles=[role_id])

    # When
    manage_route = ManageRoute(games_repository=mock_games_repository, discord_messaging=FakeDiscordMessaging(),
                               configs_repository=fake_configs_repository)
    discord_response = await manage_route.list_games(event)

    # Then
    mock_message_formatter.channel_manage_list_closed_games.assert_called()
    used_games = mock_message_formatter.channel_manage_list_closed_games.call_args.args[0]
    assert closed_game in used_games
    assert open_game not in used_games

    assert discord_response.type == ResponseType.CHANNEL_MESSAGE
    assert discord_response.content == list_games_message


@patch.object(manage, 'message_formatter', autospec=True)
async def test_list_all_open_games(mock_message_formatter):
    # Given
    guild_id = 100
    role_id = 500

    list_games_message = "message listing all games, open and closed"
    mock_message_formatter.channel_manage_list_open_games.return_value = list_games_message

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

    open_game = Game()
    open_game.closed = False

    closed_game = Game()
    closed_game.closed = True
    games = [open_game, closed_game]
    mock_games_repository = MagicMock(GamesRepository, autospec=True)
    mock_games_repository.get_all.return_value = games

    fake_configs_repository = FakeConfigsRepository(management_roles=[role_id])

    # When
    manage_route = ManageRoute(games_repository=mock_games_repository, discord_messaging=FakeDiscordMessaging(),
                               configs_repository=fake_configs_repository)
    discord_response = await manage_route.list_games(event)

    # Then
    mock_message_formatter.channel_manage_list_open_games.assert_called()
    used_games = mock_message_formatter.channel_manage_list_open_games.call_args.args[0]
    assert closed_game not in used_games
    assert open_game in used_games

    assert discord_response.type == ResponseType.CHANNEL_MESSAGE
    assert discord_response.content == list_games_message


class FakeConfigsRepository(ConfigsRepository):
    def __init__(self, management_channels: List[int] = None, management_roles: List[int] = None):
        if management_channels is None:
            management_channels = []

        if management_roles is None:
            management_roles = []

        self.management_channels = management_channels
        self.management_roles = management_roles

    def get(self, guild_id: int) -> GuildConfig:
        return GuildConfig(
            guild_id=guild_id,
            management_channels=self.management_channels,
            management_roles=self.management_roles
        )


async def test_post_disallowed():
    # Given
    management_channel = 100
    event_channel = 101
    management_role = 200
    event_role = 201
    test_config_repository = FakeConfigsRepository(management_channels=[management_channel],
                                                   management_roles=[management_role])

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

    manage_route = ManageRoute(configs_repository=test_config_repository, games_repository=GamesRepository(),
                               discord_messaging=DiscordMessaging())
    try:
        await manage_route.list_games(event)
        assert False
    except DiscordEventDisallowedError:
        pass


async def test_list_disallowed():
    assert False


async def test_close_disallowed():
    assert False
