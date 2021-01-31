from unittest.mock import patch, MagicMock, call

import pytest
from eternal_guesses.model.data.game import Game, ChannelMessage
from eternal_guesses.model.discord_event import DiscordCommand, DiscordEvent, DiscordMember
from eternal_guesses.routes import guess

pytestmark = pytest.mark.asyncio


@patch.object(guess, 'discord_messaging', autospec=True)
@patch.object(guess, 'GamesRepository', autospec=True)
async def test_guess_updates_game_guesses(mock_games_repository, mock_discord_messaging):
    # Given
    game_id = 'game-id'
    guild_id = 'guild-1'
    user_id = 'user-1'

    existing_game = Game()
    existing_game.game_id = game_id
    existing_game.guesses = {
        'other-user': '50',
    }
    mock_games_repository.get.return_value = existing_game

    # When
    event = create_guess_event(guild_id, game_id, user_id)
    await guess.call(event)

    # Then
    mock_games_repository.get.assert_called_with(guild_id, game_id)

    mock_games_repository.save.assert_called()
    call_args = mock_games_repository.save.call_args

    save_guild_id = call_args[0][0]
    assert save_guild_id == guild_id

    saved_game = call_args[0][1]
    assert saved_game.guesses['other-user'] == '50'
    assert saved_game.guesses[user_id] == '42'


@patch.object(guess, 'message_formatter', autospec=True)
@patch.object(guess, 'discord_messaging', autospec=True)
@patch.object(guess, 'GamesRepository', autospec=True)
async def test_guess_updates_channel_messages(mock_games_repository, mock_discord_messaging, mock_message_formatter):
    # Given
    user_id = 'user-id-2'
    channel_message_1 = ChannelMessage(1000, 5000)
    channel_message_2 = ChannelMessage(1005, 5005)

    list_guesses_message = "message with new gues"
    mock_message_formatter.channel_list_game_guesses.return_value = list_guesses_message

    game = Game()
    game.game_id = 'game-id'
    game.channel_messages = [channel_message_1, channel_message_2]
    mock_games_repository.get.return_value = game

    # When
    event = create_guess_event('guild-id', game.game_id, user_id)
    await guess.call(event)

    # Then
    update_channel_message_calls = mock_discord_messaging.update_channel_message.call_args_list
    assert len(update_channel_message_calls) == 2
    assert call(channel_message_1.channel_id, channel_message_1.message_id,
                list_guesses_message) in update_channel_message_calls
    assert call(channel_message_1.channel_id, channel_message_1.message_id,
                list_guesses_message) in update_channel_message_calls

    mock_message_formatter.channel_list_game_guesses.assert_called()
    assert user_id in mock_message_formatter.channel_list_game_guesses.call_args.args[0].guesses.keys(
    )


@patch.object(guess, 'message_formatter', autospec=True)
@patch.object(guess, 'discord_messaging', autospec=True)
@patch.object(guess, 'GamesRepository', autospec=True)
async def test_guess_sends_dm_to_user(mock_games_repository, mock_discord_messaging, mock_message_formatter):
    # Given
    user_id = 'user-3'

    dm_message = "message with new gues"
    mock_message_formatter.dm_guess_added.return_value = dm_message

    game = Game()
    game.game_id = 'game-id'
    mock_games_repository.get.return_value = game

    # When
    event = create_guess_event('guild-id', game.game_id, user_id)
    await guess.call(event)

    # Then
    mock_discord_messaging.send_dm.assert_called_with(event.member, dm_message)


@patch.object(guess, 'message_formatter', autospec=True)
@patch.object(guess, 'discord_messaging', autospec=True)
@patch.object(guess, 'GamesRepository', autospec=True)
async def test_guess_game_does_not_exist(mock_games_repository: MagicMock, mock_discord_messaging: MagicMock,
                                         mock_message_formatter: MagicMock):
    # Given
    guild_id = 'guild-3'
    game_id = 'fun-game'
    user_id = 'user-5'

    mock_games_repository.get.return_value = None

    event = create_guess_event(guild_id, game_id, user_id)

    dm_error = "error dm"
    mock_message_formatter.dm_error_game_not_found.return_value = dm_error

    # When
    await guess.call(event)

    # Then
    mock_games_repository.get.assert_called_with(guild_id, game_id)
    mock_games_repository.save.assert_not_called()

    mock_discord_messaging.send_dm.assert_called_with(event.member, dm_error)


@patch.object(guess, 'discord_messaging', autospec=True)
@patch.object(guess, 'GamesRepository', autospec=True)
async def test_guess_duplicate_guess(mock_games_repository, mock_discord_messaging):
    # Given
    game_id = 'game-id'

    existing_game = Game()
    existing_game.game_id = game_id
    existing_game.guesses = {
        'user': '100',
    }
    mock_games_repository.get.return_value = existing_game

    # And: we add our guess '42'
    command = DiscordCommand()
    command.options = {
        'game-id': game_id,
        'guess': '150'
    }

    member = DiscordMember()
    member.user_id = 'user'

    event = DiscordEvent()
    event.command = command
    event.member = member

    # When
    await guess.call(event)

    # Then
    mock_games_repository.save.assert_not_called()

    mock_discord_messaging.send_dm.assert_called()
    sent_member = mock_discord_messaging.send_dm.call_args.args[0]
    assert sent_member.user_id == member.user_id


def create_guess_event(guild_id, game_id, user_id):
    command = DiscordCommand()
    command.options = {
        'game-id': game_id,
        'guess': '42'
    }
    member = DiscordMember()
    member.user_id = user_id
    event = DiscordEvent()
    event.command = command
    event.member = member
    event.guild_id = guild_id
    return event
