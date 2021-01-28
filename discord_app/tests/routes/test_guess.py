from unittest.mock import patch, MagicMock

from eternal_guesses.model.data.game import Game
from eternal_guesses.model.discord_event import DiscordCommand, DiscordEvent, DiscordMember
from eternal_guesses.routes import guess


@patch.object(guess, 'games_repository', autospec=True)
def test_add_new_guess(mock_games_repository):
    # Given: the games_repository will find a game for the given id
    game_id = 'game-id'
    guild_id = 'guild-1'

    existing_game = Game()
    existing_game.game_id = game_id
    existing_game.guesses = {
        'other-user': '50',
    }
    mock_games_repository.get.return_value = existing_game

    # And: we add our guess '42'
    command = DiscordCommand()
    command.options = {
        'game-id': game_id,
        'guess': '42'
    }

    member = DiscordMember()
    member.user_id = 'user'

    event = DiscordEvent()
    event.command = command
    event.member = member
    event.guild_id = guild_id

    # When
    guess.call(event)

    # Then
    mock_games_repository.get.assert_called_with(guild_id, game_id)

    mock_games_repository.put.assert_called()
    call_args = mock_games_repository.put.call_args

    save_guild_id = call_args[0][0]
    assert save_guild_id == guild_id

    saved_game = call_args[0][1]
    assert saved_game.guesses['other-user'] == '50'
    assert saved_game.guesses['user'] == '42'


@patch.object(guess, 'discord_messaging', autospec=True)
@patch.object(guess, 'games_repository', autospec=True)
def test_guess_game_does_not_exist(mock_games_repository: MagicMock, mock_discord_messaging: MagicMock):
    # Given
    guild_id = 'guild-3'
    game_id = 'fun-game'

    mock_games_repository.get.return_value = None

    command = DiscordCommand()
    command.options = {
        'game-id': game_id,
        'guess': '42'
    }

    member = DiscordMember()
    member.user_id = 'user'

    event = DiscordEvent()
    event.guild_id = guild_id
    event.command = command
    event.member = member

    # When
    guess.call(event)

    # Then
    mock_games_repository.get.assert_called_with(guild_id, game_id)
    mock_games_repository.put.assert_not_called()

    mock_discord_messaging.send_dm.assert_called()
    sent_member = mock_discord_messaging.send_dm.call_args.args[0]
    assert sent_member.user_id == member.user_id


@patch.object(guess, 'discord_messaging', autospec=True)
@patch.object(guess, 'games_repository', autospec=True)
def test_guess_duplicate_guess(mock_games_repository, mock_discord_messaging):
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
    guess.call(event)

    # Then
    mock_games_repository.put.assert_not_called()

    mock_discord_messaging.send_dm.assert_called()
    sent_member = mock_discord_messaging.send_dm.call_args.args[0]
    assert sent_member.user_id == member.user_id
