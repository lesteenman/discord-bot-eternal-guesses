from pprint import pprint
from unittest.mock import patch

import pytest
from eternal_guesses.model.data.game import Game, ChannelMessage
from eternal_guesses.model.discord_event import DiscordEvent, DiscordCommand, DiscordMember
from eternal_guesses.routes import manage
from eternal_guesses.model.discord_response import ResponseType

pytestmark = pytest.mark.asyncio


@patch.object(manage, 'message_formatter', autospec=True)
@patch.object(manage, 'GamesRepository', autospec=True)
@patch.object(manage, 'discord_messaging', autospec=True)
async def test_post_creates_channel_message(mock_discord_messaging, mock_games_repository, mock_message_formatter):
    # Given
    guild_id = 'guild-1'
    game_id = 'game-1'
    channel_id = 50001

    formatted_message = "mock formatted message"
    mock_message_formatter.channel_list_game_guesses.return_value = formatted_message

    game = Game()
    mock_games_repository.get.return_value = game

    command = DiscordCommand()
    command.options = {
        'game-id': game_id,
        'channel': channel_id,
    }

    event = DiscordEvent()
    event.guild_id = guild_id
    event.command = command

    # When
    await manage.post(event)

    # Then
    mock_games_repository.get.assert_called_with(guild_id, game_id)
    mock_message_formatter.channel_list_game_guesses.assert_called_with(game)
    mock_discord_messaging.create_channel_message.assert_called_with(
        channel_id, formatted_message)

    mock_games_repository.save.assert_called()
    saved_guild_id = mock_games_repository.save.call_args.args[0]
    saved_game = mock_games_repository.save.call_args.args[1]
    assert saved_guild_id == guild_id
    assert len(saved_game.channel_messages) == 1


@patch.object(manage, 'message_formatter', autospec=True)
@patch.object(manage, 'GamesRepository', autospec=True)
@patch.object(manage, 'discord_messaging', autospec=True)
async def test_post_without_channel_uses_event_channel(mock_discord_messaging, mock_games_repository,
                                                       mock_message_formatter):
    # Given
    guild_id = 'guild-1'
    game_id = 'game-1'
    event_channel_id = 50001

    formatted_message = "mock formatted message"
    mock_message_formatter.channel_list_game_guesses.return_value = formatted_message

    game = Game()
    mock_games_repository.get.return_value = game

    command = DiscordCommand()
    command.options = {
        'game-id': game_id,
    }

    event = DiscordEvent()
    event.guild_id = guild_id
    event.channel_id = event_channel_id
    event.command = command

    # When
    await manage.post(event)

    # Then
    mock_games_repository.get.assert_called_with(guild_id, game_id)
    mock_message_formatter.channel_list_game_guesses.assert_called_with(game)
    mock_discord_messaging.create_channel_message.assert_called_with(event_channel_id, formatted_message)


@patch.object(manage, 'GamesRepository', autospec=True)
@patch.object(manage, 'discord_messaging', autospec=True)
async def test_post_saves_message_id_to_game(mock_discord_messaging, mock_games_repository):
    # Given
    guild_id = 'guild-1'
    game_id = 'game-1'
    channel_id = 50001

    new_message_id = 1000
    mock_discord_messaging.create_channel_message.return_value = new_message_id

    game = Game()
    game.game_id = game_id
    mock_games_repository.get.return_value = game

    command = DiscordCommand()
    command.options = {
        'game-id': game_id,
        'channel': channel_id,
    }

    event = DiscordEvent()
    event.guild_id = guild_id
    event.command = command

    # When
    await manage.post(event)

    # Then
    mock_games_repository.save.assert_called()

    args = mock_games_repository.save.call_args.args

    assert args[0] == guild_id

    updated_game = args[1]
    assert updated_game.channel_messages is not None

    pprint(updated_game.channel_messages)
    pprint(ChannelMessage(channel_id, new_message_id))
    assert any(channel_message.channel_id == channel_id and channel_message.message_id == new_message_id
               for channel_message in updated_game.channel_messages)


@patch.object(manage, 'message_formatter', autospec=True)
@patch.object(manage, 'GamesRepository', autospec=True)
@patch.object(manage, 'discord_messaging', autospec=True)
async def test_post_invalid_game_id_sends_dm_error(mock_discord_messaging, mock_games_repository,
                                                   mock_message_formatter):
    # Given
    guild_id = 'guild-1'
    game_id = 'game-1'
    channel_id = 50001

    formatted_error = "mock formatted error"
    mock_message_formatter.dm_error_game_not_found.return_value = formatted_error

    mock_games_repository.get.return_value = None

    command = DiscordCommand()
    command.options = {
        'game-id': game_id,
        'channel': channel_id,
    }

    member = DiscordMember()

    event = DiscordEvent()
    event.guild_id = guild_id
    event.command = command
    event.member = member

    # When
    await manage.post(event)

    # Then
    mock_message_formatter.dm_error_game_not_found.assert_called_with(game_id)
    mock_discord_messaging.send_dm.assert_called_with(member, formatted_error)

    mock_discord_messaging.create_channel_message.assert_not_called()


@patch.object(manage, 'message_formatter', autospec=True)
@patch.object(manage, 'GamesRepository', autospec=True)
async def test_list_all_without_closed_option(mock_games_repository, mock_message_formatter):
    # Given
    guild_id = 100

    list_games_message = "message listing all games, open and closed"
    mock_message_formatter.channel_manage_list_all_games.return_value = list_games_message

    command = DiscordCommand()
    command.options = {}

    member = DiscordMember()

    event = DiscordEvent()
    event.guild_id = guild_id
    event.command = command
    event.member = member

    open_game = Game()
    open_game.closed = False

    closed_game = Game()
    closed_game.closed = True

    games = [open_game, closed_game]
    mock_games_repository.get_all.return_value = games

    # When
    discord_response = await manage.list_games(event)

    # Then
    mock_message_formatter.channel_manage_list_all_games.assert_called()
    used_games = mock_message_formatter.channel_manage_list_all_games.call_args.args[0]
    assert closed_game in used_games
    assert open_game in used_games

    assert discord_response.type == ResponseType.CHANNEL_MESSAGE
    assert discord_response.content == list_games_message


@patch.object(manage, 'message_formatter', autospec=True)
@patch.object(manage, 'GamesRepository', autospec=True)
async def test_list_all_closed_games(mock_games_repository, mock_message_formatter):
    # Given
    guild_id = 100

    list_games_message = "message listing all games, open and closed"
    mock_message_formatter.channel_manage_list_closed_games.return_value = list_games_message

    command = DiscordCommand()
    command.options = {
        'closed': True
    }

    member = DiscordMember()

    event = DiscordEvent()
    event.guild_id = guild_id
    event.command = command
    event.member = member

    open_game = Game()
    open_game.closed = False

    closed_game = Game()
    closed_game.closed = True

    games = [open_game, closed_game]
    mock_games_repository.get_all.return_value = games

    # When
    discord_response = await manage.list_games(event)

    # Then
    mock_message_formatter.channel_manage_list_closed_games.assert_called()
    used_games = mock_message_formatter.channel_manage_list_closed_games.call_args.args[0]
    assert closed_game in used_games
    assert open_game not in used_games

    assert discord_response.type == ResponseType.CHANNEL_MESSAGE
    assert discord_response.content == list_games_message


@patch.object(manage, 'message_formatter', autospec=True)
@patch.object(manage, 'GamesRepository', autospec=True)
async def test_list_all_open_games(mock_games_repository, mock_message_formatter):
    # Given
    guild_id = 100

    list_games_message = "message listing all games, open and closed"
    mock_message_formatter.channel_manage_list_open_games.return_value = list_games_message

    command = DiscordCommand()
    command.options = {
        'closed': False
    }

    member = DiscordMember()

    event = DiscordEvent()
    event.guild_id = guild_id
    event.command = command
    event.member = member

    open_game = Game()
    open_game.closed = False

    closed_game = Game()
    closed_game.closed = True
    games = [open_game, closed_game]
    mock_games_repository.get_all.return_value = games

    # When
    discord_response = await manage.list_games(event)

    # Then
    mock_message_formatter.channel_manage_list_open_games.assert_called()
    used_games = mock_message_formatter.channel_manage_list_open_games.call_args.args[0]
    assert closed_game not in used_games
    assert open_game in used_games

    assert discord_response.type == ResponseType.CHANNEL_MESSAGE
    assert discord_response.content == list_games_message
