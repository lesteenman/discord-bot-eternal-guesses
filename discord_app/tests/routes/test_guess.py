from unittest.mock import patch

from eternal_guesses.model.data.game import Game
from eternal_guesses.model.discord_event import DiscordCommand, DiscordEvent, DiscordMember
from eternal_guesses.routes import guess


@patch.object(guess, 'games_repository')
def test_add_new_guess(mock_games_repository):
    # Given: the games_repository will find a game for the given id
    game_id = 'game-id'

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

    # When
    guess.call(event)

    # Then
    mock_games_repository.update.assert_called()

    saved_game = mock_games_repository.update.call_args[0][0]
    assert saved_game.guesses['other-user'] == '50'
    assert saved_game.guesses['user'] == '42'


@patch.object(guess, 'games_repository')
def test_guess_game_does_not_exist(mock_games_repository):
    mock_games_repository.get.return_value = None

    command = DiscordCommand()
    command.options = {
        'game-id': 'fun-game',
        'guess': '42'
    }

    member = DiscordMember()
    member.user_id = 'user'

    event = DiscordEvent()
    event.command = command
    event.member = member

    # When
    guess.call(event)

    # Then
    mock_games_repository.update.assert_not_called()


@patch.object(guess, 'games_repository')
def test_guess_duplicate_guess(mock_games_repository):
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
    mock_games_repository.update.assert_not_called()
