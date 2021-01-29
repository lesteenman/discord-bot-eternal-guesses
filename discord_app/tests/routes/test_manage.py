from unittest.mock import patch

import pytest
from eternal_guesses.model.data.game import Game
from eternal_guesses.model.discord_event import DiscordEvent, DiscordCommand, DiscordMember
from eternal_guesses.routes import manage

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
    mock_discord_messaging.create_channel_message.assert_called_with(channel_id, formatted_message)


@patch.object(manage, 'GamesRepository', autospec=True)
@patch.object(manage, 'discord_messaging', autospec=True)
async def test_post_saves_message_id_to_game(mock_discord_messaging, mock_games_repository):
    # Given
    guild_id = 'guild-1'
    game_id = 'game-1'
    channel_id = 50001

    channel_message_id = 1000
    mock_discord_messaging.create_channel_message.return_value = channel_message_id

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
    assert channel_message_id in updated_game.channel_messages


@patch.object(manage, 'message_formatter', autospec=True)
@patch.object(manage, 'GamesRepository', autospec=True)
@patch.object(manage, 'discord_messaging', autospec=True)
async def test_post_invalid_game_id_sends_dm_error(mock_discord_messaging, mock_games_repository, mock_message_formatter):
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
